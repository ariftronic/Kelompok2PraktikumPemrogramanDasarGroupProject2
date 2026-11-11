"""Menjalankan sembilan skenario wajib Proyek II lewat `python main.py` sungguhan.

Pemakaian (dari folder proyek):  python tests/skenario_wajib.py

Skrip bekerja pada salinan sementara proyek (folder data/ asli tidak disentuh), memeriksa hasilnya, lalu menulis
ulang docs/bukti_eksekusi_skenario.md. Berkas ini sengaja tidak bernama test*.py agar tidak ikut `python -m unittest`.
"""
import datetime
import itertools
import os
import shutil
import subprocess
import sys
import tempfile

if __name__ != '__main__':
    raise ImportError('tests/skenario_wajib.py adalah skrip. Jalankan dengan: python tests/skenario_wajib.py')

PROYEK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_MD = os.path.join(PROYEK, 'docs', 'bukti_eksekusi_skenario.md')
TMP = tempfile.mkdtemp()
DATA = ('mahasiswa.txt', 'alat.txt', 'transaksi.txt', 'detail_transaksi.txt')
SEMUA_FILE = DATA + ('log.txt',)
HARI_INI = datetime.date.today()
TGL = HARI_INI.strftime('%Y-%m-%d')
BATAS = (HARI_INI + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
MD = []
RINGKAS = []


def versi_kode():
    try:
        hash_ = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=PROYEK, capture_output=True, text=True, timeout=30).stdout.strip()
        kotor = subprocess.run(['git', 'status', '--porcelain', '--', 'app', 'main.py'], cwd=PROYEK, capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 'tidak diketahui (git tidak tersedia)'
    if not hash_:
        return 'tidak diketahui (bukan repository git)'
    return '`%s`%s' % (hash_, ' ditambah perubahan yang belum di-commit' if kotor else '')


def proyek_baru(nama):
    dst = os.path.join(TMP, nama)
    os.makedirs(dst)
    shutil.copytree(os.path.join(PROYEK, 'app'), os.path.join(dst, 'app'), ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy(os.path.join(PROYEK, 'main.py'), dst)
    return dst


_CTR = itertools.count(1)


def salin(dst, nama):
    baru = os.path.join(TMP, '%s_%d' % (nama, next(_CTR)))
    shutil.copytree(dst, baru)
    return baru


def jalan(dst, masukan):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, 'main.py'], cwd=dst, input='\n'.join(masukan) + '\n', capture_output=True,
                       text=True, encoding='utf-8', timeout=120, env=env)
    return r.returncode, r.stdout, r.stderr


def isi(dst, nama):
    p = os.path.join(dst, 'data', nama)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return f.read()


def semua(dst):
    return tuple(isi(dst, n) for n in DATA)


def baris_file(dst, nama):
    return (isi(dst, nama) or '').splitlines()


def tag(out, *tags):
    hasil = []
    for baris in out.splitlines():
        for t in tags:
            if t in baris:
                hasil.append(baris[baris.index(t):].strip())
                break
    return hasil


def blok_dari(out, penanda, ke=-1, maks=20):
    baris = out.splitlines()
    idx = [i for i, b in enumerate(baris) if penanda in b]
    if not idx:
        return ['(tidak ditemukan: %s)' % penanda]
    i = idx[ke]
    hasil = [baris[i][baris[i].index(penanda):].strip()]
    for lanjut in baris[i + 1:i + 1 + maks]:
        if lanjut.startswith('-----'):
            continue
        if not lanjut.strip() or lanjut.startswith('='):
            break
        hasil.append(lanjut.rstrip())
    return hasil


def tanpa_error(*hasil):
    return all('Traceback' not in o and 'Traceback' not in e for _, o, e in hasil)


def h(teks=''):
    MD.append(teks)


def kode(isi_blok):
    if isinstance(isi_blok, list):
        baris = isi_blok
    else:
        baris = (isi_blok if isi_blok is not None else '(file tidak ada)').rstrip('\n').split('\n')
    if baris == ['']:
        baris = ['(kosong)']
    MD.append('```text')
    MD.extend(baris)
    MD.append('```')


def selesai(no, judul, cek):
    lulus = all(ok for _, ok in cek)
    h('**Pemeriksaan otomatis**')
    h()
    for ket, ok in cek:
        h('- [%s] %s' % ('x' if ok else ' ', ket))
    h()
    h('**Hasil: %s**' % ('LULUS' if lulus else 'GAGAL'))
    h()
    h('---')
    h()
    RINGKAS.append((no, judul, lulus, len(cek), [k for k, ok in cek if not ok]))


