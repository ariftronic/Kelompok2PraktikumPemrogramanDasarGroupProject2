from datetime import date, datetime
from app.konstanta import FORMAT_TANGGAL, FORMAT_WAKTU_LOG
from app.manager.manager_pengembalian import ManagerPengembalian
LEBAR_GARIS = 70

class ManagerLaporan:
    """Tantangan F: membuat laporan text file yang rapi di folder laporan/."""

    def __init__(self, file_manager_laporan, manager_alat, manager_mahasiswa, manager_transaksi, manager_pemeliharaan):
        self.file_manager = file_manager_laporan
        self.manager_alat = manager_alat
        self.manager_mahasiswa = manager_mahasiswa
        self.manager_transaksi = manager_transaksi
        self.manager_pemeliharaan = manager_pemeliharaan

    @staticmethod
    def _kepala(judul):
        return [judul, 'Dibuat: %s' % datetime.now().strftime(FORMAT_WAKTU_LOG), '=' * LEBAR_GARIS, '']

    @staticmethod
    def _tabel(kepala, isi):
        # lebar kolom mengikuti isi terpanjang supaya kolom tetap lurus
        lebar = [max([len(judul)] + [len(baris[i]) for baris in isi]) for i, judul in enumerate(kepala)]

        def susun(sel):
            return '  '.join((teks.ljust(lebar[i]) for i, teks in enumerate(sel))).rstrip()
        garis = '-' * (sum(lebar) + 2 * (len(lebar) - 1))
        if not isi:
            return [susun(kepala), garis, '(tidak ada data)', garis]
        return [susun(kepala), garis] + [susun(baris) for baris in isi] + [garis]

    def _nama_file(self, jenis):
        return '%s_%s.txt' % (jenis, date.today().strftime(FORMAT_TANGGAL))

    def _nama_alat(self, kode):
        alat = self.manager_alat.cari_berdasarkan_kode(kode)
        return alat.nama if alat is not None else '-'

    def _nama_mahasiswa(self, nim):
        mahasiswa = self.manager_mahasiswa.cari_berdasarkan_nim(nim)
        return '%s %s' % (nim, mahasiswa.nama) if mahasiswa is not None else nim

    def laporan_alat_dipinjam(self):
        """Laporan alat yang sedang dipinjam beserta peminjam dan batas kembalinya; mengembalikan path file."""
        isi = []
        for nomor, alat in enumerate(self.manager_alat.dipinjam(), start=1):
            transaksi = self.manager_transaksi.transaksi_aktif_untuk_alat(alat.kode)
            if transaksi is None:
                isi.append([str(nomor), alat.kode, alat.nama, '-', '-', '-', '-'])
                continue
            terlambat = ManagerPengembalian.hari_terlambat(transaksi)
            keterangan = 'terlambat %d hari' % terlambat if terlambat else 'belum jatuh tempo'
            isi.append([str(nomor), alat.kode, alat.nama, self._nama_mahasiswa(transaksi.nim), transaksi.id_transaksi, transaksi.batas_kembali, keterangan])
        baris = self._kepala('LAPORAN ALAT YANG SEDANG DIPINJAM')
        baris += self._tabel(['No', 'Kode', 'Nama Alat', 'Peminjam', 'Transaksi', 'Batas Kembali', 'Keterangan'], isi)
        baris += ['Jumlah: %d alat' % len(isi)]
        return self.file_manager.tulis_teks(self._nama_file('alat_dipinjam'), baris)

    def laporan_alat_rusak(self):
        """Laporan alat rusak ringan/berat beserta status pemeliharaannya; mengembalikan path file."""
        isi = []
        for nomor, alat in enumerate(self.manager_alat.rusak(), start=1):
            catatan = self.manager_pemeliharaan.aktif_untuk(alat.kode) if self.manager_pemeliharaan is not None else None
            pemeliharaan = 'dalam perbaikan sejak %s' % catatan.tgl_masuk if catatan is not None else 'belum masuk pemeliharaan'
            isi.append([str(nomor), alat.kode, alat.nama, alat.kategori, alat.kondisi, pemeliharaan])
        baris = self._kepala('LAPORAN ALAT YANG RUSAK')
        baris += self._tabel(['No', 'Kode', 'Nama Alat', 'Kategori', 'Kondisi', 'Pemeliharaan'], isi)
        baris += ['Jumlah: %d alat' % len(isi)]
        return self.file_manager.tulis_teks(self._nama_file('alat_rusak'), baris)

    def laporan_riwayat_mahasiswa(self, nim):
        """Laporan semua transaksi seorang mahasiswa; ValueError bila NIM tidak terdaftar."""
        mahasiswa = self.manager_mahasiswa.ambil(nim)
        riwayat = self.manager_transaksi.riwayat_mahasiswa(mahasiswa.nim)
        baris = self._kepala('LAPORAN RIWAYAT PEMINJAMAN MAHASISWA')
        baris += ['NIM              : %s' % mahasiswa.nim, 'Nama             : %s' % mahasiswa.nama, 'Status peminjaman: %s' % mahasiswa.status_aktif, 'Jumlah transaksi : %d' % len(riwayat), '']
        if not riwayat:
            baris.append('(belum pernah meminjam)')
        for transaksi in riwayat:
            baris.append('%s | pinjam %s | batas %s | %s' % (transaksi.id_transaksi, transaksi.tgl_pinjam, transaksi.batas_kembali, transaksi.status))
            for detail in transaksi.daftar_detail:
                alat = '%s %s' % (detail.kode_alat, self._nama_alat(detail.kode_alat))
                if detail.sudah_kembali():
                    baris.append('   - %s: dikembalikan %s (%s)' % (alat, detail.tgl_kembali, detail.kondisi))
                else:
                    baris.append('   - %s: masih dipinjam' % alat)
            baris.append('')
        baris.append('-' * LEBAR_GARIS)
        return self.file_manager.tulis_teks(self._nama_file('riwayat_%s' % mahasiswa.nim), baris)
