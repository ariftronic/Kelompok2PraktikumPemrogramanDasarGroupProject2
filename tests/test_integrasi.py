import io
import os
import shutil
import tempfile
import unittest
from unittest import mock
from app.file_manager import FileManager, FileManagerError
from app.konstanta import FILE_ALAT, FILE_DETAIL_TRANSAKSI, FILE_LOG, FILE_MAHASISWA, FILE_TRANSAKSI, KONDISI_BAIK, KONDISI_RUSAK_BERAT, KONDISI_RUSAK_RINGAN, STATUS_DIPINJAM, STATUS_TERSEDIA, STATUS_TIDAK_TERSEDIA, TRX_DIPINJAM, TRX_SEBAGIAN, TRX_SELESAI
from app.logger import Logger
from app.manager.manager_alat import ManagerAlat
from app.manager.manager_mahasiswa import ManagerMahasiswa
from app.manager.manager_pengembalian import ManagerPengembalian
from app.manager.manager_transaksi import ManagerTransaksi
from app.models.transaksi import DetailTransaksi, Transaksi
DIR_SAMPEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_sampel')
FILE_DATA = (FILE_MAHASISWA, FILE_ALAT, FILE_TRANSAKSI, FILE_DETAIL_TRANSAKSI)

class Aplikasi:

    def __init__(self, folder):
        self.fm = FileManager(direktori=folder)
        self.logger = Logger(self.fm)
        self.alat = ManagerAlat(self.fm, self.logger)
        self.mahasiswa = ManagerMahasiswa(self.fm, self.logger)
        self.transaksi = ManagerTransaksi(self.fm, self.logger, self.mahasiswa, self.alat)
        self.pengembalian = ManagerPengembalian(self.fm, self.logger, self.transaksi, self.alat)
        self.alat.sambungkan_transaksi(self.transaksi)
        self.mahasiswa.sambungkan_transaksi(self.transaksi)
        self.fm.pastikan_semua_file()
        self.alat.muat()
        self.mahasiswa.muat()
        self.transaksi.muat()

    def status_alat(self, kode):
        return self.alat.ambil(kode).status

class DasarFolder(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)
        diam = mock.patch('sys.stdout', new_callable=io.StringIO)
        diam.start()
        self.addCleanup(diam.stop)

    def isi(self, nama_file):
        with open(os.path.join(self.folder, nama_file), encoding='utf-8') as f:
            return f.read()

    def tulis_mentah(self, nama_file, teks):
        with open(os.path.join(self.folder, nama_file), 'w', encoding='utf-8') as f:
            f.write(teks)

    def semua_file(self):
        return tuple((self.isi(n) for n in FILE_DATA))

class DasarUji(DasarFolder):

    def setUp(self):
        super().setUp()
        self.app = Aplikasi(self.folder)
        self.app.mahasiswa.tambah('M001', 'Andi', '081234567890')
        self.app.mahasiswa.tambah('M002', 'Budi', '')
        for kode, nama in (('A001', 'Kamera'), ('A002', 'Tripod'), ('A003', 'Kabel LAN')):
            self.app.alat.tambah(kode, nama, 'perangkat multimedia')

class UjiHurufBesarKecil(DasarUji):

    def test_masukan_huruf_kecil_diterima_di_semua_modul(self):
        t = self.app.transaksi.buat(' m001 ', ['a001', ' a002'])
        self.assertEqual((t.nim, [d.kode_alat for d in t.daftar_detail]), ('M001', ['A001', 'A002']))
        self.assertEqual(len(self.app.transaksi.cari_berdasarkan_mahasiswa('m001')), 1)
        self.assertEqual(len(self.app.transaksi.riwayat_mahasiswa('m001')), 1)
        self.assertTrue(self.app.transaksi.punya_transaksi_aktif('m001'))
        self.assertTrue(self.app.transaksi.alat_dalam_transaksi_aktif('a001'))
        self.assertEqual(len(self.app.pengembalian.daftar_belum_kembali('t001')), 2)
        hasil = self.app.pengembalian.kembalikan('t001', 'a001', KONDISI_BAIK)
        self.assertEqual(hasil.status, TRX_SEBAGIAN)
        self.assertIn('Alat A001 dikembalikan dalam kondisi baik (T001)', self.isi(FILE_LOG))

    def test_aturan_6_berlaku_untuk_masukan_huruf_kecil(self):
        self.app.transaksi.buat('M001', ['A001'])
        with self.assertRaises(ValueError):
            self.app.mahasiswa.hapus('m001')
        with self.assertRaises(ValueError):
            self.app.alat.hapus('a001')

