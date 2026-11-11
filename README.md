# Sistem Pengelolaan Peminjaman Peralatan Laboratorium

Proyek II Praktikum Pemrograman Dasar, Semester 3 Pendidikan Teknik Informatika dan Komputer (PTIK), Universitas Sebelas Maret.
Aplikasi berbasis Python (OOP) dengan penyimpanan permanen menggunakan text file (`.txt`).

> Status: implementasi selesai, memasuki tahap pengujian dan code review (periode pengerjaan 5 sampai 12 November 2026).
> Format file di bawah sesuai dengan implementasi dan UML final (`docs/final/UML_Class_Diagram_Final.drawio`, gambar: `docs/final/UML_Class_Diagram_Final.png`).

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
kembali menjadi tersedia, serta mahasiswa/alat yang masih ada di transaksi aktif atau tercatat dalam riwayat
transaksi tidak dapat dihapus. Status aktif peminjaman mahasiswa diatur otomatis oleh program (`aktif` selama
mahasiswa memiliki transaksi aktif), dan keterlambatan pengembalian dicatat di log.

Alur data: saat program mulai, semua file dibaca dan dimuat ke `list`/`dict`; setiap perubahan (tambah, edit,
hapus, transaksi, pengembalian) langsung ditulis kembali ke file; operasi yang ditolak aturan bisnis tidak
mengubah isi file.

## Cara Menjalankan

Kebutuhan: Python 3.8 atau lebih baru (diuji di Python 3.14), tanpa library tambahan.

```
python main.py
```

Pengujian otomatis (FileManager, Logger, manager, transaksi, menu dengan input berskrip, dan skenario integrasi):

```
python -m unittest -v
```

Bukti menjalankan kesembilan skenario wajib lewat `main.py` (layar dan isi file) ada di `docs/bukti_eksekusi_skenario.md`
dan dapat diulang dengan `python tests/skenario_wajib.py`.

Folder `data/` dan file di dalamnya dibuat otomatis bila belum ada.

Untuk mencoba dengan data contoh (5 mahasiswa, 10 alat, 3 transaksi), salin semua file `.txt` dari `data_sampel/`
ke `data/` sebelum menjalankan program. File yang sudah ada di `data/` akan tertimpa.

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
data_sampel/                  contoh data (5 mahasiswa, 10 alat, 3 transaksi) untuk mencoba program
docs/                         UML (final dan individu), keputusan desain, pengujian, bukti eksekusi skenario, code review, refleksi
tests/                        pengujian otomatis (unittest) dan skrip bukti skenario wajib
```

Pembagian tanggung jawab antarmodul dijelaskan di `docs/kontrak_antarmodul.md`.

## Format Text File

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
- `batas_kembali`: 0 sampai 7 hari setelah `tgl_pinjam` (baris di luar rentang dilewati dengan peringatan)
- `status_aktif` mahasiswa: `aktif` bila punya transaksi aktif, selain itu `tidak aktif` (diatur otomatis; nilai yang tidak sesuai diperbaiki saat dimuat dengan peringatan)
- kondisi alat: `baik`, `rusak ringan`, `rusak berat`
- status alat: `tersedia`, `dipinjam`, `tidak tersedia`
- status transaksi: `dipinjam`, `sebagian dikembalikan`, `selesai`
- status detail transaksi: `dipinjam`, `dikembalikan`

Perilaku pembacaan file: file yang belum ada dibuat otomatis tanpa error, file kosong dianggap tanpa data, dan baris
yang kolomnya tidak sesuai dilewati dengan peringatan `[PERINGATAN]` sehingga program tetap berjalan. Baris yang dilewati
tidak ikut tersimpan ketika program menulis ulang file, jadi salin dulu baris tersebut bila masih diperlukan.

Kapan data dibaca dan ditulis:
- dibaca: sekali saat program mulai (`muat()` pada tiap manager, berurutan alat, mahasiswa, transaksi);
- ditulis ulang utuh ke file terkait: setiap tambah, edit, hapus, transaksi, dan pengembalian (`simpan()`), serta sekali
  lagi saat keluar lewat menu 0;
- ditambahkan di akhir file (mode append): hanya `log.txt`.

Contoh isi (dua baris tiap file, diambil dari `data_sampel/` yang berisi 5 mahasiswa, 10 alat, 3 transaksi; baris log
bersifat contoh format):

```text
# mahasiswa.txt
M001|Andi Pratama|081234567890|aktif
M002|Budi Santoso|081298765432|tidak aktif

# alat.txt
A001|Multimeter Digital|pengukuran|baik|dipinjam
A004|Breadboard|prototyping|rusak ringan|tidak tersedia

# transaksi.txt
T001|M001|2026-11-02|2026-11-09|dipinjam
T003|M003|2026-11-03|2026-11-10|sebagian dikembalikan

# detail_transaksi.txt
T003|A004|dikembalikan|rusak ringan|2026-11-05
T003|A005|dipinjam|-|-

# log.txt
[2026-11-10 10:15] Mahasiswa M001 ditambahkan
[2026-11-10 10:20] Transaksi T001 dibuat oleh M001 (A001, A002)
```

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
