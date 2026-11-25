from app.file_manager import FileManager, FileManagerError
from app.logger import Logger
from app.manager.manager_alat import ManagerAlat
from app.manager.manager_laporan import ManagerLaporan
from app.manager.manager_mahasiswa import ManagerMahasiswa
from app.manager.manager_pemeliharaan import ManagerPemeliharaan
from app.manager.manager_pengembalian import ManagerPengembalian
from app.manager.manager_statistik import ManagerStatistik
from app.manager.manager_transaksi import ManagerTransaksi
from app.konstanta import BARIS_PER_HALAMAN, DIR_KARANTINA, DIR_LAPORAN, PEMISAH, KONDISI_BAIK, KONDISI_RUSAK_RINGAN, KONDISI_RUSAK_BERAT
LEBAR = 60

def baca_input(pesan, boleh_kosong=False):
    """Membaca input; karakter pemisah file ditolak, kosong ditolak kecuali diizinkan."""
    while True:
        nilai = input(pesan).strip()
        if PEMISAH in nilai:
            print("  Karakter '%s' tidak boleh digunakan. Silakan ulangi." % PEMISAH)
            continue
        if nilai == '' and (not boleh_kosong):
            print('  Input tidak boleh kosong.')
            continue
        return nilai

def baca_daftar_kode(pesan):
    """Membaca beberapa kode yang dipisahkan koma."""
    mentah = baca_input(pesan)
    return [k.strip() for k in mentah.split(',') if k.strip()]

def konfirmasi(pesan):
    """Pertanyaan y/n."""
    while True:
        jawab = input('%s (y/n): ' % pesan).strip().lower()
        if jawab in ('y', 'ya'):
            return True
        if jawab in ('n', 't', 'tidak'):
            return False
        print('  Jawab dengan y atau n.')

def pilih_kondisi():
    """Memilih kondisi alat dengan nomor."""
    pilihan = {'1': KONDISI_BAIK, '2': KONDISI_RUSAK_RINGAN, '3': KONDISI_RUSAK_BERAT}
    while True:
        print('  1. %s   2. %s   3. %s' % (KONDISI_BAIK, KONDISI_RUSAK_RINGAN, KONDISI_RUSAK_BERAT))
        nomor = input('  Pilih kondisi (1-3): ').strip()
        if nomor in pilihan:
            return pilihan[nomor]
        print('  Pilihan tidak valid.')

def pilih_kriteria_cari():
    """Memilih kriteria pencarian alat (Tantangan A)."""
    pilihan = {'': 'semua', '1': 'semua', '2': 'kode', '3': 'nama', '4': 'kategori'}
    while True:
        print('  Cari berdasarkan: 1. semua kolom   2. kode   3. sebagian nama   4. kategori')
        nomor = input('  Pilih kriteria (Enter = semua kolom): ').strip()
        if nomor in pilihan:
            return pilihan[nomor]
        print('  Pilihan tidak valid.')

def cetak_judul(judul):
    """Judul menu di antara dua garis."""
    print()
    print('=' * LEBAR)
    print(judul)
    print('=' * LEBAR)

def cetak_daftar(judul, daftar):
    """Mencetak daftar bernomor, berhenti tiap BARIS_PER_HALAMAN baris."""
    print()
    print('%s (%d data)' % (judul, len(daftar)))
    print('-' * LEBAR)
    if not daftar:
        print('(tidak ada data)')
        return
    for nomor, item in enumerate(daftar, start=1):
        print('%d. %s' % (nomor, item))
        if nomor % BARIS_PER_HALAMAN == 0 and nomor < len(daftar):
            jawab = input('-- %d dari %d data. Enter untuk lanjut, q untuk berhenti: ' % (nomor, len(daftar))).strip().lower()
            if jawab == 'q':
                return

def cetak_berhasil(pesan, objek=None):
    """Pesan [OK] beserta data yang baru diproses."""
    print('[OK] %s' % pesan)
    if objek is not None:
        print('     %s' % objek)

