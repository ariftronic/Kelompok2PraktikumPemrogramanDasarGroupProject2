# Dokumen Hasil Pengujian

Proyek II Praktikum Pemrograman Dasar, Kelompok 2. Sistem Pengelolaan Peminjaman Peralatan Laboratorium berbasis text file.

## 1. Riwayat pengujian

| Putaran | Tanggal | Versi | Lingkungan | Cara | Hasil |
|---|---|---|---|---|---|
| 1 | 12 November 2026 | commit `66f7247` | Python 3.14.6, Windows | QA manual oleh Fatimah Az Zahra dan eksekusi `main.py` berskrip | 9 dari 9 skenario lulus; 7 bug ditemukan dan diperbaiki (tabel bagian 5, no. 1-7) |
| 2 | setelah perbaikan hasil review | versi akhir di repository | lihat `docs/bukti_eksekusi_skenario.md` | `python -m unittest` dan `python tests/skenario_wajib.py` | 146 tes otomatis lulus; 9 skenario wajib dan 1 skenario tantangan lulus |

Layar dan isi file dari putaran terakhir ada di `docs/bukti_eksekusi_skenario.md`. Skrip skenario bekerja pada salinan
sementara proyek, jadi folder `data/` di repository tidak berubah saat pengujian.

## 2. Ringkasan skenario wajib

| No | Skenario | Aturan terkait | Hasil |
|----|----------|----------------|-------|
| 1 | Tambah mahasiswa dan alat | Fitur 1, 2 | Lulus |
| 2 | Pinjam beberapa alat dalam satu transaksi | Aturan 3 | Lulus |
| 3 | Pinjam alat yang tidak tersedia | Aturan 1, 2, 7 | Lulus |
| 4 | Pengembalian sebagian | Aturan 4 | Lulus |
| 5 | Pengembalian alat rusak ringan dan rusak berat | Aturan 5 | Lulus |
| 6 | Hapus mahasiswa dengan transaksi aktif | Aturan 6 | Lulus |
| 7 | Tutup lalu jalankan ulang program | Aturan 7, 8 | Lulus |
| 8 | File data dihapus atau dikosongkan | Penyimpanan file | Lulus |
| 9 | Baris file berformat salah | Penyimpanan file | Lulus |
| 10 | Tantangan B, C, dan F (tambahan) | Statistik, pemeliharaan, laporan | Lulus |

## 3. Detail skenario

Skenario 1 sampai 7 dijalankan berurutan pada data yang sama. Skenario 8 dan 9 memakai salinan data akhir Skenario 7.
Tanggal pada contoh di bawah adalah tanggal saat skrip dijalankan (2026-11-25), sehingga batas kembali menjadi 2026-12-02.
Bila skrip dijalankan pada hari lain, tanggal di bukti eksekusi ikut menyesuaikan.

### Skenario 1: Tambah mahasiswa dan alat

Langkah: menu 1 untuk menambah M001 Andi Pratama, M002 Budi Santoso, dan M003 Citra Lestari (tanpa nomor HP). Menu 2 untuk
menambah A001 Kamera Digital, A002 Tripod, A003 Kabel LAN, A004 Laptop, dan A005 Kabel HDMI. A004 memakai kategori baru
`perangkat komputasi`.

Hasil yang diharapkan: setiap data menjadi satu baris berpemisah `|`, tanpa NIM atau kode ganda, dan alat baru berstatus `tersedia`.

Hasil: `mahasiswa.txt` berisi 3 baris (nomor HP kosong ditulis `-`), `alat.txt` berisi 5 baris berstatus `baik|tersedia`,
kategori baru diterima tanpa mengubah kode program, dan pesan `[OK]` muncul 8 kali. Lulus.

### Skenario 2: Peminjaman beberapa alat dalam satu transaksi

Langkah: M001 meminjam `A001, A002, A003` dalam satu transaksi, lalu daftar alat yang dipinjam ditampilkan.

Hasil yang diharapkan: ID transaksi dibuat otomatis, batas kembali 7 hari, satu baris detail per alat, dan status alat menjadi
`dipinjam` di program maupun di file.

Hasil: `transaksi.txt` berisi `T001|M001|2026-11-25|2026-12-02|dipinjam`, `detail_transaksi.txt` berisi 3 baris berstatus
`dipinjam`, A001 sampai A003 menjadi `dipinjam` sedangkan A004 dan A005 tetap `tersedia`, layar menampilkan
`Alat yang sedang dipinjam (3 data)`, dan status aktif M001 menjadi `aktif`. Lulus.

### Skenario 3: Meminjam alat yang tidak tersedia

