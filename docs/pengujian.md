**Proyek II Praktikum Pemrograman Dasar**
Sistem Pengelolaan Peminjaman Peralatan Laboratorium Berbasis Text File

- Penguji utama: Fatimah Az Zahra
- Tanggal pengujian: 12 November 2026
- Versi program (commit/branch): `66f7247` (branch `main`)
- Lingkungan: Python 3.14.6, OS Windows

> Hasil eksekusi berskrip untuk kesembilan skenario (layar dan isi file) ada di `docs/bukti_eksekusi_skenario.md`.
> Data uji, hasil aktual, dan isi file pada bagian 3 diambil dari hasil eksekusi `main.py` tersebut (eksekusi 2026-11-11), sehingga tanggal pinjam pada contoh adalah 2026-11-11.

## 1. Persiapan Pengujian

- [V] Salinan data sampel (5 mahasiswa, 10 alat, 3 transaksi) sudah disimpan di luar folder `data/`.
- [V] Program dapat dijalankan dari `main.py`.
- [V] Semua modul sudah di-merge ke `main` (feature freeze 10 November).
- [V] Sebelum Skenario 8 dan 9, data kerja di `data/` dicadangkan agar bisa dipulihkan.

## 2. Ringkasan Hasil

| No | Skenario | Aturan terkait | Status QA manual (Lulus/Gagal) | Eksekusi `main.py` berskrip |
|----|----------|----------------|--------------------------------|-----------------------------|
| 1 | Tambah mahasiswa dan alat | Fitur 1, 2 | Lulus | Lulus |
| 2 | Pinjam beberapa alat dalam satu transaksi | Aturan 3 | Lulus | Lulus |
| 3 | Pinjam alat yang tidak tersedia | Aturan 1, 2, 7 | Lulus | Lulus |
| 4 | Pengembalian sebagian | Aturan 4 | Lulus | Lulus |
| 5 | Pengembalian alat rusak ringan/berat | Aturan 5 | Lulus | Lulus |
| 6 | Hapus mahasiswa dengan transaksi aktif | Aturan 6 | Lulus | Lulus |
| 7 | Tutup lalu jalankan ulang program | Aturan 7, 8 | Lulus | Lulus |
| 8 | File data dihapus/dikosongkan | Persyaratan file | Lulus | Lulus |
| 9 | Baris file berformat salah | Persyaratan file | Lulus | Lulus |

## 3. Detail Skenario

### Skenario 1: Tambah mahasiswa dan alat

**Tujuan:** Data baru tercatat di `mahasiswa.txt` dan `alat.txt`.

**Langkah:**
1. Jalankan program.
2. Pilih menu Kelola data mahasiswa, lalu tambah beberapa mahasiswa.
3. Pilih menu Kelola data alat, lalu tambah beberapa alat dari kategori berbeda (termasuk satu kategori baru).
4. Buka `data/mahasiswa.txt` dan `data/alat.txt`.

**Hasil yang diharapkan:** Setiap data baru muncul sebagai satu baris berpemisah `|`; NIM dan kode alat tidak ganda; alat baru berstatus `tersedia`.

**Data uji:** mahasiswa M001 Andi Pratama (081234567890), M002 Budi Santoso (085612345678), M003 Citra Lestari (tanpa no. HP); alat A001 Kamera Digital, A002 Tripod, A004 Laptop (kategori baru `perangkat komputasi`), A005 Kabel HDMI, dan A003 Kabel LAN.
**Hasil aktual:** 3 mahasiswa dan 5 alat tercatat; pesan `[OK]` muncul 8 kali; kategori baru `perangkat komputasi` diterima tanpa mengubah kode; tidak ada NIM atau kode alat ganda; program berakhir normal.
**Isi file setelah pengujian:**
```
# mahasiswa.txt
M001|Andi Pratama|081234567890|tidak aktif
M002|Budi Santoso|085612345678|tidak aktif
M003|Citra Lestari|-|tidak aktif

# alat.txt
A001|Kamera Digital|perangkat multimedia|baik|tersedia
A002|Tripod|perangkat multimedia|baik|tersedia
A003|Kabel LAN|perangkat jaringan|baik|tersedia
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia
```
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 1
**Status:** Lulus

---

### Skenario 2: Peminjaman beberapa alat dalam satu transaksi

**Tujuan:** Satu transaksi dapat memuat banyak alat dan status alat berubah.

**Langkah:**
1. Catat status alat sebelum pinjam.
2. Buat transaksi untuk satu mahasiswa dengan minimal 3 alat.
3. Tampilkan transaksi di program.
4. Periksa `transaksi.txt`, `detail_transaksi.txt`, dan `alat.txt`.

**Hasil yang diharapkan:** ID transaksi dibuat otomatis (format T001, nomor terbesar + 1); batas kembali 7 hari dari tanggal pinjam; `detail_transaksi.txt` berisi satu baris per alat; status alat di program dan di file menjadi `dipinjam`.

