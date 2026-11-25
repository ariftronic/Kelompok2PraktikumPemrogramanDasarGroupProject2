from app import validasi
from app.konstanta import NILAI_KOSONG, DAFTAR_KONDISI, DETAIL_DIPINJAM, DETAIL_DIKEMBALIKAN, TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI

class DetailTransaksi:
    """Satu alat di dalam sebuah transaksi beserta data pengembaliannya (satu baris detail_transaksi.txt)."""

    def __init__(self, id_transaksi, kode_alat, status=DETAIL_DIPINJAM, kondisi=NILAI_KOSONG, tgl_kembali=NILAI_KOSONG):
        self.id_transaksi = id_transaksi
        self.kode_alat = kode_alat
        self.status = status
        self.kondisi = kondisi
        self.tgl_kembali = tgl_kembali

    @classmethod
    def dari_baris(cls, kolom):
        """Membuat objek dari kolom detail_transaksi.txt; ValueError bila isinya tidak valid."""
        _, _, status, kondisi, tgl_kembali = kolom
        if status == DETAIL_DIKEMBALIKAN:
            if kondisi not in DAFTAR_KONDISI:
                raise ValueError("kondisi alat tidak dikenal: '%s'" % kondisi)
            validasi.validasi_tanggal(tgl_kembali, 'tgl_kembali')
        elif status == DETAIL_DIPINJAM:
            if kondisi != NILAI_KOSONG or tgl_kembali != NILAI_KOSONG:
                raise ValueError("alat yang masih dipinjam harus berkondisi dan bertanggal kembali '%s'" % NILAI_KOSONG)
        else:
            raise ValueError("status detail tidak dikenal: '%s'" % status)
        return cls(*kolom)

    def ke_baris(self):
        """Kolom untuk detail_transaksi.txt."""
        return [self.id_transaksi, self.kode_alat, self.status, self.kondisi, self.tgl_kembali]

    def sudah_kembali(self):
        """True bila alat ini sudah dikembalikan."""
        return self.status == DETAIL_DIKEMBALIKAN

    def kembalikan(self, kondisi, tanggal):
        """Mencatat kondisi dan tanggal pengembalian."""
        self.status = DETAIL_DIKEMBALIKAN
        self.kondisi = kondisi
        self.tgl_kembali = tanggal

    def __str__(self):
        if self.sudah_kembali():
            return '%s: %s (%s, %s)' % (self.kode_alat, self.status, self.kondisi, self.tgl_kembali)
        return '%s: %s' % (self.kode_alat, self.status)

class Transaksi:
    """Satu transaksi peminjaman; daftar alatnya disimpan di list daftar_detail (Aturan 3)."""

    def __init__(self, id_transaksi, nim, tgl_pinjam, batas_kembali, status=TRX_DIPINJAM):
        self.id_transaksi = id_transaksi
        self.nim = nim
        self.tgl_pinjam = tgl_pinjam
        self.batas_kembali = batas_kembali
        self.status = status
        self.daftar_detail = []

    @classmethod
    def dari_baris(cls, kolom):
        """Membuat objek dari kolom transaksi.txt; ValueError bila isinya tidak valid."""
        _, _, tgl_pinjam, batas_kembali, status = kolom
        if status not in (TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI):
            raise ValueError("status transaksi tidak dikenal: '%s'" % status)
        pinjam = validasi.validasi_tanggal(tgl_pinjam, 'tgl_pinjam')
        batas = validasi.validasi_tanggal(batas_kembali, 'batas_kembali')
        # batas maksimal 7 hari diterapkan saat transaksi dibuat; di sini cukup diperiksa urutannya
        if batas < pinjam:
            raise ValueError('batas_kembali (%s) tidak boleh sebelum tgl_pinjam (%s)' % (batas_kembali, tgl_pinjam))
        return cls(*kolom)

    def ke_baris(self):
        """Kolom untuk transaksi.txt."""
        return [self.id_transaksi, self.nim, self.tgl_pinjam, self.batas_kembali, self.status]

    def baris_detail(self):
        """Kolom detail_transaksi.txt untuk setiap alat di transaksi ini."""
        return [detail.ke_baris() for detail in self.daftar_detail]

    def nomor(self):
        """Angka pada ID (T012 menjadi 12), dipakai untuk mengurutkan dan membuat ID baru."""
        angka = self.id_transaksi[1:]
        return int(angka) if angka.isdigit() else 0

    def masih_aktif(self):
        """Transaksi aktif sampai semua alat dikembalikan (Aturan 4)."""
        return self.status != TRX_SELESAI

    def perbarui_status(self):
        """Status transaksi mengikuti jumlah alat yang sudah dikembalikan."""
        jumlah_kembali = sum((1 for detail in self.daftar_detail if detail.sudah_kembali()))
        if jumlah_kembali == 0:
            self.status = TRX_DIPINJAM
        elif jumlah_kembali == len(self.daftar_detail):
            self.status = TRX_SELESAI
        else:
            self.status = TRX_SEBAGIAN

    def __str__(self):
        baris = ['%s | %s | pinjam %s | batas %s | %s' % (self.id_transaksi, self.nim, self.tgl_pinjam, self.batas_kembali, self.status)]
        baris += ['     - %s' % detail for detail in self.daftar_detail]
        return '\n'.join(baris)
