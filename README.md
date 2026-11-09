# Sistem Pengelolaan Peminjaman Peralatan Laboratorium

Proyek II Praktikum Pemrograman Dasar, Semester 3 Pendidikan Teknik Informatika dan Komputer (PTIK), Universitas Sebelas Maret.
Aplikasi berbasis Python (OOP) dengan penyimpanan permanen menggunakan text file (`.txt`).

> Status: dalam pengembangan (periode pengerjaan 5 sampai 12 November 2026).
> Bagian bertanda *(format awal)* akan disesuaikan dengan UML dan format file final hasil diskusi kelompok.

## Anggota Kelompok (Kelompok 2)

| Anggota | Peran |
|---|---|
| Arif | Koordinator dan penyimpanan file (FileManager, menu utama, logger) |
| Fatimah | Data mahasiswa dan alat |
| Faris | Peminjaman (transaksi) |
| Niken | Pengembalian dan QA |

## Deskripsi Sistem

Laboratorium menyediakan peralatan yang dapat dipinjam mahasiswa. Aplikasi ini mencatat mahasiswa, peralatan,
transaksi peminjaman (satu transaksi boleh berisi beberapa alat), pengembalian alat (boleh sebagian) beserta
kondisinya, dan menjaga seluruh data tetap tersimpan setelah program ditutup.

Aturan bisnis utama: alat yang tidak tersedia tidak dapat dipinjam, maksimal dua transaksi aktif per mahasiswa,
batas pengembalian maksimal 7 hari, alat yang dikembalikan dalam kondisi rusak ringan atau rusak berat tidak
kembali menjadi tersedia, serta mahasiswa/alat yang masih ada di transaksi aktif tidak dapat dihapus.

Alur data: saat program mulai, semua file dibaca dan dimuat ke `list`/`dict`; setiap perubahan (tambah, edit,
hapus, transaksi, pengembalian) langsung ditulis kembali ke file; operasi yang ditolak aturan bisnis tidak
mengubah isi file.

## Cara Menjalankan

Kebutuhan: Python 3.8 atau lebih baru, tanpa library tambahan.

```
python main.py
```

Pengujian otomatis untuk FileManager dan Logger:

```
python -m unittest -v
```

Folder `data/` dan file di dalamnya dibuat otomatis bila belum ada.

## Struktur Program

```
main.py                       titik masuk, hanya memanggil menu utama
app/
  konstanta.py                pemisah, path, nama kolom, string status/kondisi, aturan bisnis
  file_manager.py             satu-satunya tempat open()/with/try-except (baca, tulis, tambah)
  logger.py                   log aktivitas ke log.txt (mode append)
  validasi.py                 helper validasi input
  menu.py                     tampilan menu dan alur interaksi (tanpa logika bisnis)
  models/                     Mahasiswa, Alat, Transaksi, DetailTransaksi
  manager/                    manager_mahasiswa, manager_alat, manager_transaksi, manager_pengembalian
data/                         file penyimpanan (.txt)
docs/                         UML, keputusan desain, pengujian, code review, refleksi
tests/                        pengujian otomatis (unittest)
```

Pembagian tanggung jawab antarmodul dijelaskan di `docs/kontrak_antarmodul.md`.

## Format Text File *(format awal)*

Satu baris mewakili satu data, kolom dipisahkan tanda `|`, tanpa baris judul. Kolom tanpa nilai ditulis `-`.
Tanggal berformat `YYYY-MM-DD`. Karakter `|` dan baris baru tidak boleh ada di dalam nilai data.

| File | Kolom | Contoh |
|---|---|---|
| `mahasiswa.txt` | `NIM\|nama\|no_hp\|status_aktif` | `M001\|Andi Pratama\|081234567890\|aktif` |
| `alat.txt` | `kode\|nama\|kategori\|kondisi\|status` | `A001\|Kamera Digital\|perangkat multimedia\|baik\|dipinjam` |
| `transaksi.txt` | `id\|nim\|tgl_pinjam\|batas_kembali\|status` | `T001\|M001\|2026-11-10\|2026-11-17\|sebagian dikembalikan` |
| `detail_transaksi.txt` | `id\|kode\|status\|kondisi\|tgl_kembali` | `T001\|A001\|dikembalikan\|rusak berat\|2026-11-12` |
| `log.txt` | teks bebas berstempel waktu | `[2026-11-10 10:15] Mahasiswa M001 ditambahkan` |

Nilai yang diizinkan:
- kondisi alat: `baik`, `rusak ringan`, `rusak berat`
- status alat: `tersedia`, `dipinjam`, `tidak tersedia`
- status transaksi: `dipinjam`, `sebagian dikembalikan`, `selesai`
- status detail transaksi: `dipinjam`, `dikembalikan`

Perilaku pembacaan file: file yang belum ada dibuat otomatis tanpa error, file kosong dianggap tanpa data, dan baris
yang kolomnya tidak sesuai dilewati dengan peringatan `[PERINGATAN]` sehingga program tetap berjalan.

## Tantangan yang Dipilih

- Tantangan A: Pencarian Fleksibel (alat berdasarkan kode, sebagian nama, atau kategori)
- Tantangan D: Log Activities (`log.txt`, mode append)

## Pembagian Kontribusi

| Anggota | Kontribusi |
|---|---|
| Arif | Repository dan struktur folder, `konstanta.py`, `file_manager.py`, `logger.py`, `menu.py`, `main.py`, README, pengujian FileManager/Logger, Dokumen Keputusan Desain |
| Fatimah | `models/mahasiswa.py`, `models/alat.py`, `manager_mahasiswa.py`, `manager_alat.py`, `validasi.py`, UML final, data sampel |
| Faris | `models/transaksi.py`, `manager_transaksi.py`, slide presentasi |
| Niken | `manager_pengembalian.py`, pengujian 9 skenario, dokumen refleksi |

Riwayat kontribusi tiap anggota dapat dilihat pada histori commit repository ini.
