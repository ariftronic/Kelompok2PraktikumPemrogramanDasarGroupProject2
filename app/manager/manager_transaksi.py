from datetime import date, timedelta
from app import validasi
from app.file_manager import FileManagerError
from app.konstanta import FILE_ALAT, FILE_MAHASISWA, FILE_TRANSAKSI, FILE_DETAIL_TRANSAKSI, FORMAT_TANGGAL, MAKS_HARI_PINJAM, MAKS_TRANSAKSI_AKTIF, MHS_AKTIF, MHS_TIDAK_AKTIF, PEMISAH, STATUS_TERSEDIA, STATUS_DIPINJAM, STATUS_TIDAK_TERSEDIA
from app.models.alat import Alat
from app.models.transaksi import Transaksi, DetailTransaksi

class ManagerTransaksi:
    """Mengelola transaksi peminjaman (transaksi.txt) dan daftar alatnya (detail_transaksi.txt)."""

    def __init__(self, file_manager, logger, manager_mahasiswa, manager_alat):
        self.file_manager = file_manager
        self.logger = logger
        self.manager_mahasiswa = manager_mahasiswa
        self.manager_alat = manager_alat
        self.data_transaksi = {}
        self._id_terpakai = set()

    @staticmethod
    def _kunci(teks):
        return validasi.rapikan(teks).upper()

    def _cari_mahasiswa(self, nim):
        return self.manager_mahasiswa.cari_berdasarkan_nim(nim)

    def _cari_alat(self, kode):
        return self.manager_alat.cari_berdasarkan_kode(kode)

    def _jumlah_aktif(self, nim):
        nim = self._kunci(nim)
        return sum((1 for t in self.data_transaksi.values() if t.nim == nim and t.masih_aktif()))

    def _id_baru(self):
        # ID yang pernah dipakai baris karantina ikut dihitung supaya tidak pernah dipakai ulang (Aturan 8)
        semua_id = set(self.data_transaksi) | self._id_terpakai
        angka = [int(i[1:]) for i in semua_id if i[1:].isdigit()]
        return 'T%03d' % (max(angka, default=0) + 1)

    def muat(self):
        """Membaca transaksi dan detailnya, memeriksa rujukan antarfile, lalu menyelaraskan status."""
        fm = self.file_manager
        self.data_transaksi = {}
        daftar_nim = {m.nim for m in self.manager_mahasiswa.semua()}
        daftar_kode = {a.kode for a in self.manager_alat.semua()}
        for kolom in fm.baca_baris(FILE_TRANSAKSI):
            baris = PEMISAH.join(kolom)
            try:
                transaksi = Transaksi.dari_baris(kolom)
            except ValueError as e:
                fm.karantina(FILE_TRANSAKSI, baris, 'data tidak valid (%s)' % e)
                continue
            if transaksi.id_transaksi in self.data_transaksi:
                fm.karantina(FILE_TRANSAKSI, baris, 'ID %s ganda' % transaksi.id_transaksi)
            elif transaksi.nim not in daftar_nim:
                fm.karantina(FILE_TRANSAKSI, baris, 'NIM %s pada transaksi %s tidak ditemukan' % (transaksi.nim, transaksi.id_transaksi))
            else:
                self.data_transaksi[transaksi.id_transaksi] = transaksi
        kode_dipinjam = {}
        for kolom in fm.baca_baris(FILE_DETAIL_TRANSAKSI):
            baris = PEMISAH.join(kolom)
            try:
                detail = DetailTransaksi.dari_baris(kolom)
            except ValueError as e:
                fm.karantina(FILE_DETAIL_TRANSAKSI, baris, 'data tidak valid (%s)' % e)
                continue
            transaksi = self.data_transaksi.get(detail.id_transaksi)
            if transaksi is None:
                fm.karantina(FILE_DETAIL_TRANSAKSI, baris, 'transaksi %s tidak ditemukan' % detail.id_transaksi)
            elif detail.kode_alat not in daftar_kode:
                fm.karantina(FILE_DETAIL_TRANSAKSI, baris, 'alat %s pada transaksi %s tidak ditemukan' % (detail.kode_alat, detail.id_transaksi))
            elif any((d.kode_alat == detail.kode_alat for d in transaksi.daftar_detail)):
                fm.karantina(FILE_DETAIL_TRANSAKSI, baris, 'alat %s ganda pada transaksi %s' % (detail.kode_alat, detail.id_transaksi))
            elif not detail.sudah_kembali() and detail.kode_alat in kode_dipinjam:
                fm.karantina(FILE_DETAIL_TRANSAKSI, baris, 'alat %s masih tercatat dipinjam pada transaksi %s' % (detail.kode_alat, kode_dipinjam[detail.kode_alat]))
            else:
                transaksi.daftar_detail.append(detail)
                if not detail.sudah_kembali():
                    kode_dipinjam[detail.kode_alat] = detail.id_transaksi
        self._selaraskan()
        self._id_terpakai = {baris.split(PEMISAH)[0].strip().upper() for nama in (FILE_TRANSAKSI, FILE_DETAIL_TRANSAKSI) for baris in fm.baca_karantina(nama)}

    def _selaraskan(self):
        fm = self.file_manager
        for id_transaksi in [i for i, t in self.data_transaksi.items() if not t.daftar_detail]:
            fm.karantina(FILE_TRANSAKSI, PEMISAH.join(self.data_transaksi[id_transaksi].ke_baris()), 'transaksi %s tidak memiliki alat' % id_transaksi)
            del self.data_transaksi[id_transaksi]
        for transaksi in self.data_transaksi.values():
            status_file = transaksi.status
            transaksi.perbarui_status()
            if transaksi.status != status_file:
                fm.catat_peringatan(FILE_TRANSAKSI, "status transaksi %s diperbaiki dari '%s' menjadi '%s' mengikuti detail_transaksi.txt" % (transaksi.id_transaksi, status_file, transaksi.status))
        # Status alat hanya dikoreksi ke arah yang aman: program tidak pernah membuat alat
        # menjadi 'tersedia' sendiri, karena alat itu mungkin masih dipegang peminjam.
        sedang_dipinjam = {d.kode_alat for t in self.data_transaksi.values() for d in t.daftar_detail if not d.sudah_kembali()}
        for alat in self.manager_alat.semua():
            if alat.kode in sedang_dipinjam:
                seharusnya, alasan = (STATUS_DIPINJAM, 'mengikuti transaksi')
            elif alat.status == STATUS_DIPINJAM:
                seharusnya, alasan = (STATUS_TIDAK_TERSEDIA, 'karena tidak ada transaksi aktif yang memuatnya; periksa alat lalu ubah lewat menu Edit alat')
            elif Alat.status_dari_kondisi(alat.kondisi) == STATUS_TIDAK_TERSEDIA:
                seharusnya, alasan = (STATUS_TIDAK_TERSEDIA, 'mengikuti kondisi alat')
            else:
                seharusnya, alasan = (alat.status, '')
            if alat.status != seharusnya:
                fm.catat_peringatan(FILE_ALAT, "status alat %s diperbaiki dari '%s' menjadi '%s' %s" % (alat.kode, alat.status, seharusnya, alasan))
                alat.status = seharusnya
        nim_aktif = {t.nim for t in self.data_transaksi.values() if t.masih_aktif()}
        for mahasiswa in self.manager_mahasiswa.semua():
            seharusnya = MHS_AKTIF if mahasiswa.nim in nim_aktif else MHS_TIDAK_AKTIF
            if mahasiswa.status_aktif != seharusnya:
                fm.catat_peringatan(FILE_MAHASISWA, "status mahasiswa %s diperbaiki dari '%s' menjadi '%s' mengikuti transaksi" % (mahasiswa.nim, mahasiswa.status_aktif, seharusnya))
                mahasiswa.status_aktif = seharusnya

    def daftar_isi_file(self):
        """Isi transaksi.txt dan detail_transaksi.txt dalam bentuk (nama_file, daftar baris)."""
        daftar = self.semua()
        return [(FILE_TRANSAKSI, [t.ke_baris() for t in daftar]), (FILE_DETAIL_TRANSAKSI, [b for t in daftar for b in t.baris_detail()])]

    def simpan(self):
        """Menulis transaksi dan detailnya sekaligus."""
        self.file_manager.tulis_banyak(self.daftar_isi_file())

    def simpan_semua(self, simpan_mahasiswa=False):
        """Menyimpan transaksi, detail, alat, dan (bila diminta) mahasiswa dalam satu penulisan."""
        isi = self.daftar_isi_file() + [self.manager_alat.isi_file()]
        if simpan_mahasiswa:
            isi.append(self.manager_mahasiswa.isi_file())
        try:
            self.file_manager.tulis_banyak(isi)
        except FileManagerError:
            # Penulisan gagal sebelum ada file yang diganti, jadi data di file masih utuh:
            # muat ulang agar memori kembali sama dengan file, lalu teruskan error ke menu.
            self.manager_alat.muat()
            self.manager_mahasiswa.muat()
            self.muat()
            try:
                self.file_manager.tulis_banyak(self.daftar_isi_file() + [self.manager_alat.isi_file(), self.manager_mahasiswa.isi_file()])
            except FileManagerError:
                pass
            raise

    def buat(self, nim, daftar_kode_alat):
        """Membuat transaksi baru (Aturan 1, 2, 3); batas kembali 7 hari dari hari ini."""
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
            alat.tandai_dipinjam()
        self.data_transaksi[transaksi.id_transaksi] = transaksi
        status_berubah = self.perbarui_status_mahasiswa(nim)
        self.simpan_semua(simpan_mahasiswa=status_berubah)
        self.logger.catat('Transaksi %s dibuat oleh %s (%s)' % (transaksi.id_transaksi, nim, ', '.join(daftar_kode_alat)))
        return transaksi

    def ambil(self, id_transaksi):
        """Objek Transaksi; ValueError bila ID tidak ditemukan."""
        id_transaksi = self._kunci(id_transaksi)
        transaksi = self.data_transaksi.get(id_transaksi)
        if transaksi is None:
            raise ValueError('Transaksi %s tidak ditemukan.' % id_transaksi)
        return transaksi

    def semua(self):
        """Semua transaksi, urut menurut nomor ID (T999 sebelum T1000)."""
        return sorted(self.data_transaksi.values(), key=lambda t: (t.nomor(), t.id_transaksi))

    def cari_berdasarkan_mahasiswa(self, nim):
        """Transaksi aktif milik seorang mahasiswa."""
        nim = self._kunci(nim)
        return [t for t in self.semua() if t.nim == nim and t.masih_aktif()]

    def riwayat_mahasiswa(self, nim):
        """Semua transaksi milik seorang mahasiswa, termasuk yang sudah selesai."""
        nim = self._kunci(nim)
        return [t for t in self.semua() if t.nim == nim]

    def punya_transaksi_aktif(self, nim):
        """True bila mahasiswa masih punya transaksi aktif (Aturan 6)."""
        return self._jumlah_aktif(nim) > 0

    def perbarui_status_mahasiswa(self, nim):
        """status_aktif mahasiswa mengikuti ada tidaknya transaksi aktif; True bila berubah."""
        mahasiswa = self._cari_mahasiswa(nim)
        if mahasiswa is None:
            return False
        seharusnya = MHS_AKTIF if self.punya_transaksi_aktif(nim) else MHS_TIDAK_AKTIF
        berubah = mahasiswa.status_aktif != seharusnya
        mahasiswa.status_aktif = seharusnya
        return berubah

    def mahasiswa_punya_riwayat(self, nim):
        """True bila mahasiswa tercatat di transaksi mana pun."""
        nim = self._kunci(nim)
        return any((t.nim == nim for t in self.data_transaksi.values()))

    def alat_punya_riwayat(self, kode):
        """True bila alat tercatat di transaksi mana pun."""
        kode = self._kunci(kode)
        return any((d.kode_alat == kode for t in self.data_transaksi.values() for d in t.daftar_detail))

    def transaksi_aktif_untuk_alat(self, kode):
        """Transaksi aktif yang masih memegang alat ini, atau None."""
        kode = self._kunci(kode)
        for transaksi in self.semua():
            if transaksi.masih_aktif() and any((d.kode_alat == kode and not d.sudah_kembali() for d in transaksi.daftar_detail)):
                return transaksi
        return None

    def alat_dalam_transaksi_aktif(self, kode):
        """True bila alat masih dipinjam di transaksi aktif (Aturan 6)."""
        return self.transaksi_aktif_untuk_alat(kode) is not None
