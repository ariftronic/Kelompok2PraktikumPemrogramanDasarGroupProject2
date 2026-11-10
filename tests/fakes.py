from app.konstanta import FILE_ALAT, FILE_MAHASISWA, KONDISI_BAIK, MHS_AKTIF, STATUS_DIPINJAM, STATUS_TERSEDIA

class AlatTiruan:

    def __init__(self, kode, nama='Alat', kategori='umum', kondisi=KONDISI_BAIK, status=STATUS_TERSEDIA):
        self.kode = kode
        self.nama = nama
        self.kategori = kategori
        self.kondisi = kondisi
        self.status = status

    def ke_baris(self):
        return [self.kode, self.nama, self.kategori, self.kondisi, self.status]

    def __str__(self):
        return ' | '.join(self.ke_baris())

class MahasiswaTiruan:

    def __init__(self, nim, nama='Mahasiswa', no_hp='0812', status_aktif=MHS_AKTIF):
        self.nim = nim
        self.nama = nama
        self.no_hp = no_hp
        self.status_aktif = status_aktif

    def ke_baris(self):
        return [self.nim, self.nama, self.no_hp, self.status_aktif]

    def __str__(self):
        return ' | '.join(self.ke_baris())

class ManagerAlatTiruan:

    def __init__(self, file_manager, logger):
        self.file_manager = file_manager
        self.logger = logger
        self.data = []

    def muat(self):
        self.data = [AlatTiruan(*k) for k in self.file_manager.baca_baris(FILE_ALAT)]

    def simpan(self):
        self.file_manager.tulis_baris(FILE_ALAT, [a.ke_baris() for a in self.data])

    def semua(self):
        return list(self.data)

    def tambah(self, kode, nama, kategori, kondisi=KONDISI_BAIK):
        alat = AlatTiruan(kode, nama, kategori, kondisi)
        self.data.append(alat)
        self.simpan()
        return alat

    def tersedia(self):
        return [a for a in self.data if a.status == STATUS_TERSEDIA]

    def dipinjam(self):
        return [a for a in self.data if a.status == STATUS_DIPINJAM]

    def rusak(self):
        return [a for a in self.data if a.kondisi != KONDISI_BAIK]

class ManagerMahasiswaTiruan:

    def __init__(self, file_manager, logger):
        self.file_manager = file_manager
        self.logger = logger
        self.data = []

    def muat(self):
        self.data = [MahasiswaTiruan(*k) for k in self.file_manager.baca_baris(FILE_MAHASISWA)]

    def simpan(self):
        self.file_manager.tulis_baris(FILE_MAHASISWA, [m.ke_baris() for m in self.data])

    def semua(self):
        return list(self.data)

    def tambah(self, nim, nama, no_hp):
        mahasiswa = MahasiswaTiruan(nim, nama, no_hp)
        self.data.append(mahasiswa)
        self.simpan()
        return mahasiswa
