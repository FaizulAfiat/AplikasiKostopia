from typing import Literal, Optional
from pydantic import BaseModel
from app.schemas.common import ORMModel, PersonRef, UTCDateTime


class BarangHilangCreate(BaseModel):
    jenis: Literal["Hilang", "Temuan"] = "Hilang"
    # Opsional di skema agar nama kosong/tidak dikirim menghasilkan 422 "Nama barang wajib diisi"
    judul_barang: Optional[str] = None
    deskripsi: Optional[str] = None
    lokasi: Optional[str] = None
    foto_url: Optional[str] = None


class BarangHilangOut(ORMModel):
    id: int
    jenis: str
    judul_barang: str
    deskripsi: Optional[str] = None
    lokasi: Optional[str] = None
    foto_url: Optional[str] = None
    status_barang: str
    created_at: UTCDateTime
    selesai_at: Optional[UTCDateTime] = None
    pelapor: PersonRef
