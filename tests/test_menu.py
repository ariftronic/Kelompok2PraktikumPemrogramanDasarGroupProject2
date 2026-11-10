import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from unittest import mock
from app.file_manager import FileManager, FileManagerError
from app.konstanta import FILE_ALAT, FILE_DETAIL_TRANSAKSI, FILE_LOG, FILE_MAHASISWA, FILE_TRANSAKSI, FORMAT_TANGGAL, MAKS_HARI_PINJAM
from app.logger import Logger
from app.menu import AplikasiPeminjaman
FILE_DATA = (FILE_MAHASISWA, FILE_ALAT, FILE_TRANSAKSI, FILE_DETAIL_TRANSAKSI)
LANGKAH_DATA_AWAL = ['1', '1', 'M001', 'Andi Pratama', '081234567890', '1', 'M002', 'Budi Santoso', '', '5', '0', '2', '1', 'A001', 'Kamera Digital', 'perangkat multimedia', '', '1', 'A002', 'Tripod', 'perangkat multimedia', '', '1', 'A003', 'Kabel LAN', 'perangkat jaringan', 'rusak berat', '4', 'kamera', '0']

def input_berskrip(masukan):
    antrean = iter(masukan)

    def palsu(pesan=''):
        try:
            return next(antrean)
        except StopIteration:
            raise EOFError from None
    return palsu

class DasarMenu(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)

    def buat_aplikasi(self):
        aplikasi = AplikasiPeminjaman()
        aplikasi.file_manager = FileManager(direktori=self.folder)
        aplikasi.logger = Logger(aplikasi.file_manager)
        return aplikasi

    def jalankan(self, masukan):
        keluaran = io.StringIO()
        with mock.patch('builtins.input', input_berskrip(masukan)), redirect_stdout(keluaran):
            self.buat_aplikasi().jalankan()
        return keluaran.getvalue()

    def isi(self, nama_file):
        with open(os.path.join(self.folder, nama_file), encoding='utf-8') as f:
            return f.read()

    def tulis_mentah(self, nama_file, teks):
        with open(os.path.join(self.folder, nama_file), 'w', encoding='utf-8') as f:
            f.write(teks)

    def semua_file(self):
        return tuple((self.isi(nama) for nama in FILE_DATA))

class UjiAlurMenu(DasarMenu):

    def test_alur_lengkap_dari_data_sampai_pengembalian(self):
        keluaran = self.jalankan(LANGKAH_DATA_AWAL + ['3', 'M001', 'A001, A002', '4', '5', 'T001', 'A001', '1', '5', 'T001', 'A002', '3', '7', '8', '9', '6', 'M001', '10', 'M001', '11', '0'])
        hari_ini = date.today()
        tgl = hari_ini.strftime(FORMAT_TANGGAL)
        batas = (hari_ini + timedelta(days=MAKS_HARI_PINJAM)).strftime(FORMAT_TANGGAL)
        self.assertEqual(self.isi(FILE_MAHASISWA), 'M001|Andi Pratama|081234567890|tidak aktif\nM002|Budi Santoso|-|tidak aktif\n')
        self.assertEqual(self.isi(FILE_ALAT), 'A001|Kamera Digital|perangkat multimedia|baik|tersedia\nA002|Tripod|perangkat multimedia|rusak berat|tidak tersedia\nA003|Kabel LAN|perangkat jaringan|rusak berat|tidak tersedia\n')
        self.assertEqual(self.isi(FILE_TRANSAKSI), 'T001|M001|%s|%s|selesai\n' % (tgl, batas))
        self.assertEqual(self.isi(FILE_DETAIL_TRANSAKSI), 'T001|A001|dikembalikan|baik|%s\nT001|A002|dikembalikan|rusak berat|%s\n' % (tgl, tgl))
        for teks in ('[OK] Mahasiswa berhasil ditambahkan.', '[OK] Alat berhasil ditambahkan.', '[OK] Transaksi peminjaman berhasil dibuat.', 'Hasil pencarian alat (1 data)', 'Alat yang tersedia (1 data)', 'Alat yang sedang dipinjam (0 data)', 'Alat yang rusak (2 data)', 'Mahasiswa M001 ditambahkan', 'Data tersimpan. Sampai jumpa.'):
            self.assertIn(teks, keluaran)
        for teks in ('[DITOLAK]', '[ERROR', 'Terlambat'):
            self.assertNotIn(teks, keluaran)
        log = self.isi(FILE_LOG)
        for teks in ('Program dijalankan', 'Alat A003 ditambahkan', 'Transaksi T001 dibuat oleh M001 (A001, A002)', 'Alat A002 dikembalikan dalam kondisi rusak berat (T001)', 'Program ditutup'):
            self.assertIn(teks, log)

    def test_penolakan_aturan_bisnis_tampil_di_layar_dan_file_tidak_berubah(self):
        self.jalankan(LANGKAH_DATA_AWAL + ['3', 'M001', 'A001', '0'])
        sebelum = self.semua_file()
        keluaran = self.jalankan(['3', 'M002', 'A001', '3', 'M002', 'A003', '1', '3', 'M001', 'y', '0', '2', '3', 'A001', 'y', '0', '1', '3', 'M002', 'n', '0', '0'])
        self.assertEqual(keluaran.count('[DITOLAK]'), 4)
        self.assertIn('Dibatalkan.', keluaran)
        self.assertEqual(self.semua_file(), sebelum)

    def test_edit_mahasiswa_mengosongkan_hp_dan_status_mengikuti_peminjaman(self):
        keluaran = self.jalankan(['1', '1', 'M001', 'Andi', '081234567890', '2', 'M001', '', '-', '2', 'M001', '', '', '0', '2', '1', 'A001', 'Kamera', 'multimedia', '', '0', '3', 'M001', 'A001', '0'])
        self.assertEqual(self.isi(FILE_MAHASISWA), 'M001|Andi|-|aktif\n')
        self.assertEqual(self.isi(FILE_ALAT), 'A001|Kamera|multimedia|baik|dipinjam\n')
        self.assertTrue(self.isi(FILE_TRANSAKSI).startswith('T001|M001|'))
        self.assertIn('Tidak ada perubahan.', keluaran)
        self.assertNotIn('[DITOLAK]', keluaran)

    def test_input_berhenti_di_tengah_isian_tetap_menyimpan_dan_keluar(self):
        keluaran = self.jalankan(['1', '1', 'M001'])
        self.assertNotIn('[ERROR]', keluaran)
        self.assertIn('Data tersimpan', keluaran)
        self.assertEqual(self.isi(FILE_MAHASISWA), '')
        self.assertIn('Program ditutup', self.isi(FILE_LOG))

    def test_data_tetap_ada_setelah_program_dijalankan_ulang(self):
        self.jalankan(LANGKAH_DATA_AWAL + ['3', 'M001', 'A001, A002', '0'])
        sebelum = self.semua_file()
        keluaran = self.jalankan(['4', '8', '10', 'M001', '0'])
        self.assertNotIn('[PERINGATAN]', keluaran)
        self.assertIn('M001|Andi Pratama|081234567890|aktif', sebelum[0])
        self.assertIn('M002|Budi Santoso|-|tidak aktif', sebelum[0])
        self.assertIn('Alat yang sedang dipinjam (2 data)', keluaran)
        self.assertIn('T001 | M001', keluaran)
        self.assertEqual(self.semua_file(), sebelum)