Langkah: (a) M002 meminjam A001 yang sedang dipinjam; (b) M002 meminjam `A004, A001`; (c) NIM `M999` yang tidak terdaftar.
Tambahan Aturan 2: M001 membuat transaksi kedua, lalu mencoba transaksi ketiga.

Hasil yang diharapkan: transaksi ditolak dan isi file tidak berubah sama sekali.

Hasil: ketiga percobaan ditolak dengan pesan `[DITOLAK]`, tidak ada pesan `[OK]`, dan semua file data identik byte demi byte
sebelum dan sesudah percobaan. Transaksi kedua M001 diterima, transaksi ketiga ditolak karena maksimal 2 transaksi aktif, dan
`transaksi.txt` hanya berisi T001 dan T002. Lulus.

### Skenario 4: Pengembalian sebagian

Langkah: dari T001 (A001, A002, A003) hanya A001 dikembalikan dengan kondisi `baik`.

Hasil yang diharapkan: A001 kembali `tersedia` dengan tanggal kembali terisi, A002 dan A003 tetap `dipinjam`, dan status
transaksi menjadi `sebagian dikembalikan`.

Hasil: detail A001 tercatat `dikembalikan|baik|2026-11-25`, T001 menjadi `sebagian dikembalikan`, layar menampilkan 3 alat
tersedia (A001, A004, A005) dan 2 alat dipinjam (A002, A003), dan M001 tetap `aktif`. Lulus.

### Skenario 5: Alat dikembalikan dalam kondisi rusak

Langkah: sisa alat T001 dikembalikan, A002 dengan kondisi `rusak ringan` dan A003 dengan kondisi `rusak berat`.

Hasil yang diharapkan: kedua alat berstatus `tidak tersedia`, tidak muncul di daftar alat tersedia, dan muncul di daftar alat rusak.

Hasil: A002 tercatat `rusak ringan|tidak tersedia` dan A003 `rusak berat|tidak tersedia`. Daftar alat tersedia hanya A001, A004,
dan A005, sedangkan daftar alat rusak berisi A002 dan A003. T001 menjadi `selesai` dan M001 kembali `tidak aktif`. Lulus.

### Skenario 6: Hapus mahasiswa dengan transaksi aktif

Langkah: M002 meminjam A004 (T002 aktif). Setelah itu dicoba menghapus M002, alat A004, dan M001 (hanya punya transaksi
selesai). Sebagai pembanding, M009 ditambahkan lalu dihapus.

Hasil yang diharapkan: penghapusan ditolak dan data tetap ada di program dan di file.

Hasil: ketiga penghapusan ditolak (`[DITOLAK]`), semua file data identik sebelum dan sesudah, dan M009 yang tidak punya
transaksi berhasil dihapus. Lulus.

### Skenario 7: Tutup lalu jalankan ulang program

Langkah: M003 meminjam `A001, A005` (T003), A001 dikembalikan sehingga T003 `sebagian dikembalikan`, lalu program ditutup dan
dijalankan ulang tiga kali.

Hasil yang diharapkan: semua data dan status sama seperti sebelum ditutup, dan jumlah baris file tidak bertambah.

Hasil: setiap kali dijalankan ulang, T001 `selesai`, T002 `dipinjam`, dan T003 `sebagian dikembalikan`; A001 `tersedia`, A004
dan A005 `dipinjam`. Isi semua file tetap sama setelah tiga kali jalan ulang, tidak ada `[PERINGATAN]`, dan tidak ada NIM,
kode alat, atau ID transaksi ganda. Lulus.

### Skenario 8: File data dihapus atau dikosongkan

Langkah: untuk setiap file (`mahasiswa.txt`, `alat.txt`, `transaksi.txt`, `detail_transaksi.txt`, `pemeliharaan.txt`,
`log.txt`) dilakukan dua percobaan terpisah: file dihapus, lalu file dikosongkan. Setelah `alat.txt` dihapus, alat A100
ditambahkan lewat menu.

Hasil yang diharapkan: tidak ada error, file dibuat ulang otomatis, dan program tetap dapat dipakai.

Hasil: kedua belas percobaan berakhir normal tanpa traceback dan file yang dihapus dibuat ulang. A100 tersimpan di `alat.txt`
yang baru. Saat `mahasiswa.txt` dihapus padahal masih ada 3 transaksi, transaksi itu tidak dimuat karena NIM-nya tidak ada
(Aturan 8), tetapi barisnya tersimpan utuh di `data/karantina/transaksi.txt` dan `data/karantina/detail_transaksi.txt`.
Alat yang sedang dipinjam ditandai `tidak tersedia`, sehingga tidak bisa dipinjam orang lain. Lulus.

### Skenario 9: Baris berformat salah

Langkah: tiga baris rusak ditambahkan secara manual:

