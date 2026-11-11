**Proyek II Praktikum Pemrograman Dasar**
Sistem Pengelolaan Peminjaman Peralatan Laboratorium Berbasis Text File

- Penguji utama: Niken
- Tanggal pengujian: ........ November 2026
- Versi program (commit/branch): ........
- Lingkungan: Python ........, OS ........

> Hasil eksekusi berskrip untuk kesembilan skenario (layar dan isi file) ada di `docs/bukti_eksekusi_skenario.md`.
> Isian bertanda `........` di bagian 3 sampai 6 diisi QA saat pengujian manual, lengkap dengan tangkapan layar.

## 1. Persiapan Pengujian

- [ ] Salinan data sampel (5 mahasiswa, 10 alat, 3 transaksi) sudah disimpan di luar folder `data/`.
- [ ] Program dapat dijalankan dari `main.py`.
- [ ] Semua modul sudah di-merge ke `main` (feature freeze 10 November).
- [ ] Sebelum Skenario 8 dan 9, data kerja di `data/` dicadangkan agar bisa dipulihkan.

## 2. Ringkasan Hasil

| No | Skenario | Aturan terkait | Status QA manual (Lulus/Gagal) | Eksekusi `main.py` berskrip |
|----|----------|----------------|--------------------------------|-----------------------------|
| 1 | Tambah mahasiswa dan alat | Fitur 1, 2 | | Lulus |
| 2 | Pinjam beberapa alat dalam satu transaksi | Aturan 3 | | Lulus |
| 3 | Pinjam alat yang tidak tersedia | Aturan 1, 2, 7 | | Lulus |
| 4 | Pengembalian sebagian | Aturan 4 | | Lulus |
| 5 | Pengembalian alat rusak ringan/berat | Aturan 5 | | Lulus |
| 6 | Hapus mahasiswa dengan transaksi aktif | Aturan 6 | | Lulus |
| 7 | Tutup lalu jalankan ulang program | Aturan 7, 8 | | Lulus |
| 8 | File data dihapus/dikosongkan | Persyaratan file | | Lulus |
| 9 | Baris file berformat salah | Persyaratan file | | Lulus |

## 3. Detail Skenario

### Skenario 1: Tambah mahasiswa dan alat

**Tujuan:** Data baru tercatat di `mahasiswa.txt` dan `alat.txt`.

**Langkah:**
1. Jalankan program.
2. Pilih menu Kelola data mahasiswa, lalu tambah beberapa mahasiswa.
3. Pilih menu Kelola data alat, lalu tambah beberapa alat dari kategori berbeda (termasuk satu kategori baru).
4. Buka `data/mahasiswa.txt` dan `data/alat.txt`.

**Hasil yang diharapkan:** Setiap data baru muncul sebagai satu baris berpemisah `|`; NIM dan kode alat tidak ganda; alat baru berstatus `tersedia`.

**Data uji:** ........
**Hasil aktual:** ........
**Isi file setelah pengujian:**
```
(tempel cuplikan)
```
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

---

### Skenario 2: Peminjaman beberapa alat dalam satu transaksi

**Tujuan:** Satu transaksi dapat memuat banyak alat dan status alat berubah.

**Langkah:**
1. Catat status alat sebelum pinjam.
2. Buat transaksi untuk satu mahasiswa dengan minimal 3 alat.
3. Tampilkan transaksi di program.
4. Periksa `transaksi.txt`, `detail_transaksi.txt`, dan `alat.txt`.

**Hasil yang diharapkan:** ID transaksi dibuat otomatis (format T001, nomor terbesar + 1); batas kembali 7 hari dari tanggal pinjam; `detail_transaksi.txt` berisi satu baris per alat; status alat di program dan di file menjadi `dipinjam`.

**Data uji:** ........
**Hasil aktual:** ........
**Isi file setelah pengujian:**
```
(tempel cuplikan)
```
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

---

### Skenario 3: Meminjam alat yang tidak tersedia

**Tujuan:** Transaksi ditolak dan file tidak berubah.

**Langkah:**
1. Simpan salinan semua file data (atau catat hash/isi file).
2. Coba pinjam alat berstatus `dipinjam` atau `tidak tersedia`.
3. Bandingkan isi semua file sebelum dan sesudah.

