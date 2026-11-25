import unittest
from app.konstanta import KONDISI_BAIK
from app.manager.manager_statistik import ManagerStatistik
from tests.test_integrasi import DasarUji

class UjiStatistik(DasarUji):

    def setUp(self):
        super().setUp()
        self.statistik = ManagerStatistik(self.app.transaksi, self.app.alat, self.app.mahasiswa)

    def isi_riwayat(self):
        # T001 dan T002 selesai, T003 masih aktif; A001 dipinjam 3 kali, M001 meminjam 2 kali
        self.app.transaksi.buat('M001', ['A001', 'A002'])
        self.app.pengembalian.kembalikan('T001', 'A001', KONDISI_BAIK)
        self.app.pengembalian.kembalikan('T001', 'A002', KONDISI_BAIK)
        self.app.transaksi.buat('M001', ['A001'])
        self.app.pengembalian.kembalikan('T002', 'A001', KONDISI_BAIK)
        self.app.transaksi.buat('M002', ['A001', 'A003'])

    def test_alat_dan_mahasiswa_tersering(self):
        self.isi_riwayat()
        self.assertEqual([(a.kode, n) for a, n in self.statistik.alat_terpopuler()], [('A001', 3), ('A002', 1), ('A003', 1)])
        self.assertEqual([(a.kode, n) for a, n in self.statistik.alat_terpopuler(1)], [('A001', 3)])
        self.assertEqual([(m.nim, n) for m, n in self.statistik.mahasiswa_teraktif()], [('M001', 2), ('M002', 1)])

    def test_jumlah_transaksi_aktif_dan_selesai(self):
        self.isi_riwayat()
        self.assertEqual((self.statistik.jumlah_transaksi_aktif(), self.statistik.jumlah_transaksi_selesai()), (1, 2))

    def test_tanpa_transaksi(self):
        self.assertEqual(self.statistik.alat_terpopuler(), [])
        self.assertEqual(self.statistik.mahasiswa_teraktif(), [])
        self.assertEqual((self.statistik.jumlah_transaksi_aktif(), self.statistik.jumlah_transaksi_selesai()), (0, 0))
if __name__ == '__main__':
    unittest.main()
