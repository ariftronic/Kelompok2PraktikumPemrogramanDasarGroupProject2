# Refleksi dan Rencana Perbaikan

Kelompok 2, Proyek II Praktikum Pemrograman Dasar.

## 1. Apa kelemahan utama rancangan solusi kelompok kami?

- Setiap perubahan menulis ulang seluruh isi file yang berubah. Untuk 20.000 mahasiswa dan 10.000 alat waktunya masih wajar
  (review internal mengukur sekitar 0,25 detik per transaksi), tetapi biayanya naik terus karena riwayat transaksi tidak pernah dihapus.
- Beberapa pemeriksaan aturan memindai semua transaksi, misalnya jumlah transaksi aktif seorang mahasiswa dan riwayat alat.
- Tidak ada penguncian file. Bila dua program dijalankan bersamaan pada folder `data/` yang sama, keduanya bisa saling menimpa.
- Status turunan (status alat, status transaksi, status aktif mahasiswa) ikut disimpan di file. Program menyesuaikannya saat
  memuat, tetapi bila file diedit manual, status itu bisa berbeda dari keadaan sebenarnya sampai program dijalankan lagi.

## 2. Jika aplikasi ini dikembangkan menjadi sistem nyata, bagian apa yang pertama kali perlu diperbaiki?

1. Penyimpanan: pindah ke database, atau minimal penulisan yang tidak menulis ulang seluruh file dan memakai penguncian.
2. Pengguna dan hak akses: saat ini semua orang yang menjalankan program bisa mengubah semua data. Sistem nyata perlu
   membedakan petugas laboratorium dan mahasiswa.
3. Aturan keterlambatan: keterlambatan sudah dihitung dan dicatat di log, tetapi belum ada denda atau sanksi.

## 3. Apakah terdapat class yang memiliki terlalu banyak tanggung jawab?

Ya, dua class:

- `ManagerTransaksi` membuat transaksi, memuat dan menyelaraskan tiga file (`transaksi.txt`, `detail_transaksi.txt`, dan status
  di `alat.txt` serta `mahasiswa.txt`), memeriksa aturan hapus untuk manager lain, dan mengatur penyimpanan beberapa file.
  Bagian penyelarasan (`_selaraskan`) bisa dipisah menjadi class sendiri.
- `AplikasiPeminjaman` di `menu.py` memuat seluruh alur menu, sekarang sekitar 40 method. Menu sebaiknya dipecah per fitur,
  misalnya menu mahasiswa, menu alat, menu transaksi, dan menu tantangan.

## 4. Apakah struktur data collection yang digunakan sudah tepat?

Sebagian besar sudah. Dictionary berkunci NIM, kode alat, ID transaksi, dan ID pemeliharaan membuat pencarian berdasarkan
kunci tidak perlu memindai data dan langsung menolak kunci ganda. List dipakai untuk `daftar_detail` karena urutan alat dalam
transaksi perlu dipertahankan, dan set dipakai untuk menyimpan ID yang ada di karantina.

Yang kurang: belum ada indeks tambahan. Pemeriksaan seperti "berapa transaksi aktif milik M001" dan "apakah A001 pernah
dipinjam" masih memindai semua transaksi. Dictionary `nim -> daftar transaksi` dan `kode alat -> transaksi aktif` akan
membuat pemeriksaan itu langsung.

## 5. Apakah format text file yang dipilih mudah dibaca, diperbarui, dan dikembangkan?

Mudah dibaca dan diedit manual: satu baris satu data, kolom dipisah `|`, dan kolom kosong ditulis `-`. Bila ada baris yang
salah, program melewatinya, memberi peringatan, dan menyimpan baris itu di `data/karantina/`, jadi baris tersebut bisa
diperbaiki lalu dikembalikan.

Kekurangannya, menambah kolom berarti mengubah `KOLOM_FILE`, method `dari_baris`/`ke_baris` di model, dan semua file lama,
karena file tidak punya baris judul atau nomor versi format. Nilai data juga tidak boleh mengandung karakter `|`.

## 6. Apa kelebihan dan kekurangan penyimpanan menggunakan text file dibandingkan database?

Kelebihan:

- tidak perlu memasang apa pun selain Python;
- isi file bisa diperiksa langsung dengan editor teks;
- sesuai batasan tugas.

Kekurangan:

- tidak ada transaksi atomik yang sebenarnya. Program menulis semua file sementara dulu lalu menggantinya satu per satu,
  sehingga kegagalan saat menulis tidak merusak data, tetapi penggantian beberapa file tetap tidak bisa dilakukan sekaligus;
- tidak ada indeks dan tidak ada bahasa query;
- tidak ada kontrol akses bersamaan;
- makin lambat ketika data makin besar karena file ditulis ulang utuh.

