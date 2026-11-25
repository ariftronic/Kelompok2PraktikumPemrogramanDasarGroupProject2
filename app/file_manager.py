import os
from app.konstanta import DIR_DATA, DIR_KARANTINA, PEMISAH, NILAI_KOSONG, JUMLAH_KOLOM, FILE_LOG

class FileManagerError(Exception):
    """Kesalahan saat membaca atau menulis file."""
    pass

class FileManager:
    """Satu-satunya class yang membuka file; manager lain membaca dan menulis lewat class ini."""

    def __init__(self, direktori=DIR_DATA):
        self.direktori = direktori
        self.daftar_peringatan = []
        self.jumlah_karantina = 0

    def path_file(self, nama_file):
        """Path lengkap file di dalam folder milik FileManager ini."""
        return os.path.join(self.direktori, nama_file)

    def pastikan_file(self, nama_file):
        """Membuat folder dan file kosong bila belum ada, lalu mengembalikan path-nya."""
        path = self.path_file(nama_file)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                with open(path, 'a', encoding='utf-8'):
                    pass
        except OSError as e:
            raise FileManagerError("Tidak dapat menyiapkan file '%s': %s" % (nama_file, e))
        return path

    def pastikan_semua_file(self):
        """Menyiapkan semua file data dan file log."""
        for nama_file in list(JUMLAH_KOLOM) + [FILE_LOG]:
            self.pastikan_file(nama_file)

    def catat_peringatan(self, sumber, pesan):
        """Menyimpan dan menampilkan peringatan yang muncul saat data dimuat."""
        teks = '[PERINGATAN] %s: %s' % (sumber, pesan)
        self.daftar_peringatan.append(teks)
        print(teks)

    def karantina(self, nama_file, baris, alasan):
        """Menyalin baris yang dilewati ke folder karantina agar tidak hilang saat file ditulis ulang."""
        self.tambah_baris(os.path.join(DIR_KARANTINA, nama_file), baris)
        self.jumlah_karantina += 1
        self.catat_peringatan(nama_file, '%s; baris dilewati dan dipindahkan ke %s/%s: %s' % (alasan, DIR_KARANTINA, nama_file, baris))

    def baca_karantina(self, nama_file):
        """Isi karantina sebuah file data, atau list kosong bila belum pernah ada baris yang dikarantina."""
        nama = os.path.join(DIR_KARANTINA, nama_file)
        if not os.path.exists(self.path_file(nama)):
            return []
        return self.baca_teks(nama)

    def _baca_mentah(self, nama_file):
        path = self.pastikan_file(nama_file)
        hasil = []
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                for nomor, baris in enumerate(f, start=1):
                    teks = baris.strip()
                    if teks:
                        hasil.append((nomor, teks))
        except (OSError, UnicodeDecodeError) as e:
            raise FileManagerError("Tidak dapat membaca file '%s': %s" % (nama_file, e))
        return hasil

    def baca_teks(self, nama_file):
        """Semua baris tidak kosong dari sebuah file, tanpa dipecah per kolom."""
        return [teks for _, teks in self._baca_mentah(nama_file)]

    def baca_baris(self, nama_file, jumlah_kolom=None):
        """Membaca file data per kolom; baris yang tidak sesuai format dikarantina."""
        if jumlah_kolom is None:
            jumlah_kolom = JUMLAH_KOLOM.get(nama_file)
        hasil = []
        for nomor, teks in self._baca_mentah(nama_file):
            kolom = [k.strip() for k in teks.split(PEMISAH)]
            if jumlah_kolom is not None and len(kolom) != jumlah_kolom:
                self.karantina(nama_file, teks, 'baris %d tidak sesuai format (ada %d kolom, seharusnya %d)' % (nomor, len(kolom), jumlah_kolom))
                continue
            if '' in kolom:
                self.karantina(nama_file, teks, 'baris %d tidak sesuai format (ada kolom kosong)' % nomor)
                continue
            hasil.append(kolom)
        return hasil

    @staticmethod
    def periksa_nilai(nilai):
        """Mengubah satu nilai menjadi teks kolom; nilai kosong ditulis '-'."""
        teks = NILAI_KOSONG if nilai is None else str(nilai).strip()
        if teks == '':
            teks = NILAI_KOSONG
        if PEMISAH in teks or '\n' in teks or '\r' in teks:
            raise ValueError("Data tidak boleh mengandung karakter '%s' atau baris baru: %r" % (PEMISAH, teks))
        return teks

    def _susun_baris(self, nama_file, baris):
        if isinstance(baris, str):
            if '\n' in baris or '\r' in baris:
                raise ValueError('Satu baris data tidak boleh mengandung baris baru.')
            nilai = baris.split(PEMISAH)
        else:
            nilai = list(baris)
        kolom = [self.periksa_nilai(v) for v in nilai]
        jumlah = JUMLAH_KOLOM.get(nama_file)
        if jumlah is not None and len(kolom) != jumlah:
            raise ValueError('File %s memerlukan %d kolom, bukan %d: %s' % (nama_file, jumlah, len(kolom), kolom))
        return PEMISAH.join(kolom)

    def _tulis_atomik(self, daftar):
        # Semua isi ditulis ke file .tmp dulu. File lama baru diganti setelah semua .tmp berhasil,
        # sehingga kegagalan di tengah jalan tidak mengubah file mana pun.
        sementara = []
        try:
            for nama_file, teks_baris in daftar:
                path = self.path_file(nama_file)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                sementara.append(path + '.tmp')
                with open(path + '.tmp', 'w', encoding='utf-8', newline='\n') as f:
                    for teks in teks_baris:
                        f.write(teks + '\n')
            for (nama_file, _), path_sementara in zip(daftar, sementara):
                os.replace(path_sementara, self.path_file(nama_file))
        except OSError as e:
            for path_sementara in sementara:
                try:
                    if os.path.isfile(path_sementara):
                        os.remove(path_sementara)
                except OSError:
                    pass
            raise FileManagerError("Tidak dapat menulis file '%s': %s" % (', '.join((n for n, _ in daftar)), e))

    def tulis_banyak(self, daftar_isi):
        """Menulis ulang beberapa file data sekaligus; bila satu gagal, tidak ada file yang berubah."""
        daftar = [(nama_file, [self._susun_baris(nama_file, b) for b in daftar_baris]) for nama_file, daftar_baris in daftar_isi]
        self._tulis_atomik(daftar)

    def tulis_baris(self, nama_file, daftar_baris):
        """Menulis ulang satu file data."""
        self.tulis_banyak([(nama_file, daftar_baris)])

    def tulis_teks(self, nama_file, daftar_baris):
        """Menulis teks bebas apa adanya (misalnya laporan), lalu mengembalikan path file."""
        for baris in daftar_baris:
            if '\n' in baris or '\r' in baris:
                raise ValueError('Satu baris teks tidak boleh mengandung baris baru.')
        self._tulis_atomik([(nama_file, list(daftar_baris))])
        return self.path_file(nama_file)

    def tambah_baris(self, nama_file, teks):
        """Menambahkan satu baris di akhir file (mode append)."""
        path = self.pastikan_file(nama_file)
        satu_baris = ' '.join(str(teks).splitlines()).strip()
        try:
            with open(path, 'a', encoding='utf-8', newline='\n') as f:
                f.write(satu_baris + '\n')
        except OSError as e:
            raise FileManagerError("Tidak dapat menambah baris ke '%s': %s" % (nama_file, e))
