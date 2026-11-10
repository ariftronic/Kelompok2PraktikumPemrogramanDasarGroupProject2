from datetime import datetime
from app.konstanta import NILAI_KOSONG, FORMAT_TANGGAL, DAFTAR_KONDISI, DETAIL_DIPINJAM, DETAIL_DIKEMBALIKAN, TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI

def _periksa_tanggal(nilai, nama_kolom):
    try:
        datetime.strptime(nilai, FORMAT_TANGGAL)
    except ValueError:
        raise ValueError("%s harus berformat YYYY-MM-DD: '%s'" % (nama_kolom, nilai))

class DetailTransaksi:

    def __init__(self, id_transaksi, kode_alat, status=DETAIL_DIPINJAM, kondisi=NILAI_KOSONG, tgl_kembali=NILAI_KOSONG):
        self.id_transaksi = id_transaksi
        self.kode_alat = kode_alat
        self.status = status
        self.kondisi = kondisi
        self.tgl_kembali = tgl_kembali

    @classmethod
    def dari_baris(cls, kolom):
        _, _, status, kondisi, tgl_kembali = kolom
        if status == DETAIL_DIKEMBALIKAN:
            if kondisi not in DAFTAR_KONDISI:
                raise ValueError("kondisi alat tidak dikenal: '%s'" % kondisi)
            _periksa_tanggal(tgl_kembali, 'tgl_kembali')
        elif status == DETAIL_DIPINJAM:
            if kondisi != NILAI_KOSONG or tgl_kembali != NILAI_KOSONG:
                raise ValueError("alat yang masih dipinjam harus berkondisi dan bertanggal kembali '%s'" % NILAI_KOSONG)
        else:
            raise ValueError("status detail tidak dikenal: '%s'" % status)
        return cls(*kolom)

    def ke_baris(self):
        return [self.id_transaksi, self.kode_alat, self.status, self.kondisi, self.tgl_kembali]

    def sudah_kembali(self):
        return self.status == DETAIL_DIKEMBALIKAN

    def kembalikan(self, kondisi, tanggal):
        self.status = DETAIL_DIKEMBALIKAN
        self.kondisi = kondisi
        self.tgl_kembali = tanggal

    def __str__(self):
        if self.sudah_kembali():
            return '%s: %s (%s, %s)' % (self.kode_alat, self.status, self.kondisi, self.tgl_kembali)
        return '%s: %s' % (self.kode_alat, self.status)

class Transaksi:

    def __init__(self, id_transaksi, nim, tgl_pinjam, batas_kembali, status=TRX_DIPINJAM):
        self.id_transaksi = id_transaksi
        self.nim = nim
        self.tgl_pinjam = tgl_pinjam
        self.batas_kembali = batas_kembali
        self.status = status
        self.daftar_detail = []

    @classmethod
    def dari_baris(cls, kolom):
        _, _, tgl_pinjam, batas_kembali, status = kolom
        if status not in (TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI):
            raise ValueError("status transaksi tidak dikenal: '%s'" % status)
        _periksa_tanggal(tgl_pinjam, 'tgl_pinjam')
        _periksa_tanggal(batas_kembali, 'batas_kembali')
        return cls(*kolom)

    def ke_baris(self):
        return [self.id_transaksi, self.nim, self.tgl_pinjam, self.batas_kembali, self.status]

    def baris_detail(self):
        return [detail.ke_baris() for detail in self.daftar_detail]

    def masih_aktif(self):
        return self.status != TRX_SELESAI

    def perbarui_status(self):
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