def tidak_ganda(daftar_baris):
    kunci = [b.split('|')[0] for b in daftar_baris]
    return len(kunci) == len(set(kunci))


# ===================== Skenario 1 =====================
P = proyek_baru('utama')
m1 = ['1', '1', 'M001', 'Andi Pratama', '081234567890', '1', 'M002', 'Budi Santoso', '085612345678',
      '1', 'M003', 'Citra Lestari', '', '5', '0',
      '2', '1', 'A001', 'Kamera Digital', 'perangkat multimedia', '',
      '1', 'A002', 'Tripod', 'perangkat multimedia', '',
      '1', 'A003', 'Kabel LAN', 'perangkat jaringan', '',
      '1', 'A004', 'Laptop', 'perangkat komputasi', '',
      '1', 'A005', 'Kabel HDMI', 'perangkat multimedia', 'baik',
      '5', '0', '0']
r1 = jalan(P, m1)
mhs, alat = isi(P, 'mahasiswa.txt'), isi(P, 'alat.txt')
h('## Skenario 1: Tambah mahasiswa dan alat')
h()
h('**Langkah:** menu 1 (Kelola data mahasiswa) lalu Tambah untuk M001, M002, M003 (M003 tanpa nomor HP); menu 2 (Kelola data alat) lalu Tambah '
  'untuk A001 sampai A005 dari tiga kategori. A004 memakai kategori baru `perangkat komputasi`. Setelah itu program ditutup lewat menu 0.')
h()
h('**Layar (cuplikan):**')
h()
kode(blok_dari(r1[1], 'Daftar mahasiswa (') + [''] + blok_dari(r1[1], 'Daftar alat ('))
h()
h('**Isi `mahasiswa.txt`:**')
h()
kode(mhs)
h()
h('**Isi `alat.txt`:**')
h()
kode(alat)
h()
cek = [
    ('`mahasiswa.txt` berisi 3 baris sesuai masukan, no. HP kosong ditulis `-`',
     mhs == 'M001|Andi Pratama|081234567890|tidak aktif\nM002|Budi Santoso|085612345678|tidak aktif\nM003|Citra Lestari|-|tidak aktif\n'),
    ('`alat.txt` berisi 5 baris, semuanya `baik` dan `tersedia`',
     len(alat.splitlines()) == 5 and all(b.endswith('|baik|tersedia') for b in alat.splitlines())),
    ('kategori baru `perangkat komputasi` tercatat tanpa mengubah kode program', 'A004|Laptop|perangkat komputasi|baik|tersedia' in alat),
    ('tidak ada NIM atau kode alat ganda', tidak_ganda(mhs.splitlines()) and tidak_ganda(alat.splitlines())),
    ('pesan `[OK]` muncul 8 kali (3 mahasiswa + 5 alat)', len(tag(r1[1], '[OK]')) == 8),
    ('program berakhir normal (kode keluar 0, tanpa traceback)', r1[0] == 0 and tanpa_error(r1)),
]
selesai(1, 'Tambah mahasiswa dan alat', cek)

# ===================== Skenario 2 =====================
r2 = jalan(P, ['3', 'M001', 'A001, A002, A003', '4', '8', '0'])
h('## Skenario 2: Peminjaman beberapa alat dalam satu transaksi')
h()
h('**Langkah:** menu 3 (Buat transaksi peminjaman), NIM `M001`, kode alat `A001, A002, A003`; lalu menu 4 (Tampilkan transaksi) dan menu 8 '
  '(Tampilkan alat yang sedang dipinjam).')
h()
h('**Layar (cuplikan):**')
h()
kode(blok_dari(r2[1], '[OK] Transaksi') + [''] + blok_dari(r2[1], 'Alat yang sedang dipinjam ('))
h()
for nama in ('transaksi.txt', 'detail_transaksi.txt', 'alat.txt', 'mahasiswa.txt'):
    h('**Isi `%s`:**' % nama)
    h()
    kode(isi(P, nama))
    h()
