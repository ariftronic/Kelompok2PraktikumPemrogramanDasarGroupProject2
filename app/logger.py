from datetime import datetime
from app.file_manager import FileManagerError
from app.konstanta import FILE_LOG, FORMAT_WAKTU_LOG

class Logger:

    def __init__(self, file_manager, nama_file=FILE_LOG):
        self.file_manager = file_manager
        self.nama_file = nama_file

    def catat(self, pesan):
        waktu = datetime.now().strftime(FORMAT_WAKTU_LOG)
        try:
            self.file_manager.tambah_baris(self.nama_file, '[%s] %s' % (waktu, pesan))
            return True
        except FileManagerError as e:
            print('[PERINGATAN] Log gagal ditulis: %s' % e)
            return False

    def baca_terakhir(self, jumlah=20):
        baris = self.file_manager.baca_teks(self.nama_file)
        return baris[-jumlah:] if jumlah > 0 else []
