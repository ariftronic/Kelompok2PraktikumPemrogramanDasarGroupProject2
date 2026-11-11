# Bukti Eksekusi Skenario Pengujian Wajib

Dokumen ini berisi hasil menjalankan **`python main.py` sungguhan** untuk kesembilan skenario wajib pada soal Proyek II. Masukan keyboard diberikan lewat stdin, jadi layar dan isi file di bawah adalah keluaran program yang sebenarnya, bukan hasil ketikan ulang.

| Item | Isian |
|---|---|
| Tanggal eksekusi | 2026-11-11 |
| Lingkungan | Python 3.14.6, Windows |
| Kode yang diuji | isi `app/` dan `main.py` pada commit `66f7247` |
| Cara mengulang | `python tests/skenario_wajib.py` dari folder proyek (menulis ulang dokumen ini) |
| Tempat eksekusi | salinan sementara proyek dengan folder `data/` kosong; folder `data/` di repository tidak disentuh |
| Pemeriksaan | tiap skenario memuat daftar pemeriksaan yang dihitung oleh skrip, lalu hasil LULUS/GAGAL ditentukan dari daftar itu |

Skenario 1 sampai 7 dijalankan berurutan pada data yang sama (data dari skenario sebelumnya dipakai skenario berikutnya). Skenario 8 dan 9 memakai salinan dari data akhir Skenario 7. Tanggal pinjam pada contoh sama dengan tanggal eksekusi.

**Yang belum dicakup dokumen ini:** pengujian manual oleh QA dengan tangkapan layar (kolom "Bukti (screenshot)" di `docs/pengujian.md`) dan review oleh kelompok lain. Dokumen ini dapat dipakai sebagai pembanding hasilnya.

## Ringkasan

| No | Skenario | Jumlah pemeriksaan | Hasil |
|---|---|---|---|
| 1 | Tambah mahasiswa dan alat | 6 | LULUS |
| 2 | Peminjaman beberapa alat dalam satu transaksi | 6 | LULUS |
| 3 | Meminjam alat yang tidak tersedia | 7 | LULUS |
| 4 | Pengembalian sebagian | 7 | LULUS |
| 5 | Pengembalian alat rusak ringan dan rusak berat | 8 | LULUS |
| 6 | Hapus mahasiswa/alat dengan transaksi aktif | 7 | LULUS |
| 7 | Tutup lalu jalankan ulang (termasuk transaksi sebagian) | 7 | LULUS |
| 8 | File data dihapus atau dikosongkan | 4 | LULUS |
| 9 | Baris berformat salah | 7 | LULUS |

---

## Skenario 1: Tambah mahasiswa dan alat

**Langkah:** menu 1 (Kelola data mahasiswa) lalu Tambah untuk M001, M002, M003 (M003 tanpa nomor HP); menu 2 (Kelola data alat) lalu Tambah untuk A001 sampai A005 dari tiga kategori. A004 memakai kategori baru `perangkat komputasi`. Setelah itu program ditutup lewat menu 0.

**Layar (cuplikan):**

```text
Daftar mahasiswa (3 data)
1. M001 | Andi Pratama | HP: 081234567890 | peminjaman: tidak aktif
2. M002 | Budi Santoso | HP: 085612345678 | peminjaman: tidak aktif
3. M003 | Citra Lestari | HP: - | peminjaman: tidak aktif

Daftar alat (5 data)
1. A001 | Kamera Digital | kategori: perangkat multimedia | kondisi: baik | status: tersedia
2. A002 | Tripod | kategori: perangkat multimedia | kondisi: baik | status: tersedia
3. A003 | Kabel LAN | kategori: perangkat jaringan | kondisi: baik | status: tersedia
4. A004 | Laptop | kategori: perangkat komputasi | kondisi: baik | status: tersedia
5. A005 | Kabel HDMI | kategori: perangkat multimedia | kondisi: baik | status: tersedia
```

**Isi `mahasiswa.txt`:**