alat2 = isi(P, 'alat.txt')
cek = [
    ('`transaksi.txt` berisi satu baris `T001|M001|%s|%s|dipinjam` (batas kembali tepat 7 hari)' % (TGL, BATAS),
     isi(P, 'transaksi.txt') == 'T001|M001|%s|%s|dipinjam\n' % (TGL, BATAS)),
    ('`detail_transaksi.txt` berisi satu baris per alat (3 baris) berstatus `dipinjam`',
     isi(P, 'detail_transaksi.txt') == 'T001|A001|dipinjam|-|-\nT001|A002|dipinjam|-|-\nT001|A003|dipinjam|-|-\n'),
    ('status A001, A002, A003 di file menjadi `dipinjam`; A004 dan A005 tetap `tersedia`',
     all(('%s|' % k) in alat2 for k in ('A001', 'A002', 'A003')) and
     [b.split('|')[4] for b in alat2.splitlines()] == ['dipinjam', 'dipinjam', 'dipinjam', 'tersedia', 'tersedia']),
    ('layar menampilkan `Alat yang sedang dipinjam (3 data)`', 'Alat yang sedang dipinjam (3 data)' in r2[1]),
    ('status aktif M001 menjadi `aktif` di file', 'M001|Andi Pratama|081234567890|aktif' in isi(P, 'mahasiswa.txt')),
    ('program berakhir normal', r2[0] == 0 and tanpa_error(r2)),
]
selesai(2, 'Peminjaman beberapa alat dalam satu transaksi', cek)

# ===================== Skenario 3 =====================
sebelum = semua(P)
r3 = jalan(P, ['3', 'M002', 'A001', '3', 'M002', 'A004, A001', '3', 'M999', 'A004', '0'])
sesudah = semua(P)
Q = salin(P, 's3_aturan2')
r3b = jalan(Q, ['3', 'M001', 'A004', '3', 'M001', 'A005', '0'])
h('## Skenario 3: Meminjam alat yang tidak tersedia')
h()
h('**Langkah:** menu 3 dengan tiga percobaan: (a) M002 meminjam A001 yang berstatus `dipinjam`; (b) M002 meminjam `A004, A001` (A004 tersedia, '
  'A001 tidak); (c) NIM `M999` yang tidak terdaftar. Keempat file data dibandingkan sebelum dan sesudah. Tambahan (Aturan 2) pada salinan terpisah: '
  'M001 yang sudah punya 1 transaksi aktif membuat transaksi kedua (A004), lalu transaksi ketiga (A005).')
h()
h('**Layar (penolakan):**')
h()
kode(tag(r3[1], '[DITOLAK]', '[OK]'))
h()
h('**Isi file sebelum dan sesudah (jumlah baris dan kesamaan):**')
h()
kode(['%-22s sebelum: %d baris | sesudah: %d baris | identik: %s' % (n, len(sebelum[i].splitlines()), len(sesudah[i].splitlines()), sebelum[i] == sesudah[i])
      for i, n in enumerate(DATA)])
h()
h('**Tambahan, Aturan 2 (salinan terpisah):**')
h()
kode(tag(r3b[1], '[OK]', '[DITOLAK]'))
h()
cek = [
    ('ketiga percobaan ditolak (3 pesan `[DITOLAK]`)', len(tag(r3[1], '[DITOLAK]')) == 3),
    ('pesan penolakan menyebut alat A001 tidak tersedia', any('A001 tidak tersedia' in b for b in tag(r3[1], '[DITOLAK]'))),
    ('tidak ada pesan `[OK]` pada percobaan yang ditolak', not tag(r3[1], '[OK]')),
    ('keempat file data identik byte demi byte sebelum dan sesudah', sebelum == sesudah),
    ('transaksi kedua M001 diterima, transaksi ketiga ditolak karena maksimal 2 transaksi aktif',
     len(tag(r3b[1], '[OK]')) == 1 and any('maksimal 2' in b for b in tag(r3b[1], '[DITOLAK]'))),
    ('setelah penolakan Aturan 2, `transaksi.txt` hanya berisi T001 dan T002', len(baris_file(Q, 'transaksi.txt')) == 2),
    ('program tetap berjalan sampai keluar normal', r3[0] == 0 and r3b[0] == 0 and tanpa_error(r3, r3b)),
]
selesai(3, 'Meminjam alat yang tidak tersedia', cek)

# ===================== Skenario 4 =====================
r4 = jalan(P, ['5', 'T001', 'A001', '1', '7', '8', '4', '0'])
h('## Skenario 4: Pengembalian sebagian')
h()
h('**Langkah:** menu 5 (Proses pengembalian alat), ID `T001`, mengembalikan hanya `A001` dengan kondisi `1` (baik); lalu menu 7 (alat tersedia), '
  'menu 8 (alat sedang dipinjam), dan menu 4 (tampilkan transaksi).')
