import os
import unittest
from datetime import date
from app.file_manager import FileManager
from app.konstanta import FORMAT_TANGGAL
from app.manager.manager_laporan import ManagerLaporan
from tests.test_integrasi import Aplikasi, DasarFolder
HARI_INI = date.today().strftime(FORMAT_TANGGAL)

class UjiLaporan(DasarFolder):

    def setUp(self):
        super().setUp()
        self.salin_sampel()
        self.app = Aplikasi(self.folder)
        self.folder_laporan = os.path.join(self.folder, 'laporan')
        self.laporan = ManagerLaporan(FileManager(direktori=self.folder_laporan), self.app.alat, self.app.mahasiswa, self.app.transaksi, self.app.pemeliharaan)

    def baca(self, path):
        with open(path, encoding='utf-8') as f:
            return f.read()

    def test_laporan_alat_dipinjam_memuat_peminjam_dan_batas_kembali(self):
        path = self.laporan.laporan_alat_dipinjam()
        self.assertEqual(path, os.path.join(self.folder_laporan, 'alat_dipinjam_%s.txt' % HARI_INI))
        isi = self.baca(path)
        for teks in ('A001', 'Multimeter Digital', 'M001 Andi Pratama', 'T001', '2026-11-09', 'A005', 'M003 Citra Lestari', 'terlambat', 'Jumlah: 3 alat'):
            self.assertIn(teks, isi)
        self.assertNotIn('A003', isi)

    def test_laporan_alat_rusak_memuat_kondisi_dan_pemeliharaan(self):
        isi = self.baca(self.laporan.laporan_alat_rusak())
        for teks in ('A004', 'Breadboard', 'rusak ringan', 'belum masuk pemeliharaan', 'A009', 'rusak berat', 'dalam perbaikan sejak 2026-11-06', 'Jumlah: 2 alat'):
            self.assertIn(teks, isi)

    def test_laporan_riwayat_mahasiswa(self):
        path = self.laporan.laporan_riwayat_mahasiswa('m003')
        self.assertEqual(os.path.basename(path), 'riwayat_M003_%s.txt' % HARI_INI)
        isi = self.baca(path)
        for teks in ('M003', 'Citra Lestari', 'T003', 'A004 Breadboard: dikembalikan 2026-11-05 (rusak ringan)', 'A005 Arduino Uno: masih dipinjam'):
            self.assertIn(teks, isi)

    def test_nim_tidak_terdaftar_ditolak_tanpa_membuat_file(self):
        with self.assertRaises(ValueError):
            self.laporan.laporan_riwayat_mahasiswa('M999')
        self.assertFalse(os.path.exists(self.folder_laporan))

    def test_membuat_laporan_tidak_mengubah_file_data(self):
        sebelum = self.semua_file()
        self.laporan.laporan_alat_dipinjam()
        self.laporan.laporan_alat_rusak()
        self.laporan.laporan_riwayat_mahasiswa('M001')
        self.assertEqual(self.semua_file(), sebelum)
if __name__ == '__main__':
    unittest.main()