```text
M001|Andi Pratama|081234567890|tidak aktif
M002|Budi Santoso|085612345678|tidak aktif
M003|Citra Lestari|-|tidak aktif
```

**Isi `alat.txt`:**

```text
A001|Kamera Digital|perangkat multimedia|baik|tersedia
A002|Tripod|perangkat multimedia|baik|tersedia
A003|Kabel LAN|perangkat jaringan|baik|tersedia
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia
```

**Pemeriksaan otomatis**

- [x] `mahasiswa.txt` berisi 3 baris sesuai masukan, no. HP kosong ditulis `-`
- [x] `alat.txt` berisi 5 baris, semuanya `baik` dan `tersedia`
- [x] kategori baru `perangkat komputasi` tercatat tanpa mengubah kode program
- [x] tidak ada NIM atau kode alat ganda
- [x] pesan `[OK]` muncul 8 kali (3 mahasiswa + 5 alat)
- [x] program berakhir normal (kode keluar 0, tanpa traceback)

**Hasil: LULUS**

---

## Skenario 2: Peminjaman beberapa alat dalam satu transaksi

**Langkah:** menu 3 (Buat transaksi peminjaman), NIM `M001`, kode alat `A001, A002, A003`; lalu menu 4 (Tampilkan transaksi) dan menu 8 (Tampilkan alat yang sedang dipinjam).

**Layar (cuplikan):**

```text
[OK] Transaksi peminjaman berhasil dibuat.
     T001 | M001 | pinjam 2026-11-11 | batas 2026-11-18 | dipinjam
     - A001: dipinjam
     - A002: dipinjam
     - A003: dipinjam

Alat yang sedang dipinjam (3 data)
1. A001 | Kamera Digital | kategori: perangkat multimedia | kondisi: baik | status: dipinjam
2. A002 | Tripod | kategori: perangkat multimedia | kondisi: baik | status: dipinjam
3. A003 | Kabel LAN | kategori: perangkat jaringan | kondisi: baik | status: dipinjam
```

**Isi `transaksi.txt`:**

```text
T001|M001|2026-11-11|2026-11-18|dipinjam
```

**Isi `detail_transaksi.txt`:**

```text
T001|A001|dipinjam|-|-
T001|A002|dipinjam|-|-
T001|A003|dipinjam|-|-
```

**Isi `alat.txt`:**

```text
A001|Kamera Digital|perangkat multimedia|baik|dipinjam
A002|Tripod|perangkat multimedia|baik|dipinjam
A003|Kabel LAN|perangkat jaringan|baik|dipinjam
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia
```

**Isi `mahasiswa.txt`:**

```text
M001|Andi Pratama|081234567890|aktif
M002|Budi Santoso|085612345678|tidak aktif
M003|Citra Lestari|-|tidak aktif
```

**Pemeriksaan otomatis**

- [x] `transaksi.txt` berisi satu baris `T001|M001|2026-11-11|2026-11-18|dipinjam` (batas kembali tepat 7 hari)
- [x] `detail_transaksi.txt` berisi satu baris per alat (3 baris) berstatus `dipinjam`
- [x] status A001, A002, A003 di file menjadi `dipinjam`; A004 dan A005 tetap `tersedia`
- [x] layar menampilkan `Alat yang sedang dipinjam (3 data)`
- [x] status aktif M001 menjadi `aktif` di file
- [x] program berakhir normal

**Hasil: LULUS**

---

## Skenario 3: Meminjam alat yang tidak tersedia

**Langkah:** menu 3 dengan tiga percobaan: (a) M002 meminjam A001 yang berstatus `dipinjam`; (b) M002 meminjam `A004, A001` (A004 tersedia, A001 tidak); (c) NIM `M999` yang tidak terdaftar. Keempat file data dibandingkan sebelum dan sesudah. Tambahan (Aturan 2) pada salinan terpisah: M001 yang sudah punya 1 transaksi aktif membuat transaksi kedua (A004), lalu transaksi ketiga (A005).

