from app import validasi
from app.file_manager import FileManagerError
from app.konstanta import FILE_MAHASISWA
from app.models.mahasiswa import Mahasiswa

class ManagerMahasiswa:

    def __init__(self, file_manager, logger):
        self.file_manager = file_manager
        self.logger = logger
        self.manager_transaksi = None
        self._data_mahasiswa = {}

    @property
    def data_mahasiswa(self):
        return self._data_mahasiswa

    def sambungkan_transaksi(self, manager_transaksi):
        self.manager_transaksi = manager_transaksi

    def muat(self):
        data = {}
        for kolom in self.file_manager.baca_baris(FILE_MAHASISWA):
            try:
                mhs = Mahasiswa.dari_baris(kolom)
            except ValueError as e:
                self.file_manager.catat_peringatan(FILE_MAHASISWA, 'baris dilewati (%s): %s' % (e, kolom))
                continue
            if mhs.nim in data:
                self.file_manager.catat_peringatan(FILE_MAHASISWA, 'NIM %s ganda, baris dilewati' % mhs.nim)
                continue
            data[mhs.nim] = mhs
        self._data_mahasiswa = data

    def simpan(self):
        self.file_manager.tulis_baris(FILE_MAHASISWA, [m.ke_baris() for m in self.semua()])

    def _simpan_atau_pulihkan(self):
        try:
            self.simpan()
        except FileManagerError:
            self.muat()
            raise

    @staticmethod
    def _kunci(nim):
        return validasi.rapikan(nim).upper()

    def cari_berdasarkan_nim(self, nim):
        return self._data_mahasiswa.get(self._kunci(nim))

    def ada(self, nim):
        return self._kunci(nim) in self._data_mahasiswa

    def ambil(self, nim):
        mhs = self.cari_berdasarkan_nim(nim)
        if mhs is None:
            raise ValueError('Mahasiswa dengan NIM %s tidak ditemukan.' % self._kunci(nim))
        return mhs

    def tambah(self, nim, nama, no_hp=''):
        nim = validasi.validasi_nim(nim)
        nama = validasi.validasi_nama(nama)
        no_hp = validasi.validasi_no_hp(no_hp)
        if nim in self._data_mahasiswa:
            raise ValueError('NIM %s sudah terdaftar.' % nim)
        mhs = Mahasiswa(nim, nama, no_hp)
        self._data_mahasiswa[nim] = mhs
        self._simpan_atau_pulihkan()
        self.logger.catat('Mahasiswa %s ditambahkan' % nim)
        return mhs

    def edit(self, nim, nama=None, no_hp=None):
        mhs = self.ambil(nim)
        nama_baru = mhs.nama if validasi.kosong(nama) else validasi.validasi_nama(nama)
        hp_baru = mhs.no_hp if validasi.kosong(no_hp) else validasi.validasi_no_hp(no_hp)
        mhs.nama, mhs.no_hp = (nama_baru, hp_baru)
        self._simpan_atau_pulihkan()
        self.logger.catat('Mahasiswa %s diubah' % mhs.nim)
        return mhs

    def hapus(self, nim):
        mhs = self.ambil(nim)
        if self.manager_transaksi is not None and self.manager_transaksi.punya_transaksi_aktif(mhs.nim):
            raise ValueError('Mahasiswa %s masih memiliki transaksi aktif, tidak dapat dihapus.' % mhs.nim)
        del self._data_mahasiswa[mhs.nim]
        self._simpan_atau_pulihkan()
        self.logger.catat('Mahasiswa %s dihapus' % mhs.nim)

    def cari(self, kata_kunci):
        if validasi.kosong(kata_kunci):
            raise ValueError('Kata kunci tidak boleh kosong.')
        return [m for m in self.semua() if validasi.cocok_kata_kunci(kata_kunci, m.nim, m.nama)]

    def semua(self):
        return sorted(self._data_mahasiswa.values(), key=lambda m: m.nim)
