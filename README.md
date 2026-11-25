# Sistem Pengelolaan Peminjaman Peralatan Laboratorium

Proyek II Praktikum Pemrograman Dasar, Kelompok 2, Pendidikan Teknik Informatika dan Komputer (PTIK), Universitas Sebelas Maret.

Aplikasi konsol berbasis Python (OOP) untuk mencatat peminjaman peralatan laboratorium. Semua data disimpan di text file (`.txt`),
jadi data tetap ada setelah program ditutup dan dijalankan lagi.

## Anggota kelompok

| Nama | NIM | Peran |
|---|---|---|
| Muhammad Nur Arif | K3525034 | Koordinator, akses file (`FileManager`), menu utama, log |
| Fatimah Az Zahra | K3525006 | Data mahasiswa dan alat, pencarian alat (Tantangan A), UML |
| Faris Rafiuddin Hannan | K3525058 | Transaksi peminjaman, statistik (Tantangan B) |
| Niken Syafira Zulfarida | K3525038 | Pengembalian, pemeliharaan (Tantangan C), laporan (Tantangan F), pengujian |

## Deskripsi sistem

Laboratorium meminjamkan peralatan kepada mahasiswa. Aplikasi ini mencatat:

- data mahasiswa (NIM, nama, nomor HP, status aktif peminjaman);
- data alat (kode, nama, kategori, kondisi, status); kategori baru bisa langsung dipakai tanpa mengubah kode program;
- transaksi peminjaman, dengan satu transaksi boleh berisi beberapa alat dan batas kembali 7 hari;
- pengembalian alat, boleh sebagian, beserta kondisi dan tanggal kembalinya;
- pemeliharaan alat yang rusak sampai alat itu kembali tersedia.

Aturan bisnis yang dijalankan program:

1. Alat yang tidak tersedia tidak dapat dipinjam.
2. Seorang mahasiswa paling banyak memiliki dua transaksi aktif.
3. Satu transaksi dapat memuat banyak alat (disimpan sebagai list `DetailTransaksi`, bukan variabel terpisah).
4. Pengembalian boleh sebagian; transaksi tetap aktif sampai semua alat kembali.
5. Alat yang kembali dalam kondisi rusak ringan atau rusak berat tidak dihitung sebagai alat tersedia.
6. Mahasiswa atau alat yang masih ada di transaksi aktif tidak dapat dihapus. Program juga menolak penghapusan data yang
   tercatat di riwayat transaksi atau pemeliharaan, supaya rujukan di file transaksi tetap valid (Aturan 8).
7. Data di program dan di file selalu sama; operasi yang ditolak tidak mengubah file.
8. NIM dan kode alat di file transaksi harus ada di file mahasiswa dan alat. ID transaksi, NIM, dan kode alat tidak boleh ganda,
   termasuk setelah program dijalankan ulang.

Status aktif peminjaman mahasiswa diatur program: `aktif` selama mahasiswa masih punya transaksi aktif, selain itu `tidak aktif`.
Keterlambatan pengembalian dihitung, ditampilkan saat alat dikembalikan, dan dicatat di log.

## Menu program

| No | Menu |
|---|---|
| 1 | Kelola data mahasiswa (tambah, edit, hapus, cari, tampilkan) |
| 2 | Kelola data alat (tambah, edit, hapus, cari, tampilkan) |
| 3 | Buat transaksi peminjaman |
| 4 | Tampilkan transaksi |
| 5 | Proses pengembalian alat |
| 6 | Cari transaksi (aktif) berdasarkan mahasiswa |
| 7 | Tampilkan alat yang tersedia |
| 8 | Tampilkan alat yang sedang dipinjam |
| 9 | Tampilkan alat yang rusak |
| 10 | Tampilkan riwayat peminjaman mahasiswa |
| 11 | Lihat log aktivitas |
| 12 | Statistik peminjaman (Tantangan B) |
| 13 | Pemeliharaan alat (Tantangan C) |
| 14 | Ekspor laporan (Tantangan F) |
| 0 | Keluar (semua data disimpan ke file) |

Daftar yang panjang ditampilkan 20 baris per halaman.

## Tantangan yang dikerjakan

| Tantangan | Isi |
|---|---|
| A. Pencarian fleksibel | Cari alat berdasarkan kode, sebagian nama, kategori, atau ketiganya sekaligus (menu 2, lalu Cari alat) |
| B. Statistik peminjaman | Alat yang paling sering dipinjam, mahasiswa yang paling sering meminjam, jumlah transaksi selesai dan aktif |
| C. Pemeliharaan peralatan | Alat rusak dimasukkan ke daftar pemeliharaan, lalu kembali tersedia setelah selesai diperbaiki; disimpan di `pemeliharaan.txt` |
| D. Log aktivitas | Setiap aktivitas ditambahkan di akhir `log.txt` (mode append) |
| F. Ekspor laporan | Laporan alat yang sedang dipinjam, alat yang rusak, dan riwayat seorang mahasiswa, disimpan di folder `laporan/` |

