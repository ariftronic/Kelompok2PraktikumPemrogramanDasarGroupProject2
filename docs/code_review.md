# Hasil Code Review

Proyek II Praktikum Pemrograman Dasar: Sistem Pengelolaan Peminjaman Peralatan Laboratorium Berbasis Text File

| | |
|---|---|
| Objek review | Repository **Kelompok 2** (`Kelompok2PraktikumPemrogramanDasarGroupProject2-main`), 13 file Python (`main.py` dan `app/`, tanpa `__init__.py`) |
| Tanggal | 12 November 2026 |
| Pembagian aspek | Kesesuaian rancangan: Rara/Fatimah. Ketepatan solusi: Niken. Pengelolaan file: Arif. Skalabilitas: Faris |
| Cara review | Seluruh kode di `app/`, README, UML final, dan dokumen di `docs/` dibaca. Tes bawaan dan sembilan skenario dijalankan. Percobaan tambahan (E1 sampai E11) dijalankan pada **salinan** repo dengan data sementara, sehingga folder `data/` asli tidak berubah |
| Lingkungan | Python 3.13 (README menyebut diuji di 3.14), tanpa library tambahan |
| Belum diperiksa | Histori commit dan akun GitHub tiap anggota (ZIP tidak memuat `.git`), isi gambar UML individu, serta pengujian manual QA |

> **Catatan cakupan.** Repository ini adalah repository kelompok sendiri. Bila dokumen ini dipakai sebagai hasil *cross-group* review, ulangi percobaan E1 sampai E11 (skrip dapat diminta) pada repository kelompok yang ditugaskan. Temuan di bawah disusun dari analisis kode, jadi reviewer tiap aspek sebaiknya memverifikasinya sebelum dikumpulkan.

## Ringkasan

Program berjalan benar untuk alur utama. **105 tes otomatis lulus dan kesembilan skenario wajib lulus.** Struktur class jelas, `FileManager` menjadi satu-satunya tempat `open()`, penulisan memakai file sementara lalu `os.replace`, dan aturan bisnis diperiksa sebelum data berubah.

Kelemahan terbesarnya ada di **penanganan data yang rusak atau aturan yang berubah**: program melewati baris yang bermasalah lalu menulis ulang seluruh file saat keluar, sehingga baris itu dan data yang bergantung padanya hilang permanen (temuan F1, S2). Soal skala data, kecepatan tulis ulang file ternyata masih memadai untuk 20.000 mahasiswa dan 10.000 alat; yang bermasalah di skala itu adalah tampilan menu (S4).

| Tingkat | Jumlah | Temuan |
|---|---|---|
| Tinggi | 2 | F1, S2 |
| Sedang | 5 | K1, F2, S3, S4, S5 |
| Rendah | 6 | R1, R2, R3, K2, K3, S6 |

Tingkat: **Tinggi** = data hilang atau aturan bisnis terlanggar dalam penggunaan wajar; **Sedang** = menyulitkan pengembangan atau menurunkan kegunaan; **Rendah** = perbaikan kecil.

---

## 1. Kesesuaian Rancangan dan Implementasi

Reviewer: Rara/Fatimah

| Pemeriksaan | Hasil |
|---|---|
| Class pada UML final diimplementasikan | Sesuai. `Mahasiswa`, `Alat`, `Transaksi`, `DetailTransaksi`, empat manager, `FileManager`, `FileManagerError`, `Logger`, dan `AplikasiPeminjaman` ada di kode |
| Atribut dan method sesuai UML | Sesuai. Seluruh method pada UML ditemukan di kode dengan nama yang sama |
| Hubungan antarclass | Sesuai. `Transaksi` berisi `DetailTransaksi`, manager memakai `FileManager` dan `Logger`, dan referensi dua arah alat/mahasiswa dengan transaksi dibuat lewat `sambungkan_transaksi` |
| Format file sesuai README | Sesuai. Kolom di README sama dengan `KOLOM_FILE` di `konstanta.py`, begitu pula nilai status dan kondisi yang diizinkan |
| Struktur folder sesuai rekomendasi | Hampir sesuai. `file_manager.py`, `logger.py`, `validasi.py`, dan `menu.py` ada di `app/`. Folder data sampel bernama `data_sampel/` (README menjelaskannya) |