## 7. Apakah terdapat duplikasi kode?

Sebelum review, `ManagerMahasiswa` dan `ManagerAlat` punya `muat`, `simpan`, `_simpan_atau_pulihkan`, dan `_kunci` yang hampir
sama. Bagian itu sekarang dipindah ke `ManagerDasar`.

Duplikasi yang masih tersisa:

- `ManagerTransaksi` dan `ManagerPemeliharaan` sama-sama membuat ID baru dari angka terbesar dan sama-sama membaca ID dari karantina;
- normalisasi kunci (`rapikan(...).upper()`) ditulis di beberapa manager;
- beberapa method menu hanya berbeda judul dan sumber daftar.

## 8. Bagaimana desain struktur class dapat diperbaiki agar lebih scalable?

- Penyimpanan dibuat sebagai antarmuka, misalnya `PenyimpananTeks` dan `PenyimpananDatabase`, sehingga manager tidak perlu
  tahu data disimpan di mana. Saat ini manager hanya berhubungan dengan file lewat `muat()`, `simpan()`, dan `FileManager`,
  jadi perubahan ini tidak menyentuh menu dan aturan bisnis.
- Aturan peminjaman dikumpulkan dalam satu objek kebijakan, misalnya `KebijakanPeminjaman(maks_aktif, maks_hari, denda_per_hari)`,
  yang bisa berbeda per jenis pengguna (mahasiswa, dosen, asisten). Saat ini `MAKS_TRANSAKSI_AKTIF` dan `MAKS_HARI_PINJAM` berlaku global.
- Indeks di memori untuk pemeriksaan yang sering dipakai (lihat jawaban nomor 4).
- `ManagerTransaksi` dan `menu.py` dipecah seperti pada jawaban nomor 3.

## 9. Perubahan apa yang kami lakukan setelah menerima hasil code review?

Hasil review internal (`docs/review_internal.md`) dan perubahan yang dilakukan:

| Temuan | Perubahan |
|---|---|
| F1: baris yang dilewati hilang permanen saat file ditulis ulang | baris dipindahkan ke `data/karantina/`, file utama langsung disamakan, dan peringatan dicatat ke `log.txt` |
| K1: alat yang masih dipinjam bisa berubah menjadi `tersedia` | status alat hanya dikoreksi ke arah aman |
| ID transaksi lama bisa dipakai lagi (ditemukan saat pengujian ulang) | ID di karantina ikut dihitung |
| F2: penyimpanan transaksi dan detail tidak sekaligus | `FileManager.tulis_banyak` menulis semua file sementara dulu |
| S2: batas 7 hari menolak data lama bila aturan berubah | batas 7 hari hanya diterapkan saat transaksi dibuat |
| K2: tanggal tidak baku diterima | tanggal harus persis `YYYY-MM-DD` |
| R1: method model tidak dipakai, aturan kondisi ke status tersebar | manager memakai `tandai_dipinjam`, `tandai_dikembalikan`, dan `status_dari_kondisi` |
| R3: belum ada docstring | class serta method publik di model, manager, `FileManager`, dan `Logger` diberi docstring singkat |
| S4: menu mencetak ribuan baris sekaligus | paginasi 20 baris |
| S6: urutan T1000 sebelum T999 | transaksi diurutkan menurut nomor ID |
| duplikasi manager mahasiswa dan alat | dipindah ke `ManagerDasar` |

Hasil review dari kelompok lain dicatat di `docs/code_review_lintas_kelompok.md` bagian 2, bersama perubahan yang kami lakukan
karena review tersebut.

## Rencana perbaikan solusi

| Prioritas | Perbaikan | Cara | Penanggung jawab |
|---|---|---|---|
| 1 | Indeks di memori | dictionary `nim -> transaksi` dan himpunan kode alat yang sedang dipinjam, diperbarui saat transaksi dibuat dan alat dikembalikan | Faris |
| 2 | Kebijakan peminjaman dan denda | class `KebijakanPeminjaman` per jenis pengguna; denda dihitung dari `hari_terlambat` | Faris dan Niken |
| 3 | Penyimpanan sebagai antarmuka | `FileManager` dijadikan salah satu implementasi penyimpanan, disiapkan untuk database | Arif |
| 4 | Penguncian file | file kunci di folder `data/` agar program tidak dijalankan dua kali bersamaan | Arif |
| 5 | Memecah class besar | penyelarasan data dipisah dari `ManagerTransaksi`; menu dipecah per fitur | Faris dan Arif |
| 6 | Memulihkan baris karantina lewat menu | menu untuk melihat isi `data/karantina/` dan mengembalikan baris yang sudah diperbaiki | Fatimah dan Niken |