**Layar (penolakan):**

```text
[DITOLAK] Alat A001 tidak tersedia (status: dipinjam).
[DITOLAK] Alat A001 tidak tersedia (status: dipinjam).
[DITOLAK] Mahasiswa dengan NIM M999 tidak ditemukan.
```

**Isi file sebelum dan sesudah (jumlah baris dan kesamaan):**

```text
mahasiswa.txt          sebelum: 3 baris | sesudah: 3 baris | identik: True
alat.txt               sebelum: 5 baris | sesudah: 5 baris | identik: True
transaksi.txt          sebelum: 1 baris | sesudah: 1 baris | identik: True
detail_transaksi.txt   sebelum: 3 baris | sesudah: 3 baris | identik: True
```

**Tambahan, Aturan 2 (salinan terpisah):**

```text
[OK] Transaksi peminjaman berhasil dibuat.
[DITOLAK] Mahasiswa M001 sudah memiliki 2 transaksi aktif (maksimal 2).
```

**Pemeriksaan otomatis**

- [x] ketiga percobaan ditolak (3 pesan `[DITOLAK]`)
- [x] pesan penolakan menyebut alat A001 tidak tersedia
- [x] tidak ada pesan `[OK]` pada percobaan yang ditolak
- [x] keempat file data identik byte demi byte sebelum dan sesudah
- [x] transaksi kedua M001 diterima, transaksi ketiga ditolak karena maksimal 2 transaksi aktif
- [x] setelah penolakan Aturan 2, `transaksi.txt` hanya berisi T001 dan T002
- [x] program tetap berjalan sampai keluar normal

**Hasil: LULUS**

---

## Skenario 4: Pengembalian sebagian

**Langkah:** menu 5 (Proses pengembalian alat), ID `T001`, mengembalikan hanya `A001` dengan kondisi `1` (baik); lalu menu 7 (alat tersedia), menu 8 (alat sedang dipinjam), dan menu 4 (tampilkan transaksi).

**Layar (cuplikan):**

```text
[OK] Alat A001 dikembalikan (baik).
     T001 | M001 | pinjam 2026-11-11 | batas 2026-11-18 | sebagian dikembalikan
     - A001: dikembalikan (baik, 2026-11-11)
     - A002: dipinjam
     - A003: dipinjam

Alat yang tersedia (3 data)
1. A001 | Kamera Digital | kategori: perangkat multimedia | kondisi: baik | status: tersedia
2. A004 | Laptop | kategori: perangkat komputasi | kondisi: baik | status: tersedia
3. A005 | Kabel HDMI | kategori: perangkat multimedia | kondisi: baik | status: tersedia

Alat yang sedang dipinjam (2 data)
1. A002 | Tripod | kategori: perangkat multimedia | kondisi: baik | status: dipinjam
2. A003 | Kabel LAN | kategori: perangkat jaringan | kondisi: baik | status: dipinjam
```

**Isi `transaksi.txt`:**

```text
T001|M001|2026-11-11|2026-11-18|sebagian dikembalikan
```

**Isi `detail_transaksi.txt`:**

```text
T001|A001|dikembalikan|baik|2026-11-11
T001|A002|dipinjam|-|-
T001|A003|dipinjam|-|-
```

**Isi `alat.txt`:**

```text
A001|Kamera Digital|perangkat multimedia|baik|tersedia
A002|Tripod|perangkat multimedia|baik|dipinjam
A003|Kabel LAN|perangkat jaringan|baik|dipinjam
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia
```

**Pemeriksaan otomatis**

- [x] status transaksi berubah menjadi `sebagian dikembalikan`
- [x] `A001` tercatat `dikembalikan|baik|2026-11-11` di `detail_transaksi.txt`
- [x] A002 dan A003 tetap `dipinjam` di detail dan di `alat.txt`
- [x] A001 kembali `baik|tersedia`
- [x] layar: 3 alat tersedia (A001, A004, A005) dan 2 alat dipinjam (A002, A003)
- [x] M001 tetap `aktif` karena transaksinya belum selesai
- [x] program berakhir normal

