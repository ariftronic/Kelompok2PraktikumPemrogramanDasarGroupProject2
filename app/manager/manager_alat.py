from app import validasi
from app.konstanta import FILE_ALAT, KONDISI_BAIK, STATUS_TERSEDIA, STATUS_DIPINJAM
from app.manager.manager_dasar import ManagerDasar
from app.models.alat import Alat
KRITERIA_CARI = ('semua', 'kode', 'nama', 'kategori')

class ManagerAlat(ManagerDasar):
    """Mengelola data alat dan menyimpannya ke alat.txt."""
    NAMA_FILE = FILE_ALAT
    MODEL = Alat
    NAMA_KUNCI = 'kode alat'
    ATRIBUT_KUNCI = 'kode'

    def __init__(self, file_manager, logger):
        super().__init__(file_manager, logger)
        self.manager_transaksi = None
        self.manager_pemeliharaan = None

    @property
    def data_alat(self):
        """Dictionary kode -> Alat."""
        return self._data

    def sambungkan_transaksi(self, manager_transaksi):
        """Menyimpan referensi ManagerTransaksi untuk pemeriksaan Aturan 6."""
        self.manager_transaksi = manager_transaksi

    def sambungkan_pemeliharaan(self, manager_pemeliharaan):
        """Menyimpan referensi ManagerPemeliharaan agar alat yang diperbaiki tidak diubah atau dihapus."""
        self.manager_pemeliharaan = manager_pemeliharaan

    def cari_berdasarkan_kode(self, kode):
        """Objek Alat atau None."""
        return self._data.get(self._kunci(kode))

    def ada(self, kode):
        """True bila kode alat terdaftar."""
        return self._kunci(kode) in self._data

    def ambil(self, kode):
        """Objek Alat; ValueError bila kode tidak terdaftar."""
        alat = self.cari_berdasarkan_kode(kode)
        if alat is None:
            raise ValueError('Alat dengan kode %s tidak ditemukan.' % self._kunci(kode))
        return alat

    def daftar_kategori(self):
        """Nama kategori yang sudah dipakai, urut abjad."""
        return sorted({a.kategori for a in self._data.values()}, key=str.lower)

    def _normalisasi_kategori(self, kategori):
        bersih = validasi.validasi_kategori(kategori)
        for ada in self.daftar_kategori():
            if ada.lower() == bersih.lower():
                return ada
        return bersih.lower()

    def tambah(self, kode, nama, kategori, kondisi=KONDISI_BAIK):
        """Menambah alat baru; kategori baru langsung diterima dan kode ganda ditolak."""
        kode = validasi.validasi_kode_alat(kode)
        nama = validasi.validasi_nama_alat(nama)
        kategori = self._normalisasi_kategori(kategori)
        kondisi = validasi.validasi_kondisi(kondisi)
        if kode in self._data:
            raise ValueError('Kode alat %s sudah terdaftar.' % kode)
        alat = Alat(kode, nama, kategori, kondisi)
        self._data[kode] = alat
        self._simpan_atau_pulihkan()
        self.logger.catat('Alat %s ditambahkan' % kode)
        return alat

    def _sedang_diperbaiki(self, kode):
        return self.manager_pemeliharaan is not None and self.manager_pemeliharaan.sedang_diperbaiki(kode)

    def edit(self, kode, nama=None, kategori=None, kondisi=None):
        """Mengubah nama, kategori, dan/atau kondisi; None berarti tidak diubah."""
        alat = self.ambil(kode)
        nama_baru = alat.nama if validasi.kosong(nama) else validasi.validasi_nama_alat(nama)
        kategori_baru = alat.kategori if validasi.kosong(kategori) else self._normalisasi_kategori(kategori)
        kondisi_baru = alat.kondisi if validasi.kosong(kondisi) else validasi.validasi_kondisi(kondisi)
        if kondisi_baru != alat.kondisi and self._sedang_diperbaiki(alat.kode):
            raise ValueError('Alat %s sedang dalam pemeliharaan; kondisinya diubah lewat menu Pemeliharaan alat.' % alat.kode)
        alat.nama, alat.kategori, alat.kondisi = (nama_baru, kategori_baru, kondisi_baru)
        if not self._sedang_diperbaiki(alat.kode):
            alat.sesuaikan_status()
        self._simpan_atau_pulihkan()
        self.logger.catat('Alat %s diubah' % alat.kode)
        return alat

    def hapus(self, kode):
        """Menghapus alat yang tidak sedang dipinjam dan tidak tercatat di riwayat transaksi/pemeliharaan."""
        alat = self.ambil(kode)
        aktif = self.manager_transaksi is not None and self.manager_transaksi.alat_dalam_transaksi_aktif(alat.kode)
        if aktif or alat.status == STATUS_DIPINJAM:
            raise ValueError('Alat %s sedang dipinjam (transaksi aktif), tidak dapat dihapus.' % alat.kode)
        if self.manager_transaksi is not None and self.manager_transaksi.alat_punya_riwayat(alat.kode):
            raise ValueError('Alat %s tercatat dalam riwayat transaksi, tidak dapat dihapus agar riwayat tetap utuh.' % alat.kode)
        if self.manager_pemeliharaan is not None and self.manager_pemeliharaan.alat_punya_riwayat(alat.kode):
            raise ValueError('Alat %s tercatat dalam data pemeliharaan, tidak dapat dihapus agar riwayat tetap utuh.' % alat.kode)
        del self._data[alat.kode]
        self._simpan_atau_pulihkan()
        self.logger.catat('Alat %s dihapus' % alat.kode)

    def cari(self, kata_kunci, berdasarkan='semua'):
        """Tantangan A: mencari alat menurut kode, sebagian nama, kategori, atau ketiganya."""
        if validasi.kosong(kata_kunci):
            raise ValueError('Kata kunci tidak boleh kosong.')
        if berdasarkan not in KRITERIA_CARI:
            raise ValueError('Kriteria pencarian harus salah satu dari: %s.' % ', '.join(KRITERIA_CARI))
        persis = self._kunci(kata_kunci)
        if berdasarkan == 'kode':
            return [a for a in self.semua() if persis in a.kode]
        if berdasarkan == 'nama':
            hasil = [a for a in self.semua() if validasi.cocok_kata_kunci(kata_kunci, a.nama)]
        elif berdasarkan == 'kategori':
            hasil = [a for a in self.semua() if validasi.cocok_kata_kunci(kata_kunci, a.kategori)]
        else:
            hasil = [a for a in self.semua() if validasi.cocok_kata_kunci(kata_kunci, a.kode, a.nama, a.kategori)]
        return sorted(hasil, key=lambda a: (a.kode != persis, a.kode))

    def tersedia(self):
        """Alat yang dapat dipinjam."""
        return [a for a in self.semua() if a.status == STATUS_TERSEDIA]

    def dipinjam(self):
        """Alat yang sedang dipinjam."""
        return [a for a in self.semua() if a.status == STATUS_DIPINJAM]

    def rusak(self):
        """Alat berkondisi rusak ringan atau rusak berat."""
        return [a for a in self.semua() if a.kondisi != KONDISI_BAIK]