h()
h('**Layar (cuplikan):**')
h()
kode(blok_dari(r4[1], '[OK] Alat A001') + [''] + blok_dari(r4[1], 'Alat yang tersedia (') + [''] + blok_dari(r4[1], 'Alat yang sedang dipinjam ('))
h()
for nama in ('transaksi.txt', 'detail_transaksi.txt', 'alat.txt'):
    h('**Isi `%s`:**' % nama)
    h()
    kode(isi(P, nama))
    h()
alat4 = isi(P, 'alat.txt').splitlines()
cek = [
    ('status transaksi berubah menjadi `sebagian dikembalikan`', isi(P, 'transaksi.txt') == 'T001|M001|%s|%s|sebagian dikembalikan\n' % (TGL, BATAS)),
    ('`A001` tercatat `dikembalikan|baik|%s` di `detail_transaksi.txt`' % TGL, 'T001|A001|dikembalikan|baik|%s' % TGL in isi(P, 'detail_transaksi.txt')),
    ('A002 dan A003 tetap `dipinjam` di detail dan di `alat.txt`',
     'T001|A002|dipinjam|-|-' in isi(P, 'detail_transaksi.txt') and 'T001|A003|dipinjam|-|-' in isi(P, 'detail_transaksi.txt')
     and alat4[1].endswith('|dipinjam') and alat4[2].endswith('|dipinjam')),
    ('A001 kembali `baik|tersedia`', alat4[0] == 'A001|Kamera Digital|perangkat multimedia|baik|tersedia'),
    ('layar: 3 alat tersedia (A001, A004, A005) dan 2 alat dipinjam (A002, A003)',
     'Alat yang tersedia (3 data)' in r4[1] and 'Alat yang sedang dipinjam (2 data)' in r4[1]),
    ('M001 tetap `aktif` karena transaksinya belum selesai', 'M001|Andi Pratama|081234567890|aktif' in isi(P, 'mahasiswa.txt')),
    ('program berakhir normal', r4[0] == 0 and tanpa_error(r4)),
]
selesai(4, 'Pengembalian sebagian', cek)

# ===================== Skenario 5 =====================
r5 = jalan(P, ['5', 'T001', 'A002, A003', '2', '3', '7', '9', '4', '0'])
h('## Skenario 5: Alat dikembalikan dalam kondisi rusak')
h()
h('**Langkah:** menu 5, ID `T001`, mengembalikan sisa alat `A002, A003`: A002 dengan kondisi `2` (rusak ringan), A003 dengan kondisi `3` (rusak berat). '
  'Lalu menu 7 (alat tersedia), menu 9 (alat rusak), dan menu 4 (tampilkan transaksi). Ini sekaligus menyelesaikan transaksi T001 (tambahan Skenario 4).')
h()
h('**Layar (cuplikan):**')
h()
kode(tag(r5[1], '[OK]', '[DITOLAK]') + [''] + blok_dari(r5[1], 'Alat yang tersedia (') + [''] + blok_dari(r5[1], 'Alat yang rusak ('))
h()
for nama in ('alat.txt', 'detail_transaksi.txt', 'transaksi.txt', 'mahasiswa.txt'):
    h('**Isi `%s`:**' % nama)
    h()
    kode(isi(P, nama))
    h()
alat5 = isi(P, 'alat.txt')
tersedia5 = blok_dari(r5[1], 'Alat yang tersedia (')
rusak5 = blok_dari(r5[1], 'Alat yang rusak (')
cek = [
    ('A002 tercatat `rusak ringan|tidak tersedia`', 'A002|Tripod|perangkat multimedia|rusak ringan|tidak tersedia' in alat5),
    ('A003 tercatat `rusak berat|tidak tersedia`', 'A003|Kabel LAN|perangkat jaringan|rusak berat|tidak tersedia' in alat5),
    ('kondisi dan tanggal pengembalian tercatat di `detail_transaksi.txt`',
     'T001|A002|dikembalikan|rusak ringan|%s' % TGL in isi(P, 'detail_transaksi.txt') and 'T001|A003|dikembalikan|rusak berat|%s' % TGL in isi(P, 'detail_transaksi.txt')),
    ('daftar alat tersedia hanya A001, A004, A005 (A002 dan A003 tidak muncul)',
     tersedia5[0] == 'Alat yang tersedia (3 data)' and not any(('A002' in b or 'A003' in b) for b in tersedia5[1:])),
    ('daftar alat rusak berisi A002 dan A003', rusak5[0] == 'Alat yang rusak (2 data)' and 'A002' in ' '.join(rusak5) and 'A003' in ' '.join(rusak5)),
    ('transaksi T001 menjadi `selesai`', isi(P, 'transaksi.txt') == 'T001|M001|%s|%s|selesai\n' % (TGL, BATAS)),
    ('M001 kembali `tidak aktif` setelah transaksi selesai', 'M001|Andi Pratama|081234567890|tidak aktif' in isi(P, 'mahasiswa.txt')),
    ('program berakhir normal', r5[0] == 0 and tanpa_error(r5)),
]
selesai(5, 'Pengembalian alat rusak ringan dan rusak berat', cek)