**Hasil yang diharapkan:** Muncul pesan penolakan; tidak ada baris baru atau perubahan di file mana pun; program tetap berjalan.

**Data uji:** ........
**Hasil aktual:** ........
**Perbandingan file (sebelum/sesudah):** ........
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

**Tambahan (opsional):** mahasiswa yang sudah memiliki 2 transaksi aktif mencoba membuat transaksi ketiga (Aturan 2).

---

### Skenario 4: Pengembalian sebagian

**Tujuan:** Mengembalikan sebagian alat, transaksi tetap aktif.

**Langkah:**
1. Pilih transaksi yang berisi minimal 3 alat.
2. Proses pengembalian untuk 1 atau 2 alat dengan kondisi `baik`.
3. Tampilkan alat tersedia, alat sedang dipinjam, dan transaksi.
4. Periksa `detail_transaksi.txt`, `transaksi.txt`, `alat.txt`.

**Hasil yang diharapkan:**
- Alat yang dikembalikan berstatus `tersedia`; kondisi `baik`; tanggal kembali terisi.
- Alat yang belum dikembalikan tetap `dipinjam` dan muncul di daftar alat sedang dipinjam.
- Status transaksi menjadi `sebagian dikembalikan`.

**Data uji:** ........
**Hasil aktual:** ........
**Isi file setelah pengujian:**
```
(tempel cuplikan)
```
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

**Tambahan:** kembalikan semua alat tersisa, lalu pastikan status transaksi menjadi `selesai`.

---

### Skenario 5: Alat dikembalikan dalam kondisi rusak

**Tujuan:** Alat rusak tidak dihitung sebagai stok tersedia.

**Langkah:**
1. Kembalikan satu alat dengan kondisi `rusak ringan`.
2. Kembalikan alat lain dengan kondisi `rusak berat`.
3. Tampilkan alat tersedia dan alat rusak.
4. Periksa `alat.txt` dan `detail_transaksi.txt`.

**Hasil yang diharapkan:** Kedua alat berstatus `tidak tersedia`; kondisi tercatat sesuai input; tidak muncul di daftar alat tersedia; muncul di daftar alat rusak.

**Data uji:** ........
**Hasil aktual:** ........
**Isi file setelah pengujian:**
```
(tempel cuplikan)
```
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

---

### Skenario 6: Hapus mahasiswa dengan transaksi aktif

**Tujuan:** Penghapusan ditolak.

**Langkah:**
1. Pilih mahasiswa yang masih punya transaksi aktif.
2. Coba hapus melalui menu Kelola data mahasiswa.
3. Periksa `mahasiswa.txt`.

**Hasil yang diharapkan:** Muncul pesan penolakan; data mahasiswa tetap ada di program dan file.

**Data uji:** ........
**Hasil aktual:** ........
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

**Tambahan:** coba hapus alat yang masih tercatat di transaksi aktif; harus ditolak juga (Aturan 6).

---

### Skenario 7: Tutup lalu jalankan ulang program

**Tujuan:** Data permanen dan tidak ganda.

**Langkah:**
1. Pastikan ada transaksi berstatus `sebagian dikembalikan`.
2. Keluar lewat menu 0 (Keluar).
3. Jalankan program lagi; tampilkan mahasiswa, alat, dan transaksi.
4. Ulangi tutup-jalankan beberapa kali dan periksa jumlah baris di setiap file.

**Hasil yang diharapkan:** Semua data dan status sama seperti sebelum program ditutup; jumlah baris file tidak bertambah.

**Hasil aktual:** ........
**Jumlah baris per file (sebelum/sesudah):** ........
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

---

### Skenario 8: File data dihapus atau dikosongkan

**Tujuan:** Program tidak error dan membuat file baru otomatis.

**Langkah:**
1. Cadangkan folder `data/`.
2. Hapus salah satu file (misalnya `alat.txt`), lalu jalankan program.
3. Kosongkan file lain (isi 0 byte), lalu jalankan program.
4. Tambah satu data lewat menu dan periksa file.
5. Pulihkan data dari cadangan.

**Hasil yang diharapkan:** Tidak muncul error/traceback; file dibuat otomatis; program dapat dipakai seperti biasa.

