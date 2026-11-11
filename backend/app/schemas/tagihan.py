from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.common import ORMModel, PersonRef, UTCDateTime


class KomponenBiaya(BaseModel):
    nama: str
    jumlah: int


class TagihanOut(ORMModel):
    id: int
    periode: str
    periode_label: str
    jumlah_tagihan: int
    komponen: List[KomponenBiaya] = []
    jatuh_tempo: date
    batas_tenggang: date
    status_tagihan: str
    bukti_bayar_url: Optional[str] = None
    alasan_tolak: Optional[str] = None
    tanggal_unggah: Optional[UTCDateTime] = None
    diverifikasi_at: Optional[UTCDateTime] = None
    penghuni: Optional[PersonRef] = None
    kamar: Optional[str] = None


class BuktiBayarIn(BaseModel):
    bukti_bayar_url: str


class VerifikasiIn(BaseModel):
    disetujui: bool
    alasan: Optional[str] = None
