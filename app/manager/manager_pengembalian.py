from datetime import date, datetime
from app.file_manager import FileManagerError
from app import validasi
from app.konstanta import DAFTAR_KONDISI, FORMAT_TANGGAL, KONDISI_BAIK, STATUS_TERSEDIA, STATUS_TIDAK_TERSEDIA

class ManagerPengembalian:

    def __init__(self, file_manager, logger, manager_transaksi, manager_alat):
        self.file_manager = file_manager
        self.logger = logger
        self.manager_transaksi = manager_transaksi
        self.manager_alat = manager_alat

    def daftar_belum_kembali(self, id_transaksi):
        transaksi = self.manager_transaksi.ambil(id_transaksi)
        return [d for d in transaksi.daftar_detail if not d.sudah_kembali()]

    @staticmethod
    def hari_terlambat(transaksi, tanggal=None):
        tanggal = tanggal or date.today()
        batas = datetime.strptime(transaksi.batas_kembali, FORMAT_TANGGAL).date()
        return max((tanggal - batas).days, 0)

    def kembalikan(self, id_transaksi, kode_alat, kondisi):
        kode_alat = validasi.rapikan(kode_alat).upper()
        kondisi = validasi.rapikan(kondisi).lower() if kondisi is not None else kondisi
        if kondisi not in DAFTAR_KONDISI:
            raise ValueError('Kondisi harus salah satu dari: %s.' % ', '.join(DAFTAR_KONDISI))
        transaksi = self.manager_transaksi.ambil(id_transaksi)
        detail = next((d for d in transaksi.daftar_detail if d.kode_alat == kode_alat), None)
        if detail is None:
            raise ValueError('Alat %s tidak ada pada transaksi %s.' % (kode_alat, id_transaksi))
        if detail.sudah_kembali():
            raise ValueError('Alat %s pada transaksi %s sudah dikembalikan.' % (kode_alat, id_transaksi))
        alat = self.manager_alat.cari_berdasarkan_kode(kode_alat)
        if alat is None:
            raise ValueError('Alat %s tidak ditemukan di data alat.' % kode_alat)
        kondisi_lama = alat.kondisi
        terlambat = self.hari_terlambat(transaksi)
        detail.kembalikan(kondisi, date.today().strftime(FORMAT_TANGGAL))
        alat.kondisi = kondisi
        alat.status = STATUS_TERSEDIA if kondisi == KONDISI_BAIK else STATUS_TIDAK_TERSEDIA
        transaksi.perbarui_status()
        status_berubah = self.manager_transaksi.perbarui_status_mahasiswa(transaksi.nim)
        try:
            self.manager_transaksi.simpan_semua(simpan_mahasiswa=status_berubah)
        except FileManagerError:
            # simpan_semua() sudah memuat ulang data dari file; kondisi alat harus
            # dikembalikan manual karena file alat sempat tertulis dengan kondisi baru.
            alat_pulih = self.manager_alat.cari_berdasarkan_kode(kode_alat)
            if alat_pulih is not None:
                alat_pulih.kondisi = kondisi_lama
                try:
                    self.manager_alat.simpan()
                except FileManagerError:
                    pass
            raise
        pesan = 'Alat %s dikembalikan dalam kondisi %s (%s)' % (kode_alat, kondisi, transaksi.id_transaksi)
        if terlambat:
            pesan += ' - TERLAMBAT %d hari' % terlambat
        self.logger.catat(pesan)
        return transaksi