# ===================== Skenario 6 =====================
r6a = jalan(P, ['3', 'M002', 'A004', '0'])
sebelum6 = semua(P)
r6b = jalan(P, ['1', '3', 'M002', 'y', '0', '2', '3', 'A004', 'y', '0', '1', '3', 'M001', 'y', '0', '0'])
sesudah6 = semua(P)
r6c = jalan(P, ['1', '1', 'M009', 'Mahasiswa Sementara', '08111111111', '3', 'M009', 'y', '5', '0', '0'])
h('## Skenario 6: Hapus mahasiswa atau alat yang masih punya transaksi aktif')
h()
h('**Langkah:** M002 meminjam A004 (transaksi T002 aktif). Lalu menu 1 > Hapus untuk `M002` (konfirmasi `y`), menu 2 > Hapus untuk alat `A004`, dan '
  'Hapus untuk `M001` (hanya punya riwayat transaksi selesai). Terakhir, sebagai pembanding, menambah `M009` lalu menghapusnya.')
h()
h('**Layar (penolakan):**')
h()
kode(tag(r6b[1], '[DITOLAK]', '[OK]'))
h()
h('**Layar (pembanding, M009 tanpa transaksi):**')
h()
kode(tag(r6c[1], '[OK]', '[DITOLAK]'))
h()
h('**Isi file sebelum dan sesudah percobaan hapus:**')
h()
kode(['%-22s identik: %s' % (n, sebelum6[i] == sesudah6[i]) for i, n in enumerate(DATA)])
h()
h('**Isi `mahasiswa.txt` sesudah semua langkah:**')
h()
kode(isi(P, 'mahasiswa.txt'))
h()
pesan6 = tag(r6b[1], '[DITOLAK]')
cek = [
    ('M002 (transaksi aktif) ditolak dihapus', len(pesan6) == 3 and 'transaksi aktif' in pesan6[0] and 'M002' in pesan6[0]),
    ('alat A004 (sedang dipinjam) ditolak dihapus', 'A004' in pesan6[1] and 'transaksi aktif' in pesan6[1]),
    ('M001 (hanya riwayat) ditolak dihapus agar riwayat transaksi tetap valid (Aturan 8)', 'riwayat' in pesan6[2]),
    ('keempat file data identik sebelum dan sesudah penolakan', sebelum6 == sesudah6),
    ('mahasiswa tanpa transaksi (M009) dapat dihapus, jadi larangan hanya berlaku bila ada transaksi',
     any('M009 dihapus' in b for b in tag(r6c[1], '[OK]')) and 'M009' not in isi(P, 'mahasiswa.txt')),
    ('pinjaman M002 diterima sebelum percobaan hapus', len(tag(r6a[1], '[OK]')) == 1 and 'M002|Budi Santoso|085612345678|aktif' in sebelum6[0]),
    ('program berakhir normal', all(r[0] == 0 for r in (r6a, r6b, r6c)) and tanpa_error(r6a, r6b, r6c)),
]
selesai(6, 'Hapus mahasiswa/alat dengan transaksi aktif', cek)

# ===================== Skenario 7 =====================
r7a = jalan(P, ['3', 'M003', 'A001, A005', '5', 'T003', 'A001', '1', '4', '0'])
awal7 = semua(P)
restart = [jalan(P, ['4', '1', '5', '0', '2', '5', '0', '0']) for _ in range(3)]
akhir7 = semua(P)
h('## Skenario 7: Tutup lalu jalankan ulang program')
h()
h('**Langkah:** M003 meminjam `A001, A005` (T003), lalu hanya A001 dikembalikan sehingga T003 berstatus `sebagian dikembalikan`. Program ditutup (menu 0). '
  'Program dijalankan ulang 3 kali; tiap kali menampilkan transaksi (menu 4), mahasiswa (menu 1 > 5), dan alat (menu 2 > 5), lalu keluar.')
