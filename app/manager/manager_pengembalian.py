from datetime import date
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

    def kembalikan(self, id_transaksi, kode_alat, kondisi):
        kode_alat = validasi.rapikan(kode_alat).upper()
        if kondisi not in DAFTAR_KONDISI:
            raise ValueError('Kondisi harus salah satu dari: %s.' % ', '.join(DAFTAR_KONDISI))
        transaksi = self.manager_transaksi.ambil(id_transaksi)
        detail = next((d for d in transaksi.daftar_detail if d.kode_alat == kode_alat), None)
        if detail is None:
            raise ValueError('Alat %s tidak ada pada transaksi %s.' % (kode_alat, id_transaksi))
        if detail.sudah_kembali():
            raise ValueError('Alat %s pada transaksi %s sudah dikembalikan.' % (kode_alat, id_transaksi))
        alat = next((a for a in self.manager_alat.semua() if a.kode == kode_alat), None)
        if alat is None:
            raise ValueError('Alat %s tidak ditemukan di data alat.' % kode_alat)
        detail.kembalikan(kondisi, date.today().strftime(FORMAT_TANGGAL))
        alat.kondisi = kondisi
        alat.status = STATUS_TERSEDIA if kondisi == KONDISI_BAIK else STATUS_TIDAK_TERSEDIA
        transaksi.perbarui_status()
        self.manager_transaksi.simpan_semua()
        self.logger.catat('Alat %s dikembalikan dalam kondisi %s (%s)' % (kode_alat, kondisi, transaksi.id_transaksi))
        return transaksi
