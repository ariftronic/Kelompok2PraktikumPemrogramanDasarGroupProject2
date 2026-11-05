import os

from app.konstanta import (
    DIR_DATA, PEMISAH, NILAI_KOSONG, JUMLAH_KOLOM,
    FILE_LOG,
)


class FileManagerError(Exception):
    pass


class FileManager:
    def __init__(self, direktori=DIR_DATA):
        self.direktori = direktori
        self.daftar_peringatan = []

    def path_file(self, nama_file):
        return os.path.join(self.direktori, nama_file)

    def pastikan_file(self, nama_file):
        path = self.path_file(nama_file)
        try:
            os.makedirs(self.direktori, exist_ok=True)
            if not os.path.exists(path):
                with open(path, "a", encoding="utf-8"):
                    pass
        except OSError as e:
            raise FileManagerError("Tidak dapat menyiapkan file '%s': %s" % (nama_file, e))
        return path

    def pastikan_semua_file(self):
        for nama_file in list(JUMLAH_KOLOM) + [FILE_LOG]:
            self.pastikan_file(nama_file)

    def catat_peringatan(self, sumber, pesan):
        teks = "[PERINGATAN] %s: %s" % (sumber, pesan)
        self.daftar_peringatan.append(teks)
        print(teks)

    def _baca_mentah(self, nama_file):
        path = self.pastikan_file(nama_file)
        hasil = []
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                for nomor, baris in enumerate(f, start=1):
                    teks = baris.strip()
                    if teks:
                        hasil.append((nomor, teks))
        except (OSError, UnicodeDecodeError) as e:
            raise FileManagerError("Tidak dapat membaca file '%s': %s" % (nama_file, e))
        return hasil

    def baca_teks(self, nama_file):
        return [teks for _, teks in self._baca_mentah(nama_file)]

    def baca_baris(self, nama_file, jumlah_kolom=None):
        if jumlah_kolom is None:
            jumlah_kolom = JUMLAH_KOLOM.get(nama_file)
        hasil = []
        for nomor, teks in self._baca_mentah(nama_file):
            kolom = [k.strip() for k in teks.split(PEMISAH)]
            if jumlah_kolom is not None and len(kolom) != jumlah_kolom:
                self.catat_peringatan(
                    nama_file,
                    "baris %d dilewati (ada %d kolom, seharusnya %d): %s"
                    % (nomor, len(kolom), jumlah_kolom, teks))
                continue
            if "" in kolom:
                self.catat_peringatan(
                    nama_file, "baris %d dilewati (ada kolom kosong): %s" % (nomor, teks))
                continue
            hasil.append(kolom)
        return hasil

    @staticmethod
    def periksa_nilai(nilai):
        teks = NILAI_KOSONG if nilai is None else str(nilai).strip()
        if teks == "":
            teks = NILAI_KOSONG
        if PEMISAH in teks or "\n" in teks or "\r" in teks:
            raise ValueError("Data tidak boleh mengandung karakter '%s' atau baris baru: %r"
                             % (PEMISAH, teks))
        return teks

    def _susun_baris(self, nama_file, baris):
        if isinstance(baris, str):
            if "\n" in baris or "\r" in baris:
                raise ValueError("Satu baris data tidak boleh mengandung baris baru.")
            nilai = baris.split(PEMISAH)
        else:
            nilai = list(baris)
        kolom = [self.periksa_nilai(v) for v in nilai]
        jumlah = JUMLAH_KOLOM.get(nama_file)
        if jumlah is not None and len(kolom) != jumlah:
            raise ValueError("File %s memerlukan %d kolom, bukan %d: %s"
                             % (nama_file, jumlah, len(kolom), kolom))
        return PEMISAH.join(kolom)

    def tulis_baris(self, nama_file, daftar_baris):
        teks_baris = [self._susun_baris(nama_file, b) for b in daftar_baris]
        path = self.pastikan_file(nama_file)
        path_sementara = path + ".tmp"
        try:
            with open(path_sementara, "w", encoding="utf-8", newline="\n") as f:
                for teks in teks_baris:
                    f.write(teks + "\n")
            os.replace(path_sementara, path)
        except OSError as e:
            try:
                if os.path.exists(path_sementara):
                    os.remove(path_sementara)
            except OSError:
                pass
            raise FileManagerError("Tidak dapat menulis file '%s': %s" % (nama_file, e))

    def tambah_baris(self, nama_file, teks):
        path = self.pastikan_file(nama_file)
        satu_baris = " ".join(str(teks).splitlines()).strip()
        try:
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                f.write(satu_baris + "\n")
        except OSError as e:
            raise FileManagerError("Tidak dapat menambah baris ke '%s': %s" % (nama_file, e))