**Hasil aktual:** ........
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

---

### Skenario 9: Baris berformat salah

**Tujuan:** Baris rusak dilewati disertai peringatan.

**Langkah:**
1. Cadangkan folder `data/`.
2. Tambahkan secara manual satu baris dengan kolom kurang ke salah satu file data (misalnya `alat.txt`).
3. Jalankan program.
4. Gunakan fitur lain seperti biasa dan simpan perubahan.
5. Periksa isi file setelah program ditutup.
6. Pulihkan data dari cadangan.

**Hasil yang diharapkan:** Muncul peringatan untuk baris tersebut; baris dilewati; program tetap berjalan normal.

**Baris yang ditambahkan:** ........
**Hasil aktual:** ........
**Catatan:** apakah baris rusak tetap ada atau hilang dari file setelah program menyimpan? Pada eksekusi berskrip: hilang. Baris rusak dilewati saat dimuat dan tidak ikut tersimpan ketika program menulis ulang file (lihat `docs/bukti_eksekusi_skenario.md`, Skenario 9). Konfirmasi QA secara manual: ........
**Bukti (screenshot):** ........
**Status:** Lulus / Gagal

## 4. Daftar Bug yang Ditemukan

| No | Skenario | Deskripsi bug | Penanggung jawab modul | Status perbaikan | Commit perbaikan |
|----|----------|---------------|------------------------|------------------|------------------|
| 1 | analisis kode; terkait Skenario 6 | Alat atau mahasiswa yang hanya ada di transaksi selesai dapat dihapus; saat data dimuat ulang transaksinya ikut dibuang karena rujukannya putus (Aturan 8) | `manager_alat`, `manager_mahasiswa` (Fatimah) | Diperbaiki: penghapusan ditolak bila tercatat di riwayat transaksi | `66f7247` |
| 2 | analisis kode; terkait Skenario 5 | Bila penulisan `transaksi.txt` gagal saat pengembalian, kondisi alat di `alat.txt` tetap berubah (Aturan 7) | `manager_pengembalian` (Niken) | Diperbaiki: kondisi alat dipulihkan | `66f7247` |
| 3 | analisis kode; terkait Skenario 2 dan 5 | `status_aktif` mahasiswa tidak pernah berubah sehingga tidak mencerminkan peminjaman aktif | `manager_mahasiswa`, `manager_transaksi` (Fatimah, Faris) | Diperbaiki: diatur otomatis dari transaksi aktif dan dipulihkan bila penyimpanan gagal | `66f7247` |
| 4 | analisis kode; terkait Skenario 7 dan 9 | Kondisi dan status alat di file yang bertentangan (misalnya `rusak berat` dengan `tersedia`) dimuat apa adanya sehingga alat rusak dapat dipinjam (Aturan 5) | `manager_transaksi` (Faris) | Diperbaiki: disinkronkan saat dimuat, dengan peringatan | `66f7247` |
| 5 | analisis kode; terkait Skenario 9 | `batas_kembali` di file tidak dibatasi 7 hari | `models/transaksi` (Faris) | Diperbaiki: baris di luar 0 sampai 7 hari dilewati dengan peringatan | `66f7247` |
| 6 | analisis kode; terkait Skenario 5 | Keterlambatan pengembalian tidak dideteksi, padahal soal menyebutnya sebagai masalah utama | `manager_pengembalian` (Niken) | Ditambahkan: `hari_terlambat`, peringatan di layar, dan catatan di log | `66f7247` |
| 7 | analisis kode; berlaku untuk semua skenario | `menu.py` tidak tercakup tes, dan Ctrl+Z atau Ctrl+D di tengah isian tampil sebagai `[ERROR]` | `menu` (Arif) | Diperbaiki, ditambah `tests/test_menu.py` | `66f7247` |

## 5. Pengujian Silang (Setiap Anggota Menguji Modul Anggota Lain)

| Penguji | Modul yang diuji | Temuan |
|---------|------------------|--------|
| Arif | | |
| Fatimah | | |
| Faris | | |
| Niken | | |

## 6. Kesimpulan

