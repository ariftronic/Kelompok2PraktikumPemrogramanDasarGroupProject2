# Dokumen Keputusan Desain

Kelompok 2, Proyek II Praktikum Pemrograman Dasar.

Gambar yang dirujuk:

- rancangan individu: `docs/individu/` (UML Arif, Fatimah, Faris, dan Niken);
- UML final hasil diskusi Tahap 1: `docs/final/UML Final Hasil Diskusi Kelompok 2.drawio.png`;
- UML yang sesuai dengan program akhir: `docs/final/UML Implementasi Akhir Kelompok 2.drawio`.

## 1. Rancangan yang menjadi dasar solusi kelompok

UML final hasil diskusi memakai struktur rancangan Arif. Rancangan Fatimah sejak awal hampir sama: `MenuApp`, tiga manager per
entitas (`MahasiswaManager`, `AlatManager`, `TransaksiManager`), `FileHandler` untuk akses file, serta `Transaksi` yang berisi
`DetailTransaksi`.

Alasan rancangan ini dipilih sebagai dasar:

- satu manager untuk satu entitas, sehingga pekerjaan bisa dibagi per anggota dan tiap bagian bisa diuji sendiri;
- akses file dipisah ke satu class, sesuai ketentuan bahwa kode baca/tulis tidak boleh ditulis berulang di setiap menu;
- `Transaksi` memegang list `DetailTransaksi`, sehingga jumlah alat per transaksi tidak dibatasi (Aturan 3) dan pengembalian
  per alat bisa dicatat (Aturan 4).

## 2. Perbandingan rancangan individu

| Aspek | Arif | Fatimah | Faris | Niken |
|---|---|---|---|---|
| Pemegang data dan aturan bisnis | `MahasiswaManager`, `AlatManager`, `TransaksiManager` | sama dengan Arif | tiga manager dengan nama yang sama | satu class `PeminjamanService` |
| Akses file | `FileHandler` | `FileHandler` | `FileManager` | `FileManager`, menyimpan daftar peringatan |
| Isi transaksi | `Transaksi` berisi `DetailTransaksi` | sama | `Transaksi` berisi `DetailTransaksi` | `TransaksiPeminjaman` berisi `ItemPeminjaman` |
| Konversi objek dan baris file | `dari_baris`, `ke_baris` | sama | `from_line`, `to_line` | `dari_baris`, `ke_baris` |
| Proses pengembalian | `TransaksiManager.proses_pengembalian` | sama | `TransaksiManager.kembalikan_alat` | `PeminjamanService.proses_pengembalian` |
| Pemeriksaan hapus (Aturan 6) | `TransaksiManager.hapus_mahasiswa` dan `hapus_alat` | sama | `hapus(nim, trx_mgr)` di manager masing-masing | method hapus di `PeminjamanService` |
| Status aktif mahasiswa | atribut `status_aktif` | sama | `MahasiswaManager.set_status_aktif` | `Mahasiswa.set_status_aktif` |
| Mode append | tidak ada | tidak ada | tidak ada | `FileManager.tambah_baris` |

## 3. Bagian yang diambil atau dimodifikasi dari rancangan anggota lain

Diambil dari rancangan Niken:

- nama dan peran `FileManager` sebagai satu-satunya class yang membuka file, termasuk daftar peringatan untuk baris yang
  dilewati (`daftar_peringatan`, `catat_peringatan`);
- `tambah_baris` untuk menulis dengan mode append, yang dipakai `Logger`;
- alur penyimpanan: data dibaca saat program mulai, ditulis setiap ada perubahan, operasi yang ditolak tidak menyimpan, dan
  semua data disimpan sekali lagi saat keluar;
- `baris_detail()` pada `Transaksi` untuk menyusun isi `detail_transaksi.txt`.

Diambil dari rancangan Faris:

