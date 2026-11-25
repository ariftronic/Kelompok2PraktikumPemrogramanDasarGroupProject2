from app import validasi
from app.konstanta import NILAI_KOSONG, PML_PROSES, PML_SELESAI

class Pemeliharaan:
    """Satu catatan pemeliharaan alat rusak (satu baris pemeliharaan.txt)."""

    def __init__(self, id_pemeliharaan, kode_alat, tgl_masuk, tgl_selesai=NILAI_KOSONG, status=PML_PROSES):
        self.id_pemeliharaan = id_pemeliharaan
        self.kode_alat = kode_alat
        self.tgl_masuk = tgl_masuk
        self.tgl_selesai = tgl_selesai
        self.status = status

    @classmethod
    def dari_baris(cls, kolom):
        """Membuat objek dari kolom pemeliharaan.txt; ValueError bila isinya tidak valid."""
        _, _, tgl_masuk, tgl_selesai, status = kolom
        masuk = validasi.validasi_tanggal(tgl_masuk, 'tgl_masuk')
        if status == PML_PROSES:
            if tgl_selesai != NILAI_KOSONG:
                raise ValueError("pemeliharaan yang masih diproses harus bertanggal selesai '%s'" % NILAI_KOSONG)
        elif status == PML_SELESAI:
            if validasi.validasi_tanggal(tgl_selesai, 'tgl_selesai') < masuk:
                raise ValueError('tgl_selesai (%s) tidak boleh sebelum tgl_masuk (%s)' % (tgl_selesai, tgl_masuk))
        else:
            raise ValueError("status pemeliharaan tidak dikenal: '%s'" % status)
        return cls(*kolom)

    def ke_baris(self):
        """Kolom untuk pemeliharaan.txt."""
        return [self.id_pemeliharaan, self.kode_alat, self.tgl_masuk, self.tgl_selesai, self.status]

    def nomor(self):
        """Angka pada ID (P012 menjadi 12)."""
        angka = self.id_pemeliharaan[1:]
        return int(angka) if angka.isdigit() else 0

    def masih_proses(self):
        """True selama alat belum selesai diperbaiki."""
        return self.status == PML_PROSES

    def selesaikan(self, tanggal):
        """Mencatat tanggal selesai perbaikan."""
        self.status = PML_SELESAI
        self.tgl_selesai = tanggal

    def __str__(self):
        if self.masih_proses():
            return '%s | %s | masuk %s | %s' % (self.id_pemeliharaan, self.kode_alat, self.tgl_masuk, self.status)
        return '%s | %s | masuk %s | selesai %s' % (self.id_pemeliharaan, self.kode_alat, self.tgl_masuk, self.tgl_selesai)