Temuan:

| No | Tingkat | Temuan | Saran |
|---|---|---|---|
| R1 | Rendah | `Alat.tandai_dipinjam()` dan `Alat.tandai_dikembalikan()` tercantum di UML tetapi **tidak pernah dipanggil**. `ManagerTransaksi.buat` dan `ManagerPengembalian.kembalikan` mengubah `alat.status` dan `alat.kondisi` langsung. Aturan kondisi menjadi status juga ditulis di tiga tempat: `Alat.status_dari_kondisi`, `ManagerPengembalian.kembalikan`, dan `ManagerTransaksi._selaraskan` | Panggil method model dari manager lalu hapus duplikasinya, atau hapus method yang tidak dipakai dari kode dan UML |
| R2 | Rendah | `_selaraskan()` memuat logika penting (memperbaiki status transaksi, alat, dan mahasiswa dari detail) tetapi tidak tampil di UML karena bersifat privat | Tambahkan ke UML atau jelaskan di `keputusan_desain.md` |
| R3 | Rendah | **0 dari 127** class dan method publik memiliki docstring, padahal pembagian tugas kelompok meminta docstring singkat. Atribut `id_transaksi` dan `kode_alat` juga berbeda dari nama kolom `id` dan `kode` (kemungkinan sengaja agar tidak menimpa `id` bawaan Python, tetapi belum didokumentasikan) | Tambahkan docstring satu baris. Catat alasan penamaan atribut di README |

Dokumen yang belum final: `keputusan_desain.md` masih memuat 4 bagian `[ISI TIM]` dan menyatakan UML Fatimah belum ada, padahal `docs/individu/` kini memilikinya. Nama file di `docs/individu/` memakai "Kelompok3" padahal kelompok ini Kelompok 2. `pengujian.md` masih memuat 33 isian `........`.

## 2. Ketepatan Solusi

Reviewer: Niken

Hasil menjalankan program:

- `python -m unittest`: **105 tes, semua lulus**.
- `python tests/skenario_wajib.py`: **Skenario 1 sampai 9 lulus**.
- Percobaan tambahan (E11) dengan input beragam:

| Aturan | Percobaan | Hasil |
|---|---|---|
| 1 | Pinjam alat `A004` (rusak ringan, tidak tersedia) | Ditolak dengan pesan jelas |
| 2 | Mahasiswa `M004` membuat transaksi ke-3 | Ditolak (maksimal 2 aktif) |
| 3 | Satu transaksi berisi beberapa alat, input `" m004 "` dan `"a003"` huruf kecil | Diterima, ID `T004` |
| 4 | Kembalikan satu alat, lalu kembalikan alat yang sama lagi | Pertama diterima, kedua ditolak |
| 6 | Hapus mahasiswa dan alat yang masih ada di transaksi aktif | Ditolak |
| 7 | Isi file setelah operasi ditolak | Tidak berubah |

Temuan:

| No | Tingkat | Temuan | Saran |
|---|---|---|---|
| K1 | Sedang | **Aturan 1 dapat terlanggar setelah satu baris rusak** (percobaan E2b). Bila satu baris `transaksi.txt` rusak (misalnya tanggal `2026-13-45`), detail transaksinya ikut dilewati, lalu status alat yang sebenarnya masih dipinjam "diperbaiki" menjadi `tersedia` oleh `_selaraskan`. Alat itu kemudian bisa dipinjam mahasiswa lain, padahal masih dipegang peminjam pertama. Penyebab lengkapnya ada di F1 | Lihat F1. Jangan ubah status alat menjadi tersedia bila alat itu tercatat di baris yang dilewati |
| K2 | Rendah | Tanggal berformat tidak baku seperti `2026-11-2` **diterima tanpa peringatan** dan ditulis kembali apa adanya (E10), karena `strptime` menerima bulan dan hari satu digit. Dokumen desain menyebut tanggal "mudah dibandingkan sebagai teks", yang tidak berlaku untuk bentuk ini | Setelah `strptime`, bandingkan hasil `strftime` dengan teks asli, atau simpan ulang dalam bentuk baku |
| K3 | Rendah | `riwayat_mahasiswa()` mengembalikan transaksi menurut urutan file, bukan menurut tanggal. Urutan ini sama dengan kronologis hanya selama ID selalu naik | Urutkan menurut `(tgl_pinjam, nomor ID)` bila riwayat ditampilkan |