h()
h('**Layar pada jalan ulang ketiga (cuplikan):**')
h()
kode(blok_dari(restart[-1][1], 'Daftar transaksi (', maks=24) + [''] + blok_dari(restart[-1][1], 'Daftar mahasiswa (') + [''] + blok_dari(restart[-1][1], 'Daftar alat ('))
h()
h('**Jumlah baris per file (sesudah penutupan pertama dan sesudah 3 kali jalan ulang):**')
h()
kode(['%-22s %d baris -> %d baris | isi identik: %s' % (n, len(awal7[i].splitlines()), len(akhir7[i].splitlines()), awal7[i] == akhir7[i]) for i, n in enumerate(DATA)])
h()
h('**Isi `transaksi.txt` sesudah jalan ulang:**')
h()
kode(isi(P, 'transaksi.txt'))
h()
cek = [
    ('transaksi T003 masih `sebagian dikembalikan` setelah dijalankan ulang', 'T003|M003|%s|%s|sebagian dikembalikan' % (TGL, BATAS) in isi(P, 'transaksi.txt')),
    ('layar jalan ulang menampilkan T001 `selesai`, T002 `dipinjam`, dan T003 `sebagian dikembalikan`',
     all(s in restart[-1][1] for s in ('T001 | M001', '| selesai', 'T002 | M002', 'T003 | M003', '| sebagian dikembalikan'))),
    ('alat: A001 `tersedia`, A005 `dipinjam`, A004 `dipinjam` (T002)',
     'A001|Kamera Digital|perangkat multimedia|baik|tersedia' in isi(P, 'alat.txt') and 'A005|Kabel HDMI|perangkat multimedia|baik|dipinjam' in isi(P, 'alat.txt')
     and 'A004|Laptop|perangkat komputasi|baik|dipinjam' in isi(P, 'alat.txt')),
    ('jumlah baris dan isi semua file tidak berubah setelah 3 kali jalan ulang (tidak ada data ganda)', awal7 == akhir7),
    ('tidak ada `[PERINGATAN]` pada ketiga jalan ulang', all('[PERINGATAN]' not in r[1] for r in restart)),
    ('tidak ada NIM, kode alat, atau ID transaksi ganda',
     tidak_ganda(baris_file(P, 'mahasiswa.txt')) and tidak_ganda(baris_file(P, 'alat.txt')) and tidak_ganda(baris_file(P, 'transaksi.txt'))),
    ('semua jalan berakhir normal', r7a[0] == 0 and all(r[0] == 0 for r in restart) and tanpa_error(r7a, *restart)),
]
selesai(7, 'Tutup lalu jalankan ulang (termasuk transaksi sebagian)', cek)

# ===================== Skenario 8 =====================
baris8 = []
for nama in SEMUA_FILE:
    for aksi in ('dihapus', 'dikosongkan'):
        W = salin(P, 's8_tmp')
        path = os.path.join(W, 'data', nama)
        if aksi == 'dihapus':
            os.remove(path)
        else:
            open(path, 'w').close()
        k, o, e = jalan(W, ['0'])
        baris8.append((nama, aksi, k, 'Traceback' in o + e, os.path.exists(path), o.count('[PERINGATAN]')))
        shutil.rmtree(W, ignore_errors=True)
X = salin(P, 's8_orphan')
os.remove(os.path.join(X, 'data', 'mahasiswa.txt'))
trx_sebelum = isi(X, 'transaksi.txt')
kx, ox, ex = jalan(X, ['0'])
trx_sesudah = isi(X, 'transaksi.txt')
W = salin(P, 's8_tambah')
os.remove(os.path.join(W, 'data', 'alat.txt'))
k8, o8, e8 = jalan(W, ['2', '1', 'A100', 'Osiloskop', 'pengukuran', '', '0', '0'])
alat8 = isi(W, 'alat.txt')
h('## Skenario 8: File data dihapus atau dikosongkan')
h()
h('**Langkah:** untuk setiap file (`mahasiswa.txt`, `alat.txt`, `transaksi.txt`, `detail_transaksi.txt`, `log.txt`) dilakukan dua percobaan terpisah pada '
  'salinan data dari Skenario 7: file dihapus, lalu file dikosongkan (0 byte). Tiap percobaan menjalankan program dan langsung keluar (menu 0). '
  'Lalu, setelah `alat.txt` dihapus, menambah alat `A100` lewat menu.')
