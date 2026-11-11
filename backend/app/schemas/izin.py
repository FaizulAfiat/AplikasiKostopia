from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, field_validator, model_validator
from app.schemas.common import ORMModel, PersonRef, UTCDateTime

JenisIzin = Literal["Pulang Kampung", "Menginap di Luar", "Pulang Larut", "Lainnya"]


class IzinCreate(BaseModel):
    jenis_izin: JenisIzin
    tanggal_mulai: date
    tanggal_selesai: date
    alasan: str

    @field_validator("alasan")
    @classmethod
    def alasan_wajib(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Alasan wajib diisi")
        return v.strip()

    @model_validator(mode="after")
    def cek_tanggal(self):
        if self.tanggal_selesai < self.tanggal_mulai:
            raise ValueError("Tanggal selesai tidak boleh sebelum tanggal mulai")
        return self


class IzinUpdate(BaseModel):
    status_izin: Literal["Disetujui", "Ditolak"]
    catatan_pemilik: Optional[str] = None


class IzinOut(ORMModel):
    id: int
    jenis_izin: str
    tanggal_mulai: date
    tanggal_selesai: Optional[date] = None
    durasi: Optional[str] = None
    alasan: Optional[str] = None
    status_izin: str
    catatan_pemilik: Optional[str] = None
    created_at: UTCDateTime
    pemohon: PersonRef
