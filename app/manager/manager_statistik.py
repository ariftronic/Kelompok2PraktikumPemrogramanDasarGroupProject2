class ManagerStatistik:
    """Tantangan B: statistik peminjaman yang dihitung dari data transaksi di memori."""

    def __init__(self, manager_transaksi, manager_alat, manager_mahasiswa):
        self.manager_transaksi = manager_transaksi
        self.manager_alat = manager_alat
        self.manager_mahasiswa = manager_mahasiswa

    @staticmethod
    def _urutkan(hitungan, cari, jumlah):
        hasil = []
        for kunci, banyak in sorted(hitungan.items(), key=lambda item: (-item[1], item[0])):
            objek = cari(kunci)
            if objek is not None:
                hasil.append((objek, banyak))
        return hasil[:jumlah]

    def alat_terpopuler(self, jumlah=5):
        """Alat yang paling sering dipinjam, berupa list (Alat, berapa kali dipinjam)."""
        hitungan = {}
        for transaksi in self.manager_transaksi.semua():
            for detail in transaksi.daftar_detail:
                hitungan[detail.kode_alat] = hitungan.get(detail.kode_alat, 0) + 1
        return self._urutkan(hitungan, self.manager_alat.cari_berdasarkan_kode, jumlah)

    def mahasiswa_teraktif(self, jumlah=5):
        """Mahasiswa yang paling sering meminjam, berupa list (Mahasiswa, jumlah transaksi)."""
        hitungan = {}
        for transaksi in self.manager_transaksi.semua():
            hitungan[transaksi.nim] = hitungan.get(transaksi.nim, 0) + 1
        return self._urutkan(hitungan, self.manager_mahasiswa.cari_berdasarkan_nim, jumlah)

    def jumlah_transaksi_aktif(self):
        """Banyaknya transaksi yang belum selesai."""
        return sum((1 for t in self.manager_transaksi.semua() if t.masih_aktif()))

    def jumlah_transaksi_selesai(self):
        """Banyaknya transaksi yang semua alatnya sudah dikembalikan."""
        return sum((1 for t in self.manager_transaksi.semua() if not t.masih_aktif()))