h()
h('| File | Tindakan | Kode keluar | Traceback | File ada setelah dijalankan | Jumlah `[PERINGATAN]` |')
h('|---|---|---|---|---|---|')
for nama, aksi, k, tb, ada, w in baris8:
    h('| `%s` | %s | %d | %s | %s | %d |' % (nama, aksi, k, 'ya' if tb else 'tidak', 'ya' if ada else 'tidak', w))
h()
h('Jumlah `[PERINGATAN]` berbeda-beda karena program membuang baris yang rujukannya hilang (Aturan 8) dan memperbaiki status alat atau mahasiswa '
  'yang bergantung padanya. `log.txt` tidak dirujuk file lain, jadi tidak menimbulkan peringatan.')
h()
h('**Menambah data setelah `alat.txt` dihapus (layar dan isi file):**')
h()
kode(tag(o8, '[PERINGATAN]')[:3] + tag(o8, '[OK]'))
h()
kode(alat8)
h()
h('**Dampak yang perlu diketahui:** baris yang dibuang saat memuat tidak ikut tersimpan lagi. Contoh pada salinan terpisah, `mahasiswa.txt` dihapus '
  'saat masih ada 3 transaksi:')
h()
kode(tag(ox, '[PERINGATAN]')[:3] + ['...', 'transaksi.txt sebelum: %d baris | sesudah program ditutup: %d baris' % (len(trx_sebelum.splitlines()), len((trx_sesudah or '').splitlines()))])
h()
h('Jadi menghapus `mahasiswa.txt` atau `alat.txt` tidak membuat program error, tetapi transaksi yang merujuk data itu hilang dari file. '
  'Salin folder `data/` terlebih dahulu sebelum menguji skenario ini.')
h()
cek = [
    ('semua 10 percobaan berakhir dengan kode keluar 0', all(b[2] == 0 for b in baris8)),
    ('tidak ada traceback pada satupun percobaan', not any(b[3] for b in baris8)),
    ('file yang dihapus dibuat ulang otomatis pada semua percobaan', all(b[4] for b in baris8)),
    ('program tetap dapat dipakai: alat `A100` tersimpan di `alat.txt` yang dibuat ulang',
     k8 == 0 and 'A100|Osiloskop|pengukuran|baik|tersedia' in (alat8 or '') and tanpa_error((k8, o8, e8))),
]
selesai(8, 'File data dihapus atau dikosongkan', cek)

# ===================== Skenario 9 =====================
W = salin(P, 's9')
tambah = {'alat.txt': 'A777|Kolom Kurang|perangkat jaringan\n', 'mahasiswa.txt': 'M777|Terlalu|Banyak|Kolom|tidak aktif|lebih\n',
          'transaksi.txt': 'T777|M001|2026-11-01\n'}
asli9 = {n: baris_file(W, n) for n in tambah}
for n, t in tambah.items():
    with open(os.path.join(W, 'data', n), 'a', encoding='utf-8') as f:
        f.write(t)
k9, o9, e9 = jalan(W, ['2', '5', '0', '2', '1', 'A200', 'Sensor Suhu', 'sensor', '', '0', '0'])
h('## Skenario 9: Baris berformat salah')
h()
h('**Langkah:** pada salinan data ditambahkan secara manual satu baris rusak ke tiga file: `alat.txt` (3 kolom, seharusnya 5), `mahasiswa.txt` '
  '(6 kolom, seharusnya 4), dan `transaksi.txt` (3 kolom, seharusnya 5). Program dijalankan, daftar alat ditampilkan (menu 2 > 5), alat baru '
  '`A200` ditambahkan, lalu program ditutup.')
h()
h('**Baris yang ditambahkan:**')
h()
kode([t.strip() for t in tambah.values()])
h()
h('**Layar (peringatan dan operasi sesudahnya):**')
h()
kode(tag(o9, '[PERINGATAN]') + [''] + blok_dari(o9, 'Daftar alat (', ke=0) + [''] + tag(o9, '[OK]'))
h()
h('**Catatan perilaku:** baris rusak dilewati saat dimuat dan tidak ikut tersimpan. Setelah program menyimpan, baris rusak tersebut hilang dari file '
  '(lihat pemeriksaan di bawah). Bila baris itu masih ingin dipertahankan, salin dulu sebelum menjalankan program.')