class UjiKeterlambatan(DasarMenu):

    def test_pengembalian_terlambat_menampilkan_peringatan_dan_log(self):
        self.tulis_mentah(FILE_MAHASISWA, 'M001|Andi|0812345678|aktif\n')
        self.tulis_mentah(FILE_ALAT, 'A001|Kamera|umum|baik|dipinjam\n')
        self.tulis_mentah(FILE_TRANSAKSI, 'T001|M001|2020-01-01|2020-01-08|dipinjam\n')
        self.tulis_mentah(FILE_DETAIL_TRANSAKSI, 'T001|A001|dipinjam|-|-\n')
        keluaran = self.jalankan(['5', 'T001', 'A001', '1', '0'])
        self.assertIn('Terlambat', keluaran)
        self.assertIn('TERLAMBAT', self.isi(FILE_LOG))
        self.assertIn('A001|Kamera|umum|baik|tersedia', self.isi(FILE_ALAT))

class UjiSiapkan(DasarMenu):

    def test_menyiapkan_file_dan_menyambungkan_manager(self):
        aplikasi = self.buat_aplikasi()
        with redirect_stdout(io.StringIO()):
            self.assertTrue(aplikasi.siapkan())
        for nama in FILE_DATA + (FILE_LOG,):
            self.assertTrue(os.path.exists(os.path.join(self.folder, nama)), nama)
        manager = aplikasi.manager
        self.assertIs(manager['alat'].manager_transaksi, manager['transaksi'])
        self.assertIs(manager['mahasiswa'].manager_transaksi, manager['transaksi'])
        self.assertIs(manager['pengembalian'].manager_transaksi, manager['transaksi'])

    def test_baris_rusak_dilewati_dengan_peringatan(self):
        self.tulis_mentah(FILE_MAHASISWA, 'M001|Andi|0812345678|aktif\nRUSAK|hanya dua kolom\n')
        aplikasi = self.buat_aplikasi()
        keluaran = io.StringIO()
        with redirect_stdout(keluaran):
            self.assertTrue(aplikasi.siapkan())
        self.assertIn('[PERINGATAN]', keluaran.getvalue())
        self.assertEqual([m.nim for m in aplikasi.manager['mahasiswa'].semua()], ['M001'])

    def test_gagal_menyiapkan_file_menghentikan_program(self):
        aplikasi = self.buat_aplikasi()
        keluaran = io.StringIO()
        with mock.patch.object(aplikasi.file_manager, 'pastikan_semua_file', side_effect=FileManagerError('izin ditolak')), mock.patch('builtins.input', side_effect=AssertionError('menu tidak boleh tampil')), redirect_stdout(keluaran):
            aplikasi.jalankan()
        self.assertIn('[ERROR FILE]', keluaran.getvalue())
        self.assertIn('tidak dapat dimulai', keluaran.getvalue())
if __name__ == '__main__':
    unittest.main()
