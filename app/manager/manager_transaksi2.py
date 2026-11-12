"""ManagerTransaksi: peminjaman, pencarian transaksi, dan riwayat mahasiswa.

Dependensi (dibagikan dari main.py agar data selalu sama di seluruh modul):
    file_manager         -> FileManager (baca_baris, tulis_baris)
    manager_mahasiswa    -> punya .data_mahasiswa (dict NIM -> Mahasiswa), .simpan()
    manager_alat         -> punya .data_alat (dict kode -> Alat), .simpan()
Objek Mahasiswa dipakai dengan atribut nim, status_aktif; Alat dengan kode, status.
"""
from app.konstanta import STATUS_DIPINJAM, STATUS_TERSEDIA
from app.models.transaksi import (
    DetailTransaksi, Transaksi, MAKS_HARI_PINJAM,
)

FILE_TRANSAKSI = "transaksi.txt"
FILE_DETAIL = "detail_transaksi.txt"
MAKS_TRANSAKSI_AKTIF = 2
AWALAN_ID = "T"
STATUS_MHS_AKTIF = "aktif"
STATUS_MHS_TIDAK_AKTIF = "tidak aktif"


class ManagerTransaksi:
    """Mengelola data_transaksi (dict: ID transaksi -> Transaksi)."""

    def __init__(self, file_manager, manager_mahasiswa, manager_alat):
        self._file = file_manager
        self._mhs = manager_mahasiswa
        self._alat = manager_alat
        self.data_transaksi = {}

    # ---------------- muat / simpan ----------------
    def muat(self):
        """Muat transaksi dan detail dari file; baris rusak/ganda dilewati."""
        self.data_transaksi = {}
        for baris in self._file.baca_baris(FILE_TRANSAKSI):
            try:
                trx = Transaksi.dari_baris(baris)
            except ValueError as err:
                print("Peringatan: baris transaksi dilewati (%s): %s"
                      % (err, "|".join(baris)))
                continue
            if trx.id_transaksi in self.data_transaksi:
                print("Peringatan: ID transaksi ganda dilewati: " + trx.id_transaksi)
            elif trx.nim not in self._mhs.data_mahasiswa:
                print("Peringatan: NIM %s tidak ada, transaksi %s dilewati"
                      % (trx.nim, trx.id_transaksi))
            else:
                self.data_transaksi[trx.id_transaksi] = trx

        for baris in self._file.baca_baris(FILE_DETAIL):
            try:
                detail = DetailTransaksi.dari_baris(baris)
            except ValueError as err:
                print("Peringatan: baris detail dilewati (%s): %s"
                      % (err, "|".join(baris)))
                continue
            trx = self.data_transaksi.get(detail.id_transaksi)
            if trx is None:
                print("Peringatan: detail untuk transaksi tidak dikenal dilewati: "
                      + detail.id_transaksi)
            elif detail.kode not in self._alat.data_alat:
                print("Peringatan: kode alat %s tidak ada, detail dilewati"
                      % detail.kode)
            elif trx.cari_detail(detail.kode) is not None:
                print("Peringatan: detail ganda dilewati: %s %s"
                      % (detail.id_transaksi, detail.kode))
            else:
                trx.daftar_detail.append(detail)

    def simpan(self):
        """Tulis seluruh transaksi dan detail ke file."""
        baris_trx, baris_detail = [], []
        for trx in self.data_transaksi.values():
            baris_trx.append(trx.ke_baris())
            baris_detail.extend(d.ke_baris() for d in trx.daftar_detail)
        self._file.tulis_baris(FILE_TRANSAKSI, baris_trx)
        self._file.tulis_baris(FILE_DETAIL, baris_detail)

    # ---------------- peminjaman ----------------
    def buat_id_baru(self):
        """ID = nomor terbesar yang ada + 1 (format T001)."""
        nomor = [int(i[len(AWALAN_ID):]) for i in self.data_transaksi
                 if i[len(AWALAN_ID):].isdigit()]
        return "%s%03d" % (AWALAN_ID, (max(nomor) if nomor else 0) + 1)

    def jumlah_transaksi_aktif(self, nim):
        """Jumlah transaksi aktif milik mahasiswa."""
        return len(self.transaksi_aktif_mahasiswa(nim))

    def transaksi_aktif_mahasiswa(self, nim):
        """List transaksi aktif milik mahasiswa."""
        return [t for t in self.data_transaksi.values()
                if t.nim == nim and t.aktif()]

    def buat_transaksi(self, nim, daftar_kode, lama_hari=MAKS_HARI_PINJAM,
                       tgl_pinjam=None):
        """Buat transaksi peminjaman multi-alat dan simpan ke file.

        Semua validasi dilakukan sebelum data diubah (Aturan 7).
        Raise ValueError jika ditolak. Mengembalikan objek Transaksi baru.
        """
        nim = nim.strip()
        kode_bersih = [k.strip() for k in daftar_kode if k.strip()]
        for teks in [nim] + kode_bersih:
            if "|" in teks:
                raise ValueError("input tidak boleh mengandung karakter '|'")

        # --- validasi ---
        if nim not in self._mhs.data_mahasiswa:
            raise ValueError("NIM %s tidak ditemukan" % nim)
        if not kode_bersih:
            raise ValueError("pilih minimal satu alat")
        if len(set(kode_bersih)) != len(kode_bersih):
            raise ValueError("kode alat tidak boleh dobel dalam satu transaksi")
        if self.jumlah_transaksi_aktif(nim) >= MAKS_TRANSAKSI_AKTIF:
            raise ValueError("mahasiswa sudah memiliki %d transaksi aktif"
                             % MAKS_TRANSAKSI_AKTIF)
        for kode in kode_bersih:
            alat = self._alat.data_alat.get(kode)
            if alat is None:
                raise ValueError("alat %s tidak ditemukan" % kode)
            if alat.status != STATUS_TERSEDIA:
                raise ValueError("alat %s tidak tersedia (%s)" % (kode, alat.status))
        trx = Transaksi.baru(self.buat_id_baru(), nim, kode_bersih,
                             lama_hari, tgl_pinjam)  # ValueError jika hari tidak valid

        # --- ubah data, lalu simpan ---
        self.data_transaksi[trx.id_transaksi] = trx
        for kode in kode_bersih:
            self._alat.data_alat[kode].status = STATUS_DIPINJAM
        self.sinkron_status_mahasiswa(nim)
        self.simpan()
        self._alat.simpan()
        self._mhs.simpan()
        return trx

    def sinkron_status_mahasiswa(self, nim):
        """status_aktif mahasiswa = 'aktif' jika punya transaksi aktif.

        Tidak menyimpan file; pemanggil yang memanggil manager_mahasiswa.simpan().
        Bisa dipanggil modul pengembalian setelah transaksi berubah.
        """
        mhs = self._mhs.data_mahasiswa.get(nim)
        if mhs is not None:
            mhs.status_aktif = (STATUS_MHS_AKTIF if self.jumlah_transaksi_aktif(nim)
                                else STATUS_MHS_TIDAK_AKTIF)

    # ---------------- tampilan / pencarian ----------------
    def semua_transaksi(self):
        """List seluruh transaksi, urut ID."""
        return [self.data_transaksi[i] for i in sorted(self.data_transaksi)]

    def cari_transaksi(self, id_transaksi):
        """Ambil satu transaksi berdasarkan ID, atau raise ValueError."""
        trx = self.data_transaksi.get(id_transaksi.strip().upper())
        if trx is None:
            raise ValueError("transaksi %s tidak ditemukan" % id_transaksi)
        return trx

    def cari_per_mahasiswa(self, nim):
        """List transaksi milik satu mahasiswa; ValueError jika NIM tak ada."""
        nim = nim.strip()
        if nim not in self._mhs.data_mahasiswa:
            raise ValueError("NIM %s tidak ditemukan" % nim)
        return [t for t in self.semua_transaksi() if t.nim == nim]

    def riwayat_mahasiswa(self, nim):
        """Riwayat peminjaman satu mahasiswa, terbaru lebih dulu.

        Mengembalikan list tuple (Transaksi, DetailTransaksi) agar tiap alat
        yang pernah dipinjam tampil beserta kondisi dan tanggal kembalinya.
        """
        hasil = []
        for trx in sorted(self.cari_per_mahasiswa(nim),
                          key=lambda t: (t.tgl_pinjam, t.id_transaksi),
                          reverse=True):
            hasil.extend((trx, d) for d in trx.daftar_detail)
        return hasil