h()
h('**Isi `alat.txt` sesudah program ditutup:**')
h()
kode(isi(W, 'alat.txt'))
h()
cek = [
    ('muncul tepat 3 `[PERINGATAN]`, satu untuk tiap baris rusak, lengkap dengan nama file dan nomor baris',
     len(tag(o9, '[PERINGATAN]')) == 3 and all('baris' in b and 'dilewati' in b for b in tag(o9, '[PERINGATAN]'))),
    ('peringatan menyebut ketiga file (`alat.txt`, `mahasiswa.txt`, `transaksi.txt`)',
     all(any(n in b for b in tag(o9, '[PERINGATAN]')) for n in tambah)),
    ('program tetap berjalan: daftar alat tampil dan alat `A200` berhasil ditambahkan',
     'Daftar alat (' in o9 and any('Alat berhasil ditambahkan' in b for b in tag(o9, '[OK]'))),
    ('semua baris valid sebelumnya tetap ada di ketiga file',
     all(all(b in baris_file(W, n) for b in asli9[n]) for n in tambah)),
    ('baris rusak tidak tersimpan kembali ke file', not any(x in (isi(W, n) or '') for n, x in (('alat.txt', 'A777'), ('mahasiswa.txt', 'M777'), ('transaksi.txt', 'T777')))),
    ('`A200` tersimpan di `alat.txt`', 'A200|Sensor Suhu|sensor|baik|tersedia' in isi(W, 'alat.txt')),
    ('program berakhir normal', k9 == 0 and tanpa_error((k9, o9, e9))),
]
selesai(9, 'Baris berformat salah', cek)

# ===================== Penyusunan dokumen =====================
kepala = [
    '# Bukti Eksekusi Skenario Pengujian Wajib',
    '',
    'Dokumen ini berisi hasil menjalankan **`python main.py` sungguhan** untuk kesembilan skenario wajib pada soal Proyek II. Masukan keyboard '
    'diberikan lewat stdin, jadi layar dan isi file di bawah adalah keluaran program yang sebenarnya, bukan hasil ketikan ulang.',
    '',
    '| Item | Isian |',
    '|---|---|',
    '| Tanggal eksekusi | %s |' % TGL,
    '| Lingkungan | Python %s, Windows |' % sys.version.split()[0],
    '| Kode yang diuji | isi `app/` dan `main.py` pada commit %s |' % versi_kode(),
    '| Cara mengulang | `python tests/skenario_wajib.py` dari folder proyek (menulis ulang dokumen ini) |',
    '| Tempat eksekusi | salinan sementara proyek dengan folder `data/` kosong; folder `data/` di repository tidak disentuh |',
    '| Pemeriksaan | tiap skenario memuat daftar pemeriksaan yang dihitung oleh skrip, lalu hasil LULUS/GAGAL ditentukan dari daftar itu |',
    '',
    'Skenario 1 sampai 7 dijalankan berurutan pada data yang sama (data dari skenario sebelumnya dipakai skenario berikutnya). Skenario 8 dan 9 '
    'memakai salinan dari data akhir Skenario 7. Tanggal pinjam pada contoh sama dengan tanggal eksekusi.',
    '',
    '**Yang belum dicakup dokumen ini:** pengujian manual oleh QA dengan tangkapan layar (kolom "Bukti (screenshot)" di `docs/pengujian.md`) dan '
    'review oleh kelompok lain. Dokumen ini dapat dipakai sebagai pembanding hasilnya.',
    '',
    '## Ringkasan',
    '',
    '| No | Skenario | Jumlah pemeriksaan | Hasil |',
    '|---|---|---|---|',
]
for no, judul, lulus, n, gagal in RINGKAS:
    kepala.append('| %d | %s | %d | %s |' % (no, judul, n, 'LULUS' if lulus else 'GAGAL'))
kepala += ['', '---', '']
with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(kepala + MD).rstrip('\n') + '\n')
shutil.rmtree(TMP, ignore_errors=True)
print('Dokumen ditulis:', OUT_MD)
for no, judul, lulus, n, gagal in RINGKAS:
    print('Skenario %d: %s (%d pemeriksaan)%s' % (no, 'LULUS' if lulus else 'GAGAL', n, '' if lulus else ' -> ' + '; '.join(gagal)))
