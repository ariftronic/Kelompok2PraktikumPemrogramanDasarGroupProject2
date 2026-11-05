import importlib

from app.file_manager import FileManager, FileManagerError
from app.logger import Logger
from app.konstanta import (
    PEMISAH, KONDISI_BAIK, KONDISI_RUSAK_RINGAN, KONDISI_RUSAK_BERAT,
)

LEBAR = 60

LOKASI_MANAGER = {
    "alat": ("app.manager.manager_alat", "ManagerAlat"),
    "mahasiswa": ("app.manager.manager_mahasiswa", "ManagerMahasiswa"),
    "transaksi": ("app.manager.manager_transaksi", "ManagerTransaksi"),
    "pengembalian": ("app.manager.manager_pengembalian", "ManagerPengembalian"),
}


class ModulBelumTersedia(Exception):
    pass


def baca_input(pesan, boleh_kosong=False):
    while True:
        nilai = input(pesan).strip()
        if PEMISAH in nilai:
            print("  Karakter '%s' tidak boleh digunakan. Silakan ulangi." % PEMISAH)
            continue
        if nilai == "" and not boleh_kosong:
            print("  Input tidak boleh kosong.")
            continue
        return nilai


def baca_daftar_kode(pesan):
    mentah = baca_input(pesan)
    return [k.strip() for k in mentah.split(",") if k.strip()]


def konfirmasi(pesan):
    while True:
        jawab = input("%s (y/n): " % pesan).strip().lower()
        if jawab in ("y", "ya"):
            return True
        if jawab in ("n", "t", "tidak"):
            return False
        print("  Jawab dengan y atau n.")


def pilih_kondisi():
    pilihan = {"1": KONDISI_BAIK, "2": KONDISI_RUSAK_RINGAN, "3": KONDISI_RUSAK_BERAT}
    while True:
        print("  1. %s   2. %s   3. %s" % (KONDISI_BAIK, KONDISI_RUSAK_RINGAN, KONDISI_RUSAK_BERAT))
        nomor = input("  Pilih kondisi (1-3): ").strip()
        if nomor in pilihan:
            return pilihan[nomor]
        print("  Pilihan tidak valid.")


def cetak_judul(judul):
    print()
    print("=" * LEBAR)
    print(judul)
    print("=" * LEBAR)


def cetak_daftar(judul, daftar):
    print()
    print("%s (%d data)" % (judul, len(daftar)))
    print("-" * LEBAR)
    if not daftar:
        print("(tidak ada data)")
        return
    for nomor, item in enumerate(daftar, start=1):
        print("%d. %s" % (nomor, item))


def cetak_berhasil(pesan, objek=None):
    print("[OK] %s" % pesan)
    if objek is not None:
        print("     %s" % objek)


