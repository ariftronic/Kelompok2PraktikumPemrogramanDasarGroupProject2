from datetime import date, timedelta
from app import validasi
from app.file_manager import FileManagerError
from app.konstanta import FILE_ALAT, FILE_TRANSAKSI, FILE_DETAIL_TRANSAKSI, FORMAT_TANGGAL, KONDISI_BAIK, MAKS_HARI_PINJAM, MAKS_TRANSAKSI_AKTIF, STATUS_TERSEDIA, STATUS_DIPINJAM, STATUS_TIDAK_TERSEDIA
from app.models.transaksi import Transaksi, DetailTransaksi

class ManagerTransaksi:

    def __init__(self, file_manager, logger, manager_mahasiswa, manager_alat):
        self.file_manager = file_manager
        self.logger = logger
        self.manager_mahasiswa = manager_mahasiswa
        self.manager_alat = manager_alat
        self.data_transaksi = {}

    @staticmethod
    def _kunci(teks):
        return validasi.rapikan(teks).upper()

    def _cari_mahasiswa(self, nim):
        nim = self._kunci(nim)
        return next((m for m in self.manager_mahasiswa.semua() if m.nim == nim), None)

    def _cari_alat(self, kode):
        kode = self._kunci(kode)
        return next((a for a in self.manager_alat.semua() if a.kode == kode), None)

    def _jumlah_aktif(self, nim):
        nim = self._kunci(nim)
        return sum((1 for t in self.data_transaksi.values() if t.nim == nim and t.masih_aktif()))

    def _id_baru(self):
        angka = [int(i[1:]) for i in self.data_transaksi if i[1:].isdigit()]
        return 'T%03d' % (max(angka, default=0) + 1)

    def muat(self):
        self.data_transaksi = {}
        daftar_nim = {m.nim for m in self.manager_mahasiswa.semua()}
        daftar_kode = {a.kode for a in self.manager_alat.semua()}
        for kolom in self.file_manager.baca_baris(FILE_TRANSAKSI):
            try:
                transaksi = Transaksi.dari_baris(kolom)
            except ValueError as e:
                self.file_manager.catat_peringatan(FILE_TRANSAKSI, 'baris dilewati (%s): %s' % (e, '|'.join(kolom)))
                continue
            if transaksi.id_transaksi in self.data_transaksi:
                self.file_manager.catat_peringatan(FILE_TRANSAKSI, 'ID %s ganda, baris dilewati' % transaksi.id_transaksi)
            elif transaksi.nim not in daftar_nim:
                self.file_manager.catat_peringatan(FILE_TRANSAKSI, 'NIM %s pada transaksi %s tidak ditemukan, baris dilewati' % (transaksi.nim, transaksi.id_transaksi))
            else:
                self.data_transaksi[transaksi.id_transaksi] = transaksi
        for kolom in self.file_manager.baca_baris(FILE_DETAIL_TRANSAKSI):
            try:
                detail = DetailTransaksi.dari_baris(kolom)
            except ValueError as e:
                self.file_manager.catat_peringatan(FILE_DETAIL_TRANSAKSI, 'baris dilewati (%s): %s' % (e, '|'.join(kolom)))
                continue
            transaksi = self.data_transaksi.get(detail.id_transaksi)
            if transaksi is None:
                self.file_manager.catat_peringatan(FILE_DETAIL_TRANSAKSI, 'transaksi %s tidak ditemukan, baris dilewati' % detail.id_transaksi)
            elif detail.kode_alat not in daftar_kode:
                self.file_manager.catat_peringatan(FILE_DETAIL_TRANSAKSI, 'alat %s pada transaksi %s tidak ditemukan, baris dilewati' % (detail.kode_alat, detail.id_transaksi))
            elif any((d.kode_alat == detail.kode_alat for d in transaksi.daftar_detail)):
                self.file_manager.catat_peringatan(FILE_DETAIL_TRANSAKSI, 'alat %s ganda pada transaksi %s, baris dilewati' % (detail.kode_alat, detail.id_transaksi))
            else:
                transaksi.daftar_detail.append(detail)
        self._selaraskan()

    def _selaraskan(self):
        for id_transaksi in [i for i, t in self.data_transaksi.items() if not t.daftar_detail]:
            self.file_manager.catat_peringatan(FILE_TRANSAKSI, 'transaksi %s tidak memiliki alat, baris dilewati' % id_transaksi)
            del self.data_transaksi[id_transaksi]
        for transaksi in self.data_transaksi.values():
            status_file = transaksi.status
            transaksi.perbarui_status()
            if transaksi.status != status_file:
                self.file_manager.catat_peringatan(FILE_TRANSAKSI, "status transaksi %s diperbaiki dari '%s' menjadi '%s' mengikuti detail_transaksi.txt" % (transaksi.id_transaksi, status_file, transaksi.status))
        sedang_dipinjam = {d.kode_alat for t in self.data_transaksi.values() for d in t.daftar_detail if not d.sudah_kembali()}
        for alat in self.manager_alat.semua():
            if alat.kode in sedang_dipinjam:
                seharusnya = STATUS_DIPINJAM
            elif alat.status == STATUS_DIPINJAM:
                seharusnya = STATUS_TERSEDIA if alat.kondisi == KONDISI_BAIK else STATUS_TIDAK_TERSEDIA
            else:
                continue
            if alat.status != seharusnya:
                self.file_manager.catat_peringatan(FILE_ALAT, "status alat %s diperbaiki dari '%s' menjadi '%s' mengikuti transaksi" % (alat.kode, alat.status, seharusnya))
                alat.status = seharusnya

    def simpan(self):
        daftar = list(self.data_transaksi.values())
        self.file_manager.tulis_baris(FILE_TRANSAKSI, [t.ke_baris() for t in daftar])
        self.file_manager.tulis_baris(FILE_DETAIL_TRANSAKSI, [baris for t in daftar for baris in t.baris_detail()])

    def simpan_semua(self):
        try:
            self.manager_alat.simpan()
            self.simpan()
        except FileManagerError:
            self.manager_alat.muat()
            self.muat()
            try:
                self.manager_alat.simpan()
            except FileManagerError:
                pass
            raise

    def buat(self, nim, daftar_kode_alat):
        nim = self._kunci(nim)
        daftar_kode_alat = [self._kunci(k) for k in daftar_kode_alat]
        if not daftar_kode_alat:
            raise ValueError('Pilih minimal satu alat.')
        if len(set(daftar_kode_alat)) != len(daftar_kode_alat):
            raise ValueError('Kode alat tidak boleh dobel dalam satu transaksi.')
        if self._cari_mahasiswa(nim) is None:
            raise ValueError('Mahasiswa dengan NIM %s tidak ditemukan.' % nim)
        if self._jumlah_aktif(nim) >= MAKS_TRANSAKSI_AKTIF:
            raise ValueError('Mahasiswa %s sudah memiliki %d transaksi aktif (maksimal %d).' % (nim, self._jumlah_aktif(nim), MAKS_TRANSAKSI_AKTIF))
        daftar_alat = []
        for kode in daftar_kode_alat:
            alat = self._cari_alat(kode)
            if alat is None:
                raise ValueError('Alat %s tidak ditemukan.' % kode)
            if alat.status != STATUS_TERSEDIA:
                raise ValueError('Alat %s tidak tersedia (status: %s).' % (kode, alat.status))
            daftar_alat.append(alat)
        hari_ini = date.today()
        batas = hari_ini + timedelta(days=MAKS_HARI_PINJAM)
        transaksi = Transaksi(self._id_baru(), nim, hari_ini.strftime(FORMAT_TANGGAL), batas.strftime(FORMAT_TANGGAL))
        for alat in daftar_alat:
            transaksi.daftar_detail.append(DetailTransaksi(transaksi.id_transaksi, alat.kode))
            alat.status = STATUS_DIPINJAM
        self.data_transaksi[transaksi.id_transaksi] = transaksi
        self.simpan_semua()
        self.logger.catat('Transaksi %s dibuat oleh %s (%s)' % (transaksi.id_transaksi, nim, ', '.join(daftar_kode_alat)))
        return transaksi

    def ambil(self, id_transaksi):
        id_transaksi = self._kunci(id_transaksi)
        transaksi = self.data_transaksi.get(id_transaksi)
        if transaksi is None:
            raise ValueError('Transaksi %s tidak ditemukan.' % id_transaksi)
        return transaksi

    def semua(self):
        return list(self.data_transaksi.values())

    def cari_berdasarkan_mahasiswa(self, nim):
        nim = self._kunci(nim)
        return [t for t in self.data_transaksi.values() if t.nim == nim and t.masih_aktif()]

    def riwayat_mahasiswa(self, nim):
        nim = self._kunci(nim)
        return [t for t in self.data_transaksi.values() if t.nim == nim]

    def punya_transaksi_aktif(self, nim):
        return self._jumlah_aktif(nim) > 0

    def alat_dalam_transaksi_aktif(self, kode):
        kode = self._kunci(kode)
        return any((not d.sudah_kembali() and d.kode_alat == kode for t in self.data_transaksi.values() if t.masih_aktif() for d in t.daftar_detail))
