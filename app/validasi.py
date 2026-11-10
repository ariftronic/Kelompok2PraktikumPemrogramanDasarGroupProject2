from app.konstanta import PEMISAH, NILAI_KOSONG, DAFTAR_KONDISI
HURUF_KODE_TAMBAHAN = '-_'

def rapikan(teks):
    if teks is None:
        return ''
    return ' '.join(str(teks).split())

def bersihkan_teks(teks, nama_bidang, wajib=True):
    hasil = rapikan(teks)
    if PEMISAH in hasil:
        raise ValueError("%s tidak boleh mengandung karakter '%s'." % (nama_bidang, PEMISAH))
    if wajib and hasil == '':
        raise ValueError('%s tidak boleh kosong.' % nama_bidang)
    return hasil

def kosong(nilai):
    return nilai is None or rapikan(nilai) == ''

def validasi_nim(nim):
    hasil = bersihkan_teks(nim, 'NIM').upper()
    if ' ' in hasil or not hasil.isascii() or (not hasil.isalnum()) or (not 3 <= len(hasil) <= 20):
        raise ValueError('NIM harus 3-20 karakter huruf/angka tanpa spasi (contoh: M001).')
    return hasil

def validasi_nama(nama):
    hasil = bersihkan_teks(nama, 'Nama')
    if not any((c.isalpha() for c in hasil)):
        raise ValueError('Nama harus memuat huruf.')
    if len(hasil) > 60:
        raise ValueError('Nama maksimal 60 karakter.')
    return hasil

def validasi_no_hp(no_hp):
    hasil = bersihkan_teks(no_hp, 'No. HP', wajib=False)
    if hasil in ('', NILAI_KOSONG):
        return ''
    hasil = hasil.replace(' ', '').replace('-', '')
    angka = hasil[1:] if hasil.startswith('+') else hasil
    if not (angka.isascii() and angka.isdigit() and (8 <= len(angka) <= 15)):
        raise ValueError("No. HP harus 8-15 angka (boleh diawali '+').")
    return hasil

def validasi_kode_alat(kode):
    hasil = bersihkan_teks(kode, 'Kode alat').upper()
    sah = all((c.isascii() and (c.isalnum() or c in HURUF_KODE_TAMBAHAN) for c in hasil))
    if not sah or not any((c.isalnum() for c in hasil)) or (not 2 <= len(hasil) <= 15):
        raise ValueError("Kode alat harus 2-15 karakter huruf/angka/'-'/'_' tanpa spasi (contoh: A001).")
    return hasil

def validasi_nama_alat(nama):
    hasil = bersihkan_teks(nama, 'Nama alat')
    if len(hasil) > 60:
        raise ValueError('Nama alat maksimal 60 karakter.')
    return hasil

def validasi_kategori(kategori):
    hasil = bersihkan_teks(kategori, 'Kategori')
    if len(hasil) > 40:
        raise ValueError('Kategori maksimal 40 karakter.')
    return hasil

def validasi_kondisi(kondisi):
    hasil = rapikan(str(kondisi).lower().replace('_', ' ').replace('-', ' '))
    if hasil not in DAFTAR_KONDISI:
        raise ValueError('Kondisi harus salah satu dari: %s.' % ', '.join(DAFTAR_KONDISI))
    return hasil

def normalisasi_pencarian(teks):
    return rapikan(str(teks).lower().replace('_', ' ').replace('-', ' '))

def cocok_kata_kunci(kata_kunci, *bidang):
    kata = normalisasi_pencarian(kata_kunci).split()
    if not kata:
        return False
    gabungan = ' '.join((normalisasi_pencarian(b) for b in bidang))
    rapat = gabungan.replace(' ', '')
    return all((k in gabungan or k in rapat for k in kata))
