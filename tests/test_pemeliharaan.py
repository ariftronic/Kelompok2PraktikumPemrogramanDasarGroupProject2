import unittest
from datetime import date
from app.konstanta import FILE_ALAT, FILE_PEMELIHARAAN, FORMAT_TANGGAL, KONDISI_BAIK, KONDISI_RUSAK_BERAT, KONDISI_RUSAK_RINGAN, PML_PROSES, PML_SELESAI, STATUS_TERSEDIA, STATUS_TIDAK_TERSEDIA
from tests.test_integrasi import Aplikasi, DasarUji
HARI_INI = date.today().strftime(FORMAT_TANGGAL)

class UjiPemeliharaan(DasarUji):

    def rusakkan(self, kode, kondisi=KONDISI_RUSAK_BERAT):
        self.app.alat.edit(kode, kondisi=kondisi)

    def test_alat_rusak_masuk_lalu_selesai_pemeliharaan_kembali_tersedia(self):
        self.app.transaksi.buat('M001', ['A001'])
        self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_RUSAK_BERAT)
        p = self.app.pemeliharaan.mulai('A001')
        self.assertEqual((p.id_pemeliharaan, p.status), ('P001', PML_PROSES))
        self.assertEqual(self.isi(FILE_PEMELIHARAAN), 'P001|A001|%s|-|dalam perbaikan\n' % HARI_INI)
        self.assertNotIn('A001', [a.kode for a in self.app.alat.tersedia()])
        self.app.pemeliharaan.selesai('a001')
        self.assertEqual(self.isi(FILE_PEMELIHARAAN), 'P001|A001|%s|%s|selesai\n' % (HARI_INI, HARI_INI))
        self.assertIn('A001|Kamera|perangkat multimedia|baik|tersedia', self.isi(FILE_ALAT))
        self.assertEqual(self.app.status_alat('A001'), STATUS_TERSEDIA)

    def test_alat_baik_dipinjam_atau_tidak_ada_ditolak_dan_file_tidak_berubah(self):
        self.app.transaksi.buat('M001', ['A002'])
        sebelum = self.semua_file()
        for kode in ('A001', 'A002', 'A999'):
            with self.assertRaises(ValueError, msg=kode):
                self.app.pemeliharaan.mulai(kode)
        with self.assertRaises(ValueError):
            self.app.pemeliharaan.selesai('A003')
        self.assertEqual(self.semua_file(), sebelum)

    def test_alat_tidak_bisa_masuk_pemeliharaan_dua_kali(self):
        self.rusakkan('A001')
        self.app.pemeliharaan.mulai('A001')
        with self.assertRaises(ValueError):
            self.app.pemeliharaan.mulai('A001')
        self.assertEqual(len(self.app.pemeliharaan.semua()), 1)

    def test_alat_dalam_pemeliharaan_tidak_bisa_dipinjam_diedit_kondisinya_atau_dihapus(self):
        self.rusakkan('A001', KONDISI_RUSAK_RINGAN)
        self.app.pemeliharaan.mulai('A001')
        with self.assertRaises(ValueError):
            self.app.transaksi.buat('M001', ['A001'])
        with self.assertRaises(ValueError):
            self.app.alat.edit('A001', kondisi=KONDISI_BAIK)
        with self.assertRaises(ValueError):
            self.app.alat.hapus('A001')
        self.app.alat.edit('A001', nama='Kamera Lama')
        self.assertEqual(self.app.status_alat('A001'), STATUS_TIDAK_TERSEDIA)
        self.app.pemeliharaan.selesai('A001')
        with self.assertRaises(ValueError):
            self.app.alat.hapus('A001')

    def test_pemeliharaan_bertahan_setelah_dijalankan_ulang_dan_id_berlanjut(self):
        self.rusakkan('A001')
        self.rusakkan('A002')
        self.app.pemeliharaan.mulai('A001')
        self.app.pemeliharaan.selesai('A001')
        self.app.pemeliharaan.mulai('A002')
        baru = Aplikasi(self.folder)
        self.assertEqual(baru.fm.daftar_peringatan, [])
        self.assertEqual([(p.id_pemeliharaan, p.status) for p in baru.pemeliharaan.semua()], [('P001', PML_SELESAI), ('P002', PML_PROSES)])
        self.assertTrue(baru.pemeliharaan.sedang_diperbaiki('A002'))
        baru.alat.edit('A003', kondisi=KONDISI_RUSAK_BERAT)
        self.assertEqual(baru.pemeliharaan.mulai('A003').id_pemeliharaan, 'P003')

class UjiMuatPemeliharaan(DasarUji):

    def test_baris_merujuk_alat_tidak_ada_atau_tanggal_mundur_masuk_karantina(self):
        self.tulis_mentah(FILE_PEMELIHARAAN, 'P001|A999|2026-11-01|-|dalam perbaikan\nP002|A001|2026-11-01|2026-10-01|selesai\n')
        baru = Aplikasi(self.folder)
        self.assertEqual(baru.pemeliharaan.semua(), [])
        self.assertEqual(len(self.karantina(FILE_PEMELIHARAAN)), 2)
        baru.alat.edit('A001', kondisi=KONDISI_RUSAK_BERAT)
        self.assertEqual(baru.pemeliharaan.mulai('A001').id_pemeliharaan, 'P003')

    def test_alat_dalam_proses_yang_tercatat_tersedia_ditahan(self):
        self.tulis_mentah(FILE_PEMELIHARAAN, 'P001|A001|2026-11-01|-|dalam perbaikan\n')
        baru = Aplikasi(self.folder)
        self.assertEqual(baru.status_alat('A001'), STATUS_TIDAK_TERSEDIA)
        self.assertEqual(len(baru.fm.daftar_peringatan), 1)
        with self.assertRaises(ValueError):
            baru.transaksi.buat('M001', ['A001'])
    def test_edit_alat_yang_sedang_diperbaiki_tidak_membuatnya_tersedia(self):
        self.tulis_mentah(FILE_PEMELIHARAAN, 'P001|A001|2026-11-01|-|dalam perbaikan\n')
        baru = Aplikasi(self.folder)
        baru.alat.edit('A001', nama='Kamera Lama')
        self.assertEqual(baru.status_alat('A001'), STATUS_TIDAK_TERSEDIA)
if __name__ == '__main__':
    unittest.main()