```
alat.txt        A777|Kolom Kurang|perangkat jaringan
mahasiswa.txt   M777|Terlalu|Banyak|Kolom|tidak aktif|lebih
transaksi.txt   T777|M001|2026-11-01
```

Lalu program dijalankan, daftar alat ditampilkan, dan alat A200 ditambahkan.

Hasil yang diharapkan: peringatan muncul untuk setiap baris rusak, baris itu dilewati, dan program tetap berjalan.

Hasil: muncul tepat 3 `[PERINGATAN]` lengkap dengan nama file dan nomor baris, daftar alat tampil, dan A200 tersimpan. Ketiga
baris rusak dipindahkan utuh ke `data/karantina/`, semua baris valid tetap ada, dan saat program dijalankan lagi peringatan
tidak muncul lagi. Lulus.

### Skenario 10 (tambahan): Tantangan B, C, dan F

Langkah: pada salinan `data_sampel/`, buka menu 12 (statistik); menu 13 untuk memasukkan A004 ke pemeliharaan, menyelesaikan
pemeliharaan A009, dan menampilkan riwayat; menu 14 untuk membuat ketiga laporan.

Hasil: statistik menampilkan 2 transaksi aktif dan 1 transaksi selesai. A004 masuk pemeliharaan sebagai P003, P002 selesai dan
A009 kembali `baik|tersedia`. Ketiga laporan dibuat di folder `laporan/`, dan laporan alat dipinjam memuat 3 alat beserta
peminjamnya. Data mahasiswa dan transaksi tidak berubah. Lulus.

## 4. Pengujian otomatis

Semua tes dijalankan dengan `python -m unittest -v` dari folder proyek. Setiap tes memakai folder sementara.

| File tes | Jumlah | Yang diuji |
|---|---|---|
| `tests/test_file_manager.py` | 25 | baca/tulis file, file belum ada atau kosong, baris salah format, karantina, `tulis_banyak` yang gagal tanpa mengubah file, `tulis_teks`, log mode append |
| `tests/test_mahasiswa_alat.py` | 27 | tambah, edit, hapus, dan cari mahasiswa/alat; data ganda dikarantina; kategori baru; pencarian per kriteria (Tantangan A); `validasi_tanggal` |
| `tests/test_transaksi.py` | 24 | pembuatan transaksi, Aturan 1-4, pengembalian, kegagalan simpan, urutan transaksi |
| `tests/test_integrasi.py` | 39 | sembilan skenario wajib di tingkat manager, konsistensi antarfile, karantina, status alat arah aman, ID tidak dipakai ulang |
| `tests/test_menu.py` | 15 | alur menu dengan input berskrip, karantina lewat menu, menu 12-14, paginasi, NIM tidak terdaftar |
| `tests/test_pemeliharaan.py` | 8 | Tantangan C: masuk dan selesai pemeliharaan, penolakan, data bertahan setelah dijalankan ulang |
| `tests/test_statistik.py` | 3 | Tantangan B: alat dan mahasiswa tersering, jumlah transaksi aktif dan selesai |
| `tests/test_laporan.py` | 5 | Tantangan F: isi ketiga laporan, NIM tidak terdaftar, laporan tidak mengubah file data |
| Jumlah | 146 | semua lulus (`OK`) |

Sintaks semua file `.py` juga diperiksa dengan `ast.parse(..., feature_version=(3, 8))` agar tetap bisa dijalankan di Python 3.8.

## 5. Daftar bug yang ditemukan dan perbaikannya