- `daftar_kategori()` pada `ManagerAlat`, dipakai menu saat menambah alat dengan kategori baru;
- `riwayat_mahasiswa(nim)` untuk menu riwayat peminjaman;
- pemeriksaan alat di transaksi aktif (`alat_dipakai_trx_aktif` menjadi `alat_dalam_transaksi_aktif`);
- nama `tandai_dikembalikan(kondisi)` pada `Alat`;
- status aktif mahasiswa yang diatur manager (`set_status_aktif` menjadi `perbarui_status_mahasiswa`).

Dimodifikasi dari rancangan dasar:

- `FileHandler` diganti `FileManager`, mengikuti nama di rancangan Niken dan Faris.
- Pemeriksaan hapus dipindah dari `TransaksiManager` ke `ManagerMahasiswa.hapus` dan `ManagerAlat.hapus`. Keduanya bertanya
  ke `ManagerTransaksi` lewat referensi yang disimpan sekali dengan `sambungkan_transaksi`. Rancangan Faris mengirim `trx_mgr`
  sebagai parameter pada setiap pemanggilan hapus.
- Proses pengembalian dipisah ke class `ManagerPengembalian`. Class ini tidak ada di rancangan individu mana pun; pemisahan ini
  mengikuti pembagian tugas (pengembalian dikerjakan Niken) dan menjaga `ManagerTransaksi` tidak semakin besar.
- `Logger` ditambahkan untuk Tantangan D.

## 4. Alasan memilih struktur class

| Class | Tanggung jawab | Alasan |
|---|---|---|
| `Mahasiswa`, `Alat`, `Transaksi`, `DetailTransaksi`, `Pemeliharaan` | menyimpan data satu baris, memeriksa isi baris (`dari_baris`), dan menyusun baris file (`ke_baris`) | format file cukup diketahui model; manager dan menu tidak perlu tahu urutan kolom |
| `Transaksi` berisi list `DetailTransaksi` | satu transaksi memuat banyak alat | Aturan 3: jumlah dan jenis alat dinamis tanpa variabel terpisah |
| `ManagerDasar` | pola `muat`, `simpan`, `isi_file`, dan `semua` yang sama untuk mahasiswa dan alat | sebelumnya kode ini ditulis dua kali di `ManagerMahasiswa` dan `ManagerAlat` |
| `ManagerMahasiswa`, `ManagerAlat`, `ManagerTransaksi`, `ManagerPengembalian`, `ManagerPemeliharaan` | menyimpan data di dictionary, menjalankan aturan bisnis, dan memicu penyimpanan | aturan bisnis berada di satu tempat per entitas dan bisa diuji tanpa menu |
| `ManagerStatistik`, `ManagerLaporan` | menghitung statistik dan menyusun laporan dari data di memori | hanya membaca data, jadi tidak mengubah file data |
| `FileManager` | satu-satunya tempat `open()`, `with`, dan `try-except`; karantina baris bermasalah; penulisan beberapa file sekaligus | kode baca/tulis tidak berulang, dan bila penyimpanan diganti database cukup bagian ini dan `muat`/`simpan` di manager yang berubah |
| `Logger` | menulis `log.txt` dengan mode append | kegagalan menulis log tidak menggagalkan operasi utama |
| `AplikasiPeminjaman` (`menu.py`) | tampilan menu dan alur input | tidak berisi aturan bisnis; penolakan dari manager (`ValueError`) ditampilkan sebagai `[DITOLAK]` |
| `validasi.py`, `konstanta.py` | fungsi validasi dan nilai tetap | string status, kondisi, dan batas aturan tidak ditulis berulang |

Dictionary dipakai dengan kunci NIM, kode alat, ID transaksi, dan ID pemeliharaan. Pencarian berdasarkan kunci tidak perlu
memindai semua data, dan kunci ganda langsung ketahuan (Aturan 8). List dipakai untuk `daftar_detail` karena urutan alat dalam
satu transaksi perlu dipertahankan.

## 5. Alasan memilih format text file dan pemisah