**Data uji:** mahasiswa M001 meminjam tiga alat: `A001, A002, A003`.
**Hasil aktual:** transaksi T001 dibuat dengan batas kembali tepat 7 hari (2026-11-11 sampai 2026-11-18); `detail_transaksi.txt` berisi 3 baris berstatus `dipinjam`; A001, A002, A003 menjadi `dipinjam` di layar dan file, A004 dan A005 tetap `tersedia`; layar menampilkan `Alat yang sedang dipinjam (3 data)`; status aktif M001 menjadi `aktif`.
**Isi file setelah pengujian:**
```
# transaksi.txt
T001|M001|2026-11-11|2026-11-18|dipinjam

# detail_transaksi.txt
T001|A001|dipinjam|-|-
T001|A002|dipinjam|-|-
T001|A003|dipinjam|-|-

# alat.txt
A001|Kamera Digital|perangkat multimedia|baik|dipinjam
A002|Tripod|perangkat multimedia|baik|dipinjam
A003|Kabel LAN|perangkat jaringan|baik|dipinjam
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia
```
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 2
**Status:** Lulus

---

### Skenario 3: Meminjam alat yang tidak tersedia

**Tujuan:** Transaksi ditolak dan file tidak berubah.

**Langkah:**
1. Simpan salinan semua file data (atau catat hash/isi file).
2. Coba pinjam alat berstatus `dipinjam` atau `tidak tersedia`.
3. Bandingkan isi semua file sebelum dan sesudah.

**Hasil yang diharapkan:** Muncul pesan penolakan; tidak ada baris baru atau perubahan di file mana pun; program tetap berjalan.

**Data uji:** (a) M002 meminjam A001 yang berstatus `dipinjam`; (b) M002 meminjam `A004, A001` (A004 tersedia, A001 tidak); (c) NIM `M999` yang tidak terdaftar.
**Hasil aktual:** ketiga percobaan ditolak dengan pesan `[DITOLAK] Alat A001 tidak tersedia (status: dipinjam).` (dua kali) dan `[DITOLAK] Mahasiswa dengan NIM M999 tidak ditemukan.`; tidak ada pesan `[OK]`; program tetap berjalan.
**Perbandingan file (sebelum/sesudah):**
```
mahasiswa.txt          sebelum: 3 baris | sesudah: 3 baris | identik: True
alat.txt               sebelum: 5 baris | sesudah: 5 baris | identik: True
transaksi.txt          sebelum: 1 baris | sesudah: 1 baris | identik: True
detail_transaksi.txt   sebelum: 3 baris | sesudah: 3 baris | identik: True
```
**Hasil tambahan (Aturan 2):** M001 membuat transaksi kedua (diterima), lalu transaksi ketiga ditolak dengan `[DITOLAK] Mahasiswa M001 sudah memiliki 2 transaksi aktif (maksimal 2).`; `transaksi.txt` hanya berisi T001 dan T002.
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 3
**Status:** Lulus

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

**Data uji:** transaksi T001 (A001, A002, A003); hanya A001 dikembalikan dengan kondisi `baik`.
**Hasil aktual:** `[OK] Alat A001 dikembalikan (baik).`; status T001 menjadi `sebagian dikembalikan`; A001 `dikembalikan|baik|2026-11-11` dan kembali `tersedia`; A002 dan A003 tetap `dipinjam`; layar menampilkan 3 alat tersedia (A001, A004, A005) dan 2 alat dipinjam (A002, A003); M001 tetap `aktif`.
**Isi file setelah pengujian:**
```
# transaksi.txt
T001|M001|2026-11-11|2026-11-18|sebagian dikembalikan

# detail_transaksi.txt
T001|A001|dikembalikan|baik|2026-11-11
T001|A002|dipinjam|-|-
T001|A003|dipinjam|-|-

# alat.txt
A001|Kamera Digital|perangkat multimedia|baik|tersedia
A002|Tripod|perangkat multimedia|baik|dipinjam
A003|Kabel LAN|perangkat jaringan|baik|dipinjam
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia
```
**Hasil tambahan:** sisa alat dikembalikan pada Skenario 5; setelah itu T001 berstatus `selesai`.
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 4
**Status:** Lulus

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

**Data uji:** sisa alat T001 dikembalikan: A002 dengan kondisi `rusak ringan`, A003 dengan kondisi `rusak berat`.
**Hasil aktual:** `[OK] Alat A002 dikembalikan (rusak ringan).` dan `[OK] Alat A003 dikembalikan (rusak berat).`; keduanya `tidak tersedia`; daftar alat tersedia hanya A001, A004, A005; daftar alat rusak berisi A002 dan A003; T001 menjadi `selesai`; M001 kembali `tidak aktif`.
**Isi file setelah pengujian:**
```
# alat.txt
A001|Kamera Digital|perangkat multimedia|baik|tersedia
A002|Tripod|perangkat multimedia|rusak ringan|tidak tersedia
A003|Kabel LAN|perangkat jaringan|rusak berat|tidak tersedia
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia

# detail_transaksi.txt
T001|A001|dikembalikan|baik|2026-11-11
T001|A002|dikembalikan|rusak ringan|2026-11-11
T001|A003|dikembalikan|rusak berat|2026-11-11
```
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 5
**Status:** Lulus