| No | Sumber | Deskripsi bug | Modul | Perbaikan | Tes |
|----|--------|---------------|-------|-----------|-----|
| 1 | putaran 1, terkait Skenario 6 | alat atau mahasiswa yang hanya ada di transaksi selesai dapat dihapus, sehingga transaksinya terbuang saat dimuat ulang | `manager_alat`, `manager_mahasiswa` | penghapusan ditolak bila tercatat di riwayat transaksi | `test_alat_dan_mahasiswa_dengan_riwayat_tidak_boleh_dihapus` |
| 2 | putaran 1, terkait Skenario 5 | bila penulisan `transaksi.txt` gagal saat pengembalian, kondisi alat di `alat.txt` tetap berubah | `manager_pengembalian` | penyimpanan semua file dibuat semua-atau-tidak (lihat no. 11) | `test_gagal_simpan_pengembalian_memulihkan_kondisi_alat` |
| 3 | putaran 1 | `status_aktif` mahasiswa tidak pernah berubah | `manager_transaksi` | diatur otomatis dari transaksi aktif | `test_status_aktif_mahasiswa_mengikuti_transaksi_aktif` |
| 4 | putaran 1 | kondisi dan status alat yang bertentangan di file dimuat apa adanya, sehingga alat rusak dapat dipinjam | `manager_transaksi` | disesuaikan saat dimuat, dengan peringatan | `test_status_alat_hanya_dikoreksi_ke_arah_aman` |
| 5 | putaran 1 | `batas_kembali` di file tidak diperiksa | `models/transaksi` | `batas_kembali` tidak boleh sebelum `tgl_pinjam` (lihat no. 12) | `test_batas_kembali_lama_tetap_dimuat_dan_tidak_boleh_mundur` |
| 6 | putaran 1 | keterlambatan pengembalian tidak dideteksi | `manager_pengembalian` | dihitung, ditampilkan, dan dicatat di log | `test_keterlambatan_dihitung_dan_dicatat_di_log` |
| 7 | putaran 1 | menu belum tercakup tes, dan Ctrl+Z/Ctrl+D tampil sebagai `[ERROR]` | `menu` | diperbaiki dan ditambah `tests/test_menu.py` | `test_input_berhenti_di_tengah_isian_tetap_menyimpan_dan_keluar` |
| 8 | review internal (F1) | baris yang dilewati saat dimuat hilang permanen saat file ditulis ulang; menghapus `mahasiswa.txt` lalu keluar menghapus semua transaksi | `file_manager`, semua manager, `menu` | baris dipindahkan ke `data/karantina/` dan file utama langsung disamakan | `test_mahasiswa_txt_hilang_transaksi_masuk_karantina_bukan_terhapus`, `test_file_mahasiswa_dihapus_lalu_keluar_transaksi_tidak_hilang` |
| 9 | review internal (K1) | satu tanggal rusak di transaksi membuat alat yang masih dipegang peminjam menjadi `tersedia` dan bisa dipinjam orang lain | `manager_transaksi` | status alat hanya dikoreksi ke arah aman | `test_baris_transaksi_rusak_tidak_membuat_alat_dipinjam_dua_kali` |
| 10 | pengujian ulang | transaksi baru bisa mendapat ID yang sama dengan transaksi lama yang dilewati | `manager_transaksi` | ID di karantina ikut dihitung saat membuat ID baru | `test_id_transaksi_di_karantina_tidak_dipakai_ulang` |
| 11 | review internal (F2) | penyimpanan transaksi dan detail tidak sekaligus; kegagalan di tengah meninggalkan baris transaksi tanpa detail | `file_manager`, `manager_transaksi` | `tulis_banyak` menulis semua file sementara dulu, baru mengganti file lama | `test_gagal_menulis_detail_tidak_mengubah_file_apa_pun`, `test_tulis_banyak_gagal_tidak_mengubah_file_apa_pun` |
| 12 | review internal (S2) | batas 7 hari diperiksa saat memuat, sehingga perubahan aturan membuat transaksi lama ditolak | `models/transaksi` | batas 7 hari hanya diterapkan saat transaksi dibuat | `test_batas_kembali_lama_tetap_dimuat_dan_tidak_boleh_mundur` |
| 13 | review internal (K2) | tanggal tidak baku seperti `2026-11-2` diterima | `validasi` | tanggal harus persis `YYYY-MM-DD` | `test_validasi_tanggal_menolak_format_tidak_baku`, `test_tanggal_transaksi_tidak_baku_ditolak` |
| 14 | pengujian ulang | alat yang sama bisa tercatat `dipinjam` di dua transaksi aktif bila file diedit manual | `manager_transaksi` | detail kedua dikarantina | `test_alat_dipinjam_di_dua_transaksi_aktif_dikarantina` |
| 15 | review internal (S4, S6) | menu mencetak ribuan baris sekaligus; T1000 tampil sebelum T999 | `menu`, `manager_transaksi` | paginasi 20 baris; urutan menurut nomor ID | `test_daftar_panjang_ditampilkan_per_halaman`, `test_transaksi_diurutkan_menurut_nomor` |
| 16 | review akhir | bila file diedit manual sehingga alat yang sedang diperbaiki berkondisi `baik`, mengedit nama alat itu membuatnya `tersedia` | `manager_alat` | status alat tidak disesuaikan selama alat masih dalam pemeliharaan | `test_edit_alat_yang_sedang_diperbaiki_tidak_membuatnya_tersedia` |

## 6. Kesimpulan

- Skenario wajib lulus: 9 dari 9, ditambah 1 skenario tantangan yang juga lulus.
- Tes otomatis: 146 tes, semuanya lulus.
- Program tidak pernah berhenti dengan traceback, termasuk saat file dihapus, dikosongkan, atau berisi baris rusak.
- Baris yang bermasalah tidak lagi hilang: semuanya tersimpan di `data/karantina/` dan dapat dipulihkan.