Keputusan yang berbeda dari teks soal dan sudah didokumentasikan: Aturan 6 dibuat lebih ketat (alat dan mahasiswa yang punya riwayat tidak dapat dihapus), serta `status_aktif` mahasiswa diatur otomatis. Keduanya tercatat sebagai tafsiran yang belum dikonfirmasi ke asisten. Sebaiknya dikonfirmasi sebelum presentasi.

## 3. Pengelolaan File

Reviewer: Arif

| Pemeriksaan | Hasil |
|---|---|
| Data dimuat benar saat program dijalankan | Ya. `muat()` pada alat, mahasiswa, lalu transaksi, dengan pemeriksaan rujukan antarfile |
| Isi file selalu sama dengan data di program | Ya untuk operasi normal. Saat penyimpanan gagal, data dimuat ulang dari file. Pengecualian ada di F2 |
| Tidak error bila file belum ada atau kosong | Ya. `pastikan_file` membuat file baru otomatis (Skenario 8 lulus) |
| Baris tidak sesuai format ditangani | Ya. Dilewati dengan peringatan `[PERINGATAN]`, program tetap berjalan. Akibat sampingnya ada di F1 |
| File dibuka dan ditutup dengan benar | Ya. Keempat `open()` ada di `file_manager.py` dan semuanya memakai `with`, dengan `try-except` |
| Tidak ada data ganda setelah dijalankan berulang | Ya. NIM, kode alat, ID transaksi, dan alat ganda dalam satu transaksi dilewati saat dimuat |
| Karakter `|` dan baris baru | Ditolak saat input (`menu.py`, `validasi.py`) dan saat menulis (`FileManager.periksa_nilai`) |
| Penulisan aman | Tulis ke `*.tmp` lalu `os.replace`, sehingga kegagalan di tengah tidak merusak file lama |

Temuan:

| No | Tingkat | Temuan | Saran |
|---|---|---|---|
| F1 | **Tinggi** | **Data hilang permanen setelah menjalankan lalu menutup program.** `_keluar()` menulis ulang semua file, termasuk data yang tadinya sudah dilewati. Dua contoh terukur: (a) **E9**: file `mahasiswa.txt` dihapus (persis Skenario 8) lalu program ditutup lewat menu 0. Hasilnya `transaksi.txt` dari 3 baris menjadi 0 dan `detail_transaksi.txt` dari 5 baris menjadi 0, serta semua alat yang sedang dipinjam tercatat `tersedia`. (b) **E2b**: satu tanggal rusak pada `T003` menghapus `T003` beserta dua detailnya dari file. Tes Skenario 8 dan 9 hanya memeriksa bahwa program tidak error, jadi akibat ini tidak terdeteksi | Sebelum menulis ulang file yang barisnya dilewati, salin dulu file aslinya ke `*.bak` atau pindahkan baris yang dilewati ke `*.rusak.txt`. Lebih baik lagi: jangan tulis ulang di `_keluar()` bila tidak ada perubahan, karena setiap operasi sudah menyimpan sendiri. Jangan hapus data yang bergantung pada baris yang dilewati |
| F2 | Sedang | **Penyimpanan transaksi tidak atomik antara dua file** (E4). `simpan()` menulis `transaksi.txt` lalu `detail_transaksi.txt`. Bila penulisan kedua gagal, `transaksi.txt` sudah memuat `T004` sedangkan `detail_transaksi.txt` belum. Program memuat ulang data dan memulihkan alat, tetapi **tidak menulis ulang `transaksi.txt`**, sehingga file berisi baris yatim dan berbeda dari memori (Aturan 7) sampai ada penyimpanan berikutnya | Pada cabang `except` di `simpan_semua()`, setelah `self.muat()`, panggil juga `self.simpan()` seperti yang sudah dilakukan untuk alat dan mahasiswa |

Catatan: peringatan hanya dicetak ke layar dan disimpan di `FileManager.daftar_peringatan`; tidak masuk ke `log.txt`, sehingga jejak baris yang dibuang hilang begitu terminal ditutup.

