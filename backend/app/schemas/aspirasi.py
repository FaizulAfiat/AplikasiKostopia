from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.common import ORMModel, PersonRef, UTCDateTime

KategoriAspirasi = Literal["Kerusakan", "Fasilitas", "Kebersihan", "Keamanan", "Saran"]
StatusAspirasi = Literal["Menunggu", "Sedang Diproses", "Selesai"]


class AspirasiCreate(BaseModel):
    judul: str
    kategori: KategoriAspirasi
    deskripsi_kendala: str
    lampiran_foto_urls: List[str] = Field(default_factory=list, max_length=3)

    @field_validator("judul", "deskripsi_kendala")
    @classmethod
    def tidak_kosong(cls, v: str, info):
        if not v or not v.strip():
            nama = "Judul" if info.field_name == "judul" else "Deskripsi kendala"
            raise ValueError(f"{nama} wajib diisi")
        return v.strip()


class AspirasiUpdate(BaseModel):
    status_penanganan: Optional[StatusAspirasi] = None
    tanggapan_pemilik: Optional[str] = None


class AspirasiOut(ORMModel):
    id: int
    judul: Optional[str] = None
    kategori: Optional[str] = None
    deskripsi_kendala: str
    lampiran_foto_urls: List[str] = []
    status_penanganan: str
    tanggapan_pemilik: Optional[str] = None
    created_at: UTCDateTime
    updated_at: Optional[UTCDateTime] = None
    pelapor: PersonRef