class AplikasiPeminjaman:
    """Menu interaktif; hanya mengatur tampilan dan input, aturan bisnis ada di manager."""

    def __init__(self):
        self.file_manager = FileManager()
        self.file_manager_laporan = FileManager(direktori=DIR_LAPORAN)
        self.logger = Logger(self.file_manager)
        self.manager = {}

    def siapkan(self):
        """Membuat manager, memuat semua file, dan menyelaraskan file bila ada baris yang bermasalah."""
        try:
            self.file_manager.pastikan_semua_file()
            fm, lg = (self.file_manager, self.logger)
            alat = ManagerAlat(fm, lg)
            mahasiswa = ManagerMahasiswa(fm, lg)
            transaksi = ManagerTransaksi(fm, lg, mahasiswa, alat)
            pengembalian = ManagerPengembalian(fm, lg, transaksi, alat)
            pemeliharaan = ManagerPemeliharaan(fm, lg, alat, transaksi)
            alat.sambungkan_transaksi(transaksi)
            alat.sambungkan_pemeliharaan(pemeliharaan)
            mahasiswa.sambungkan_transaksi(transaksi)
            self.manager = {'alat': alat, 'mahasiswa': mahasiswa, 'transaksi': transaksi, 'pengembalian': pengembalian, 'pemeliharaan': pemeliharaan, 'statistik': ManagerStatistik(transaksi, alat, mahasiswa), 'laporan': ManagerLaporan(self.file_manager_laporan, alat, mahasiswa, transaksi, pemeliharaan)}
            for kunci in ('alat', 'mahasiswa', 'transaksi', 'pemeliharaan'):
                self.manager[kunci].muat()
            if fm.daftar_peringatan:
                self._selaraskan_file()
        except FileManagerError as e:
            print('[ERROR FILE] %s' % e)
            print('Program tidak dapat dimulai karena data gagal dimuat.')
            return False
        return True

    def _selaraskan_file(self):
        # Baris yang dilewati sudah disalin ke karantina, jadi file utama langsung ditulis ulang
        # agar isinya sama dengan data di program (Aturan 7) dan peringatan tidak muncul lagi.
        fm = self.file_manager
        isi = self.manager['transaksi'].daftar_isi_file()
        isi += [self.manager[kunci].isi_file() for kunci in ('alat', 'mahasiswa', 'pemeliharaan')]
        fm.tulis_banyak(isi)
        for peringatan in fm.daftar_peringatan:
            self.logger.catat(peringatan)
        if fm.jumlah_karantina:
            print('[INFO] %d baris bermasalah dipindahkan ke folder %s agar tidak hilang.' % (fm.jumlah_karantina, fm.path_file(DIR_KARANTINA)))
            print('       Periksa folder tersebut bila data perlu dipulihkan.')

    def _manager(self, kunci):
        return self.manager[kunci]

    def _jalankan_aksi(self, aksi):
        try:
            aksi()
        except ValueError as e:
            print('[DITOLAK] %s' % e)
        except FileManagerError as e:
            print('[ERROR FILE] %s' % e)
        except EOFError:
            raise
        except Exception as e:
            print('[ERROR] Terjadi kesalahan tak terduga (%s): %s' % (type(e).__name__, e))

    def _loop_menu(self, judul, pilihan, label_nol):
        while True:
            cetak_judul(judul)
            for nomor, (label, _) in enumerate(pilihan, start=1):
                print('%2d. %s' % (nomor, label))
            print('%2d. %s' % (0, label_nol))
            masukan = input('Pilih menu: ').strip()
            if masukan == '0':
                return
            if masukan.isdigit() and 1 <= int(masukan) <= len(pilihan):
                self._jalankan_aksi(pilihan[int(masukan) - 1][1])
            else:
                print('Pilihan tidak valid.')

    def jalankan(self):
        """Titik awal program: menyiapkan data lalu menampilkan menu utama."""
        cetak_judul('SISTEM PENGELOLAAN PEMINJAMAN PERALATAN LABORATORIUM')
        if not self.siapkan():
            return
        self.logger.catat('Program dijalankan')
        pilihan_utama = [('Kelola data mahasiswa', self.menu_mahasiswa), ('Kelola data alat', self.menu_alat), ('Buat transaksi peminjaman', self.buat_transaksi), ('Tampilkan transaksi', self.tampilkan_transaksi), ('Proses pengembalian alat', self.proses_pengembalian), ('Cari transaksi berdasarkan mahasiswa', self.cari_transaksi_mahasiswa), ('Tampilkan alat yang tersedia', self.tampilkan_alat_tersedia), ('Tampilkan alat yang sedang dipinjam', self.tampilkan_alat_dipinjam), ('Tampilkan alat yang rusak', self.tampilkan_alat_rusak), ('Tampilkan riwayat peminjaman mahasiswa', self.tampilkan_riwayat), ('Lihat log aktivitas', self.lihat_log), ('Statistik peminjaman', self.tampilkan_statistik), ('Pemeliharaan alat', self.menu_pemeliharaan), ('Ekspor laporan', self.menu_laporan)]
        try:
            self._loop_menu('MENU UTAMA', pilihan_utama, 'Keluar')
        except (KeyboardInterrupt, EOFError):
            print()
        finally:
            self._keluar()

    def _keluar(self):
        print('\nMenyimpan data...')
        for kunci in ('alat', 'mahasiswa', 'transaksi', 'pemeliharaan'):
            try:
                if self.manager.get(kunci) is not None:
                    self.manager[kunci].simpan()
            except FileManagerError as e:
                print('[ERROR FILE] Data %s gagal disimpan: %s' % (kunci, e))
        self.logger.catat('Program ditutup')
        print('Data tersimpan. Sampai jumpa.')

    def menu_mahasiswa(self):
        self._loop_menu('KELOLA DATA MAHASISWA', [('Tambah mahasiswa', self.tambah_mahasiswa), ('Edit mahasiswa', self.edit_mahasiswa), ('Hapus mahasiswa', self.hapus_mahasiswa), ('Cari mahasiswa (NIM / nama)', self.cari_mahasiswa), ('Tampilkan semua mahasiswa', self.tampilkan_mahasiswa)], 'Kembali')

    def tambah_mahasiswa(self):
        m = self._manager('mahasiswa')
        nim = baca_input('NIM    : ')
        nama = baca_input('Nama   : ')
        no_hp = baca_input('No. HP (boleh dikosongkan) : ', boleh_kosong=True)
        cetak_berhasil('Mahasiswa berhasil ditambahkan.', m.tambah(nim, nama, no_hp))

    def edit_mahasiswa(self):
        m = self._manager('mahasiswa')
        nim = baca_input('NIM yang diedit : ')
        print('Kosongkan (Enter) bila tidak ingin mengubah.')
        nama = baca_input('Nama baru   : ', boleh_kosong=True)
        no_hp = baca_input("No. HP baru ('-' untuk mengosongkan) : ", boleh_kosong=True)
        if not (nama or no_hp):
            print('Tidak ada perubahan.')
            return
        cetak_berhasil('Data mahasiswa diperbarui.', m.edit(nim, nama=nama or None, no_hp=no_hp or None))

    def hapus_mahasiswa(self):
        m = self._manager('mahasiswa')
        nim = baca_input('NIM yang dihapus : ')
        if not konfirmasi('Yakin menghapus mahasiswa %s?' % nim):
            print('Dibatalkan.')
            return
        m.hapus(nim)
        cetak_berhasil('Mahasiswa %s dihapus.' % nim)

    def cari_mahasiswa(self):
        m = self._manager('mahasiswa')
        kata = baca_input('Kata kunci (NIM / nama) : ')
        cetak_daftar('Hasil pencarian mahasiswa', m.cari(kata))

    def tampilkan_mahasiswa(self):
        cetak_daftar('Daftar mahasiswa', self._manager('mahasiswa').semua())

    def menu_alat(self):
        self._loop_menu('KELOLA DATA ALAT', [('Tambah alat', self.tambah_alat), ('Edit alat', self.edit_alat), ('Hapus alat', self.hapus_alat), ('Cari alat (kode / nama / kategori)', self.cari_alat), ('Tampilkan semua alat', self.tampilkan_alat)], 'Kembali')

    def tambah_alat(self):
        m = self._manager('alat')
        kode = baca_input('Kode alat : ')
        nama = baca_input('Nama alat : ')
        kategori_ada = m.daftar_kategori()
        if kategori_ada:
            print('Kategori yang sudah ada: %s' % ', '.join(kategori_ada))
            print('(ketik kategori baru bila belum ada)')
        kategori = baca_input('Kategori  : ')
        kondisi = baca_input('Kondisi (baik/rusak ringan/rusak berat) [%s] : ' % KONDISI_BAIK, boleh_kosong=True) or KONDISI_BAIK
        cetak_berhasil('Alat berhasil ditambahkan.', m.tambah(kode, nama, kategori, kondisi))

    def edit_alat(self):
        m = self._manager('alat')
        kode = baca_input('Kode alat yang diedit : ')
        print('Kosongkan (Enter) bila tidak ingin mengubah.')
        nama = baca_input('Nama baru     : ', boleh_kosong=True)
        kategori = baca_input('Kategori baru : ', boleh_kosong=True)
        kondisi = baca_input('Kondisi baru  : ', boleh_kosong=True)
        if not (nama or kategori or kondisi):
            print('Tidak ada perubahan.')
            return
        cetak_berhasil('Data alat diperbarui.', m.edit(kode, nama=nama or None, kategori=kategori or None, kondisi=kondisi or None))

    def hapus_alat(self):
        m = self._manager('alat')
        kode = baca_input('Kode alat yang dihapus : ')
        if not konfirmasi('Yakin menghapus alat %s?' % kode):
            print('Dibatalkan.')
            return
        m.hapus(kode)
        cetak_berhasil('Alat %s dihapus.' % kode)

    def cari_alat(self):
        m = self._manager('alat')
        kriteria = pilih_kriteria_cari()
        kata = baca_input('Kata kunci : ')
        cetak_daftar('Hasil pencarian alat', m.cari(kata, kriteria))

    def tampilkan_alat(self):
        cetak_daftar('Daftar alat', self._manager('alat').semua())

    def tampilkan_alat_tersedia(self):
        cetak_daftar('Alat yang tersedia', self._manager('alat').tersedia())

    def tampilkan_alat_dipinjam(self):
        cetak_daftar('Alat yang sedang dipinjam', self._manager('alat').dipinjam())

    def tampilkan_alat_rusak(self):
        cetak_daftar('Alat yang rusak', self._manager('alat').rusak())

    def buat_transaksi(self):
        t = self._manager('transaksi')
        cetak_daftar('Alat yang tersedia', self._manager('alat').tersedia())
        nim = baca_input('NIM peminjam : ')
        daftar_kode = baca_daftar_kode('Kode alat (pisahkan dengan koma) : ')
        cetak_berhasil('Transaksi peminjaman berhasil dibuat.', t.buat(nim, daftar_kode))

    def tampilkan_transaksi(self):
        cetak_daftar('Daftar transaksi', self._manager('transaksi').semua())

    def cari_transaksi_mahasiswa(self):
        mhs = self._manager('mahasiswa').ambil(baca_input('NIM mahasiswa : '))
        cetak_daftar('Transaksi aktif milik %s - %s' % (mhs.nim, mhs.nama), self._manager('transaksi').cari_berdasarkan_mahasiswa(mhs.nim))

    def tampilkan_riwayat(self):
        mhs = self._manager('mahasiswa').ambil(baca_input('NIM mahasiswa : '))
        cetak_daftar('Riwayat peminjaman %s - %s' % (mhs.nim, mhs.nama), self._manager('transaksi').riwayat_mahasiswa(mhs.nim))

    def proses_pengembalian(self):
        p = self._manager('pengembalian')
        id_transaksi = baca_input('ID transaksi : ')
        belum = p.daftar_belum_kembali(id_transaksi)
        cetak_daftar('Alat yang belum dikembalikan pada %s' % id_transaksi, belum)
        if not belum:
            return
        for kode in baca_daftar_kode('Kode alat yang dikembalikan (pisahkan dengan koma) : '):
            print('Kondisi alat %s:' % kode)
            kondisi = pilih_kondisi()
            try:
                hasil = p.kembalikan(id_transaksi, kode, kondisi)
                cetak_berhasil('Alat %s dikembalikan (%s).' % (kode, kondisi), hasil)
                terlambat = p.hari_terlambat(hasil)
                if terlambat:
                    print('     [PERINGATAN] Terlambat %d hari dari batas %s.' % (terlambat, hasil.batas_kembali))
            except ValueError as e:
                print('[DITOLAK] %s: %s' % (kode, e))

    def lihat_log(self):
        cetak_daftar('Log aktivitas terbaru', self.logger.baca_terakhir(20))

    def tampilkan_statistik(self):
        s = self._manager('statistik')
        cetak_judul('STATISTIK PEMINJAMAN')
        print('Jumlah transaksi aktif   : %d' % s.jumlah_transaksi_aktif())
        print('Jumlah transaksi selesai : %d' % s.jumlah_transaksi_selesai())
        cetak_daftar('Alat yang paling sering dipinjam', ['%s %s (%d kali)' % (a.kode, a.nama, n) for a, n in s.alat_terpopuler()])
        cetak_daftar('Mahasiswa yang paling sering meminjam', ['%s %s (%d transaksi)' % (m.nim, m.nama, n) for m, n in s.mahasiswa_teraktif()])

    def menu_pemeliharaan(self):
        self._loop_menu('PEMELIHARAAN ALAT', [('Masukkan alat rusak ke pemeliharaan', self.mulai_pemeliharaan), ('Selesaikan pemeliharaan (alat kembali tersedia)', self.selesaikan_pemeliharaan), ('Tampilkan alat yang sedang diperbaiki', self.tampilkan_pemeliharaan_aktif), ('Tampilkan riwayat pemeliharaan', self.tampilkan_riwayat_pemeliharaan)], 'Kembali')

    def _teks_pemeliharaan(self, catatan):
        alat = self._manager('alat').cari_berdasarkan_kode(catatan.kode_alat)
        nama = alat.nama if alat is not None else '-'
        selesai = 'selesai %s' % catatan.tgl_selesai if not catatan.masih_proses() else catatan.status
        return '%s | %s %s | masuk %s | %s' % (catatan.id_pemeliharaan, catatan.kode_alat, nama, catatan.tgl_masuk, selesai)

    def mulai_pemeliharaan(self):
        p = self._manager('pemeliharaan')
        calon = [a for a in self._manager('alat').rusak() if not p.sedang_diperbaiki(a.kode)]
        cetak_daftar('Alat rusak yang belum masuk pemeliharaan', calon)
        if not calon:
            return
        kode = baca_input('Kode alat : ')
        cetak_berhasil('Alat masuk daftar pemeliharaan.', self._teks_pemeliharaan(p.mulai(kode)))

    def selesaikan_pemeliharaan(self):
        p = self._manager('pemeliharaan')
        aktif = p.aktif()
        cetak_daftar('Alat yang sedang diperbaiki', [self._teks_pemeliharaan(c) for c in aktif])
        if not aktif:
            return
        kode = baca_input('Kode alat yang selesai diperbaiki : ')
        cetak_berhasil('Pemeliharaan selesai, alat kembali tersedia.', self._teks_pemeliharaan(p.selesai(kode)))

    def tampilkan_pemeliharaan_aktif(self):
        cetak_daftar('Alat yang sedang diperbaiki', [self._teks_pemeliharaan(c) for c in self._manager('pemeliharaan').aktif()])

    def tampilkan_riwayat_pemeliharaan(self):
        cetak_daftar('Riwayat pemeliharaan', [self._teks_pemeliharaan(c) for c in self._manager('pemeliharaan').semua()])

    def menu_laporan(self):
        self._loop_menu('EKSPOR LAPORAN', [('Laporan alat yang sedang dipinjam', self.laporan_alat_dipinjam), ('Laporan alat yang rusak', self.laporan_alat_rusak), ('Laporan riwayat peminjaman mahasiswa', self.laporan_riwayat)], 'Kembali')

    def laporan_alat_dipinjam(self):
        cetak_berhasil('Laporan disimpan di %s' % self._manager('laporan').laporan_alat_dipinjam())

    def laporan_alat_rusak(self):
        cetak_berhasil('Laporan disimpan di %s' % self._manager('laporan').laporan_alat_rusak())

    def laporan_riwayat(self):
        nim = baca_input('NIM mahasiswa : ')
        cetak_berhasil('Laporan disimpan di %s' % self._manager('laporan').laporan_riwayat_mahasiswa(nim))

def tampilkan_menu_utama():
    """Dipanggil main.py untuk menjalankan aplikasi."""
    AplikasiPeminjaman().jalankan()
