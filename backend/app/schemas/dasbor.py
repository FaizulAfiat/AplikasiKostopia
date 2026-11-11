from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.common import UTCDateTime
from app.schemas.keuangan import PemasukanBulanan
from app.schemas.tagihan import TagihanOut
from app.schemas.pengumuman import PengumumanOut


class PerluTindakan(BaseModel):
    bukti_menunggu: int
    izin_pending: int
    aspirasi_baru: int
    sewa_berakhir_7_hari: int


class KamarPeta(BaseModel):
    id: int
    nomor: str
    status: str  # Lunas, Belum Bayar, Menunggu, Masa Tenggang, Kosong
    penghuni: Optional[str] = None


class LantaiPeta(BaseModel):
    lantai: int
    kamar: List[KamarPeta]


class Aktivitas(BaseModel):
    jenis: str  # Aspirasi, Izin, Lunas, Ulasan, Barang Hilang
    judul: str
    nama: Optional[str] = None
    kamar: Optional[str] = None
    waktu: UTCDateTime


class DasborPemilik(BaseModel):
    nama_kos: str
    total_kamar: int
    kamar_terisi: int
    pemasukan_bulan_ini: int
    tagihan_lunas: int
    total_tagihan: int
    tunggakan: int
    jumlah_penunggak: int
    jumlah_tenggang: int
    rating_rata: float
    jumlah_ulasan: int
    perlu_tindakan: PerluTindakan
    pemasukan_6_bulan: List[PemasukanBulanan]
    peta_kamar: List[LantaiPeta]
    menunggu_verifikasi: List[TagihanOut]
    aktivitas: List[Aktivitas]


class Permintaan(BaseModel):
    jenis: str  # Aspirasi / Izin
    id: int
    judul: str
    status: str
    created_at: UTCDateTime


class DasborPenghuni(BaseModel):
    nama_kos: str
    kamar: Optional[str] = None
    status_sewa: Optional[str] = None
    sewa_mulai: Optional[date] = None
    sewa_sampai: Optional[date] = None
    tagihan_aktif: Optional[TagihanOut] = None
    pengumuman_terbaru: Optional[PengumumanOut] = None
    permintaan: List[Permintaan]
    jumlah_aturan_aktif: int