## Cara menjalankan

Kebutuhan: Python 3.8 atau lebih baru, tanpa library tambahan.

```
python main.py
```

Folder `data/` sudah berisi data contoh (5 mahasiswa, 10 alat, 3 transaksi, 2 catatan pemeliharaan). Salinannya ada di
`data_sampel/`. Untuk mengulang dari data contoh, salin semua file `.txt` dari `data_sampel/` ke `data/`. Bila folder atau file
di `data/` belum ada, program membuatnya otomatis.

Menjalankan pengujian:

```
python -m unittest -v
python tests/skenario_wajib.py
```

Perintah pertama menjalankan seluruh tes otomatis. Perintah kedua menjalankan sembilan skenario wajib (ditambah satu skenario
tantangan) lewat `main.py` sungguhan pada salinan sementara proyek, lalu menulis hasilnya ke `docs/bukti_eksekusi_skenario.md`.

## Struktur program

```
main.py                         titik masuk, memanggil menu utama
app/
  konstanta.py                  nama file, pemisah, nama kolom, status, kondisi, batas aturan bisnis
  file_manager.py               FileManager: satu-satunya tempat open() + with + try-except
  logger.py                     Logger: menulis log.txt (append)
  validasi.py                   fungsi validasi input dan tanggal
  menu.py                       AplikasiPeminjaman: tampilan menu dan input (tanpa aturan bisnis)
  models/                       Mahasiswa, Alat, Transaksi, DetailTransaksi, Pemeliharaan
  manager/
    manager_dasar.py            ManagerDasar: muat/simpan bersama untuk mahasiswa dan alat
    manager_mahasiswa.py        ManagerMahasiswa
    manager_alat.py             ManagerAlat (termasuk pencarian Tantangan A)
    manager_transaksi.py        ManagerTransaksi
    manager_pengembalian.py     ManagerPengembalian
    manager_pemeliharaan.py     ManagerPemeliharaan (Tantangan C)
    manager_statistik.py        ManagerStatistik (Tantangan B)
    manager_laporan.py          ManagerLaporan (Tantangan F)
data/                           file data .txt yang dipakai program
data_sampel/                    salinan data contoh
docs/                           UML, rancangan format file, keputusan desain, pengujian, review, refleksi
tests/                          tes otomatis (unittest) dan skrip skenario wajib
```

Pembagian tanggung jawab antarclass dijelaskan di `docs/kontrak_antarmodul.md`, dan diagramnya ada di
`docs/final/UML Implementasi Akhir Kelompok 2.drawio` (gambar: `.drawio.png` dengan nama yang sama).

## Format text file

Satu baris berisi satu data. Kolom dipisahkan tanda `|`, tanpa baris judul. Kolom tanpa nilai ditulis `-`, dan tanggal ditulis
`YYYY-MM-DD`. Nilai data tidak boleh mengandung `|` atau baris baru; program menolaknya saat input.

| File | Kolom | Contoh |
|---|---|---|
| `mahasiswa.txt` | `nim\|nama\|no_hp\|status_aktif` | `M001\|Andi Pratama\|081234567890\|aktif` |
| `alat.txt` | `kode\|nama\|kategori\|kondisi\|status` | `A004\|Breadboard\|prototyping\|rusak ringan\|tidak tersedia` |
| `transaksi.txt` | `id\|nim\|tgl_pinjam\|batas_kembali\|status` | `T003\|M003\|2026-11-03\|2026-11-10\|sebagian dikembalikan` |
| `detail_transaksi.txt` | `id\|kode\|status\|kondisi\|tgl_kembali` | `T003\|A004\|dikembalikan\|rusak ringan\|2026-11-05` |
| `pemeliharaan.txt` | `id\|kode\|tgl_masuk\|tgl_selesai\|status` | `P002\|A009\|2026-11-06\|-\|dalam perbaikan` |
| `log.txt` | teks bebas berstempel waktu | `[2026-11-10 10:20] Transaksi T001 dibuat oleh M001 (A001, A002)` |

Nilai yang diizinkan:

- `status_aktif`: `aktif`, `tidak aktif`
- kondisi alat: `baik`, `rusak ringan`, `rusak berat`
- status alat: `tersedia`, `dipinjam`, `tidak tersedia`
- status transaksi: `dipinjam`, `sebagian dikembalikan`, `selesai`
- status detail transaksi: `dipinjam`, `dikembalikan` (kolom kondisi dan tanggal kembali berisi `-` selama alat masih dipinjam)
- status pemeliharaan: `dalam perbaikan`, `selesai` (tanggal selesai berisi `-` selama masih diperbaiki)
- `batas_kembali` tidak boleh sebelum `tgl_pinjam`; saat transaksi dibuat, batasnya selalu 7 hari setelah tanggal pinjam

Kapan file dibaca dan ditulis:

- Saat program mulai, semua file dibaca sekali lalu dimuat ke dictionary (berurutan: alat, mahasiswa, transaksi, pemeliharaan).
- Setiap tambah, edit, hapus, transaksi, pengembalian, dan pemeliharaan langsung menulis ulang file yang berubah. Bila satu
  operasi mengubah beberapa file, semuanya ditulis ke file sementara (`.tmp`) dulu dan baru menggantikan file lama setelah
  semuanya berhasil. Bila gagal, tidak ada file yang berubah.
- Saat keluar lewat menu 0, semua data disimpan sekali lagi.
- `log.txt` hanya ditambah di bagian akhir (mode append).

File yang belum ada dibuat otomatis, dan file kosong dianggap tanpa data. Baris yang tidak sesuai format, berisi data ganda,
atau merujuk data yang tidak ada dilewati dengan peringatan `[PERINGATAN]`. Baris itu dipindahkan ke folder
`data/karantina/` dengan nama file yang sama, sehingga tidak hilang dan bisa diperbaiki lalu dikembalikan secara manual.
Setelah itu file utama langsung ditulis ulang agar sama dengan data di program. Alat yang tercatat `dipinjam` tetapi
transaksinya tidak ada ditandai `tidak tersedia` sampai diperiksa petugas (lewat Edit alat), supaya tidak dipinjam orang lain.

Laporan Tantangan F disimpan di folder `laporan/` dengan nama `alat_dipinjam_<tanggal>.txt`, `alat_rusak_<tanggal>.txt`, dan
`riwayat_<NIM>_<tanggal>.txt`. Contohnya ada di `docs/contoh_laporan/`.

## Dokumen

| Dokumen | Isi |
|---|---|
| `docs/individu/` | UML dan rancangan format text file tiap anggota (Tahap 1) |
| `docs/final/UML Final Hasil Diskusi Kelompok 2.drawio.png` | UML final hasil diskusi kelompok (Tahap 1) |
| `docs/final/UML Implementasi Akhir Kelompok 2.drawio` | UML yang sesuai dengan program akhir |
| `docs/final/Rancangan Format Text File Final Kelompok 2.txt` | rancangan format text file final |
| `docs/keputusan_desain.md` | dokumen keputusan desain dan perubahan dari UML Tahap 1 ke program |
| `docs/kontrak_antarmodul.md` | method yang dipakai antarmodul |
| `docs/pengujian.md` | hasil pengujian, termasuk sembilan skenario wajib |
| `docs/bukti_eksekusi_skenario.md` | layar dan isi file hasil menjalankan skenario lewat `main.py` |
| `docs/review_internal.md` | review kode oleh anggota kelompok sendiri |
| `docs/code_review_lintas_kelompok.md` | hasil cross-group code review |
| `docs/refleksi.md` | jawaban pertanyaan refleksi dan rencana perbaikan |

## Pembagian kontribusi

| Anggota | Modul dan dokumen yang menjadi tanggung jawab |
|---|---|
| Muhammad Nur Arif | `konstanta.py`, `file_manager.py`, `logger.py`, `menu.py`, `main.py`, `tests/test_file_manager.py`, `tests/test_menu.py`, README, kontrak antarmodul |
| Fatimah Az Zahra | `models/mahasiswa.py`, `models/alat.py`, `manager_dasar.py`, `manager_mahasiswa.py`, `manager_alat.py`, `validasi.py`, `tests/test_mahasiswa_alat.py`, UML final, data sampel |
| Faris Rafiuddin Hannan | `models/transaksi.py`, `manager_transaksi.py`, `manager_statistik.py`, `tests/test_transaksi.py`, `tests/test_statistik.py`, `tests/test_integrasi.py`, review internal (skalabilitas) |
| Niken Syafira Zulfarida | `manager_pengembalian.py`, `models/pemeliharaan.py`, `manager_pemeliharaan.py`, `manager_laporan.py`, `tests/test_pemeliharaan.py`, `tests/test_laporan.py`, `tests/skenario_wajib.py`, dokumen pengujian, refleksi |

Riwayat kontribusi tiap anggota dapat dilihat pada histori commit repository ini.