**Hasil: LULUS**

---

## Skenario 5: Alat dikembalikan dalam kondisi rusak

**Langkah:** menu 5, ID `T001`, mengembalikan sisa alat `A002, A003`: A002 dengan kondisi `2` (rusak ringan), A003 dengan kondisi `3` (rusak berat). Lalu menu 7 (alat tersedia), menu 9 (alat rusak), dan menu 4 (tampilkan transaksi). Ini sekaligus menyelesaikan transaksi T001 (tambahan Skenario 4).

**Layar (cuplikan):**

```text
[OK] Alat A002 dikembalikan (rusak ringan).
[OK] Alat A003 dikembalikan (rusak berat).

Alat yang tersedia (3 data)
1. A001 | Kamera Digital | kategori: perangkat multimedia | kondisi: baik | status: tersedia
2. A004 | Laptop | kategori: perangkat komputasi | kondisi: baik | status: tersedia
3. A005 | Kabel HDMI | kategori: perangkat multimedia | kondisi: baik | status: tersedia

Alat yang rusak (2 data)
1. A002 | Tripod | kategori: perangkat multimedia | kondisi: rusak ringan | status: tidak tersedia
2. A003 | Kabel LAN | kategori: perangkat jaringan | kondisi: rusak berat | status: tidak tersedia
```

**Isi `alat.txt`:**

```text
A001|Kamera Digital|perangkat multimedia|baik|tersedia
A002|Tripod|perangkat multimedia|rusak ringan|tidak tersedia
A003|Kabel LAN|perangkat jaringan|rusak berat|tidak tersedia
A004|Laptop|perangkat komputasi|baik|tersedia
A005|Kabel HDMI|perangkat multimedia|baik|tersedia
```

**Isi `detail_transaksi.txt`:**

```text
T001|A001|dikembalikan|baik|2026-11-11
T001|A002|dikembalikan|rusak ringan|2026-11-11
T001|A003|dikembalikan|rusak berat|2026-11-11
```

**Isi `transaksi.txt`:**

```text
T001|M001|2026-11-11|2026-11-18|selesai
```

**Isi `mahasiswa.txt`:**

```text
M001|Andi Pratama|081234567890|tidak aktif
M002|Budi Santoso|085612345678|tidak aktif
M003|Citra Lestari|-|tidak aktif
```

**Pemeriksaan otomatis**

- [x] A002 tercatat `rusak ringan|tidak tersedia`
- [x] A003 tercatat `rusak berat|tidak tersedia`
- [x] kondisi dan tanggal pengembalian tercatat di `detail_transaksi.txt`
- [x] daftar alat tersedia hanya A001, A004, A005 (A002 dan A003 tidak muncul)
- [x] daftar alat rusak berisi A002 dan A003
- [x] transaksi T001 menjadi `selesai`
- [x] M001 kembali `tidak aktif` setelah transaksi selesai
- [x] program berakhir normal

**Hasil: LULUS**

---

## Skenario 6: Hapus mahasiswa atau alat yang masih punya transaksi aktif

**Langkah:** M002 meminjam A004 (transaksi T002 aktif). Lalu menu 1 > Hapus untuk `M002` (konfirmasi `y`), menu 2 > Hapus untuk alat `A004`, dan Hapus untuk `M001` (hanya punya riwayat transaksi selesai). Terakhir, sebagai pembanding, menambah `M009` lalu menghapusnya.

**Layar (penolakan):**

```text
[DITOLAK] Mahasiswa M002 masih memiliki transaksi aktif, tidak dapat dihapus.
[DITOLAK] Alat A004 sedang dipinjam (transaksi aktif), tidak dapat dihapus.
[DITOLAK] Mahasiswa M001 tercatat dalam riwayat transaksi, tidak dapat dihapus agar riwayat tetap utuh.
```