- Jumlah skenario lulus: 9 dari 9 pada eksekusi `main.py` berskrip (`docs/bukti_eksekusi_skenario.md`); pengujian manual QA: ... dari 9
- Jumlah skenario gagal: 0 pada eksekusi berskrip; pengujian manual QA: ...
- Catatan umum: penghapusan alat atau mahasiswa yang tercatat di riwayat transaksi sengaja ditolak (lebih ketat dari Aturan 6, mengikuti Aturan 8), dan baris rusak atau rujukan yang hilang dibuang dari file saat program menyimpan. QA: ........

---

## 7. Hasil Pengujian Otomatis (Unit & Integration Tests)

Seluruh pengujian otomatis dijalankan dengan `python -m unittest -v` dari folder proyek. Setiap tes memakai
folder sementara sehingga folder `data/` tidak berubah.

### 7.1 Skenario wajib

| No | Skenario | Tes otomatis (`tests/test_integrasi.py`) | Hasil yang diharapkan |
|---|---|---|---|
| 1 | Tambah mahasiswa dan alat | `test_skenario_1_data_tercatat_di_file` | Data muncul di `mahasiswa.txt` dan `alat.txt` |
| 2 | Pinjam beberapa alat dalam satu transaksi | `test_skenario_2_status_alat_berubah_di_program_dan_file` | Status alat `dipinjam` di memori dan file |
| 3 | Pinjam alat yang tidak tersedia | `test_skenario_3_alat_tidak_tersedia_ditolak_file_tidak_berubah` | Ditolak, isi semua file tetap |
| 4 | Pengembalian sebagian | `test_skenario_4_pengembalian_sebagian` | Transaksi `sebagian dikembalikan`, alat lain tetap `dipinjam` |
| 5 | Kembali dalam kondisi rusak | `test_skenario_5_alat_rusak_tidak_kembali_tersedia` | Status `tidak tersedia` |
| 6 | Hapus mahasiswa/alat bertransaksi aktif | `test_skenario_6_hapus_mahasiswa_dan_alat_aktif_ditolak` | Ditolak, file tetap |
| 7 | Tutup dan jalankan ulang | `test_skenario_7_*` | Data dan status sama, tanpa duplikasi |
| 8 | File dihapus atau dikosongkan | `test_skenario_8_file_dihapus_atau_dikosongkan_tidak_error` | File dibuat ulang tanpa error |
| 9 | Baris berformat salah | `test_skenario_9_baris_salah_format_dilewati_dan_program_tetap_dapat_dipakai` | Baris dilewati dengan `[PERINGATAN]` |

### 7.2 Pengujian tambahan (hasil analisis kode)

| Masalah yang ditemukan | Tes (`UjiPerbaikanAnalisis`) |
|---|---|
| Penghapusan alat/mahasiswa merusak riwayat transaksi setelah dimuat ulang | `test_alat_dan_mahasiswa_dengan_riwayat_tidak_boleh_dihapus`, `test_alat_sudah_kembali_pada_transaksi_aktif_tidak_boleh_dihapus` |
| Kondisi alat tidak pulih saat penulisan file transaksi gagal | `test_gagal_simpan_pengembalian_memulihkan_kondisi_alat` |
| Status aktif peminjaman mahasiswa tidak pernah diperbarui | `test_status_aktif_mahasiswa_mengikuti_transaksi_aktif`, `test_status_aktif_mahasiswa_bertahan_setelah_dijalankan_ulang` |
| Status mahasiswa di file salah; mahasiswa `tidak aktif` tidak boleh terblokir saat meminjam | `test_status_aktif_yang_salah_di_file_diperbaiki_dan_tidak_memblokir_peminjaman` |
| Status mahasiswa tidak pulih saat penyimpanan gagal | `test_gagal_menyimpan_transaksi_memulihkan_status_aktif_mahasiswa`, `test_gagal_menyimpan_pengembalian_memulihkan_status_aktif_mahasiswa` |
| Kondisi dan status alat dari file bertentangan | `test_status_alat_tidak_konsisten_dengan_kondisi_diperbaiki` |
| Keterlambatan tidak tercatat | `test_keterlambatan_dihitung_dan_dicatat_di_log` |
| No. HP tidak dapat dikosongkan lewat edit (Enter berarti tidak diubah, `-` mengosongkan) | `test_edit_mahasiswa_dapat_mengosongkan_no_hp` |
| `batas_kembali` dari file tidak dibatasi 7 hari | `test_batas_kembali_harus_dalam_rentang_tujuh_hari` |