## 4. Skalabilitas Program

Reviewer: Faris

Skenario yang dinilai: dari 50 alat dan 100 mahasiswa menjadi 10.000 alat dan 20.000 mahasiswa, serta kebutuhan baru (kategori, jenis pengguna, aturan, denda, database).

### 4.1 Pengukuran (E1)

Data uji: 20.000 mahasiswa, 10.000 alat, 60.000 transaksi selesai dengan 60.000 detail (total file sekitar 6,3 MB), diukur pada container tempat review ini dijalankan. Angka bergantung perangkat dan hanya dipakai untuk membandingkan.

| Operasi | Waktu |
|---|---|
| Memuat semua data saat program mulai | 0,92 dtk |
| Buat satu transaksi | 0,26 dtk |
| Kembalikan satu alat | 0,25 dtk |
| Tambah satu mahasiswa | 0,03 dtk |
| `alat_punya_riwayat`, `_jumlah_aktif` | kurang dari 0,003 dtk |
| `alat.tersedia()` | 0,001 dtk, tetapi menu mencetak **10.000 baris** |
| Ambil 20 baris terakhir dari log 300.000 baris (19 MB) | 0,09 dtk |

Kesimpulan: **pada skala yang disebut soal, kecepatan masih dapat diterima.** Setiap operasi menulis ulang file, jadi biayanya naik sebanding dengan jumlah riwayat. Karena transaksi tidak pernah dihapus, riwayat terus bertambah. Dengan perkiraan linear, 10 kali lebih banyak transaksi membuat satu operasi mendekati 2,6 detik, dan mengembalikan 5 alat memanggil `simpan_semua` 5 kali.

### 4.2 Jawaban atas tiga pertanyaan penilaian

**Apakah struktur program cukup mudah dikembangkan?** Untuk kategori alat baru, ya: tidak ada kode yang bergantung pada nama kategori. Untuk aturan baru, kurang: batas 2 transaksi dan 7 hari adalah konstanta global yang diperiksa langsung di `ManagerTransaksi.buat` dan di validasi pemuatan (S2, S3).

**Apakah baca/tulis file masih efisien untuk data sangat besar?** Cukup pada 20.000 mahasiswa dan 10.000 alat (tabel di atas). Tidak pada 10 kali lipat riwayat. Bagian yang pertama kali bermasalah adalah tampilan menu (S4), lalu penulisan ulang total (S5).

**Seberapa mudah text file diganti database?** Cukup mudah. Data sudah berada di dictionary dan manager hanya berhubungan dengan penyimpanan lewat `muat()` dan `simpan()` (empat tempat) serta `FileManager`. Yang ikut berubah: `dari_baris`/`ke_baris` pada model dan `KOLOM_FILE`. Menu dan aturan bisnis hampir tidak perlu berubah.

### 4.3 Temuan

