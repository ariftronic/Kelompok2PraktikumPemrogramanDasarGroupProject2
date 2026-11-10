import os
import shutil
import tempfile
import unittest
from app.file_manager import FileManager, FileManagerError
from app.logger import Logger
from app.konstanta import FILE_MAHASISWA, FILE_ALAT, FILE_LOG, STATUS_TERSEDIA, STATUS_DIPINJAM, STATUS_TIDAK_TERSEDIA, KONDISI_BAIK, KONDISI_RUSAK_RINGAN, KONDISI_RUSAK_BERAT
from app.manager.manager_alat import ManagerAlat
from app.manager.manager_mahasiswa import ManagerMahasiswa
DIR_SAMPEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_sampel')

class TransaksiPalsu:

    def __init__(self, nim_aktif=(), kode_aktif=()):
        self.nim_aktif = set(nim_aktif)
        self.kode_aktif = set(kode_aktif)

    def punya_transaksi_aktif(self, nim):
        return nim in self.nim_aktif

    def alat_dalam_transaksi_aktif(self, kode):
        return kode in self.kode_aktif

class DasarUji(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.fm = FileManager(direktori=self.folder)
        self.logger = Logger(self.fm)
        self.mhs = ManagerMahasiswa(self.fm, self.logger)
        self.alat = ManagerAlat(self.fm, self.logger)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def isi(self, nama_file):
        with open(os.path.join(self.folder, nama_file), encoding='utf-8') as f:
            return f.read()

    def tulis_mentah(self, nama_file, teks):
        with open(os.path.join(self.folder, nama_file), 'w', encoding='utf-8') as f:
            f.write(teks)

    def muat_sampel(self):
        for nama in (FILE_MAHASISWA, FILE_ALAT):
            shutil.copy(os.path.join(DIR_SAMPEL, nama), self.folder)
        self.alat.muat()
        self.mhs.muat()

class UjiMahasiswa(DasarUji):

    def test_tambah_tersimpan_dan_tercatat_log(self):
        m = self.mhs.tambah('m001', '  Andi   Pratama ', '081234567890')
        self.assertEqual((m.nim, m.nama), ('M001', 'Andi Pratama'))
        self.assertEqual(self.isi(FILE_MAHASISWA), 'M001|Andi Pratama|081234567890|aktif\n')
        self.assertIn('Mahasiswa M001 ditambahkan', self.isi(FILE_LOG))

    def test_no_hp_kosong_ditulis_strip_dan_dibaca_kembali_kosong(self):
        self.mhs.tambah('M001', 'Andi', '')
        self.assertEqual(self.isi(FILE_MAHASISWA), 'M001|Andi|-|aktif\n')
        baru = ManagerMahasiswa(self.fm, self.logger)
        baru.muat()
        self.assertEqual(baru.ambil('M001').no_hp, '')

    def test_nim_ganda_ditolak_dan_file_tidak_berubah(self):
        self.mhs.tambah('M001', 'Andi', '081234567890')
        sebelum = self.isi(FILE_MAHASISWA)
        with self.assertRaises(ValueError):
            self.mhs.tambah('m001', 'Budi', '081111111111')
        self.assertEqual(self.isi(FILE_MAHASISWA), sebelum)

    def test_input_tidak_valid_ditolak(self):
        for nim, nama, hp in [('', 'Andi', ''), ('M 1', 'Andi', ''), ('M001', '', ''), ('M001', '123', ''), ('M001', 'A|B', ''), ('M001', 'Andi', 'abc'), ('M001', 'Andi', '123')]:
            with self.assertRaises(ValueError, msg=(nim, nama, hp)):
                self.mhs.tambah(nim, nama, hp)
        self.assertEqual(self.mhs.semua(), [])

    def test_edit_sebagian_dan_tidak_ada(self):
        self.mhs.tambah('M001', 'Andi', '081234567890')
        self.mhs.edit('M001', nama='Andi P')
        self.assertEqual(self.mhs.ambil('M001').no_hp, '081234567890')
        self.mhs.edit('M001', no_hp='089999999999')
        self.assertEqual(self.mhs.ambil('M001').nama, 'Andi P')
        with self.assertRaises(ValueError):
            self.mhs.edit('M999', nama='X')

    def test_edit_tidak_valid_tidak_mengubah_data(self):
        self.mhs.tambah('M001', 'Andi', '081234567890')
        with self.assertRaises(ValueError):
            self.mhs.edit('M001', nama='Budi', no_hp='abc')
        self.assertEqual(self.mhs.ambil('M001').nama, 'Andi')

    def test_hapus_ditolak_bila_transaksi_aktif(self):
        self.mhs.tambah('M001', 'Andi', '')
        self.mhs.sambungkan_transaksi(TransaksiPalsu(nim_aktif={'M001'}))
        with self.assertRaises(ValueError):
            self.mhs.hapus('M001')
        self.assertTrue(self.mhs.ada('M001'))
        self.assertIn('M001', self.isi(FILE_MAHASISWA))

    def test_hapus_berhasil(self):
        self.mhs.tambah('M001', 'Andi', '')
        self.mhs.sambungkan_transaksi(TransaksiPalsu())
        self.mhs.hapus('M001')
        self.assertEqual(self.isi(FILE_MAHASISWA), '')
        self.assertIn('Mahasiswa M001 dihapus', self.isi(FILE_LOG))
        with self.assertRaises(ValueError):
            self.mhs.hapus('M001')

    def test_muat_melewati_ganda_dan_baris_tidak_valid(self):
        self.tulis_mentah(FILE_MAHASISWA, 'M001|Andi|0812345678|aktif\nM001|Andi Kembar|0812345678|aktif\nM002|Budi|0812345678|entah\nM003|Citra|-|aktif\n')
        self.mhs.muat()
        self.assertEqual([m.nim for m in self.mhs.semua()], ['M001', 'M003'])
        self.assertEqual(len(self.fm.daftar_peringatan), 2)
        self.mhs.muat()
        self.assertEqual(len(self.mhs.semua()), 2)

    def test_cari_fleksibel(self):
        self.muat_sampel()
        self.assertEqual([m.nim for m in self.mhs.cari('andi')], ['M001'])
        self.assertEqual([m.nim for m in self.mhs.cari('M00')], ['M001', 'M002', 'M003', 'M004', 'M005'])
        self.assertEqual([m.nim for m in self.mhs.cari('pratama andi')], ['M001'])
        self.assertEqual(self.mhs.cari('tidakada'), [])
        with self.assertRaises(ValueError):
            self.mhs.cari('   ')

    def test_gagal_simpan_memulihkan_memori(self):
        self.mhs.tambah('M001', 'Andi', '')
        asli = self.fm.tulis_baris

        def gagal(*a, **k):
            raise FileManagerError('disk penuh')
        self.fm.tulis_baris = gagal
        with self.assertRaises(FileManagerError):
            self.mhs.tambah('M002', 'Budi', '')
        self.fm.tulis_baris = asli
        self.assertEqual([m.nim for m in self.mhs.semua()], ['M001'])

class UjiAlat(DasarUji):

    def test_tambah_default_baik_tersedia(self):
        a = self.alat.tambah('a001', 'Multimeter Digital', 'Pengukuran')
        self.assertEqual((a.kode, a.kategori, a.kondisi, a.status), ('A001', 'pengukuran', KONDISI_BAIK, STATUS_TERSEDIA))
        self.assertEqual(self.isi(FILE_ALAT), 'A001|Multimeter Digital|pengukuran|baik|tersedia\n')
        self.assertIn('Alat A001 ditambahkan', self.isi(FILE_LOG))

    def test_alat_rusak_tidak_tersedia(self):
        a = self.alat.tambah('A002', 'Osiloskop', 'pengukuran', 'Rusak Ringan')
        self.assertEqual((a.kondisi, a.status), (KONDISI_RUSAK_RINGAN, STATUS_TIDAK_TERSEDIA))

    def test_kode_ganda_dan_kondisi_salah_ditolak(self):
        self.alat.tambah('A001', 'Multimeter', 'pengukuran')
        with self.assertRaises(ValueError):
            self.alat.tambah('a001', 'Lain', 'pengukuran')
        with self.assertRaises(ValueError):
            self.alat.tambah('A002', 'Lain', 'pengukuran', 'setengah rusak')
        self.assertEqual(len(self.alat.semua()), 1)

    def test_kategori_baru_diterima_dan_dipakai_ulang(self):
        self.alat.tambah('A001', 'Multimeter', 'Pengukuran')
        self.alat.tambah('A002', 'Osiloskop', 'PENGUKURAN')
        self.alat.tambah('A003', 'Kamera', 'perangkat multimedia')
        self.assertEqual(self.alat.daftar_kategori(), ['pengukuran', 'perangkat multimedia'])

    def test_edit_kondisi_menyesuaikan_status(self):
        self.alat.tambah('A001', 'Multimeter', 'pengukuran')
        a = self.alat.edit('A001', kondisi=KONDISI_RUSAK_BERAT)
        self.assertEqual(a.status, STATUS_TIDAK_TERSEDIA)
        a = self.alat.edit('A001', kondisi=KONDISI_BAIK, nama='Multimeter Baru')
        self.assertEqual((a.status, a.nama), (STATUS_TERSEDIA, 'Multimeter Baru'))

    def test_edit_alat_dipinjam_tidak_mengubah_status(self):
        self.alat.tambah('A001', 'Multimeter', 'pengukuran')
        self.alat.ambil('A001').tandai_dipinjam()
        a = self.alat.edit('A001', kondisi=KONDISI_RUSAK_RINGAN)
        self.assertEqual(a.status, STATUS_DIPINJAM)

    def test_hapus_ditolak_bila_transaksi_aktif_atau_dipinjam(self):
        self.alat.tambah('A001', 'Multimeter', 'pengukuran')
        self.alat.tambah('A002', 'Osiloskop', 'pengukuran')
        self.alat.sambungkan_transaksi(TransaksiPalsu(kode_aktif={'A001'}))
        with self.assertRaises(ValueError):
            self.alat.hapus('A001')
        self.alat.ambil('A002').tandai_dipinjam()
        with self.assertRaises(ValueError):
            self.alat.hapus('A002')
        self.assertEqual(len(self.alat.semua()), 2)

    def test_hapus_berhasil(self):
        self.alat.tambah('A001', 'Multimeter', 'pengukuran')
        self.alat.hapus('A001')
        self.assertEqual(self.isi(FILE_ALAT), '')
        self.assertIn('Alat A001 dihapus', self.isi(FILE_LOG))

    def test_tandai_dipinjam_dan_dikembalikan(self):
        a = self.alat.tambah('A001', 'Multimeter', 'pengukuran')
        a.tandai_dipinjam()
        with self.assertRaises(ValueError):
            a.tandai_dipinjam()
        a.tandai_dikembalikan(KONDISI_RUSAK_RINGAN)
        self.assertEqual(a.status, STATUS_TIDAK_TERSEDIA)
        a.tandai_dikembalikan(KONDISI_BAIK)
        self.assertEqual(a.status, STATUS_TERSEDIA)

    def test_data_sampel_termuat_tanpa_peringatan(self):
        self.muat_sampel()
        self.assertEqual(len(self.mhs.semua()), 5)
        self.assertEqual(len(self.alat.semua()), 10)
        self.assertEqual(self.fm.daftar_peringatan, [])
        self.assertEqual([a.kode for a in self.alat.dipinjam()], ['A001', 'A002', 'A005'])
        self.assertEqual([a.kode for a in self.alat.rusak()], ['A004', 'A009'])
        self.assertEqual(len(self.alat.tersedia()), 5)

    def test_cari_fleksibel_tantangan_a(self):
        self.muat_sampel()
        kode = lambda hasil: [a.kode for a in hasil]
        self.assertEqual(kode(self.alat.cari('a003')), ['A003'])
        self.assertEqual(kode(self.alat.cari('A-003')), ['A003'])
        self.assertEqual(kode(self.alat.cari('multi')), ['A001'])
        self.assertEqual(kode(self.alat.cari('PENGUKURAN')), ['A001', 'A002', 'A008', 'A009'])
        self.assertEqual(kode(self.alat.cari('pengukuran digital')), ['A001'])
        self.assertEqual(kode(self.alat.cari('ultrasonik hc sr04')), ['A010'])
        self.assertEqual(self.alat.cari('tidakada'), [])
        with self.assertRaises(ValueError):
            self.alat.cari('')

    def test_muat_melewati_kode_ganda_dan_baris_tidak_valid(self):
        self.tulis_mentah(FILE_ALAT, 'A001|Multimeter|pengukuran|baik|tersedia\nA001|Kembar|pengukuran|baik|tersedia\nA002|Osiloskop|pengukuran|baik|rusak\nA003|Power Supply|sumber daya|baik|tersedia\n')
        self.alat.muat()
        self.assertEqual([a.kode for a in self.alat.semua()], ['A001', 'A003'])
        self.assertEqual(len(self.fm.daftar_peringatan), 2)
if __name__ == '__main__':
    unittest.main()
