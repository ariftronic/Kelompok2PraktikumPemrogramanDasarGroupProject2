from app import validasi
from app.konstanta import MHS_AKTIF, MHS_TIDAK_AKTIF, NILAI_KOSONG

class Mahasiswa:

    def __init__(self, nim, nama, no_hp='', status_aktif=MHS_TIDAK_AKTIF):
        self.nim = nim
        self.nama = nama
        self.no_hp = no_hp
        # 'aktif' selama mahasiswa punya transaksi aktif; diatur ManagerTransaksi, bukan diisi manual.
        self.status_aktif = status_aktif

    @classmethod
    def dari_baris(cls, kolom):
        if len(kolom) != 4:
            raise ValueError('baris mahasiswa harus 4 kolom, bukan %d' % len(kolom))
        nim, nama, no_hp, status_aktif = kolom
        if status_aktif not in (MHS_AKTIF, MHS_TIDAK_AKTIF):
            raise ValueError("status_aktif tidak dikenal: '%s'" % status_aktif)
        return cls(validasi.validasi_nim(nim), validasi.validasi_nama(nama), validasi.validasi_no_hp(no_hp), status_aktif)

    def ke_baris(self):
        return [self.nim, self.nama, self.no_hp or NILAI_KOSONG, self.status_aktif]

    def __str__(self):
        return '%s | %s | HP: %s | peminjaman: %s' % (self.nim, self.nama, self.no_hp or NILAI_KOSONG, self.status_aktif)