| No | Tingkat | Temuan | Saran |
|---|---|---|---|
| S1 | (informasi) | Hal yang sudah baik: dictionary berkunci NIM, kode alat, dan ID sehingga pencarian O(1). `daftar_detail` berupa list sehingga jumlah alat dinamis. Dependensi diberikan lewat constructor. Konstanta terpusat di `konstanta.py`. Pemulihan saat penyimpanan gagal sudah ada. Tulis atomik per file | Pertahankan |
| S2 | **Tinggi** | **Aturan baru membuat data lama ditolak.** `Transaksi.dari_baris` menolak baris yang selisih `batas_kembali − tgl_pinjam` melebihi `MAKS_HARI_PINJAM` *saat ini*. Percobaan E3: setelah batas diubah dari 7 ke 3 hari, **ketiga transaksi sampel ditolak saat dimuat**, detailnya ikut dilewati, tiga alat berubah menjadi `tersedia`, dan semuanya akan terhapus dari file pada penyimpanan berikutnya (mekanisme sama dengan F1). Aturan yang berubah seharusnya hanya berlaku untuk transaksi baru | Saat memuat, cukup periksa `batas_kembali >= tgl_pinjam`. Terapkan batas hari hanya di `ManagerTransaksi.buat` |
| S3 | Sedang | Jenis pengguna baru, aturan per kategori alat, atau denda memerlukan percabangan di dalam `buat()` dan `kembalikan()`, karena `MAKS_TRANSAKSI_AKTIF` dan `MAKS_HARI_PINJAM` global. Keterlambatan sudah dihitung (`hari_terlambat`) tetapi hanya untuk tampilan dan log | Kumpulkan aturan dalam satu objek kebijakan, misalnya `KebijakanPeminjaman(maks_aktif, maks_hari, denda_per_hari)`, yang dipilih berdasarkan jenis pengguna |
| S4 | Sedang | **Menu mencetak seluruh daftar tanpa halaman.** `buat_transaksi()` mencetak semua alat tersedia (10.000 baris) sebelum menanyakan NIM, dan `tampilkan_mahasiswa` mencetak 20.000 baris. Pada skala besar menu tidak dapat dipakai | Tambahkan paginasi (misalnya 20 baris per halaman) pada `cetak_daftar`, dan ganti daftar alat di `buat_transaksi` dengan pencarian |
| S5 | Sedang | **Tulis ulang total dan pemindaian linear.** Setiap operasi menulis ulang file terkait. `_keluar()` menulis ulang alat, mahasiswa, transaksi, dan detail lagi walaupun semuanya sudah disimpan. `_jumlah_aktif`, `alat_punya_riwayat`, `mahasiswa_punya_riwayat`, dan `alat_dalam_transaksi_aktif` memindai semua transaksi. `kembalikan` menyimpan tiga file untuk setiap alat | Hapus penyimpanan ganda di `_keluar()`. Tambahkan indeks dict di memori (`nim → daftar transaksi`, himpunan `kode alat yang dipinjam`). Untuk transaksi baru, tulis dengan mode append |
| S6 | Rendah | **ID transaksi melewati `T999`** (E5): `T1000` dibuat dengan benar, tetapi bila ID diurutkan sebagai teks, `T1000` berada sebelum `T999`. Selain itu, `ManagerMahasiswa` dan `ManagerAlat` memiliki `muat`, `simpan`, `_simpan_atau_pulihkan`, dan `_kunci` yang hampir sama (sudah tercatat di refleksi) | Urutkan menurut `int(id[1:])`. Pindahkan pola bersama ke class dasar |

### 4.4 Bagian yang paling sulit dipelihara bila sistem berkembang

1. **`ManagerTransaksi`** menangani pembuatan transaksi, sinkronisasi tiga file (`_selaraskan`), pemeriksaan aturan hapus, dan koordinasi penyimpanan. Ia juga menulis file alat dan mahasiswa milik manager lain.
2. **Aturan yang tersebar:** kondisi menjadi status ada di tiga tempat, dan batas hari di dua (pembuatan dan pemuatan).
3. **`menu.py`** memuat seluruh alur interaksi dalam satu class (277 baris). Aman sekarang, tetapi perlu dipecah per fitur bila menu bertambah.

---

## Rekomendasi Prioritas

1. **F1 dan S2**: jangan menimpa file bila ada baris yang dilewati (buat cadangan atau karantina), batasi `_keluar()` agar tidak menulis ulang tanpa perubahan, dan terapkan batas hari hanya pada transaksi baru. Ini mencegah kehilangan data permanen dan alat yang tercatat tersedia padahal masih dipinjam.
2. **F2**: tambahkan `self.simpan()` pada cabang pemulihan `simpan_semua()`.
3. **S4**: paginasi di menu.
4. **R1, R3, S3**: bersihkan kode mati, satukan aturan kondisi-status, tambahkan docstring, dan kumpulkan aturan peminjaman dalam satu tempat.
5. Lengkapi dokumen: `keputusan_desain.md` (bagian `[ISI TIM]`), `pengujian.md` (isian `........`), dan nama file UML individu.

## Tindak Lanjut

| Temuan | Pemilik yang disarankan | Status |
|---|---|---|
| F1, F2, S5 (bagian `_keluar`) | Arif | `[ ]` |
| S2, S3, S5 (indeks), K3, S6 | Faris | `[ ]` |
| R1, R3, K2 | Rara/Fatimah | `[ ]` |
| S4 (menu), dokumen yang belum final | Arif dan Niken | `[ ]` |

Perubahan setelah menerima hasil review dicatat pada `docs/refleksi.md` (pertanyaan 9).
