from datetime import date, datetime
from app import validasi
from app.konstanta import FORMAT_TANGGAL

class ManagerPengembalian:
    """Memproses pengembalian alat, termasuk pengembalian sebagian (Aturan 4) dan kondisi alat (Aturan 5)."""

    def __init__(self, file_manager, logger, manager_transaksi, manager_alat):
        self.file_manager = file_manager
        self.logger = logger
        self.manager_transaksi = manager_transaksi
        self.manager_alat = manager_alat

    def daftar_belum_kembali(self, id_transaksi):
        """Detail alat yang belum dikembalikan pada sebuah transaksi."""
        transaksi = self.manager_transaksi.ambil(id_transaksi)
        return [d for d in transaksi.daftar_detail if not d.sudah_kembali()]

    @staticmethod
    def hari_terlambat(transaksi, tanggal=None):
        """Jumlah hari melewati batas_kembali (0 bila belum terlambat)."""
        tanggal = tanggal or date.today()
        batas = datetime.strptime(transaksi.batas_kembali, FORMAT_TANGGAL).date()
        return max((tanggal - batas).days, 0)

    def kembalikan(self, id_transaksi, kode_alat, kondisi):
        """Mengembalikan satu alat; status alat mengikuti kondisinya dan status transaksi diperbarui."""
        kode_alat = validasi.rapikan(kode_alat).upper()
        kondisi = validasi.validasi_kondisi(kondisi)
        transaksi = self.manager_transaksi.ambil(id_transaksi)
        detail = next((d for d in transaksi.daftar_detail if d.kode_alat == kode_alat), None)
        if detail is None:
            raise ValueError('Alat %s tidak ada pada transaksi %s.' % (kode_alat, transaksi.id_transaksi))
        if detail.sudah_kembali():
            raise ValueError('Alat %s pada transaksi %s sudah dikembalikan.' % (kode_alat, transaksi.id_transaksi))
        alat = self.manager_alat.cari_berdasarkan_kode(kode_alat)
        if alat is None:
            raise ValueError('Alat %s tidak ditemukan di data alat.' % kode_alat)
        terlambat = self.hari_terlambat(transaksi)
        detail.kembalikan(kondisi, date.today().strftime(FORMAT_TANGGAL))
        alat.tandai_dikembalikan(kondisi)
        transaksi.perbarui_status()
        status_berubah = self.manager_transaksi.perbarui_status_mahasiswa(transaksi.nim)
        # Bila penyimpanan gagal, simpan_semua() memuat ulang data dari file yang masih utuh,
        # sehingga kondisi alat dan status transaksi otomatis kembali seperti sebelumnya.
        self.manager_transaksi.simpan_semua(simpan_mahasiswa=status_berubah)
        pesan = 'Alat %s dikembalikan dalam kondisi %s (%s)' % (kode_alat, kondisi, transaksi.id_transaksi)
        if terlambat:
            pesan += ' - TERLAMBAT %d hari' % terlambat
        self.logger.catat(pesan)
        return transaksi