class UjiSkenarioWajib(DasarUji):

    def test_skenario_1_data_tercatat_di_file(self):
        self.assertEqual(self.isi(FILE_MAHASISWA), 'M001|Andi|081234567890|aktif\nM002|Budi|-|aktif\n')
        self.assertEqual(len(self.isi(FILE_ALAT).splitlines()), 3)

    def test_skenario_2_status_alat_berubah_di_program_dan_file(self):
        self.app.transaksi.buat('M001', ['A001', 'A002'])
        self.assertEqual(self.app.status_alat('A001'), STATUS_DIPINJAM)
        self.assertEqual(self.app.status_alat('A003'), STATUS_TERSEDIA)
        self.assertIn('A001|Kamera|perangkat multimedia|baik|dipinjam', self.isi(FILE_ALAT))
        self.assertIn('A002|Tripod|perangkat multimedia|baik|dipinjam', self.isi(FILE_ALAT))
        self.assertEqual(len(self.isi(FILE_DETAIL_TRANSAKSI).splitlines()), 2)

    def test_skenario_3_alat_tidak_tersedia_ditolak_file_tidak_berubah(self):
        self.app.transaksi.buat('M001', ['A001'])
        sebelum = self.semua_file()
        with self.assertRaises(ValueError):
            self.app.transaksi.buat('M002', ['A002', 'A001'])
        self.assertEqual(self.semua_file(), sebelum)

    def test_skenario_4_pengembalian_sebagian(self):
        self.app.transaksi.buat('M001', ['A001', 'A002'])
        t = self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.assertEqual(t.status, TRX_SEBAGIAN)
        self.assertEqual(self.app.status_alat('A001'), STATUS_TERSEDIA)
        self.assertEqual(self.app.status_alat('A002'), STATUS_DIPINJAM)
        self.assertEqual([d.kode_alat for d in self.app.pengembalian.daftar_belum_kembali('T001')], ['A002'])
        self.assertTrue(self.isi(FILE_TRANSAKSI).strip().endswith('sebagian dikembalikan'))

    def test_skenario_5_alat_rusak_tidak_kembali_tersedia(self):
        self.app.transaksi.buat('M001', ['A001', 'A002'])
        self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_RUSAK_RINGAN)
        t = self.app.pengembalian.kembalikan('T001', 'A002', KONDISI_RUSAK_BERAT)
        self.assertEqual(t.status, TRX_SELESAI)
        self.assertEqual(self.app.status_alat('A001'), STATUS_TIDAK_TERSEDIA)
        self.assertEqual(self.app.status_alat('A002'), STATUS_TIDAK_TERSEDIA)
        self.assertEqual([a.kode for a in self.app.alat.rusak()], ['A001', 'A002'])
        self.assertEqual([a.kode for a in self.app.alat.tersedia()], ['A003'])

    def test_skenario_6_hapus_mahasiswa_dan_alat_aktif_ditolak(self):
        self.app.transaksi.buat('M001', ['A001'])
        sebelum = self.semua_file()
        with self.assertRaises(ValueError):
            self.app.mahasiswa.hapus('M001')
        with self.assertRaises(ValueError):
            self.app.alat.hapus('A001')
        self.assertEqual(self.semua_file(), sebelum)
        self.app.mahasiswa.hapus('M002')

    def test_skenario_7_data_sama_setelah_program_ditutup_dan_dijalankan_lagi(self):
        self.app.transaksi.buat('M001', ['A001', 'A002'])
        self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_RUSAK_RINGAN)
        baru = Aplikasi(self.folder)
        self.assertEqual([m.nim for m in baru.mahasiswa.semua()], ['M001', 'M002'])
        self.assertEqual([a.kode for a in baru.alat.semua()], ['A001', 'A002', 'A003'])
        t = baru.transaksi.ambil('T001')
        self.assertEqual(t.status, TRX_SEBAGIAN)
        self.assertEqual([str(d) for d in t.daftar_detail], [str(d) for d in self.app.transaksi.ambil('T001').daftar_detail])
        self.assertEqual(baru.status_alat('A001'), STATUS_TIDAK_TERSEDIA)
        self.assertEqual(baru.status_alat('A002'), STATUS_DIPINJAM)
        self.assertEqual(baru.fm.daftar_peringatan, [])

    def test_skenario_7_muat_berulang_tidak_menggandakan_data(self):
        self.app.transaksi.buat('M001', ['A001'])
        for _ in range(3):
            baru = Aplikasi(self.folder)
            baru.transaksi.simpan()
            baru.alat.simpan()
            baru.mahasiswa.simpan()
        self.assertEqual(len(baru.transaksi.semua()), 1)
        self.assertEqual(len(self.isi(FILE_TRANSAKSI).splitlines()), 1)
        self.assertEqual(len(self.isi(FILE_DETAIL_TRANSAKSI).splitlines()), 1)
        self.assertEqual(len(self.isi(FILE_ALAT).splitlines()), 3)

    def test_skenario_8_file_dihapus_atau_dikosongkan_tidak_error(self):
        self.app.transaksi.buat('M001', ['A001'])
        for nama in FILE_DATA + (FILE_LOG,):
            for tindakan in ('hapus', 'kosongkan'):
                path = os.path.join(self.folder, nama)
                if tindakan == 'hapus':
                    os.remove(path)
                else:
                    open(path, 'w').close()
                Aplikasi(self.folder)
                self.assertTrue(os.path.exists(path), (nama, tindakan))

    def test_skenario_9_baris_salah_format_dilewati_dan_program_tetap_dapat_dipakai(self):
        self.app.transaksi.buat('M001', ['A001'])
        for nama in FILE_DATA:
            with open(os.path.join(self.folder, nama), 'a', encoding='utf-8') as f:
                f.write('RUSAK|hanya dua kolom\n')
        baru = Aplikasi(self.folder)
        self.assertEqual(len(baru.fm.daftar_peringatan), 4)
        self.assertEqual(len(baru.mahasiswa.semua()), 2)
        self.assertEqual(len(baru.transaksi.semua()), 1)
        self.assertEqual(baru.transaksi.buat('M002', ['A002']).id_transaksi, 'T002')

