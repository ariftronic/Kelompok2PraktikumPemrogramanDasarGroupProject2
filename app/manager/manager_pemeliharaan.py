from datetime import date
from app import validasi
from app.file_manager import FileManagerError
from app.konstanta import FILE_ALAT, FILE_PEMELIHARAAN, FORMAT_TANGGAL, KONDISI_BAIK, PEMISAH, STATUS_DIPINJAM, STATUS_TERSEDIA, STATUS_TIDAK_TERSEDIA
from app.models.pemeliharaan import Pemeliharaan

class ManagerPemeliharaan:
    """Tantangan C: daftar pemeliharaan alat rusak, disimpan di pemeliharaan.txt."""

    def __init__(self, file_manager, logger, manager_alat, manager_transaksi):
        self.file_manager = file_manager
        self.logger = logger
        self.manager_alat = manager_alat
        self.manager_transaksi = manager_transaksi
        self.data_pemeliharaan = {}
        self._id_terpakai = set()

    def muat(self):
        """Membaca pemeliharaan.txt; baris bermasalah dikarantina dan alat yang masih diperbaiki tidak boleh tersedia."""
        fm = self.file_manager
        self.data_pemeliharaan = {}
        proses_per_alat = {}
        for kolom in fm.baca_baris(FILE_PEMELIHARAAN):
            baris = PEMISAH.join(kolom)
            try:
                catatan = Pemeliharaan.dari_baris(kolom)
            except ValueError as e:
                fm.karantina(FILE_PEMELIHARAAN, baris, 'data tidak valid (%s)' % e)
                continue
            kode = catatan.kode_alat
            if catatan.id_pemeliharaan in self.data_pemeliharaan:
                fm.karantina(FILE_PEMELIHARAAN, baris, 'ID %s ganda' % catatan.id_pemeliharaan)
            elif self.manager_alat.cari_berdasarkan_kode(kode) is None:
                fm.karantina(FILE_PEMELIHARAAN, baris, 'alat %s tidak ditemukan' % kode)
            elif catatan.masih_proses() and kode in proses_per_alat:
                fm.karantina(FILE_PEMELIHARAAN, baris, 'alat %s sudah dalam pemeliharaan %s' % (kode, proses_per_alat[kode]))
            elif catatan.masih_proses() and self.manager_transaksi.alat_dalam_transaksi_aktif(kode):
                fm.karantina(FILE_PEMELIHARAAN, baris, 'alat %s sedang dipinjam' % kode)
            else:
                self.data_pemeliharaan[catatan.id_pemeliharaan] = catatan
                if catatan.masih_proses():
                    proses_per_alat[kode] = catatan.id_pemeliharaan
        for catatan in self.aktif():
            alat = self.manager_alat.cari_berdasarkan_kode(catatan.kode_alat)
            if alat.status == STATUS_TERSEDIA:
                fm.catat_peringatan(FILE_ALAT, "status alat %s diperbaiki dari 'tersedia' menjadi 'tidak tersedia' karena masih dalam pemeliharaan %s" % (alat.kode, catatan.id_pemeliharaan))
                alat.status = STATUS_TIDAK_TERSEDIA
        self._id_terpakai = {baris.split(PEMISAH)[0].strip().upper() for baris in fm.baca_karantina(FILE_PEMELIHARAAN)}

    def isi_file(self):
        """Isi pemeliharaan.txt dalam bentuk (nama_file, daftar baris)."""
        return (FILE_PEMELIHARAAN, [catatan.ke_baris() for catatan in self.semua()])

    def simpan(self):
        """Menulis ulang pemeliharaan.txt."""
        self.file_manager.tulis_baris(*self.isi_file())

    def _simpan_atau_pulihkan(self, dengan_alat=False):
        isi = [self.isi_file()]
        if dengan_alat:
            isi.append(self.manager_alat.isi_file())
        try:
            self.file_manager.tulis_banyak(isi)
        except FileManagerError:
            if dengan_alat:
                self.manager_alat.muat()
            self.muat()
            raise

    def _id_baru(self):
        semua_id = set(self.data_pemeliharaan) | self._id_terpakai
        angka = [int(i[1:]) for i in semua_id if i[1:].isdigit()]
        return 'P%03d' % (max(angka, default=0) + 1)

    @staticmethod
    def _kunci(kode):
        return validasi.rapikan(kode).upper()

    def semua(self):
        """Semua catatan pemeliharaan, urut menurut nomor ID."""
        return sorted(self.data_pemeliharaan.values(), key=lambda c: (c.nomor(), c.id_pemeliharaan))

    def aktif(self):
        """Catatan pemeliharaan yang alatnya belum selesai diperbaiki."""
        return [c for c in self.semua() if c.masih_proses()]

    def aktif_untuk(self, kode):
        """Catatan pemeliharaan yang sedang berjalan untuk alat ini, atau None."""
        kode = self._kunci(kode)
        return next((c for c in self.aktif() if c.kode_alat == kode), None)

    def sedang_diperbaiki(self, kode):
        """True bila alat sedang dalam pemeliharaan."""
        return self.aktif_untuk(kode) is not None

    def alat_punya_riwayat(self, kode):
        """True bila alat pernah tercatat di pemeliharaan."""
        kode = self._kunci(kode)
        return any((c.kode_alat == kode for c in self.data_pemeliharaan.values()))

    def mulai(self, kode):
        """Memasukkan alat rusak ke daftar pemeliharaan."""
        alat = self.manager_alat.ambil(kode)
        if alat.status == STATUS_DIPINJAM:
            raise ValueError('Alat %s sedang dipinjam, tidak dapat masuk pemeliharaan.' % alat.kode)
        if self.sedang_diperbaiki(alat.kode):
            raise ValueError('Alat %s sudah dalam pemeliharaan.' % alat.kode)
        if alat.kondisi == KONDISI_BAIK:
            raise ValueError('Alat %s dalam kondisi baik, tidak perlu masuk pemeliharaan.' % alat.kode)
        catatan = Pemeliharaan(self._id_baru(), alat.kode, date.today().strftime(FORMAT_TANGGAL))
        self.data_pemeliharaan[catatan.id_pemeliharaan] = catatan
        self._simpan_atau_pulihkan()
        self.logger.catat('Alat %s masuk pemeliharaan (%s)' % (alat.kode, catatan.id_pemeliharaan))
        return catatan

    def selesai(self, kode):
        """Menutup pemeliharaan: alat kembali berkondisi baik dan tersedia."""
        alat = self.manager_alat.ambil(kode)
        catatan = self.aktif_untuk(alat.kode)
        if catatan is None:
            raise ValueError('Alat %s tidak sedang dalam pemeliharaan.' % alat.kode)
        catatan.selesaikan(date.today().strftime(FORMAT_TANGGAL))
        alat.selesai_diperbaiki()
        self._simpan_atau_pulihkan(dengan_alat=True)
        self.logger.catat('Pemeliharaan %s selesai, alat %s kembali tersedia' % (catatan.id_pemeliharaan, alat.kode))
        return catatan
