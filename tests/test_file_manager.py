import os
import shutil
import tempfile
import unittest

from app.file_manager import FileManager, FileManagerError
from app.logger import Logger
from app.konstanta import FILE_MAHASISWA, FILE_ALAT, FILE_LOG


class DasarUji(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.fm = FileManager(direktori=self.folder)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def isi(self, nama_file):
        with open(os.path.join(self.folder, nama_file), encoding="utf-8") as f:
            return f.read()

    def tulis_mentah(self, nama_file, teks):
        with open(os.path.join(self.folder, nama_file), "w", encoding="utf-8") as f:
            f.write(teks)


class UjiBaca(DasarUji):
    def test_file_belum_ada_dibuat_otomatis(self):
        self.assertEqual(self.fm.baca_baris(FILE_MAHASISWA), [])
        self.assertTrue(os.path.exists(os.path.join(self.folder, FILE_MAHASISWA)))

    def test_folder_belum_ada_dibuat_otomatis(self):
        shutil.rmtree(self.folder)
        self.assertEqual(self.fm.baca_baris(FILE_ALAT), [])
        self.assertTrue(os.path.isdir(self.folder))

    def test_file_kosong_tidak_error(self):
        self.tulis_mentah(FILE_MAHASISWA, "")
        self.assertEqual(self.fm.baca_baris(FILE_MAHASISWA), [])
        self.tulis_mentah(FILE_MAHASISWA, "\n\n   \n")
        self.assertEqual(self.fm.baca_baris(FILE_MAHASISWA), [])

    def test_baris_salah_format_dilewati_dengan_peringatan(self):
        self.tulis_mentah(FILE_MAHASISWA,
                          "M001|Andi|0812|aktif\n"
                          "M002|Budi|0856\n"
                          "M003|Citra|0877|aktif|lebih\n"
                          "M004||0899|aktif\n"
                          "M005|Dewi|0811|aktif\n")
        hasil = self.fm.baca_baris(FILE_MAHASISWA)
        self.assertEqual([b[0] for b in hasil], ["M001", "M005"])
        self.assertEqual(len(self.fm.daftar_peringatan), 3)

    def test_spasi_dibuang_dan_bom_diterima(self):
        with open(os.path.join(self.folder, FILE_MAHASISWA), "w", encoding="utf-8-sig") as f:
            f.write("M001 | Andi Pratama | 0812 | aktif\n")
        self.assertEqual(self.fm.baca_baris(FILE_MAHASISWA), [["M001", "Andi Pratama", "0812", "aktif"]])

    def test_file_bukan_teks_utf8_menjadi_filemanagererror(self):
        with open(os.path.join(self.folder, FILE_ALAT), "wb") as f:
            f.write(b"\xff\xfe\x00\x80\x81")
        with self.assertRaises(FileManagerError):
            self.fm.baca_baris(FILE_ALAT)


class UjiTulis(DasarUji):
    def test_tulis_lalu_baca_sama(self):
        data = [["M001", "Andi Pratama", "081234567890", "aktif"],
                ["M002", "Budi Santoso", "085612345678", "tidak aktif"]]
        self.fm.tulis_baris(FILE_MAHASISWA, data)
        self.assertEqual(self.fm.baca_baris(FILE_MAHASISWA), data)

    def test_nilai_kosong_ditulis_sebagai_strip(self):
        self.fm.tulis_baris(FILE_ALAT, [["A001", "Kamera", "multimedia", None, ""]])
        self.assertEqual(self.isi(FILE_ALAT), "A001|Kamera|multimedia|-|-\n")

    def test_tulis_ulang_tidak_menggandakan_data(self):
        data = [["A001", "Kamera", "multimedia", "baik", "tersedia"]]
        for _ in range(3):
            self.fm.tulis_baris(FILE_ALAT, data)
            data = self.fm.baca_baris(FILE_ALAT)
        self.assertEqual(len(data), 1)

    def test_string_berpemisah_diterima(self):
        self.fm.tulis_baris(FILE_ALAT, ["A002|Tripod|multimedia|baik|tersedia"])
        self.assertEqual(self.fm.baca_baris(FILE_ALAT)[0][1], "Tripod")

    def test_nilai_mengandung_pemisah_ditolak_file_tidak_berubah(self):
        awal = [["M001", "Andi", "0812", "aktif"]]
        self.fm.tulis_baris(FILE_MAHASISWA, awal)
        sebelum = self.isi(FILE_MAHASISWA)
        with self.assertRaises(ValueError):
            self.fm.tulis_baris(FILE_MAHASISWA, awal + [["M002", "Bu|di", "0856", "aktif"]])
        self.assertEqual(self.isi(FILE_MAHASISWA), sebelum)

    def test_jumlah_kolom_salah_ditolak_file_tidak_berubah(self):
        self.fm.tulis_baris(FILE_MAHASISWA, [["M001", "Andi", "0812", "aktif"]])
        sebelum = self.isi(FILE_MAHASISWA)
        with self.assertRaises(ValueError):
            self.fm.tulis_baris(FILE_MAHASISWA, [["M002", "Budi"]])
        self.assertEqual(self.isi(FILE_MAHASISWA), sebelum)

    def test_baris_baru_dalam_nilai_ditolak(self):
        with self.assertRaises(ValueError):
            self.fm.tulis_baris(FILE_MAHASISWA, [["M001", "An\ndi", "0812", "aktif"]])

    def test_tidak_ada_file_sementara_tersisa(self):
        self.fm.tulis_baris(FILE_MAHASISWA, [["M001", "Andi", "0812", "aktif"]])
        self.assertFalse(any(n.endswith(".tmp") for n in os.listdir(self.folder)))


class UjiLog(DasarUji):
    def test_log_ditambah_di_akhir_isi_lama_tetap(self):
        log = Logger(self.fm)
        self.assertTrue(log.catat("Mahasiswa M001 ditambahkan"))
        self.assertTrue(log.catat("Transaksi T001 dibuat"))
        baris = self.isi(FILE_LOG).splitlines()
        self.assertEqual(len(baris), 2)
        self.assertTrue(baris[0].startswith("[") and baris[0].endswith("] Mahasiswa M001 ditambahkan"))
        self.assertTrue(baris[1].endswith("] Transaksi T001 dibuat"))

    def test_log_lama_tidak_terhapus_setelah_logger_baru(self):
        Logger(self.fm).catat("pertama")
        Logger(FileManager(direktori=self.folder)).catat("kedua")
        self.assertEqual(len(self.isi(FILE_LOG).splitlines()), 2)

    def test_baca_terakhir(self):
        log = Logger(self.fm)
        for i in range(5):
            log.catat("aktivitas %d" % i)
        terakhir = log.baca_terakhir(2)
        self.assertEqual(len(terakhir), 2)
        self.assertTrue(terakhir[-1].endswith("aktivitas 4"))

    def test_catatan_beberapa_baris_digabung_menjadi_satu(self):
        Logger(self.fm).catat("baris satu\nbaris dua")
        self.assertEqual(len(self.isi(FILE_LOG).splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
