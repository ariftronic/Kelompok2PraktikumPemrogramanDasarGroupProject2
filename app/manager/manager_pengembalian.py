"""Modul pengembalian alat (bagian Niken).

Lokasi: app/manager/manager_pengembalian.py

Asumsi antarmuka modul lain (sesuaikan dengan kesepakatan kelompok):
- ManagerTransaksi (Faris) punya properti `data_transaksi` (dict: id -> Transaksi)
  dan method `simpan()`.
- ManagerAlat (Rara) punya properti `data_alat` (dict: kode -> Alat)
  dan method `simpan()`.
- Transaksi punya atribut: id_transaksi, nim, tgl_pinjam, batas_kembali,
  status, daftar_detail (list DetailTransaksi).
- DetailTransaksi punya atribut: id_transaksi, kode_alat, status, kondisi,
  tgl_kembali.
- Alat punya atribut: kode, nama, kategori, kondisi, status.
- Tambahkan DETAIL_DIKEMBALIKAN = "dikembalikan" ke konstanta.py.
"""

from datetime import date

from app.konstanta import (
    STATUS_TERSEDIA,
    STATUS_DIPINJAM,
    STATUS_TIDAK_TERSEDIA,
    KONDISI_BAIK,
    KONDISI_RUSAK_RINGAN,
    KONDISI_RUSAK_BERAT,
    TRX_SEBAGIAN,
    TRX_SELESAI,
    DETAIL_DIKEMBALIKAN,
)

KONDISI_VALID = (KONDISI_BAIK, KONDISI_RUSAK_RINGAN, KONDISI_RUSAK_BERAT)


class ManagerPengembalian:
    """Memproses pengembalian alat (penuh maupun sebagian)."""

    def __init__(self, manager_transaksi, manager_alat, logger=None):
        self._manager_transaksi = manager_transaksi
        self._manager_alat = manager_alat
        self._logger = logger  # opsional, untuk Tantangan D

    # ---------- helper internal ----------

    def _ambil_transaksi(self, id_transaksi):
        trx = self._manager_transaksi.data_transaksi.get(id_transaksi)
        if trx is None:
            raise ValueError(f"Transaksi {id_transaksi} tidak ditemukan.")
        if trx.status == TRX_SELESAI:
            raise ValueError(f"Transaksi {id_transaksi} sudah selesai.")
        return trx

    @staticmethod
    def _cari_detail(trx, kode_alat):
        for detail in trx.daftar_detail:
            if detail.kode_alat == kode_alat:
                return detail
        return None

    @staticmethod
    def _tentukan_status(trx):
        """Transaksi selesai hanya jika semua alat sudah dikembalikan."""
        semua = all(d.status == DETAIL_DIKEMBALIKAN for d in trx.daftar_detail)
        return TRX_SELESAI if semua else TRX_SEBAGIAN

    @staticmethod
    def _validasi_tanggal(tgl_kembali, tgl_pinjam):
        try:
            tgl_k = date.fromisoformat(tgl_kembali)
            tgl_p = date.fromisoformat(tgl_pinjam)
        except ValueError:
            raise ValueError("Format tanggal harus YYYY-MM-DD.")
        if tgl_k < tgl_p:
            raise ValueError("Tanggal kembali tidak boleh sebelum tanggal pinjam.")

    # ---------- fitur utama ----------

    def kembalikan_alat(self, id_transaksi, daftar_kembali, tgl_kembali=None):
        """Proses pengembalian satu atau beberapa alat dalam satu transaksi.

        daftar_kembali: list of tuple (kode_alat, kondisi).
        Seluruh item divalidasi lebih dulu; jika ada satu yang ditolak,
        tidak ada data yang berubah (Aturan 7).
        Mengembalikan list string ringkasan hasil untuk dicetak menu.
        """
        if not daftar_kembali:
            raise ValueError("Tidak ada alat yang dikembalikan.")
        if tgl_kembali is None:
            tgl_kembali = date.today().isoformat()

        trx = self._ambil_transaksi(id_transaksi)
        self._validasi_tanggal(tgl_kembali, trx.tgl_pinjam)

        # --- Tahap 1: validasi semua item, belum mengubah data ---
        sudah_dilihat = set()
        rencana = []  # (detail, alat, kondisi)
        for kode_alat, kondisi in daftar_kembali:
            if kode_alat in sudah_dilihat:
                raise ValueError(f"Alat {kode_alat} diinput lebih dari sekali.")
            sudah_dilihat.add(kode_alat)

            if kondisi not in KONDISI_VALID:
                raise ValueError(
                    f"Kondisi '{kondisi}' tidak valid. Pilihan: "
                    + ", ".join(KONDISI_VALID)
                )
            detail = self._cari_detail(trx, kode_alat)
            if detail is None:
                raise ValueError(
                    f"Alat {kode_alat} tidak ada dalam transaksi {id_transaksi}."
                )
            if detail.status == DETAIL_DIKEMBALIKAN:
                raise ValueError(f"Alat {kode_alat} sudah dikembalikan.")
            alat = self._manager_alat.data_alat.get(kode_alat)
            if alat is None:
                raise ValueError(f"Alat {kode_alat} tidak ada di data alat.")
            rencana.append((detail, alat, kondisi))

        # --- Tahap 2: ubah data (Aturan 4 dan 5) ---
        ringkasan = []
        for detail, alat, kondisi in rencana:
            detail.status = DETAIL_DIKEMBALIKAN
            detail.kondisi = kondisi
            detail.tgl_kembali = tgl_kembali

            alat.kondisi = kondisi
            if kondisi == KONDISI_BAIK:
                alat.status = STATUS_TERSEDIA
            else:  # rusak ringan atau rusak berat tidak masuk stok
                alat.status = STATUS_TIDAK_TERSEDIA
            ringkasan.append(
                f"{alat.kode} - {alat.nama}: kondisi {kondisi}, "
                f"status alat {alat.status}"
            )

        trx.status = self._tentukan_status(trx)
        ringkasan.append(f"Status transaksi {id_transaksi}: {trx.status}")

        # --- Tahap 3: simpan ke file ---
        self._manager_alat.simpan()
        self._manager_transaksi.simpan()

        if self._logger is not None:
            for detail, alat, kondisi in rencana:
                self._logger.catat(
                    f"Alat {alat.kode} dikembalikan pada transaksi "
                    f"{id_transaksi} (kondisi {kondisi})"
                )
        return ringkasan

    def daftar_alat_dipinjam(self):
        """Data alat yang sedang dipinjam (untuk menu 8).

        Mengembalikan list dict; menu yang bertugas mencetaknya.
        """
        hasil = []
        hari_ini = date.today().isoformat()
        for trx in self._manager_transaksi.data_transaksi.values():
            if trx.status == TRX_SELESAI:
                continue
            for detail in trx.daftar_detail:
                if detail.status == DETAIL_DIKEMBALIKAN:
                    continue
                alat = self._manager_alat.data_alat.get(detail.kode_alat)
                hasil.append({
                    "id_transaksi": trx.id_transaksi,
                    "nim": trx.nim,
                    "kode_alat": detail.kode_alat,
                    "nama_alat": alat.nama if alat else "-",
                    "batas_kembali": trx.batas_kembali,
                    "terlambat": trx.batas_kembali < hari_ini,
                })
        return hasil
