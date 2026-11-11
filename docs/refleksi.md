# Refleksi

Dokumen ini ditulis dari hasil analisis kode. Jawaban terkait review kelompok lain perlu dilengkapi setelah
cross-group code review dilakukan.

## Kelemahan utama
- Penyimpanan text file menulis ulang seluruh file pada setiap perubahan (`FileManager.tulis_baris`). Untuk
  20.000 mahasiswa dan 10.000 alat, biayanya naik linear terhadap jumlah data pada setiap operasi.
- `ManagerTransaksi` memeriksa riwayat dengan memindai seluruh transaksi (`_jumlah_aktif`,
  `alat_punya_riwayat`), sehingga O(n) per pemeriksaan.
- Tidak ada penguncian file, jadi dua proses yang berjalan bersamaan dapat saling menimpa data.
- Data yang gagal dimuat (baris rusak, rujukan yang hilang, atau duplikat) hanya diberi peringatan lalu dilewati. Karena file
  ditulis ulang utuh pada penyimpanan berikutnya, baris itu hilang dari file. Ini menjaga konsistensi (Aturan 7 dan 8),
  tetapi dapat membuang data yang diedit manual, misalnya bila `mahasiswa.txt` dihapus maka transaksinya ikut terbuang.
- Status turunan (status alat, status transaksi, status aktif mahasiswa) ikut disimpan di file, sehingga dapat tidak
  sinkron bila file diedit manual. Program memperbaikinya saat memuat, tetapi lebih bersih bila data turunan
  dihitung dan tidak disimpan.

## Bagian yang pertama kali perlu diperbaiki
1. Penyimpanan: ganti penulisan ulang total dengan penyimpanan inkremental atau database.
2. Indeks di memori (NIM ke transaksi, kode alat ke transaksi) agar pemeriksaan aturan tidak memindai semua data.
3. Aturan denda keterlambatan. Saat ini keterlambatan baru dihitung dan dicatat di log, belum ada denda.

## Tanggung jawab class
- `ManagerTransaksi` menangani pembuatan transaksi, sinkronisasi antarfile (`_selaraskan`), dan pemeriksaan
  untuk aturan hapus. Bagian sinkronisasi dapat dipisah menjadi class tersendiri bila bertambah besar.
- `menu.py` memuat seluruh alur interaksi dalam satu class. Aman untuk saat ini, tetapi perlu dipecah per fitur.

## Struktur data
Dictionary (kunci NIM, kode alat, ID transaksi) dipilih karena pencarian O(1) dan mencegah duplikasi.
List dipakai untuk `daftar_detail` karena jumlah alat per transaksi dinamis dan urutannya dipertahankan.

## Format text file
Satu baris per data dengan pemisah `|` mudah dibaca dan diedit manual. Kekurangannya, nilai tidak boleh
mengandung `|` atau baris baru, dan tidak ada versi format.

## Text file dibanding database
- Kelebihan: tanpa dependensi, mudah diperiksa, sesuai batasan tugas.
- Kekurangan: tanpa transaksi atomik antarfile, tanpa indeks, tanpa kontrol akses bersamaan, dan lambat pada data besar.
  Kegagalan di antara dua penulisan file ditangani dengan memuat ulang dan memulihkan data, tetapi ini bukan
  jaminan setara database.

## Duplikasi kode
- `ManagerMahasiswa` dan `ManagerAlat` memiliki pola `muat`, `simpan`, `_simpan_atau_pulihkan`, dan `_kunci`
  yang hampir sama. Dapat diekstrak ke class dasar.

## Perubahan setelah analisis kode
- Alat/mahasiswa yang ada di riwayat transaksi tidak dapat dihapus.
- Kondisi alat dipulihkan bila penyimpanan pengembalian gagal.
- Status aktif mahasiswa diatur otomatis mengikuti transaksi aktif (tidak diedit manual dan tidak memblokir
  peminjaman); status yang salah di file diperbaiki saat dimuat, dan dipulihkan bila penyimpanan gagal.
- Ketidakcocokan kondisi dan status alat diperbaiki saat data dimuat.
- Keterlambatan dihitung, ditampilkan, dan dicatat di log.
- Pencarian mahasiswa dan alat di `ManagerTransaksi` dan `ManagerPengembalian` memakai lookup dictionary.
- Scaffolding `importlib` dan `ModulBelumTersedia` di `menu.py` dihapus; manager dibuat langsung.
- `batas_kembali` dari file divalidasi 0 sampai 7 hari setelah `tgl_pinjam` (sesuai aturan maksimal 7 hari).
- `EOFError` (Ctrl+Z/Ctrl+D) saat mengisi input tidak lagi tampil sebagai `[ERROR]`; program menyimpan dan keluar.
- Input No. HP saat menambah mahasiswa boleh dikosongkan, sesuai model `Mahasiswa`.
- Menu kini punya tes otomatis (`tests/test_menu.py`); sebelumnya `menu.py` tidak tercakup tes sama sekali.
- Kesembilan skenario wajib dijalankan lewat `main.py` sungguhan dan hasilnya didokumentasikan di
  `docs/bukti_eksekusi_skenario.md` (skrip: `tests/skenario_wajib.py`).
- `data/mahasiswa.txt` disesuaikan dengan aturan status otomatis supaya program tidak menampilkan peringatan pada
  jalankan pertama setelah repository di-clone.
- UML final (`docs/final/UML_Class_Diagram_Final.drawio`) disesuaikan dengan kode: nama atribut aktual,
  method baru, `FileManagerError`, dan `AplikasiPeminjaman`.