- Satu baris untuk satu data, dengan pemisah `|`. Formatnya mudah diurai dengan `split()` dan `join()` (soal melarang `json`,
  `csv`, dan `pickle`), dan `|` hampir tidak pernah muncul di nama atau kategori. Input yang mengandung `|` atau baris baru ditolak.
- Kolom kosong ditulis `-` agar jumlah kolom selalu tetap, sehingga baris yang kolomnya kurang atau lebih mudah dikenali.
- `detail_transaksi.txt` dipisah dari `transaksi.txt`. Setiap alat punya baris sendiri, jadi jumlah alat bebas dan status,
  kondisi, serta tanggal kembali tercatat per alat.
- Tanggal ditulis `YYYY-MM-DD` dan bentuk lain (misalnya `2026-11-2`) ditolak, sehingga tanggal bisa dibandingkan dan diurutkan.
- Penulisan memakai file sementara `.tmp` lalu `os.replace`. Bila satu operasi menyimpan beberapa file, semua file sementara
  ditulis dulu dan baru menggantikan file lama setelah semuanya berhasil.
- Baris yang dilewati saat memuat dipindahkan ke `data/karantina/` dengan format yang sama, sehingga bisa diperbaiki lalu
  dikembalikan ke file asalnya.

## 6. Alternatif yang sempat dipertimbangkan tetapi tidak dipilih

| Alternatif | Asal | Alasan tidak dipilih |
|---|---|---|
| Satu class service yang memegang semua data dan aturan | rancangan Niken | tanggung jawab bercampur dalam satu class, sulit dibagi per anggota dan sulit diuji per bagian |
| Nama `from_line` dan `to_line` | rancangan Faris | kelompok memakai nama berbahasa Indonesia agar seragam dengan nama lain di program |
| Mengirim `trx_mgr` sebagai parameter setiap kali menghapus | rancangan Faris | referensi cukup disimpan sekali, sehingga pemanggil hapus tidak perlu tahu `ManagerTransaksi` |
| Daftar alat ditulis dalam satu kolom di `transaksi.txt` | diskusi format file | sulit diurai, dan pengembalian per alat tidak tercatat rapi |
| Semua perubahan hanya ditambahkan di akhir file (append) | diskusi format file | edit dan hapus tidak bisa dilakukan; hanya `log.txt` yang memakai append |
| Database, `json`, `csv`, `pickle`, `shelve` | | dilarang oleh soal |
| `status_aktif` mahasiswa diisi manual dan memblokir peminjaman | | bisa bertentangan dengan transaksi yang sebenarnya (Aturan 7), dan tidak ada aturan yang meminta pemblokiran |
| Baris rusak dibuang saat file ditulis ulang | perilaku program sebelum review | data hilang permanen, misalnya semua transaksi terhapus ketika `mahasiswa.txt` dihapus |
| Baris rusak dibiarkan di file utama | dipertimbangkan saat memperbaiki masalah di atas | file utama tidak lagi sama dengan data di program (Aturan 7) |

## 7. Perubahan dari UML Tahap 1 ke program akhir

