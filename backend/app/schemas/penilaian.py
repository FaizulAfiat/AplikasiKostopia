from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from app.schemas.common import ORMModel, PersonRef, UTCDateTime

AspekPenilaian = Literal["Kebersihan", "Keamanan", "Fasilitas", "Pelayanan", "Umum"]


class PenilaianCreate(BaseModel):
    skor_bintang: int = Field(ge=1, le=5)
    aspek: AspekPenilaian = "Umum"
    ulasan_feedback: Optional[str] = None


class PenilaianOut(ORMModel):
    id: int
    skor_bintang: int
    aspek: str
    ulasan_feedback: Optional[str] = None
    created_at: UTCDateTime
    pengguna: PersonRef


class PerAspek(BaseModel):
    aspek: str
    rata_rata: float
    jumlah: int


class RingkasanPenilaian(BaseModel):
    rata_rata: float
    jumlah: int
    distribusi: Dict[str, int]
    per_aspek: List[PerAspek]
