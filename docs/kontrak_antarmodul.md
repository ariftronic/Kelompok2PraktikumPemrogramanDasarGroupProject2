# Kontrak Antarmodul

Daftar method yang dipanggil `app/menu.py` dan cara modul saling terhubung. Bila kontrak berubah, ubah dokumen ini dan
`menu.py` bersamaan.

## 1. Aturan umum

- Semua baca/tulis file hanya lewat `FileManager` (`app/file_manager.py`). Manager tidak memanggil `open()` sendiri.
- Setiap manager yang menyimpan data memiliki `muat()` (baca file ke memori) dan `simpan()` (tulis seluruh data ke file).
  Penyimpanan dilakukan segera setelah operasi berhasil.
- Bila satu operasi mengubah beberapa file, simpan semuanya dengan satu panggilan `file_manager.tulis_banyak([...])`, berisi
  pasangan `(nama_file, daftar_baris)`. Bila gagal, tidak ada file yang berubah.
- Pelanggaran aturan bisnis dan input tidak valid dilempar sebagai `ValueError("pesan yang jelas")`. Menu menampilkannya sebagai
  `[DITOLAK] pesan`. Semua aturan diperiksa sebelum data di memori diubah (Aturan 7).
- Bila penyimpanan gagal (`FileManagerError`), manager memuat ulang data dari file agar memori kembali sama dengan file, lalu
  melempar ulang error tersebut.
- Setiap model memiliki `dari_baris(kolom)` (classmethod, menerima list string hasil `baca_baris`), `ke_baris()` (list kolom
  sesuai urutan di `konstanta.KOLOM_FILE`), dan `__str__` yang rapi karena menu mencetak objek dengan `str()`. Nilai `-` berarti kosong.
- Gunakan konstanta dari `konstanta.py` untuk nama file, status, kondisi, pemisah, dan batas aturan.
- Saat `muat()`, baris yang tidak valid, berkunci ganda, atau merujuk data yang tidak ada dikirim ke
  `file_manager.karantina(nama_file, baris, alasan)`. Method itu menyalin baris ke `data/karantina/<nama_file>` dan mencetak `[PERINGATAN]`.
- Status alat dan status aktif mahasiswa adalah data turunan dari transaksi dan pemeliharaan. `ManagerTransaksi.muat()` dan
  `ManagerPemeliharaan.muat()` mengoreksinya hanya ke arah aman: alat tidak pernah dijadikan `tersedia` secara otomatis.
- Setiap operasi yang berhasil memanggil `logger.catat(pesan)`, misalnya `Mahasiswa M001 ditambahkan`,
  `Transaksi T001 dibuat oleh M001 (A001, A002)`, atau `Alat A009 masuk pemeliharaan (P003)`.

## 2. Pembuatan dan penyambungan (dilakukan `AplikasiPeminjaman.siapkan()`)

```python
alat         = ManagerAlat(file_manager, logger)
mahasiswa    = ManagerMahasiswa(file_manager, logger)
transaksi    = ManagerTransaksi(file_manager, logger, mahasiswa, alat)
pengembalian = ManagerPengembalian(file_manager, logger, transaksi, alat)
pemeliharaan = ManagerPemeliharaan(file_manager, logger, alat, transaksi)
statistik    = ManagerStatistik(transaksi, alat, mahasiswa)
laporan      = ManagerLaporan(file_manager_laporan, alat, mahasiswa, transaksi, pemeliharaan)

alat.sambungkan_transaksi(transaksi)        # Aturan 6
alat.sambungkan_pemeliharaan(pemeliharaan)  # alat yang diperbaiki tidak boleh diubah kondisinya atau dihapus
mahasiswa.sambungkan_transaksi(transaksi)   # Aturan 6
# urutan muat: alat -> mahasiswa -> transaksi -> pemeliharaan
# bila ada peringatan saat memuat, semua file langsung ditulis ulang agar sama dengan memori
```

## 3. Method yang dipanggil antarmodul

### FileManager

| Method | Keterangan |
|---|---|
| `baca_baris(nama_file)` | list kolom per baris; baris yang jumlah kolomnya salah atau berisi kolom kosong dikarantina |
| `tulis_baris(nama_file, daftar_baris)` | menulis ulang satu file |
| `tulis_banyak(daftar_isi)` | menulis ulang beberapa file sekaligus; semua atau tidak sama sekali |
| `tulis_teks(nama_file, daftar_baris)` | menulis teks bebas (laporan) apa adanya; mengembalikan path |
| `tambah_baris(nama_file, teks)` | menambah satu baris di akhir file (mode append, dipakai `Logger`) |
| `karantina(nama_file, baris, alasan)` | menyalin baris yang dilewati ke `data/karantina/` dan mencatat peringatan |
| `baca_karantina(nama_file)` | isi karantina; list kosong bila belum ada |

### ManagerDasar (dasar ManagerMahasiswa dan ManagerAlat)

| Method | Keterangan |
|---|---|
| `muat()`, `simpan()` | membaca dan menulis file milik manager |
| `isi_file()` | `(nama_file, daftar_baris)` untuk disimpan bersama file lain |
| `semua()` | list objek, urut menurut kunci |

### ManagerMahasiswa (Fatimah)