class UjiIsiBarisTidakValid(DasarUji):

    def test_transaksi_dengan_status_atau_tanggal_salah_dilewati(self):
        self.tulis_mentah(FILE_TRANSAKSI, 'T001|M001|2026-11-01|2026-11-08|entah\nT002|M001|bukan-tanggal|2026-11-08|dipinjam\nT003|M001|2026-11-01|2026-11-08|dipinjam\n')
        self.tulis_mentah(FILE_DETAIL_TRANSAKSI, 'T003|A001|hilang|-|-\nT003|A001|dikembalikan|hancur|2026-11-02\nT003|A001|dikembalikan|baik|31-12-2026\nT003|A001|dipinjam|baik|-\nT003|A002|dipinjam|-|-\n')
        baru = Aplikasi(self.folder)
        self.assertEqual([t.id_transaksi for t in baru.transaksi.semua()], ['T003'])
        self.assertEqual([d.kode_alat for d in baru.transaksi.ambil('T003').daftar_detail], ['A002'])
        self.assertEqual(len(baru.fm.daftar_peringatan), 2 + 4 + 1)
        self.assertEqual(baru.status_alat('A002'), STATUS_DIPINJAM)

    def test_model_menolak_isi_tidak_valid(self):
        with self.assertRaises(ValueError):
            Transaksi.dari_baris(['T001', 'M001', '2026-11-01', '2026-11-08', 'entah'])
        with self.assertRaises(ValueError):
            Transaksi.dari_baris(['T001', 'M001', '2026-13-01', '2026-11-08', 'dipinjam'])
        with self.assertRaises(ValueError):
            DetailTransaksi.dari_baris(['T001', 'A001', 'dikembalikan', '-', '2026-11-02'])
        with self.assertRaises(ValueError):
            DetailTransaksi.dari_baris(['T001', 'A001', 'dipinjam', 'baik', '-'])
        DetailTransaksi.dari_baris(['T001', 'A001', 'dikembalikan', 'baik', '2026-11-02'])