| UML final Tahap 1 | Program akhir | Alasan |
|---|---|---|
| `MenuApp` | `AplikasiPeminjaman` di `menu.py`, dengan method per fitur | menu wajib dan menu tantangan perlu method sendiri agar mudah diuji |
| `MahasiswaManager`, `AlatManager`, `TransaksiManager` | `ManagerMahasiswa`, `ManagerAlat`, `ManagerTransaksi`; dua yang pertama mewarisi `ManagerDasar` | penamaan diseragamkan dan kode muat/simpan yang sama dipindah ke class dasar |
| `FileHandler` (3 method) | `FileManager` dan `FileManagerError` | ditambah pembuatan file otomatis, peringatan, karantina, penulisan beberapa file sekaligus, dan mode append |
| `TransaksiManager.proses_pengembalian` | `ManagerPengembalian.kembalikan` | pengembalian dipisah dari pembuatan transaksi |
| `TransaksiManager.hapus_mahasiswa`, `hapus_alat` | `ManagerMahasiswa.hapus`, `ManagerAlat.hapus` | setiap manager menghapus datanya sendiri dan bertanya ke `ManagerTransaksi` |
| konstanta `FILE`, `MAKS_TRANSAKSI_AKTIF`, `MAKS_HARI` di dalam class | `konstanta.py` | nilai tetap dipakai beberapa modul |
| `get(nim)`, `get(kode)` | `ambil()` (menolak bila tidak ada) dan `cari_berdasarkan_nim()`/`cari_berdasarkan_kode()` (boleh `None`) | pemanggil bisa memilih perilaku saat data tidak ditemukan |
| `Alat.tersedia()`, `terima_kembali()` | `Alat.status_dari_kondisi()`, `tandai_dikembalikan()`, `selesai_diperbaiki()` | aturan kondisi ke status (Aturan 5) berada di model |
| `DetailTransaksi.ke_baris(id_transaksi)` | `DetailTransaksi` menyimpan `id_transaksi` dan `ke_baris()` tanpa parameter | satu baris detail bisa dibaca dan ditulis tanpa objek transaksinya |
| atribut tanggal bertipe `date` | tanggal disimpan sebagai teks `YYYY-MM-DD` dan diperiksa dengan `validasi.validasi_tanggal` | sama dengan isi file, sehingga tidak perlu konversi saat menulis |
| tidak ada | `Logger`, `ManagerStatistik`, `ManagerPemeliharaan`, `Pemeliharaan`, `ManagerLaporan` | Tantangan D, B, C, dan F |

## 8. Keputusan setelah analisis kode dan review internal

| Keputusan | Alasan | Catatan |
|---|---|---|
| Baris yang dilewati saat memuat dipindahkan ke `data/karantina/`, lalu file utama langsung ditulis ulang | sebelumnya baris itu hilang permanen saat file ditulis ulang; menghapus `mahasiswa.txt` membuat semua transaksi terhapus | peringatan juga dicatat ke `log.txt` |
| Status alat hanya dikoreksi ke arah aman: program tidak pernah membuat alat menjadi `tersedia` sendiri | sebelumnya alat yang transaksinya rusak di file berubah menjadi `tersedia` dan bisa dipinjam orang lain padahal masih dipegang peminjam (Aturan 1) | alat yang ditahan dilepas petugas lewat menu Edit alat |
| ID transaksi dan pemeliharaan di karantina tidak dipakai lagi untuk data baru | sebelumnya transaksi baru bisa mendapat ID yang sama dengan transaksi lama yang dilewati (Aturan 8) | |
| Operasi yang mengubah beberapa file ditulis sekaligus lewat `tulis_banyak` | sebelumnya kegagalan di tengah penyimpanan bisa meninggalkan baris transaksi tanpa detail (Aturan 7) | |
| Batas 7 hari hanya diperiksa saat transaksi dibuat; saat memuat cukup diperiksa bahwa `batas_kembali` tidak sebelum `tgl_pinjam` | bila aturan berubah, transaksi lama tetap bisa dimuat | |
| Tanggal yang tidak berformat `YYYY-MM-DD` persis ditolak | `2026-11-2` sebelumnya lolos | |
| Alat atau mahasiswa yang tercatat di transaksi mana pun (juga alat di data pemeliharaan) tidak dapat dihapus | Aturan 8: rujukan di file transaksi harus tetap ada | lebih ketat dari teks Aturan 6 yang hanya menyebut transaksi aktif; ini tafsiran kelompok |
| `status_aktif` mahasiswa diatur otomatis mengikuti transaksi aktif | soal menyebut "status aktif peminjaman", dan contoh pada soal cocok dengan tafsiran ini | tafsiran kelompok; status ini tidak memblokir peminjaman |
| Daftar yang panjang ditampilkan 20 baris per halaman | menu tetap bisa dipakai bila data mencapai ribuan baris | |
