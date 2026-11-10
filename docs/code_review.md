# Code Review

> TEMPLAT. Belum berisi hasil review. Isi setelah cross-group code review dilakukan. Aspek dan skenario
> mengikuti soal Proyek II (Tahap 3). Bagian bertanda **[ISI]** harus diisi oleh pengulas.

## Identitas

| Item | Isian |
|---|---|
| Kelompok pengulas | **[ISI]** |
| Kelompok yang diulas | **[ISI]** |
| Tanggal review | **[ISI]** |
| Repository yang diulas | **[ISI]** |
| Cara menjalankan program yang diulas | **[ISI]** |

## A. Review kami terhadap kelompok lain

Hasil: Ya, Sebagian, atau Tidak. Tulis bukti singkat (nama file, nomor baris, atau langkah yang dicoba).

### 1. Kesesuaian rancangan dan implementasi

| Pemeriksaan | Hasil | Bukti / catatan |
|---|---|---|
| Class pada UML benar-benar diimplementasikan | **[ISI]** | |
| Atribut sesuai rancangan | **[ISI]** | |
| Method sesuai rancangan | **[ISI]** | |
| Hubungan antarclass sesuai implementasi | **[ISI]** | |
| Format text file sesuai rancangan dan README | **[ISI]** | |

### 2. Ketepatan solusi

| Pemeriksaan | Hasil | Bukti / catatan |
|---|---|---|
| Program dapat dijalankan | **[ISI]** | |
| CRUD berfungsi dan hasilnya tersimpan ke file | **[ISI]** | |
| Transaksi peminjaman berjalan benar | **[ISI]** | |
| Status ketersediaan alat diperbarui benar | **[ISI]** | |
| Pengembalian sebagian dapat diproses | **[ISI]** | |
| Aturan bisnis 1 sampai 8 diterapkan | **[ISI]** | |

### 3. Pengelolaan file

| Pemeriksaan | Hasil | Bukti / catatan |
|---|---|---|
| Data dimuat benar saat program dijalankan | **[ISI]** | |
| Isi file selalu sama dengan data di program | **[ISI]** | |
| Tidak error saat file belum ada atau kosong | **[ISI]** | |
| Baris tidak sesuai format ditangani | **[ISI]** | |
| File dibuka dan ditutup dengan `with` | **[ISI]** | |
| Tidak ada data ganda setelah dijalankan berulang | **[ISI]** | |

### 4. Skalabilitas

| Pertanyaan | Penilaian |
|---|---|
| Apakah struktur program mudah dikembangkan untuk 10.000 alat dan 20.000 mahasiswa, kategori baru, jenis pengguna baru, aturan baru, atau denda? | **[ISI]** |
| Apakah cara membaca dan menulis file masih efisien untuk data sangat besar? | **[ISI]** |
| Seberapa mudah text file diganti database tanpa mengubah banyak bagian program? | **[ISI]** |
| Bagian kode mana yang sulit dipelihara bila sistem berkembang? | **[ISI]** |

### Skenario pengujian wajib pada program yang diulas

| No | Skenario | Hasil | Catatan |
|---|---|---|---|
| 1 | Tambah mahasiswa dan alat, periksa file | **[ISI]** | |
| 2 | Pinjam beberapa alat dalam satu transaksi | **[ISI]** | |
| 3 | Pinjam alat yang tidak tersedia (file tidak boleh berubah) | **[ISI]** | |
| 4 | Kembalikan sebagian alat | **[ISI]** | |
| 5 | Kembalikan alat dalam kondisi rusak | **[ISI]** | |
| 6 | Hapus mahasiswa yang masih punya transaksi aktif | **[ISI]** | |
| 7 | Tutup lalu jalankan ulang program | **[ISI]** | |
| 8 | Hapus atau kosongkan salah satu file data | **[ISI]** | |
| 9 | Tambah baris berformat salah secara manual | **[ISI]** | |

### Ringkasan temuan dan saran

**[ISI]**

## B. Hasil review kelompok lain terhadap program kami

| No | Temuan | Aspek | Tingkat | Tindak lanjut | Status |
|---|---|---|---|---|---|
| 1 | **[ISI]** | | | | |

## C. Perubahan setelah menerima review

**[ISI]**

## Bahan skalabilitas program kami

Bagian ini dari analisis kode, bukan hasil review kelompok lain. Boleh dipakai sebagai bahan diskusi.

- **Penyimpanan:** `FileManager.tulis_baris` menulis ulang seluruh file pada setiap perubahan. Satu peminjaman atau
  pengembalian menulis file alat, transaksi, dan detail, serta file mahasiswa bila statusnya berubah.
- **Pemeriksaan aturan:** `_jumlah_aktif`, `mahasiswa_punya_riwayat`, dan `alat_punya_riwayat` memindai seluruh
  transaksi (O(jumlah transaksi)). Pencarian mahasiswa dan alat berdasarkan NIM atau kode memakai dictionary (O(1)).
- **Mengganti dengan database:** titik sambungnya adalah `FileManager` dan pasangan `muat`/`simpan` di tiap manager.
  Format baris (`dari_baris`, `ke_baris`) berada di model, dan `ManagerTransaksi` memuat dua file sekaligus, jadi
  sebagian logika baca tulis masih tersebar di manager.
- **Kategori baru:** tidak perlu mengubah struktur (`ManagerAlat.tambah` menerima kategori baru).
- **Aturan baru atau denda:** angka aturan ada di `konstanta.py`; penerapannya di `ManagerTransaksi.buat` dan
  `ManagerPengembalian.kembalikan`. Keterlambatan sudah dihitung (`hari_terlambat`) tetapi belum ada denda.
- **Jenis pengguna baru:** belum ada konsep peran; hanya `Mahasiswa`.
- **Bagian sulit dipelihara:** `ManagerTransaksi` memegang banyak tanggung jawab (pembuatan transaksi, sinkronisasi
  status alat, mahasiswa, dan transaksi saat memuat, serta pemeriksaan aturan hapus); `menu.py` berupa satu class
  besar; pola `muat`/`simpan` di `ManagerMahasiswa` dan `ManagerAlat` hampir sama (duplikasi).