### 7.3 Pengujian menu (`tests/test_menu.py`)

Menu diuji dengan input berskrip (`input()` diganti urutan jawaban) pada folder sementara, sehingga seluruh
alur yang dilihat pengguna (pesan `[OK]`, `[DITOLAK]`, `[PERINGATAN]`, tampilan daftar) ikut diperiksa.

| Tes | Yang diperiksa |
|---|---|
| `test_alur_lengkap_dari_data_sampai_pengembalian` | tambah mahasiswa/alat, pinjam, kembali sebagian, tampil daftar, isi semua file, log |
| `test_penolakan_aturan_bisnis_tampil_di_layar_dan_file_tidak_berubah` | 4 penolakan tampil sebagai `[DITOLAK]`, konfirmasi `n` membatalkan, file tetap |
| `test_edit_mahasiswa_mengosongkan_hp_dan_status_mengikuti_peminjaman` | edit no. HP dengan `-`, mahasiswa `tidak aktif` tetap dapat meminjam, status menjadi `aktif` di file |
| `test_input_berhenti_di_tengah_isian_tetap_menyimpan_dan_keluar` | `EOFError` (Ctrl+Z/Ctrl+D) tidak menampilkan `[ERROR]` dan data tetap disimpan |
| `test_data_tetap_ada_setelah_program_dijalankan_ulang` | skenario 7 lewat menu, status mahasiswa di file, tanpa peringatan dan file tidak berubah |
| `test_pengembalian_terlambat_menampilkan_peringatan_dan_log` | peringatan terlambat di layar dan `TERLAMBAT` di log |
| `UjiSiapkan` | file dibuat otomatis, manager tersambung, baris rusak dilewati, kegagalan file menghentikan program |

### 7.4 Verifikasi menjalankan `python main.py`

Selain tes unit, program dijalankan langsung (`python main.py` dengan input dari stdin) pada salinan sementara
proyek, sehingga `data/` asli tidak berubah. Hasil yang diamati:

| Kasus | Hasil |
|---|---|
| Tanpa folder `data/` | kelima file `.txt` dibuat otomatis; kode keluar 0; tanpa pesan error |
| Dijalankan ulang setelah menambah mahasiswa, alat, dan transaksi | transaksi dan alat yang dipinjam tampil kembali; isi file sama |
| Memuat `data/` bawaan repository (salinan sementara), lalu keluar normal | 0 peringatan; keempat file data tidak berubah sesudah program berjalan dan keluar |
| Memuat `data_sampel/` | 0 peringatan; M001 dan M003 `aktif`, M002, M004, M005 `tidak aktif` |
| Skenario 9: satu baris berkolom 2 ditambahkan ke `mahasiswa.txt` | 1 `[PERINGATAN]` berisi nomor baris; program tetap berjalan |
| Skenario 8: `alat.txt` dihapus | program berjalan, file dibuat ulang, kode keluar 0 |
| M002 (`tidak aktif`) meminjam A006 dari data sampel, lalu mengembalikannya | `[OK]`; M002 menjadi `aktif` di file, lalu kembali `tidak aktif`; transaksi T004 `selesai` |

Cakupan lengkap kesembilan skenario wajib (layar dan isi file) ada di `docs/bukti_eksekusi_skenario.md` dan dapat
diulang dengan `python tests/skenario_wajib.py`. Alur serupa juga dicakup `tests/test_menu.py` dan `tests/test_integrasi.py`.

### 7.5 Kompatibilitas Python

Pengujian dijalankan di Python 3.14.6. Sintaks seluruh 23 file `.py` diperiksa dengan
`ast.parse(..., feature_version=(3, 8))` dan lolos. Pencarian tidak menemukan fungsi pustaka standar yang baru
ada di Python 3.9 ke atas, tetapi program belum dijalankan langsung di Python 3.8.

### 7.6 Hasil

Terakhir dijalankan: 105 tes, semua lulus (`OK`).

Yang belum ada: pengujian eksploratif manual oleh tim QA dan hasil cross-group code review. Keduanya perlu
dilengkapi tim setelah review dilakukan.