class AplikasiPeminjaman:
    def __init__(self):
        self.file_manager = FileManager()
        self.logger = Logger(self.file_manager)
        self.manager = {}

    def _buat(self, kunci, *argumen):
        nama_modul, nama_class = LOKASI_MANAGER[kunci]
        try:
            kelas = getattr(importlib.import_module(nama_modul), nama_class)
        except (ImportError, AttributeError):
            kelas = None
        if kelas is None or any(a is None for a in argumen):
            print("[INFO] %s belum tersedia, menu terkait dinonaktifkan sementara." % nama_class)
            self.manager[kunci] = None
            return None
        try:
            self.manager[kunci] = kelas(*argumen)
        except TypeError as e:
            print("[PERINGATAN] %s tidak dapat dibuat (cek kontrak konstruktor): %s" % (nama_class, e))
            self.manager[kunci] = None
        return self.manager[kunci]

    @staticmethod
    def _panggil_jika_ada(objek, nama_method):
        method = getattr(objek, nama_method, None) if objek is not None else None
        if callable(method):
            method()

    def siapkan(self):
        try:
            self.file_manager.pastikan_semua_file()
            fm, lg = self.file_manager, self.logger
            alat = self._buat("alat", fm, lg)
            mahasiswa = self._buat("mahasiswa", fm, lg)
            transaksi = self._buat("transaksi", fm, lg, mahasiswa, alat)
            self._buat("pengembalian", fm, lg, transaksi, alat)

            for m in (mahasiswa, alat):
                if m is not None and transaksi is not None:
                    self._panggil_jika_ada_dengan(m, "sambungkan_transaksi", transaksi)

            for kunci in ("alat", "mahasiswa", "transaksi"):
                self._panggil_jika_ada(self.manager.get(kunci), "muat")
        except FileManagerError as e:
            print("[ERROR FILE] %s" % e)
            print("Program tidak dapat dimulai karena data gagal dimuat.")
            return False
        return True

    @staticmethod
    def _panggil_jika_ada_dengan(objek, nama_method, argumen):
        method = getattr(objek, nama_method, None)
        if callable(method):
            method(argumen)

    def _manager(self, kunci):
        m = self.manager.get(kunci)
        if m is None:
            raise ModulBelumTersedia(
                "%s belum diimplementasikan, fitur ini belum dapat dipakai."
                % LOKASI_MANAGER[kunci][1])
        return m

    def _jalankan_aksi(self, aksi):
        try:
            aksi()
        except ModulBelumTersedia as e:
            print("[BELUM TERSEDIA] %s" % e)
        except ValueError as e:
            print("[DITOLAK] %s" % e)
        except FileManagerError as e:
            print("[ERROR FILE] %s" % e)
        except Exception as e:
            print("[ERROR] Terjadi kesalahan tak terduga (%s): %s" % (type(e).__name__, e))

    def _loop_menu(self, judul, pilihan, label_nol):
        while True:
            cetak_judul(judul)
            for nomor, (label, _) in enumerate(pilihan, start=1):
                print("%2d. %s" % (nomor, label))
            print("%2d. %s" % (0, label_nol))
            masukan = input("Pilih menu: ").strip()
            if masukan == "0":
                return
            if masukan.isdigit() and 1 <= int(masukan) <= len(pilihan):
                self._jalankan_aksi(pilihan[int(masukan) - 1][1])
            else:
                print("Pilihan tidak valid.")

    def jalankan(self):
        cetak_judul("SISTEM PENGELOLAAN PEMINJAMAN PERALATAN LABORATORIUM")
        if not self.siapkan():
            return
        self.logger.catat("Program dijalankan")
        pilihan_utama = [
            ("Kelola data mahasiswa", self.menu_mahasiswa),
            ("Kelola data alat", self.menu_alat),
            ("Buat transaksi peminjaman", self.buat_transaksi),
            ("Tampilkan transaksi", self.tampilkan_transaksi),
            ("Proses pengembalian alat", self.proses_pengembalian),
            ("Cari transaksi berdasarkan mahasiswa", self.cari_transaksi_mahasiswa),
            ("Tampilkan alat yang tersedia", self.tampilkan_alat_tersedia),
            ("Tampilkan alat yang sedang dipinjam", self.tampilkan_alat_dipinjam),
            ("Tampilkan alat yang rusak", self.tampilkan_alat_rusak),
            ("Tampilkan riwayat peminjaman mahasiswa", self.tampilkan_riwayat),
            ("Lihat log aktivitas", self.lihat_log),
        ]
        try:
            self._loop_menu("MENU UTAMA", pilihan_utama, "Keluar")
        except (KeyboardInterrupt, EOFError):
            print()
        finally:
            self._keluar()

    def _keluar(self):
        print("\nMenyimpan data...")
        for kunci in ("alat", "mahasiswa", "transaksi"):
            try:
                self._panggil_jika_ada(self.manager.get(kunci), "simpan")
            except FileManagerError as e:
                print("[ERROR FILE] Data %s gagal disimpan: %s" % (kunci, e))
        self.logger.catat("Program ditutup")
        print("Data tersimpan. Sampai jumpa.")

    def menu_mahasiswa(self):
        self._loop_menu("KELOLA DATA MAHASISWA", [
            ("Tambah mahasiswa", self.tambah_mahasiswa),
            ("Edit mahasiswa", self.edit_mahasiswa),
            ("Hapus mahasiswa", self.hapus_mahasiswa),
            ("Cari mahasiswa (NIM / nama)", self.cari_mahasiswa),
            ("Tampilkan semua mahasiswa", self.tampilkan_mahasiswa),
        ], "Kembali")

    def tambah_mahasiswa(self):
        m = self._manager("mahasiswa")
        nim = baca_input("NIM    : ")
        nama = baca_input("Nama   : ")
        no_hp = baca_input("No. HP : ")
        cetak_berhasil("Mahasiswa berhasil ditambahkan.", m.tambah(nim, nama, no_hp))

    def edit_mahasiswa(self):
        m = self._manager("mahasiswa")
        nim = baca_input("NIM yang diedit : ")
        print("Kosongkan (Enter) bila tidak ingin mengubah.")
        nama = baca_input("Nama baru   : ", boleh_kosong=True)
        no_hp = baca_input("No. HP baru : ", boleh_kosong=True)
        if not nama and not no_hp:
            print("Tidak ada perubahan.")
            return
        cetak_berhasil("Data mahasiswa diperbarui.", m.edit(nim, nama=nama or None, no_hp=no_hp or None))

    def hapus_mahasiswa(self):
        m = self._manager("mahasiswa")
        nim = baca_input("NIM yang dihapus : ")
        if not konfirmasi("Yakin menghapus mahasiswa %s?" % nim):
            print("Dibatalkan.")
            return
        m.hapus(nim)
        cetak_berhasil("Mahasiswa %s dihapus." % nim)

    def cari_mahasiswa(self):
        m = self._manager("mahasiswa")
        kata = baca_input("Kata kunci (NIM / nama) : ")
        cetak_daftar("Hasil pencarian mahasiswa", m.cari(kata))

    def tampilkan_mahasiswa(self):
        cetak_daftar("Daftar mahasiswa", self._manager("mahasiswa").semua())

    def menu_alat(self):
        self._loop_menu("KELOLA DATA ALAT", [
            ("Tambah alat", self.tambah_alat),
            ("Edit alat", self.edit_alat),
            ("Hapus alat", self.hapus_alat),
            ("Cari alat (kode / nama / kategori)", self.cari_alat),
            ("Tampilkan semua alat", self.tampilkan_alat),
        ], "Kembali")

    def tambah_alat(self):
        m = self._manager("alat")
        kode = baca_input("Kode alat : ")
        nama = baca_input("Nama alat : ")
        daftar_kategori = getattr(m, "daftar_kategori", None)
        if callable(daftar_kategori) and daftar_kategori():
            print("Kategori yang sudah ada: %s" % ", ".join(daftar_kategori()))
            print("(ketik kategori baru bila belum ada)")
        kategori = baca_input("Kategori  : ")
        kondisi = baca_input("Kondisi (baik/rusak ringan/rusak berat) [%s] : " % KONDISI_BAIK,
                             boleh_kosong=True) or KONDISI_BAIK
        cetak_berhasil("Alat berhasil ditambahkan.", m.tambah(kode, nama, kategori, kondisi))

    def edit_alat(self):
        m = self._manager("alat")
        kode = baca_input("Kode alat yang diedit : ")
        print("Kosongkan (Enter) bila tidak ingin mengubah.")
        nama = baca_input("Nama baru     : ", boleh_kosong=True)
        kategori = baca_input("Kategori baru : ", boleh_kosong=True)
        kondisi = baca_input("Kondisi baru  : ", boleh_kosong=True)
        if not (nama or kategori or kondisi):
            print("Tidak ada perubahan.")
            return
        cetak_berhasil("Data alat diperbarui.",
                       m.edit(kode, nama=nama or None, kategori=kategori or None, kondisi=kondisi or None))

    def hapus_alat(self):
        m = self._manager("alat")
        kode = baca_input("Kode alat yang dihapus : ")
        if not konfirmasi("Yakin menghapus alat %s?" % kode):
            print("Dibatalkan.")
            return
        m.hapus(kode)
        cetak_berhasil("Alat %s dihapus." % kode)

    def cari_alat(self):
        m = self._manager("alat")
        kata = baca_input("Kata kunci (kode / sebagian nama / kategori) : ")
        cetak_daftar("Hasil pencarian alat", m.cari(kata))

    def tampilkan_alat(self):
        cetak_daftar("Daftar alat", self._manager("alat").semua())

    def tampilkan_alat_tersedia(self):
        cetak_daftar("Alat yang tersedia", self._manager("alat").tersedia())

    def tampilkan_alat_dipinjam(self):
        cetak_daftar("Alat yang sedang dipinjam", self._manager("alat").dipinjam())

    def tampilkan_alat_rusak(self):
        cetak_daftar("Alat yang rusak", self._manager("alat").rusak())

    def buat_transaksi(self):
        t = self._manager("transaksi")
        cetak_daftar("Alat yang tersedia", self._manager("alat").tersedia())
        nim = baca_input("NIM peminjam : ")
        daftar_kode = baca_daftar_kode("Kode alat (pisahkan dengan koma) : ")
        cetak_berhasil("Transaksi peminjaman berhasil dibuat.", t.buat(nim, daftar_kode))

    def tampilkan_transaksi(self):
        cetak_daftar("Daftar transaksi", self._manager("transaksi").semua())

    def cari_transaksi_mahasiswa(self):
        t = self._manager("transaksi")
        nim = baca_input("NIM mahasiswa : ")
        cetak_daftar("Transaksi milik %s" % nim, t.cari_berdasarkan_mahasiswa(nim))

    def tampilkan_riwayat(self):
        t = self._manager("transaksi")
        nim = baca_input("NIM mahasiswa : ")
        cetak_daftar("Riwayat peminjaman %s" % nim, t.riwayat_mahasiswa(nim))

    def proses_pengembalian(self):
        p = self._manager("pengembalian")
        id_transaksi = baca_input("ID transaksi : ")
        belum = p.daftar_belum_kembali(id_transaksi)
        cetak_daftar("Alat yang belum dikembalikan pada %s" % id_transaksi, belum)
        if not belum:
            return
        for kode in baca_daftar_kode("Kode alat yang dikembalikan (pisahkan dengan koma) : "):
            print("Kondisi alat %s:" % kode)
            kondisi = pilih_kondisi()
            try:
                hasil = p.kembalikan(id_transaksi, kode, kondisi)
                cetak_berhasil("Alat %s dikembalikan (%s)." % (kode, kondisi), hasil)
            except ValueError as e:
                print("[DITOLAK] %s: %s" % (kode, e))

    def lihat_log(self):
        cetak_daftar("Log aktivitas terbaru", self.logger.baca_terakhir(20))


def tampilkan_menu_utama():
    AplikasiPeminjaman().jalankan()
