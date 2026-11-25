from app import validasi
from app.konstanta import KONDISI_BAIK, STATUS_TERSEDIA, STATUS_DIPINJAM, STATUS_TIDAK_TERSEDIA
DAFTAR_STATUS = (STATUS_TERSEDIA, STATUS_DIPINJAM, STATUS_TIDAK_TERSEDIA)

class Alat:
    """Satu unit peralatan laboratorium (satu baris alat.txt)."""

    def __init__(self, kode, nama, kategori, kondisi=KONDISI_BAIK, status=None):
        self.kode = kode
        self.nama = nama
        self.kategori = kategori
        self.kondisi = kondisi
        self.status = status if status is not None else self.status_dari_kondisi(kondisi)

    @staticmethod
    def status_dari_kondisi(kondisi):
        """Alat baik tersedia; alat rusak ringan atau rusak berat tidak tersedia (Aturan 5)."""
        return STATUS_TERSEDIA if kondisi == KONDISI_BAIK else STATUS_TIDAK_TERSEDIA

    @classmethod
    def dari_baris(cls, kolom):
        """Membuat objek dari kolom alat.txt; ValueError bila isinya tidak valid."""
        if len(kolom) != 5:
            raise ValueError('baris alat harus 5 kolom, bukan %d' % len(kolom))
        kode, nama, kategori, kondisi, status = kolom
        if status not in DAFTAR_STATUS:
            raise ValueError("status alat tidak dikenal: '%s'" % status)
        return cls(validasi.validasi_kode_alat(kode), validasi.validasi_nama_alat(nama), validasi.validasi_kategori(kategori), validasi.validasi_kondisi(kondisi), status)

    def ke_baris(self):
        """Kolom untuk alat.txt."""
        return [self.kode, self.nama, self.kategori, self.kondisi, self.status]

    def sesuaikan_status(self):
        """Menyesuaikan status dengan kondisi, kecuali alat sedang dipinjam."""
        if self.status != STATUS_DIPINJAM:
            self.status = self.status_dari_kondisi(self.kondisi)

    def tandai_dipinjam(self):
        """Mengubah status menjadi dipinjam; ValueError bila alat tidak tersedia (Aturan 1)."""
        if self.status != STATUS_TERSEDIA:
            raise ValueError('Alat %s tidak tersedia (status: %s).' % (self.kode, self.status))
        self.status = STATUS_DIPINJAM

    def tandai_dikembalikan(self, kondisi):
        """Mencatat kondisi saat dikembalikan dan menyesuaikan status (Aturan 5)."""
        self.kondisi = validasi.validasi_kondisi(kondisi)
        self.status = self.status_dari_kondisi(self.kondisi)

    def selesai_diperbaiki(self):
        """Dipanggil saat pemeliharaan selesai: alat kembali baik dan tersedia."""
        self.kondisi = KONDISI_BAIK
        self.status = STATUS_TERSEDIA

    def __str__(self):
        return '%s | %s | kategori: %s | kondisi: %s | status: %s' % (self.kode, self.nama, self.kategori, self.kondisi, self.status)