---

### Skenario 6: Hapus mahasiswa dengan transaksi aktif

**Tujuan:** Penghapusan ditolak.

**Langkah:**
1. Pilih mahasiswa yang masih punya transaksi aktif.
2. Coba hapus melalui menu Kelola data mahasiswa.
3. Periksa `mahasiswa.txt`.

**Hasil yang diharapkan:** Muncul pesan penolakan; data mahasiswa tetap ada di program dan file.

**Data uji:** M002 meminjam A004 (transaksi T002 aktif); hapus M002, hapus alat A004, dan hapus M001 (hanya punya riwayat transaksi selesai); sebagai pembanding, tambah M009 lalu hapus.
**Hasil aktual:**
```
[DITOLAK] Mahasiswa M002 masih memiliki transaksi aktif, tidak dapat dihapus.
[DITOLAK] Alat A004 sedang dipinjam (transaksi aktif), tidak dapat dihapus.
[DITOLAK] Mahasiswa M001 tercatat dalam riwayat transaksi, tidak dapat dihapus agar riwayat tetap utuh.
[OK] Mahasiswa M009 dihapus.   (pembanding, tanpa transaksi)
```
Keempat file data identik sebelum dan sesudah percobaan hapus; M002 tetap ada di `mahasiswa.txt` berstatus `aktif`.
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 6
**Status:** Lulus

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

**Hasil aktual:** M003 meminjam `A001, A005` (T003), A001 dikembalikan sehingga T003 `sebagian dikembalikan`; program ditutup lalu dijalankan ulang 3 kali. Setiap kali, T001 `selesai`, T002 `dipinjam`, T003 `sebagian dikembalikan`; A001 `tersedia`, A005 dan A004 `dipinjam`; tidak ada `[PERINGATAN]`; tidak ada NIM, kode alat, atau ID transaksi ganda.
**Jumlah baris per file (sebelum/sesudah 3 kali jalan ulang):**
```
mahasiswa.txt          3 baris -> 3 baris | isi identik: True
alat.txt               5 baris -> 5 baris | isi identik: True
transaksi.txt          3 baris -> 3 baris | isi identik: True
detail_transaksi.txt   6 baris -> 6 baris | isi identik: True
```
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 7
**Status:** Lulus

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

**Hasil aktual:** untuk tiap file (`mahasiswa.txt`, `alat.txt`, `transaksi.txt`, `detail_transaksi.txt`, `log.txt`) dilakukan dua percobaan (dihapus, lalu dikosongkan 0 byte). Seluruh 10 percobaan berakhir dengan kode keluar 0, tanpa traceback, dan file dibuat ulang otomatis. Setelah `alat.txt` dihapus, alat `A100|Osiloskop|pengukuran|baik|tersedia` berhasil ditambahkan lewat menu dan tersimpan di file yang dibuat ulang.
**Catatan:** jumlah `[PERINGATAN]` berbeda tiap file karena program membuang baris yang rujukannya hilang (Aturan 8). Menghapus `mahasiswa.txt` saat masih ada 3 transaksi membuat `transaksi.txt` menjadi 0 baris setelah program ditutup, jadi folder `data/` perlu dicadangkan terlebih dahulu.
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 8
**Status:** Lulus

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

**Baris yang ditambahkan:**
```
A777|Kolom Kurang|perangkat jaringan
M777|Terlalu|Banyak|Kolom|tidak aktif|lebih
T777|M001|2026-11-01
```
**Hasil aktual:** muncul tepat 3 `[PERINGATAN]` (satu per baris rusak, lengkap dengan nama file dan nomor baris) untuk `alat.txt`, `mahasiswa.txt`, dan `transaksi.txt`; program tetap berjalan, daftar alat tampil (5 data), dan alat baru `A200|Sensor Suhu|sensor|baik|tersedia` berhasil ditambahkan.
**Catatan:** apakah baris rusak tetap ada atau hilang dari file setelah program menyimpan? Hilang. Baris rusak dilewati saat dimuat dan tidak ikut tersimpan ketika program menulis ulang file; semua baris valid sebelumnya tetap ada di ketiga file (lihat `docs/bukti_eksekusi_skenario.md`, Skenario 9).
**Bukti:** layar dan isi file pada `docs/bukti_eksekusi_skenario.md`, Skenario 9
**Status:** Lulus

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

- Jumlah skenario lulus: 9 dari 9 pada eksekusi `main.py` berskrip (`docs/bukti_eksekusi_skenario.md`); pengujian manual QA: 9 dari 9
- Jumlah skenario gagal: 0 pada eksekusi berskrip; pengujian manual QA: 0
- Catatan umum: penghapusan alat atau mahasiswa yang tercatat di riwayat transaksi sengaja ditolak (lebih ketat dari Aturan 6, mengikuti Aturan 8), dan baris rusak atau rujukan yang hilang dibuang dari file saat program menyimpan. QA: seluruh skenario sesuai hasil yang diharapkan dan program tidak pernah berhenti dengan traceback.

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

Yang belum ada: hasil cross-group code review, yang perlu dilengkapi tim setelah review dilakukan.