class UjiKonsistensiAntarFile(DasarUji):

    def test_alat_yang_dipinjam_tetapi_tercatat_tersedia_diperbaiki(self):
        self.app.transaksi.buat('M001', ['A001'])
        self.tulis_mentah(FILE_ALAT, self.isi(FILE_ALAT).replace('|dipinjam', '|tersedia'))
        baru = Aplikasi(self.folder)
        self.assertEqual(baru.status_alat('A001'), STATUS_DIPINJAM)
        with self.assertRaises(ValueError):
            baru.transaksi.buat('M002', ['A001'])

    def test_alat_tercatat_dipinjam_tanpa_transaksi_menjadi_tersedia(self):
        self.tulis_mentah(FILE_ALAT, self.isi(FILE_ALAT).replace('A002|Tripod|perangkat multimedia|baik|tersedia', 'A002|Tripod|perangkat multimedia|baik|dipinjam'))
        baru = Aplikasi(self.folder)
        self.assertEqual(baru.status_alat('A002'), STATUS_TERSEDIA)
        self.assertEqual(len(baru.fm.daftar_peringatan), 1)

    def test_status_transaksi_mengikuti_detail(self):
        self.app.transaksi.buat('M001', ['A001', 'A002'])
        self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.tulis_mentah(FILE_TRANSAKSI, self.isi(FILE_TRANSAKSI).replace('sebagian dikembalikan', 'selesai'))
        baru = Aplikasi(self.folder)
        self.assertEqual(baru.transaksi.ambil('T001').status, TRX_SEBAGIAN)
        self.assertTrue(baru.transaksi.punya_transaksi_aktif('M001'))

    def test_transaksi_tanpa_alat_dibuang_agar_tidak_memblokir_mahasiswa(self):
        self.tulis_mentah(FILE_TRANSAKSI, 'T001|M001|2026-11-01|2026-11-08|dipinjam\nT002|M001|2026-11-02|2026-11-09|dipinjam\n')
        self.tulis_mentah(FILE_DETAIL_TRANSAKSI, '')
        baru = Aplikasi(self.folder)
        self.assertEqual(baru.transaksi.semua(), [])
        self.assertEqual(baru.transaksi.buat('M001', ['A001']).id_transaksi, 'T001')

    def test_gagal_menulis_transaksi_setelah_alat_tertulis_memulihkan_status_alat(self):
        asli = self.app.fm.tulis_baris

        def gagal(nama_file, baris):
            if nama_file == FILE_TRANSAKSI:
                raise FileManagerError('disk penuh')
            return asli(nama_file, baris)
        with mock.patch.object(self.app.fm, 'tulis_baris', side_effect=gagal):
            with self.assertRaises(FileManagerError):
                self.app.transaksi.buat('M001', ['A001'])
        self.assertEqual(self.app.status_alat('A001'), STATUS_TERSEDIA)
        self.assertEqual(self.app.transaksi.semua(), [])
        self.assertIn('A001|Kamera|perangkat multimedia|baik|tersedia', self.isi(FILE_ALAT))
        self.assertEqual(self.isi(FILE_TRANSAKSI), '')
        self.assertEqual(self.app.transaksi.buat('M001', ['A001']).id_transaksi, 'T001')

    def test_gagal_menulis_transaksi_saat_pengembalian_dapat_diulang(self):
        self.app.transaksi.buat('M001', ['A001'])
        asli = self.app.fm.tulis_baris

        def gagal(nama_file, baris):
            if nama_file == FILE_TRANSAKSI:
                raise FileManagerError('disk penuh')
            return asli(nama_file, baris)
        with mock.patch.object(self.app.fm, 'tulis_baris', side_effect=gagal):
            with self.assertRaises(FileManagerError):
                self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_RUSAK_BERAT)
        self.assertEqual(self.app.transaksi.ambil('T001').status, TRX_DIPINJAM)
        self.assertEqual(self.app.status_alat('A001'), STATUS_DIPINJAM)
        t = self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.assertEqual(t.status, TRX_SELESAI)
        self.assertEqual(self.app.status_alat('A001'), STATUS_TERSEDIA)

class UjiDataSampel(DasarFolder):

    def test_data_sampel_termuat_utuh_tanpa_peringatan(self):
        for nama in FILE_DATA:
            shutil.copy(os.path.join(DIR_SAMPEL, nama), self.folder)
        app = Aplikasi(self.folder)
        self.assertEqual(app.fm.daftar_peringatan, [])
        self.assertEqual((len(app.mahasiswa.semua()), len(app.alat.semua()), len(app.transaksi.semua())), (5, 10, 3))
        self.assertEqual([t.status for t in app.transaksi.semua()], [TRX_DIPINJAM, TRX_SELESAI, TRX_SEBAGIAN])
        self.assertEqual([a.kode for a in app.alat.dipinjam()], ['A001', 'A002', 'A005'])
        self.assertTrue(app.transaksi.punya_transaksi_aktif('M003'))
        self.assertFalse(app.transaksi.punya_transaksi_aktif('M002'))
        with self.assertRaises(ValueError):
            app.mahasiswa.hapus('M001')
if __name__ == '__main__':
    unittest.main()
