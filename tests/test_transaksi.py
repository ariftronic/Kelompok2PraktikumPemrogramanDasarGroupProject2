import os
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from unittest import mock
from app.file_manager import FileManager, FileManagerError
from app.konstanta import FILE_ALAT, FILE_DETAIL_TRANSAKSI, FILE_LOG, FILE_TRANSAKSI, FORMAT_TANGGAL, KONDISI_BAIK, KONDISI_RUSAK_BERAT, KONDISI_RUSAK_RINGAN, STATUS_DIPINJAM, STATUS_TERSEDIA, STATUS_TIDAK_TERSEDIA, TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI
from app.logger import Logger
from app.manager.manager_pengembalian import ManagerPengembalian
from app.manager.manager_transaksi import ManagerTransaksi
from app.models.transaksi import DetailTransaksi, Transaksi
from tests.fakes import ManagerAlatTiruan, ManagerMahasiswaTiruan

class DasarUji(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)
        self.fm = FileManager(direktori=self.folder)
        self.logger = Logger(self.fm)
        self.alat = ManagerAlatTiruan(self.fm, self.logger)
        self.mahasiswa = ManagerMahasiswaTiruan(self.fm, self.logger)
        for kode in ('A001', 'A002', 'A003'):
            self.alat.tambah(kode, 'Alat ' + kode, 'umum')
        self.mahasiswa.tambah('M001', 'Andi', '0812')
        self.mahasiswa.tambah('M002', 'Budi', '0856')
        self.transaksi = ManagerTransaksi(self.fm, self.logger, self.mahasiswa, self.alat)
        self.pengembalian = ManagerPengembalian(self.fm, self.logger, self.transaksi, self.alat)

    def isi(self, nama_file):
        with open(os.path.join(self.folder, nama_file), encoding='utf-8') as f:
            return f.read()

    def status_alat(self, kode):
        return next((a.status for a in self.alat.semua() if a.kode == kode))

    def muat_ulang(self):
        alat = ManagerAlatTiruan(self.fm, self.logger)
        alat.muat()
        transaksi = ManagerTransaksi(self.fm, self.logger, self.mahasiswa, alat)
        transaksi.muat()
        return transaksi

class UjiModel(unittest.TestCase):

    def test_baris_transaksi_dan_detail_bolak_balik(self):
        kolom = ['T001', 'M001', '2026-11-10', '2026-11-17', 'dipinjam']
        self.assertEqual(Transaksi.dari_baris(kolom).ke_baris(), kolom)
        kolom = ['T001', 'A001', 'dikembalikan', 'rusak berat', '2026-11-12']
        self.assertEqual(DetailTransaksi.dari_baris(kolom).ke_baris(), kolom)

    def test_perbarui_status(self):
        t = Transaksi('T001', 'M001', '2026-11-10', '2026-11-17')
        t.daftar_detail = [DetailTransaksi('T001', 'A001'), DetailTransaksi('T001', 'A002')]
        t.perbarui_status()
        self.assertEqual(t.status, TRX_DIPINJAM)
        t.daftar_detail[0].kembalikan(KONDISI_BAIK, '2026-11-12')
        t.perbarui_status()
        self.assertEqual(t.status, TRX_SEBAGIAN)
        self.assertTrue(t.masih_aktif())
        t.daftar_detail[1].kembalikan(KONDISI_BAIK, '2026-11-12')
        t.perbarui_status()
        self.assertEqual(t.status, TRX_SELESAI)
        self.assertFalse(t.masih_aktif())

