from app import validasi
from app.file_manager import FileManagerError
from app.konstanta import FILE_ALAT, KONDISI_BAIK, STATUS_TERSEDIA, STATUS_DIPINJAM
from app.models.alat import Alat

class ManagerAlat:

    def __init__(self, file_manager, logger):
        self.file_manager = file_manager
        self.logger = logger
        self.manager_transaksi = None
        self._data_alat = {}

    @property
    def data_alat(self):
        return self._data_alat

    def sambungkan_transaksi(self, manager_transaksi):
        self.manager_transaksi = manager_transaksi

    def muat(self):
        data = {}
        for kolom in self.file_manager.baca_baris(FILE_ALAT):
            try:
                alat = Alat.dari_baris(kolom)
            except ValueError as e:
                self.file_manager.catat_peringatan(FILE_ALAT, 'baris dilewati (%s): %s' % (e, kolom))
                continue
            if alat.kode in data:
                self.file_manager.catat_peringatan(FILE_ALAT, 'kode alat %s ganda, baris dilewati' % alat.kode)
                continue
            data[alat.kode] = alat
        self._data_alat = data

    def simpan(self):
        self.file_manager.tulis_baris(FILE_ALAT, [a.ke_baris() for a in self.semua()])

    def _simpan_atau_pulihkan(self):
        try:
            self.simpan()
        except FileManagerError:
            self.muat()
            raise

    @staticmethod
    def _kunci(kode):
        return validasi.rapikan(kode).upper()

    def cari_berdasarkan_kode(self, kode):
        return self._data_alat.get(self._kunci(kode))

    def ada(self, kode):
        return self._kunci(kode) in self._data_alat

    def ambil(self, kode):
        alat = self.cari_berdasarkan_kode(kode)
        if alat is None:
            raise ValueError('Alat dengan kode %s tidak ditemukan.' % self._kunci(kode))
        return alat

    def daftar_kategori(self):
        return sorted({a.kategori for a in self._data_alat.values()}, key=str.lower)

    def _normalisasi_kategori(self, kategori):
        bersih = validasi.validasi_kategori(kategori)
        for ada in self.daftar_kategori():
            if ada.lower() == bersih.lower():
                return ada
        return bersih.lower()

    def tambah(self, kode, nama, kategori, kondisi=KONDISI_BAIK):
        kode = validasi.validasi_kode_alat(kode)
        nama = validasi.validasi_nama_alat(nama)
        kategori = self._normalisasi_kategori(kategori)
        kondisi = validasi.validasi_kondisi(kondisi)
        if kode in self._data_alat:
            raise ValueError('Kode alat %s sudah terdaftar.' % kode)
        alat = Alat(kode, nama, kategori, kondisi)
        self._data_alat[kode] = alat
        self._simpan_atau_pulihkan()
        self.logger.catat('Alat %s ditambahkan' % kode)
        return alat

    def edit(self, kode, nama=None, kategori=None, kondisi=None):
        alat = self.ambil(kode)
        nama_baru = alat.nama if validasi.kosong(nama) else validasi.validasi_nama_alat(nama)
        kategori_baru = alat.kategori if validasi.kosong(kategori) else self._normalisasi_kategori(kategori)
        kondisi_baru = alat.kondisi if validasi.kosong(kondisi) else validasi.validasi_kondisi(kondisi)
        alat.nama, alat.kategori, alat.kondisi = (nama_baru, kategori_baru, kondisi_baru)
        alat.sesuaikan_status()
        self._simpan_atau_pulihkan()
        self.logger.catat('Alat %s diubah' % alat.kode)
        return alat

    def hapus(self, kode):
        alat = self.ambil(kode)
        aktif = self.manager_transaksi is not None and self.manager_transaksi.alat_dalam_transaksi_aktif(alat.kode)
        if aktif or alat.status == STATUS_DIPINJAM:
            raise ValueError('Alat %s sedang dipinjam (transaksi aktif), tidak dapat dihapus.' % alat.kode)
        if self.manager_transaksi is not None and self.manager_transaksi.alat_punya_riwayat(alat.kode):
            raise ValueError('Alat %s tercatat dalam riwayat transaksi, tidak dapat dihapus agar riwayat tetap utuh.' % alat.kode)
        del self._data_alat[alat.kode]
        self._simpan_atau_pulihkan()
        self.logger.catat('Alat %s dihapus' % alat.kode)

    def cari(self, kata_kunci):
        if validasi.kosong(kata_kunci):
            raise ValueError('Kata kunci tidak boleh kosong.')
        hasil = [a for a in self.semua() if validasi.cocok_kata_kunci(kata_kunci, a.kode, a.nama, a.kategori)]
        persis = self._kunci(kata_kunci)
        return sorted(hasil, key=lambda a: (a.kode != persis, a.kode))

    def semua(self):
        return sorted(self._data_alat.values(), key=lambda a: a.kode)

    def tersedia(self):
        return [a for a in self.semua() if a.status == STATUS_TERSEDIA]

    def dipinjam(self):
        return [a for a in self.semua() if a.status == STATUS_DIPINJAM]

    def rusak(self):
        return [a for a in self.semua() if a.kondisi != KONDISI_BAIK]