**Layar (pembanding, M009 tanpa transaksi):**

```text
[OK] Mahasiswa berhasil ditambahkan.
[OK] Mahasiswa M009 dihapus.
```

**Isi file sebelum dan sesudah percobaan hapus:**

```text
mahasiswa.txt          identik: True
alat.txt               identik: True
transaksi.txt          identik: True
detail_transaksi.txt   identik: True
```

**Isi `mahasiswa.txt` sesudah semua langkah:**

```text
M001|Andi Pratama|081234567890|tidak aktif
M002|Budi Santoso|085612345678|aktif
M003|Citra Lestari|-|tidak aktif
```

**Pemeriksaan otomatis**

- [x] M002 (transaksi aktif) ditolak dihapus
- [x] alat A004 (sedang dipinjam) ditolak dihapus
- [x] M001 (hanya riwayat) ditolak dihapus agar riwayat transaksi tetap valid (Aturan 8)
- [x] keempat file data identik sebelum dan sesudah penolakan
- [x] mahasiswa tanpa transaksi (M009) dapat dihapus, jadi larangan hanya berlaku bila ada transaksi
- [x] pinjaman M002 diterima sebelum percobaan hapus
- [x] program berakhir normal

**Hasil: LULUS**

---

## Skenario 7: Tutup lalu jalankan ulang program

**Langkah:** M003 meminjam `A001, A005` (T003), lalu hanya A001 dikembalikan sehingga T003 berstatus `sebagian dikembalikan`. Program ditutup (menu 0). Program dijalankan ulang 3 kali; tiap kali menampilkan transaksi (menu 4), mahasiswa (menu 1 > 5), dan alat (menu 2 > 5), lalu keluar.

**Layar pada jalan ulang ketiga (cuplikan):**

```text
Daftar transaksi (3 data)
1. T001 | M001 | pinjam 2026-11-11 | batas 2026-11-18 | selesai
     - A001: dikembalikan (baik, 2026-11-11)
     - A002: dikembalikan (rusak ringan, 2026-11-11)
     - A003: dikembalikan (rusak berat, 2026-11-11)
2. T002 | M002 | pinjam 2026-11-11 | batas 2026-11-18 | dipinjam
     - A004: dipinjam
3. T003 | M003 | pinjam 2026-11-11 | batas 2026-11-18 | sebagian dikembalikan
     - A001: dikembalikan (baik, 2026-11-11)
     - A005: dipinjam

Daftar mahasiswa (3 data)
1. M001 | Andi Pratama | HP: 081234567890 | peminjaman: tidak aktif
2. M002 | Budi Santoso | HP: 085612345678 | peminjaman: aktif
3. M003 | Citra Lestari | HP: - | peminjaman: aktif

Daftar alat (5 data)
1. A001 | Kamera Digital | kategori: perangkat multimedia | kondisi: baik | status: tersedia
2. A002 | Tripod | kategori: perangkat multimedia | kondisi: rusak ringan | status: tidak tersedia
3. A003 | Kabel LAN | kategori: perangkat jaringan | kondisi: rusak berat | status: tidak tersedia
4. A004 | Laptop | kategori: perangkat komputasi | kondisi: baik | status: dipinjam
5. A005 | Kabel HDMI | kategori: perangkat multimedia | kondisi: baik | status: dipinjam
```

**Jumlah baris per file (sesudah penutupan pertama dan sesudah 3 kali jalan ulang):**

```text
mahasiswa.txt          3 baris -> 3 baris | isi identik: True
alat.txt               5 baris -> 5 baris | isi identik: True
transaksi.txt          3 baris -> 3 baris | isi identik: True
detail_transaksi.txt   6 baris -> 6 baris | isi identik: True
```

**Isi `transaksi.txt` sesudah jalan ulang:**