class UjiPeminjaman(DasarUji):

    def test_buat_transaksi_banyak_alat(self):
        t = self.transaksi.buat('M001', ['A001', 'A002'])
        hari_ini = date.today()
        self.assertEqual(t.id_transaksi, 'T001')
        self.assertEqual(t.tgl_pinjam, hari_ini.strftime(FORMAT_TANGGAL))
        self.assertEqual(t.batas_kembali, (hari_ini + timedelta(days=7)).strftime(FORMAT_TANGGAL))
        self.assertEqual([d.kode_alat for d in t.daftar_detail], ['A001', 'A002'])
        self.assertEqual(self.status_alat('A001'), STATUS_DIPINJAM)
        self.assertEqual(self.status_alat('A002'), STATUS_DIPINJAM)
        self.assertEqual(self.status_alat('A003'), STATUS_TERSEDIA)

    def test_transaksi_tersimpan_ke_file_dan_log(self):
        self.transaksi.buat('M001', ['A001', 'A002'])
        self.assertEqual(len(self.isi(FILE_TRANSAKSI).splitlines()), 1)
        self.assertEqual(len(self.isi(FILE_DETAIL_TRANSAKSI).splitlines()), 2)
        self.assertIn('A001|Alat A001|umum|baik|dipinjam', self.isi(FILE_ALAT))
        self.assertIn('Transaksi T001 dibuat', self.isi(FILE_LOG))

    def test_id_transaksi_bertambah(self):
        self.transaksi.buat('M001', ['A001'])
        self.assertEqual(self.transaksi.buat('M002', ['A002']).id_transaksi, 'T002')

    def test_alat_tidak_tersedia_ditolak(self):
        self.transaksi.buat('M001', ['A001'])
        with self.assertRaises(ValueError):
            self.transaksi.buat('M002', ['A002', 'A001'])
        self.assertEqual(self.status_alat('A002'), STATUS_TERSEDIA)

    def test_maksimal_dua_transaksi_aktif(self):
        self.transaksi.buat('M001', ['A001'])
        self.transaksi.buat('M001', ['A002'])
        with self.assertRaises(ValueError):
            self.transaksi.buat('M001', ['A003'])

    def test_transaksi_selesai_tidak_dihitung_aktif(self):
        self.transaksi.buat('M001', ['A001'])
        self.transaksi.buat('M001', ['A002'])
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.assertEqual(self.transaksi.buat('M001', ['A003']).id_transaksi, 'T003')

    def test_input_tidak_valid_ditolak(self):
        with self.assertRaises(ValueError):
            self.transaksi.buat('M999', ['A001'])
        with self.assertRaises(ValueError):
            self.transaksi.buat('M001', ['A999'])
        with self.assertRaises(ValueError):
            self.transaksi.buat('M001', [])
        with self.assertRaises(ValueError):
            self.transaksi.buat('M001', ['A001', 'A001'])

    def test_penolakan_tidak_mengubah_file_atau_status(self):
        self.transaksi.buat('M001', ['A001'])
        sebelum = (self.isi(FILE_TRANSAKSI), self.isi(FILE_DETAIL_TRANSAKSI), self.isi(FILE_ALAT))
        with self.assertRaises(ValueError):
            self.transaksi.buat('M002', ['A002', 'A001'])
        sesudah = (self.isi(FILE_TRANSAKSI), self.isi(FILE_DETAIL_TRANSAKSI), self.isi(FILE_ALAT))
        self.assertEqual(sebelum, sesudah)
        self.assertEqual(len(self.transaksi.semua()), 1)

    def test_gagal_simpan_pertama_mengembalikan_memori_ke_file(self):
        with mock.patch.object(self.alat, 'simpan', side_effect=FileManagerError('disk penuh')):
            with self.assertRaises(FileManagerError):
                self.transaksi.buat('M001', ['A001'])
        self.assertEqual(self.status_alat('A001'), STATUS_TERSEDIA)
        self.assertEqual(self.transaksi.semua(), [])

    def test_muat_ulang_sama_dengan_sebelum_ditutup(self):
        self.transaksi.buat('M001', ['A001', 'A002'])
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_RUSAK_RINGAN)
        baru = self.muat_ulang()
        t = baru.ambil('T001')
        self.assertEqual(t.status, TRX_SEBAGIAN)
        self.assertEqual([str(d) for d in t.daftar_detail], [str(d) for d in self.transaksi.ambil('T001').daftar_detail])

    def test_muat_melewati_data_ganda_dan_rujukan_hilang(self):
        self.transaksi.buat('M001', ['A001'])
        with open(os.path.join(self.folder, FILE_TRANSAKSI), 'a', encoding='utf-8') as f:
            f.write('T001|M001|2026-11-10|2026-11-17|dipinjam\n')
            f.write('T002|M999|2026-11-10|2026-11-17|dipinjam\n')
        with open(os.path.join(self.folder, FILE_DETAIL_TRANSAKSI), 'a', encoding='utf-8') as f:
            f.write('T001|A001|dipinjam|-|-\n')
            f.write('T001|A999|dipinjam|-|-\n')
            f.write('T777|A001|dipinjam|-|-\n')
        baru = self.muat_ulang()
        self.assertEqual([t.id_transaksi for t in baru.semua()], ['T001'])
        self.assertEqual(len(baru.ambil('T001').daftar_detail), 1)
        self.assertEqual(len(self.fm.daftar_peringatan), 5)

    def test_pencarian_dan_riwayat(self):
        self.transaksi.buat('M001', ['A001'])
        self.transaksi.buat('M001', ['A002'])
        self.transaksi.buat('M002', ['A003'])
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.assertEqual([t.id_transaksi for t in self.transaksi.cari_berdasarkan_mahasiswa('M001')], ['T002'])
        self.assertEqual([t.id_transaksi for t in self.transaksi.riwayat_mahasiswa('M001')], ['T001', 'T002'])
        self.assertEqual(self.transaksi.cari_berdasarkan_mahasiswa('M999'), [])

    def test_pemeriksaan_untuk_aturan_penghapusan(self):
        self.transaksi.buat('M001', ['A001', 'A002'])
        self.assertTrue(self.transaksi.punya_transaksi_aktif('M001'))
        self.assertFalse(self.transaksi.punya_transaksi_aktif('M002'))
        self.assertTrue(self.transaksi.alat_dalam_transaksi_aktif('A001'))
        self.assertFalse(self.transaksi.alat_dalam_transaksi_aktif('A003'))
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.assertFalse(self.transaksi.alat_dalam_transaksi_aktif('A001'))
        self.assertTrue(self.transaksi.alat_dalam_transaksi_aktif('A002'))
        self.pengembalian.kembalikan('T001', 'A002', KONDISI_BAIK)
        self.assertFalse(self.transaksi.punya_transaksi_aktif('M001'))

    def test_ambil_transaksi_tidak_ada(self):
        with self.assertRaises(ValueError):
            self.transaksi.ambil('T999')

