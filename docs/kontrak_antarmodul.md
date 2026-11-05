# Kontrak Antarmodul (usulan untuk diskusi 7 November)

Dokumen ini mendefinisikan method yang dipanggil `app/menu.py` dan cara modul saling terhubung, supaya Rara,
Faris, dan Niken dapat bekerja paralel. Bila disepakati lain saat diskusi, ubah dokumen ini dan `menu.py` bersamaan.

## 1. Aturan umum

- Semua baca/tulis file hanya lewat `FileManager` (`app/file_manager.py`). Manager tidak memanggil `open()` sendiri.
- Setiap manager memiliki `muat()` (baca file ke memori) dan `simpan()` (tulis seluruh data ke file).
  `simpan()` dipanggil segera setelah setiap operasi berhasil.
- Pelanggaran aturan bisnis dan input tidak valid dilempar sebagai `ValueError("pesan yang jelas")`.
  Menu menampilkannya sebagai `[DITOLAK] pesan`. Periksa semua aturan SEBELUM mengubah data atau file (Aturan 7).
- Bila `simpan()` gagal (`FileManagerError`), panggil `muat()` lagi agar memori kembali sama dengan file, lalu lempar ulang.
- Setiap model memiliki `__str__` yang rapi (satu baris, atau beberapa baris untuk transaksi) karena menu mencetak hasil dengan `str()`.
- Setiap model memiliki `dari_baris(kolom)` (classmethod, menerima list string hasil `baca_baris`) dan `ke_baris()`
  (mengembalikan list kolom sesuai urutan di `konstanta.KOLOM_FILE`). Nilai `-` berarti kosong.
- Gunakan konstanta dari `konstanta.py` untuk status, kondisi, pemisah, dan aturan bisnis. Jangan menulis string literalnya.
- Saat `muat()`: lewati dan peringatkan data ganda (NIM, kode alat, ID transaksi) serta rujukan yang tidak ada
  (NIM/kode alat pada transaksi) memakai `file_manager.catat_peringatan(nama_file, pesan)` (Aturan 8).
- Hasil log: setiap operasi berhasil memanggil `logger.catat(pesan)`. Pesan yang disarankan:
  `Mahasiswa M001 ditambahkan`, `Alat A001 ditambahkan`, `Transaksi T001 dibuat`,
  `Alat A001 dikembalikan dalam kondisi baik`, `Mahasiswa M001 dihapus`.

## 2. Pembuatan dan penyambungan (dilakukan `menu.py`)

```python
alat         = ManagerAlat(file_manager, logger)
mahasiswa    = ManagerMahasiswa(file_manager, logger)
transaksi    = ManagerTransaksi(file_manager, logger, mahasiswa, alat)
pengembalian = ManagerPengembalian(file_manager, logger, transaksi, alat)

alat.sambungkan_transaksi(transaksi)       # untuk Aturan 6
mahasiswa.sambungkan_transaksi(transaksi)  # untuk Aturan 6
# urutan muat: alat.muat() -> mahasiswa.muat() -> transaksi.muat()
```

## 3. Method yang dipanggil menu

### ManagerMahasiswa (Rara)

| Method | Keterangan |
|---|---|
| `tambah(nim, nama, no_hp)` | mengembalikan objek `Mahasiswa`; tolak NIM ganda |
| `edit(nim, nama=None, no_hp=None)` | `None` berarti tidak diubah; mengembalikan objek |
| `hapus(nim)` | tolak bila `transaksi.punya_transaksi_aktif(nim)` (Aturan 6) |
| `cari(kata_kunci)` | list `Mahasiswa` (NIM atau nama) |
| `semua()` | list `Mahasiswa` |
| `sambungkan_transaksi(manager_transaksi)` | menyimpan referensi |

### ManagerAlat (Rara)

| Method | Keterangan |
|---|---|
| `tambah(kode, nama, kategori, kondisi="baik")` | kategori baru otomatis diterima (tanpa mengubah struktur utama); tolak kode ganda |
| `edit(kode, nama=None, kategori=None, kondisi=None)` | mengembalikan objek |
| `hapus(kode)` | tolak bila `transaksi.alat_dalam_transaksi_aktif(kode)` (Aturan 6) |
| `cari(kata_kunci)` | Tantangan A: cocok dengan kode, sebagian nama, atau kategori |
| `semua()`, `tersedia()`, `dipinjam()`, `rusak()` | list `Alat` |
| `daftar_kategori()` | list nama kategori yang sudah ada (opsional, dipakai menu bila ada) |
| `sambungkan_transaksi(manager_transaksi)` | menyimpan referensi |

### ManagerTransaksi (Faris)

| Method | Keterangan |
|---|---|
| `buat(nim, daftar_kode_alat)` | mengembalikan `Transaksi`; terapkan Aturan 1, 2, 3 dan batas 7 hari; ubah status alat menjadi `dipinjam`; simpan alat dan transaksi |
| `semua()` | list `Transaksi` |
| `cari_berdasarkan_mahasiswa(nim)` | list `Transaksi` (disarankan yang masih aktif) |
| `riwayat_mahasiswa(nim)` | list `Transaksi` termasuk yang sudah selesai |
| `punya_transaksi_aktif(nim)` | bool, untuk Aturan 6 |
| `alat_dalam_transaksi_aktif(kode)` | bool, untuk Aturan 6 |
| `muat()`, `simpan()` | menangani `transaksi.txt` dan `detail_transaksi.txt` |

### ManagerPengembalian (Niken)

| Method | Keterangan |
|---|---|
| `daftar_belum_kembali(id_transaksi)` | list alat/detail yang masih `dipinjam` pada transaksi tersebut |
| `kembalikan(id_transaksi, kode_alat, kondisi)` | satu alat per panggilan; kondisi salah satu `DAFTAR_KONDISI`; atur stok (Aturan 5), status transaksi (Aturan 4), simpan; mengembalikan `Transaksi` |

## 4. Fitur yang ditangani menu sendiri

Tampilan menu, pembacaan input (menolak karakter `|`), konfirmasi hapus, pemisahan input kode alat berkoma,
penyimpanan akhir saat keluar, dan tampilan log (`Logger.baca_terakhir`).
