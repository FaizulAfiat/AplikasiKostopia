from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from app.schemas.common import ORMModel
from app.schemas.user import UserOut
from app.schemas.kendaraan import KendaraanOut

StatusSewa = Literal["Aktif", "Masa Tenggang", "Sudah Keluar"]


class SewaOut(ORMModel):
    id: int
    kamar: Optional[str] = None
    room_id: int
    tanggal_mulai: date
    tanggal_jatuh_tempo: date
    status_sewa: str


class PenghuniOut(BaseModel):
    user: UserOut
    sewa: Optional[SewaOut] = None
    kendaraan: List[KendaraanOut] = []
    tagihan_bulan_ini: Optional[str] = None


class SewaCreate(BaseModel):
    room_id: int
    tanggal_mulai: date
    lama_bulan: int = Field(ge=1)


class SewaStatusUpdate(BaseModel):
    status_sewa: StatusSewa
