from app import validasi
from app.file_manager import FileManagerError
from app.konstanta import PEMISAH

class ManagerDasar:
    """Pola bersama untuk manager yang menyimpan isi satu file di dictionary berkunci."""
    NAMA_FILE = None
    MODEL = None
    NAMA_KUNCI = 'kunci'
    ATRIBUT_KUNCI = None

    def __init__(self, file_manager, logger):
        self.file_manager = file_manager
        self.logger = logger
        self._data = {}

    def muat(self):
        """Membaca file ke dictionary; baris tidak valid atau berkunci ganda dikarantina."""
        data = {}
        for kolom in self.file_manager.baca_baris(self.NAMA_FILE):
            baris = PEMISAH.join(kolom)
            try:
                objek = self.MODEL.dari_baris(kolom)
            except ValueError as e:
                self.file_manager.karantina(self.NAMA_FILE, baris, 'data tidak valid (%s)' % e)
                continue
            kunci = getattr(objek, self.ATRIBUT_KUNCI)
            if kunci in data:
                self.file_manager.karantina(self.NAMA_FILE, baris, '%s %s ganda' % (self.NAMA_KUNCI, kunci))
                continue
            data[kunci] = objek
        self._data = data

    def isi_file(self):
        """Isi file dalam bentuk (nama_file, daftar baris), untuk disimpan bersama file lain."""
        return (self.NAMA_FILE, [objek.ke_baris() for objek in self.semua()])

    def simpan(self):
        """Menulis ulang file dari isi dictionary."""
        self.file_manager.tulis_baris(*self.isi_file())

    def _simpan_atau_pulihkan(self):
        try:
            self.simpan()
        except FileManagerError:
            self.muat()
            raise

    @staticmethod
    def _kunci(teks):
        return validasi.rapikan(teks).upper()

    def semua(self):
        """Semua data, diurutkan menurut kunci."""
        return [self._data[kunci] for kunci in sorted(self._data)]
