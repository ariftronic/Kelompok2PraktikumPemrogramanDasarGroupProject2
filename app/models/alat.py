from app import validasi
from app.konstanta import KONDISI_BAIK, STATUS_TERSEDIA, STATUS_DIPINJAM, STATUS_TIDAK_TERSEDIA
DAFTAR_STATUS = (STATUS_TERSEDIA, STATUS_DIPINJAM, STATUS_TIDAK_TERSEDIA)

class Alat:

    def __init__(self, kode, nama, kategori, kondisi=KONDISI_BAIK, status=None):
        self.kode = kode
        self.nama = nama
        self.kategori = kategori
        self.kondisi = kondisi
        self.status = status if status is not None else self.status_dari_kondisi(kondisi)

    @staticmethod
    def status_dari_kondisi(kondisi):
        return STATUS_TERSEDIA if kondisi == KONDISI_BAIK else STATUS_TIDAK_TERSEDIA

    @classmethod
    def dari_baris(cls, kolom):
        if len(kolom) != 5:
            raise ValueError('baris alat harus 5 kolom, bukan %d' % len(kolom))
        kode, nama, kategori, kondisi, status = kolom
        if status not in DAFTAR_STATUS:
            raise ValueError("status alat tidak dikenal: '%s'" % status)
        return cls(validasi.validasi_kode_alat(kode), validasi.validasi_nama_alat(nama), validasi.validasi_kategori(kategori), validasi.validasi_kondisi(kondisi), status)

    def ke_baris(self):
        return [self.kode, self.nama, self.kategori, self.kondisi, self.status]

    def sesuaikan_status(self):
        if self.status != STATUS_DIPINJAM:
            self.status = self.status_dari_kondisi(self.kondisi)

    def tandai_dipinjam(self):
        if self.status != STATUS_TERSEDIA:
            raise ValueError('Alat %s tidak tersedia (status: %s).' % (self.kode, self.status))
        self.status = STATUS_DIPINJAM

    def tandai_dikembalikan(self, kondisi):
        self.kondisi = validasi.validasi_kondisi(kondisi)
        self.status = self.status_dari_kondisi(self.kondisi)

    def __str__(self):
        return '%s | %s | kategori: %s | kondisi: %s | status: %s' % (self.kode, self.nama, self.kategori, self.kondisi, self.status)
