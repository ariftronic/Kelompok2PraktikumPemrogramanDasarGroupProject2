from datetime import date, timedelta
from app.konstanta import (
    PEMISAH, STATUS_DIPINJAM, TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI,
)

KOSONG = "-"
FORMAT_TANGGAL = "%Y-%m-%d"
MAKS_HARI_PINJAM = 7
DETAIL_DIKEMBALIKAN = "dikembalikan"

def _tanggal(teks):
    return date.fromisoformat(teks)

class DetailTransaksi:

    def __init__(self, id_transaksi, kode, status=STATUS_DIPINJAM,
                 kondisi=KOSONG, tgl_kembali=KOSONG):
        self.id_transaksi = id_transaksi
        self.kode = kode
        self.status = status
        self.kondisi = kondisi
        self.tgl_kembali = tgl_kembali

    @classmethod
    def dari_baris(cls, baris):
        if len(baris) != 5:
            raise ValueError("jumlah kolom detail harus 5")
        id_trx, kode, status, kondisi, tgl = [k.strip() for k in baris]
        if not id_trx or not kode:
            raise ValueError("id atau kode alat kosong")
        if status not in (STATUS_DIPINJAM, DETAIL_DIKEMBALIKAN):
            raise ValueError("status detail tidak dikenal: " + status)
        if tgl != KOSONG:
            _tanggal(tgl)
        return cls(id_trx, kode, status, kondisi, tgl)

    def ke_baris(self):
        """Ubah objek menjadi string berpemisah '|'."""
        return PEMISAH.join([self.id_transaksi, self.kode, self.status,
                             self.kondisi, self.tgl_kembali])

    def sudah_kembali(self):
        """True jika alat ini sudah dikembalikan."""
        return self.status == DETAIL_DIKEMBALIKAN


class Transaksi:

    def __init__(self, id_transaksi, nim, tgl_pinjam, batas_kembali,
                 status=TRX_DIPINJAM):
        self.id_transaksi = id_transaksi
        self.nim = nim
        self.tgl_pinjam = tgl_pinjam          
        self.batas_kembali = batas_kembali   
        self.status = status
        self.daftar_detail = []               

    @classmethod
    def baru(cls, id_transaksi, nim, daftar_kode, lama_hari=MAKS_HARI_PINJAM,
             tgl_pinjam=None):
        if not 1 <= lama_hari <= MAKS_HARI_PINJAM:
            raise ValueError("lama pinjam harus 1 sampai %d hari" % MAKS_HARI_PINJAM)
        awal = tgl_pinjam or date.today()
        batas = awal + timedelta(days=lama_hari)
        trx = cls(id_transaksi, nim, awal.isoformat(), batas.isoformat())
        for kode in daftar_kode:
            trx.daftar_detail.append(DetailTransaksi(id_transaksi, kode))
        return trx

    @classmethod
    def dari_baris(cls, baris):
        if len(baris) != 5:
            raise ValueError("jumlah kolom transaksi harus 5")
        id_trx, nim, tgl, batas, status = [k.strip() for k in baris]
        if not id_trx or not nim:
            raise ValueError("id atau nim kosong")
        if _tanggal(batas) - _tanggal(tgl) > timedelta(days=MAKS_HARI_PINJAM):
            raise ValueError("batas kembali melebihi %d hari" % MAKS_HARI_PINJAM)
        if status not in (TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI):
            raise ValueError("status transaksi tidak dikenal: " + status)
        return cls(id_trx, nim, tgl, batas, status)

    def ke_baris(self):
        return PEMISAH.join([self.id_transaksi, self.nim, self.tgl_pinjam,
                             self.batas_kembali, self.status])

    def aktif(self):
        return self.status != TRX_SELESAI

    def kode_belum_kembali(self):
        return [d.kode for d in self.daftar_detail if not d.sudah_kembali()]

    def cari_detail(self, kode):
        for d in self.daftar_detail:
            if d.kode == kode:
                return d
        return None

    def perbarui_status(self):
        if not self.daftar_detail:
            return self.status
        kembali = [d.sudah_kembali() for d in self.daftar_detail]
        if all(kembali):
            self.status = TRX_SELESAI
        elif any(kembali):
            self.status = TRX_SEBAGIAN
        else:
            self.status = TRX_DIPINJAM
        return self.status

    def terlambat(self, hari_ini=None):
        hari_ini = hari_ini or date.today()
        return self.aktif() and hari_ini > _tanggal(self.batas_kembali)

    def ke_teks(self, data_alat=None):
        baris = ["%s | NIM %s | pinjam %s | batas %s | %s" % (
            self.id_transaksi, self.nim, self.tgl_pinjam,
            self.batas_kembali, self.status)]
        for d in self.daftar_detail:
            alat = data_alat.get(d.kode) if data_alat else None
            nama = getattr(alat, "nama", "-") if alat else "-"
            tambahan = d.status
            if d.sudah_kembali():
                tambahan += ", kondisi %s, kembali %s" % (d.kondisi, d.tgl_kembali)
            baris.append("    - %s (%s): %s" % (d.kode, nama, tambahan))
        return "\n".join(baris)