| Method | Keterangan |
|---|---|
| `tambah(nim, nama, no_hp)` | mengembalikan `Mahasiswa`; NIM ganda ditolak |
| `edit(nim, nama=None, no_hp=None)` | `None` berarti tidak diubah; `no_hp='-'` mengosongkan nomor; `status_aktif` tidak dapat diedit |
| `hapus(nim)` | ditolak bila punya transaksi aktif (Aturan 6) atau tercatat di riwayat transaksi (Aturan 8) |
| `ambil(nim)` | objek `Mahasiswa`; `ValueError` bila tidak ada |
| `cari_berdasarkan_nim(nim)` | objek `Mahasiswa` atau `None` |
| `cari(kata_kunci)` | list `Mahasiswa` yang cocok dengan NIM atau nama |

### ManagerAlat (Fatimah)

| Method | Keterangan |
|---|---|
| `tambah(kode, nama, kategori, kondisi="baik")` | kategori baru langsung diterima; kode ganda ditolak |
| `edit(kode, nama=None, kategori=None, kondisi=None)` | status menyesuaikan kondisi; kondisi alat yang sedang diperbaiki tidak dapat diubah |
| `hapus(kode)` | ditolak bila dipinjam, tercatat di riwayat transaksi, atau tercatat di pemeliharaan |
| `cari(kata_kunci, berdasarkan="semua")` | Tantangan A; `berdasarkan` salah satu dari `semua`, `kode`, `nama`, `kategori` |
| `ambil(kode)`, `cari_berdasarkan_kode(kode)` | objek `Alat` (`ambil` menolak bila tidak ada) |
| `tersedia()`, `dipinjam()`, `rusak()`, `daftar_kategori()` | list untuk menu |

### ManagerTransaksi (Faris)

| Method | Keterangan |
|---|---|
| `buat(nim, daftar_kode_alat)` | Aturan 1, 2, 3; batas kembali 7 hari; mengubah status alat dan status aktif mahasiswa; menyimpan transaksi, detail, alat, dan mahasiswa sekaligus |
| `ambil(id_transaksi)`, `semua()` | transaksi, urut menurut nomor ID |
| `cari_berdasarkan_mahasiswa(nim)` | transaksi aktif milik mahasiswa |
| `riwayat_mahasiswa(nim)` | semua transaksi milik mahasiswa |
| `transaksi_aktif_untuk_alat(kode)` | transaksi aktif yang masih memegang alat, atau `None` |
| `punya_transaksi_aktif(nim)`, `alat_dalam_transaksi_aktif(kode)` | untuk Aturan 6 |
| `mahasiswa_punya_riwayat(nim)`, `alat_punya_riwayat(kode)` | untuk menjaga Aturan 8 saat menghapus |
| `perbarui_status_mahasiswa(nim)` | `status_aktif` mengikuti transaksi aktif; `True` bila berubah |
| `simpan_semua(simpan_mahasiswa=False)` | menyimpan transaksi, detail, alat, dan mahasiswa dalam satu `tulis_banyak` |
| `daftar_isi_file()` | isi `transaksi.txt` dan `detail_transaksi.txt` untuk disimpan bersama file lain |

### ManagerPengembalian (Niken)

| Method | Keterangan |
|---|---|
| `daftar_belum_kembali(id_transaksi)` | detail alat yang masih dipinjam |
| `kembalikan(id_transaksi, kode_alat, kondisi)` | satu alat per panggilan; Aturan 4 dan 5; keterlambatan dicatat di log |
| `hari_terlambat(transaksi, tanggal=None)` | jumlah hari melewati batas kembali (0 bila tepat waktu) |

### ManagerPemeliharaan (Niken, Tantangan C)

| Method | Keterangan |
|---|---|
| `mulai(kode)` | memasukkan alat rusak ringan atau rusak berat ke pemeliharaan; alat yang dipinjam, berkondisi baik, atau sudah diperbaiki ditolak |
| `selesai(kode)` | menutup pemeliharaan; alat menjadi `baik` dan `tersedia` |
| `aktif()`, `semua()`, `aktif_untuk(kode)` | daftar pemeliharaan |
| `sedang_diperbaiki(kode)`, `alat_punya_riwayat(kode)` | dipakai `ManagerAlat` |

### ManagerStatistik (Faris, Tantangan B)

| Method | Keterangan |
|---|---|
| `alat_terpopuler(jumlah=5)` | list `(Alat, berapa kali dipinjam)` |
| `mahasiswa_teraktif(jumlah=5)` | list `(Mahasiswa, jumlah transaksi)` |
| `jumlah_transaksi_aktif()`, `jumlah_transaksi_selesai()` | angka untuk menu statistik |

### ManagerLaporan (Niken, Tantangan F)

| Method | Keterangan |
|---|---|
| `laporan_alat_dipinjam()` | laporan alat yang sedang dipinjam beserta peminjam dan keterlambatan; mengembalikan path file |
| `laporan_alat_rusak()` | laporan alat rusak beserta status pemeliharaan |
| `laporan_riwayat_mahasiswa(nim)` | laporan riwayat seorang mahasiswa; NIM yang tidak ada ditolak |

## 4. Fitur yang ditangani menu sendiri

Tampilan menu, pembacaan input (menolak karakter `|`), konfirmasi hapus, pemisahan kode alat berkoma, pemilihan kondisi dan
kriteria pencarian, paginasi daftar (20 baris per halaman), penyimpanan akhir saat keluar, dan tampilan log (`Logger.baca_terakhir`).
