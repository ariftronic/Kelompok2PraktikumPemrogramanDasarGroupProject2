from app import validasi
from app.konstanta import FILE_MAHASISWA
from app.manager.manager_dasar import ManagerDasar
from app.models.mahasiswa import Mahasiswa

class ManagerMahasiswa(ManagerDasar):
    """Mengelola data mahasiswa dan menyimpannya ke mahasiswa.txt."""
    NAMA_FILE = FILE_MAHASISWA
    MODEL = Mahasiswa
    NAMA_KUNCI = 'NIM'
    ATRIBUT_KUNCI = 'nim'

    def __init__(self, file_manager, logger):
        super().__init__(file_manager, logger)
        self.manager_transaksi = None

    @property
    def data_mahasiswa(self):
        """Dictionary NIM -> Mahasiswa."""
        return self._data

    def sambungkan_transaksi(self, manager_transaksi):
        """Menyimpan referensi ManagerTransaksi untuk pemeriksaan Aturan 6."""
        self.manager_transaksi = manager_transaksi

    def cari_berdasarkan_nim(self, nim):
        """Objek Mahasiswa atau None."""
        return self._data.get(self._kunci(nim))

    def ada(self, nim):
        """True bila NIM terdaftar."""
        return self._kunci(nim) in self._data

    def ambil(self, nim):
        """Objek Mahasiswa; ValueError bila NIM tidak terdaftar."""
        mhs = self.cari_berdasarkan_nim(nim)
        if mhs is None:
            raise ValueError('Mahasiswa dengan NIM %s tidak ditemukan.' % self._kunci(nim))
        return mhs

    def tambah(self, nim, nama, no_hp=''):
        """Menambah mahasiswa baru; NIM ganda ditolak."""
        nim = validasi.validasi_nim(nim)
        nama = validasi.validasi_nama(nama)
        no_hp = validasi.validasi_no_hp(no_hp)
        if nim in self._data:
            raise ValueError('NIM %s sudah terdaftar.' % nim)
        mhs = Mahasiswa(nim, nama, no_hp)
        self._data[nim] = mhs
        self._simpan_atau_pulihkan()
        self.logger.catat('Mahasiswa %s ditambahkan' % nim)
        return mhs

    def edit(self, nim, nama=None, no_hp=None):
        """Mengubah nama dan/atau No. HP; None berarti tidak diubah."""
        mhs = self.ambil(nim)
        nama_baru = mhs.nama if validasi.kosong(nama) else validasi.validasi_nama(nama)
        hp_baru = mhs.no_hp if validasi.kosong(no_hp) else validasi.validasi_no_hp(no_hp)
        mhs.nama, mhs.no_hp = (nama_baru, hp_baru)
        self._simpan_atau_pulihkan()
        self.logger.catat('Mahasiswa %s diubah' % mhs.nim)
        return mhs

    def hapus(self, nim):
        """Menghapus mahasiswa yang tidak punya transaksi aktif maupun riwayat transaksi."""
        mhs = self.ambil(nim)
        if self.manager_transaksi is not None and self.manager_transaksi.punya_transaksi_aktif(mhs.nim):
            raise ValueError('Mahasiswa %s masih memiliki transaksi aktif, tidak dapat dihapus.' % mhs.nim)
        if self.manager_transaksi is not None and self.manager_transaksi.mahasiswa_punya_riwayat(mhs.nim):
            raise ValueError('Mahasiswa %s tercatat dalam riwayat transaksi, tidak dapat dihapus agar riwayat tetap utuh.' % mhs.nim)
        del self._data[mhs.nim]
        self._simpan_atau_pulihkan()
        self.logger.catat('Mahasiswa %s dihapus' % mhs.nim)

    def cari(self, kata_kunci):
        """Mencari mahasiswa menurut NIM atau sebagian nama."""
        if validasi.kosong(kata_kunci):
            raise ValueError('Kata kunci tidak boleh kosong.')
        return [m for m in self.semua() if validasi.cocok_kata_kunci(kata_kunci, m.nim, m.nama)]