class UjiPengembalian(DasarUji):

    def setUp(self):
        super().setUp()
        self.transaksi.buat('M001', ['A001', 'A002'])

    def test_pengembalian_sebagian(self):
        t = self.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.assertEqual(t.status, TRX_SEBAGIAN)
        self.assertEqual(self.status_alat('A001'), STATUS_TERSEDIA)
        self.assertEqual(self.status_alat('A002'), STATUS_DIPINJAM)
        self.assertEqual([d.kode_alat for d in self.pengembalian.daftar_belum_kembali('T001')], ['A002'])
        self.assertIn('T001|A001|dikembalikan|baik|' + date.today().strftime(FORMAT_TANGGAL), self.isi(FILE_DETAIL_TRANSAKSI))

    def test_semua_dikembalikan_transaksi_selesai(self):
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        t = self.pengembalian.kembalikan('T001', 'A002', KONDISI_BAIK)
        self.assertEqual(t.status, TRX_SELESAI)
        self.assertEqual(self.pengembalian.daftar_belum_kembali('T001'), [])
        self.assertIn('T001|M001|', self.isi(FILE_TRANSAKSI))
        self.assertTrue(self.isi(FILE_TRANSAKSI).strip().endswith('selesai'))

    def test_alat_rusak_tidak_kembali_tersedia(self):
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_RUSAK_RINGAN)
        self.pengembalian.kembalikan('T001', 'A002', KONDISI_RUSAK_BERAT)
        for kode, kondisi in (('A001', KONDISI_RUSAK_RINGAN), ('A002', KONDISI_RUSAK_BERAT)):
            alat = next((a for a in self.alat.semua() if a.kode == kode))
            self.assertEqual((alat.kondisi, alat.status), (kondisi, STATUS_TIDAK_TERSEDIA))
        with self.assertRaises(ValueError):
            self.transaksi.buat('M002', ['A001'])

    def test_pengembalian_ditolak_tidak_mengubah_data(self):
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        sebelum = (self.isi(FILE_TRANSAKSI), self.isi(FILE_DETAIL_TRANSAKSI), self.isi(FILE_ALAT))
        for id_transaksi, kode, kondisi in (('T001', 'A001', KONDISI_BAIK), ('T001', 'A003', KONDISI_BAIK), ('T999', 'A002', KONDISI_BAIK), ('T001', 'A002', 'hancur')):
            with self.assertRaises(ValueError):
                self.pengembalian.kembalikan(id_transaksi, kode, kondisi)
        sesudah = (self.isi(FILE_TRANSAKSI), self.isi(FILE_DETAIL_TRANSAKSI), self.isi(FILE_ALAT))
        self.assertEqual(sebelum, sesudah)
        self.assertEqual(self.transaksi.ambil('T001').status, TRX_SEBAGIAN)

    def test_daftar_belum_kembali_transaksi_tidak_ada(self):
        with self.assertRaises(ValueError):
            self.pengembalian.daftar_belum_kembali('T999')

    def test_log_pengembalian(self):
        self.pengembalian.kembalikan('T001', 'A001', KONDISI_RUSAK_BERAT)
        self.assertIn('Alat A001 dikembalikan dalam kondisi rusak berat', self.isi(FILE_LOG))
if __name__ == '__main__':
    unittest.main()
