# Dokumen Keputusan Desain (DRAF)

Bagian bertanda **[ISI TIM]** hanya dapat dijawab oleh anggota kelompok karena menyangkut jalannya diskusi
7 November. Bagian lain ditulis dari kode dan dokumen yang ada di repository, bukan dari riwayat diskusi.

## 1. Rancangan yang menjadi dasar solusi

**[ISI TIM]** Rancangan anggota mana yang dijadikan dasar, dan mengapa.

Bahan yang ada di repository: `docs/individu/UML_Peminjaman_Lab_K3525038_Project 2.png` (satu UML individu),
`docs/kontrak_antarmodul.md` (usulan pembagian tanggung jawab antarmodul untuk diskusi 7 November), dan
`docs/final/UML_Class_Diagram_Final.drawio` (UML final).

## 2. Bagian yang diambil atau dimodifikasi dari rancangan anggota lain

**[ISI TIM]** Bagian apa saja dari rancangan tiap anggota yang digabungkan atau diubah.

## 3. Alasan memilih struktur class

| Class | Tanggung jawab | Alasan |
|---|---|---|
| `Mahasiswa`, `Alat`, `Transaksi`, `DetailTransaksi` | menyimpan data, memvalidasi satu baris file (`dari_baris`), dan membuat baris file (`ke_baris`) | satu class per entitas; format file diketahui model, bukan manager atau menu |
| `Transaksi` berisi list `DetailTransaksi` | satu transaksi memuat banyak alat | Aturan 3: jumlah dan jenis alat dinamis tanpa variabel terpisah |
| `ManagerMahasiswa`, `ManagerAlat`, `ManagerTransaksi`, `ManagerPengembalian` | menyimpan data di dictionary, menerapkan aturan bisnis, memicu penyimpanan | aturan bisnis terpusat di satu tempat per entitas dan mudah diuji tanpa menu |
| `FileManager` | satu-satunya tempat `open()`, `with`, dan `try-except` | kode baca/tulis tidak berulang; mengganti penyimpanan hanya menyentuh `FileManager` dan `muat`/`simpan` di manager |
| `Logger` | menulis `log.txt` dengan mode append | Tantangan D dipisah agar kegagalan log tidak menggagalkan operasi |
| `AplikasiPeminjaman` (`menu.py`) | tampilan dan alur input | tanpa logika bisnis; menampilkan `ValueError` sebagai `[DITOLAK]` |
| `validasi.py`, `konstanta.py` | fungsi validasi dan nilai tetap | tidak ada string status, kondisi, atau aturan yang ditulis berulang |

Dictionary dipakai dengan kunci NIM, kode alat, dan ID transaksi: pencarian O(1) dan duplikat langsung terdeteksi
(Aturan 8). List dipakai untuk `daftar_detail` karena urutan alat dipertahankan.

## 4. Alasan memilih format text file dan pemisah

- Satu baris satu data dengan pemisah `|`: mudah diurai dengan `split()` dan `join()` (soal melarang `json`, `csv`,
  dan `pickle`), dan `|` jarang muncul di nama atau kategori. Nilai yang mengandung `|` atau baris baru ditolak.
- Nilai kosong ditulis `-` agar jumlah kolom selalu tetap, sehingga baris yang kolomnya tidak sesuai mudah dikenali.
- `detail_transaksi.txt` terpisah dari `transaksi.txt`: tiap alat punya baris sendiri, sehingga jumlah alat dinamis
  dan pengembalian sebagian (status, kondisi, tanggal per alat) tercatat tanpa mengubah struktur file.
- Tanggal `YYYY-MM-DD`: mudah divalidasi dan dibandingkan sebagai teks.
- Penulisan ulang file memakai file `.tmp` lalu `os.replace`, sehingga kegagalan di tengah penulisan tidak merusak
  file lama.

## 5. Alternatif yang tidak dipilih

| Alternatif | Alasan tidak dipilih |
|---|---|
| Database, `json`, `csv`, `pickle`, `shelve` | dilarang oleh soal |
| Daftar alat dalam satu kolom di `transaksi.txt` | sulit diurai, pengembalian per alat tidak tercatat rapi |
| Menambah baris saja (append) untuk semua perubahan | edit dan hapus tidak dapat dilakukan; hanya `log.txt` memakai append |
| Satu class besar yang memegang semua data dan aturan | tanggung jawab bercampur dan sulit diuji |
| `status_aktif` sebagai penanda manual yang dapat diedit dan memblokir peminjaman | dapat bertentangan dengan transaksi yang sebenarnya (Aturan 7), dan pemblokiran tidak diminta aturan mana pun |

**[ISI TIM]** Tambahkan alternatif lain yang benar-benar dibahas saat diskusi kelompok.

## 6. Keputusan yang diambil setelah analisis kode

| Keputusan | Alasan | Catatan |
|---|---|---|
| Alat atau mahasiswa yang tercatat di transaksi mana pun tidak dapat dihapus | Aturan 8: transaksi harus merujuk NIM dan kode alat yang ada; sebelumnya penghapusan membuat transaksi selesai terbuang saat data dimuat ulang | Lebih ketat dari teks Aturan 6 (hanya transaksi aktif). Alternatif: soft delete |
| `status_aktif` mahasiswa diatur otomatis: `aktif` selama punya transaksi aktif, selain itu `tidak aktif` | Soal menyebut "status aktif peminjaman", dan contoh pada soal cocok dengan bacaan ini (M001 punya pinjaman aktif berstatus `aktif`, M002 tidak punya berstatus `tidak aktif`). Aturan 7: nilai di file harus sama dengan keadaan sebenarnya | **Tafsiran, belum dikonfirmasi ke asisten.** Mengganti default `aktif` pada model `Mahasiswa`; status tidak dapat diedit manual dan tidak memblokir peminjaman |
| Kondisi dan status alat dari file yang bertentangan diperbaiki saat dimuat, dengan peringatan | Aturan 5: alat rusak tidak boleh tersedia | `rusak berat` dengan status `tersedia` menjadi `tidak tersedia` |
| `batas_kembali` dari file harus 0 sampai 7 hari setelah `tgl_pinjam` | batas pengembalian maksimal 7 hari | baris di luar rentang dilewati dengan peringatan |
| Keterlambatan dihitung, ditampilkan, dan dicatat di log | keterlambatan pengembalian termasuk masalah yang disebut soal | belum ada denda |
| Kondisi alat dipulihkan bila penyimpanan pengembalian gagal | Aturan 7: memori dan file harus sama | `simpan_semua` memuat ulang data, lalu kondisi alat dikembalikan |