```text
T001|M001|2026-11-11|2026-11-18|selesai
T002|M002|2026-11-11|2026-11-18|dipinjam
T003|M003|2026-11-11|2026-11-18|sebagian dikembalikan
```

**Pemeriksaan otomatis**

- [x] transaksi T003 masih `sebagian dikembalikan` setelah dijalankan ulang
- [x] layar jalan ulang menampilkan T001 `selesai`, T002 `dipinjam`, dan T003 `sebagian dikembalikan`
- [x] alat: A001 `tersedia`, A005 `dipinjam`, A004 `dipinjam` (T002)
- [x] jumlah baris dan isi semua file tidak berubah setelah 3 kali jalan ulang (tidak ada data ganda)
- [x] tidak ada `[PERINGATAN]` pada ketiga jalan ulang
- [x] tidak ada NIM, kode alat, atau ID transaksi ganda
- [x] semua jalan berakhir normal

**Hasil: LULUS**

---

## Skenario 8: File data dihapus atau dikosongkan

**Langkah:** untuk setiap file (`mahasiswa.txt`, `alat.txt`, `transaksi.txt`, `detail_transaksi.txt`, `log.txt`) dilakukan dua percobaan terpisah pada salinan data dari Skenario 7: file dihapus, lalu file dikosongkan (0 byte). Tiap percobaan menjalankan program dan langsung keluar (menu 0). Lalu, setelah `alat.txt` dihapus, menambah alat `A100` lewat menu.

| File | Tindakan | Kode keluar | Traceback | File ada setelah dijalankan | Jumlah `[PERINGATAN]` |
|---|---|---|---|---|---|
| `mahasiswa.txt` | dihapus | 0 | tidak | ya | 11 |
| `mahasiswa.txt` | dikosongkan | 0 | tidak | ya | 11 |
| `alat.txt` | dihapus | 0 | tidak | ya | 11 |
| `alat.txt` | dikosongkan | 0 | tidak | ya | 11 |
| `transaksi.txt` | dihapus | 0 | tidak | ya | 10 |
| `transaksi.txt` | dikosongkan | 0 | tidak | ya | 10 |
| `detail_transaksi.txt` | dihapus | 0 | tidak | ya | 7 |
| `detail_transaksi.txt` | dikosongkan | 0 | tidak | ya | 7 |
| `log.txt` | dihapus | 0 | tidak | ya | 0 |
| `log.txt` | dikosongkan | 0 | tidak | ya | 0 |

Jumlah `[PERINGATAN]` berbeda-beda karena program membuang baris yang rujukannya hilang (Aturan 8) dan memperbaiki status alat atau mahasiswa yang bergantung padanya. `log.txt` tidak dirujuk file lain, jadi tidak menimbulkan peringatan.

**Menambah data setelah `alat.txt` dihapus (layar dan isi file):**

```text
[PERINGATAN] detail_transaksi.txt: alat A001 pada transaksi T001 tidak ditemukan, baris dilewati
[PERINGATAN] detail_transaksi.txt: alat A002 pada transaksi T001 tidak ditemukan, baris dilewati
[PERINGATAN] detail_transaksi.txt: alat A003 pada transaksi T001 tidak ditemukan, baris dilewati
[OK] Alat berhasil ditambahkan.
```

```text
A100|Osiloskop|pengukuran|baik|tersedia
```

**Dampak yang perlu diketahui:** baris yang dibuang saat memuat tidak ikut tersimpan lagi. Contoh pada salinan terpisah, `mahasiswa.txt` dihapus saat masih ada 3 transaksi:

```text
[PERINGATAN] transaksi.txt: NIM M001 pada transaksi T001 tidak ditemukan, baris dilewati
[PERINGATAN] transaksi.txt: NIM M002 pada transaksi T002 tidak ditemukan, baris dilewati
[PERINGATAN] transaksi.txt: NIM M003 pada transaksi T003 tidak ditemukan, baris dilewati
...
transaksi.txt sebelum: 3 baris | sesudah program ditutup: 0 baris
```

Jadi menghapus `mahasiswa.txt` atau `alat.txt` tidak membuat program error, tetapi transaksi yang merujuk data itu hilang dari file. Salin folder `data/` terlebih dahulu sebelum menguji skenario ini.

**Pemeriksaan otomatis**

- [x] semua 10 percobaan berakhir dengan kode keluar 0
- [x] tidak ada traceback pada satupun percobaan
- [x] file yang dihapus dibuat ulang otomatis pada semua percobaan
- [x] program tetap dapat dipakai: alat `A100` tersimpan di `alat.txt` yang dibuat ulang

**Hasil: LULUS**

---

## Skenario 9: Baris berformat salah

**Langkah:** pada salinan data ditambahkan secara manual satu baris rusak ke tiga file: `alat.txt` (3 kolom, seharusnya 5), `mahasiswa.txt` (6 kolom, seharusnya 4), dan `transaksi.txt` (3 kolom, seharusnya 5). Program dijalankan, daftar alat ditampilkan (menu 2 > 5), alat baru `A200` ditambahkan, lalu program ditutup.

**Baris yang ditambahkan:**

```text
A777|Kolom Kurang|perangkat jaringan
M777|Terlalu|Banyak|Kolom|tidak aktif|lebih
T777|M001|2026-11-01
```

**Layar (peringatan dan operasi sesudahnya):**

```text
[PERINGATAN] alat.txt: baris 6 dilewati (ada 3 kolom, seharusnya 5): A777|Kolom Kurang|perangkat jaringan
[PERINGATAN] mahasiswa.txt: baris 4 dilewati (ada 6 kolom, seharusnya 4): M777|Terlalu|Banyak|Kolom|tidak aktif|lebih
[PERINGATAN] transaksi.txt: baris 4 dilewati (ada 3 kolom, seharusnya 5): T777|M001|2026-11-01

Daftar alat (5 data)
1. A001 | Kamera Digital | kategori: perangkat multimedia | kondisi: baik | status: tersedia
2. A002 | Tripod | kategori: perangkat multimedia | kondisi: rusak ringan | status: tidak tersedia
3. A003 | Kabel LAN | kategori: perangkat jaringan | kondisi: rusak berat | status: tidak tersedia
4. A004 | Laptop | kategori: perangkat komputasi | kondisi: baik | status: dipinjam
5. A005 | Kabel HDMI | kategori: perangkat multimedia | kondisi: baik | status: dipinjam

[OK] Alat berhasil ditambahkan.
```

**Catatan perilaku:** baris rusak dilewati saat dimuat dan tidak ikut tersimpan. Setelah program menyimpan, baris rusak tersebut hilang dari file (lihat pemeriksaan di bawah). Bila baris itu masih ingin dipertahankan, salin dulu sebelum menjalankan program.

**Isi `alat.txt` sesudah program ditutup:**

```text
A001|Kamera Digital|perangkat multimedia|baik|tersedia
A002|Tripod|perangkat multimedia|rusak ringan|tidak tersedia
A003|Kabel LAN|perangkat jaringan|rusak berat|tidak tersedia
A004|Laptop|perangkat komputasi|baik|dipinjam
A005|Kabel HDMI|perangkat multimedia|baik|dipinjam
A200|Sensor Suhu|sensor|baik|tersedia
```

**Pemeriksaan otomatis**

- [x] muncul tepat 3 `[PERINGATAN]`, satu untuk tiap baris rusak, lengkap dengan nama file dan nomor baris
- [x] peringatan menyebut ketiga file (`alat.txt`, `mahasiswa.txt`, `transaksi.txt`)
- [x] program tetap berjalan: daftar alat tampil dan alat `A200` berhasil ditambahkan
- [x] semua baris valid sebelumnya tetap ada di ketiga file
- [x] baris rusak tidak tersimpan kembali ke file
- [x] `A200` tersimpan di `alat.txt`
- [x] program berakhir normal

**Hasil: LULUS**

---
