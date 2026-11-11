from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.schemas.common import ORMModel, PersonRef

StatusKamar = Literal["Tersedia", "Dihuni", "Perbaikan"]

# Struktur dasar atribut kamar
class RoomBase(BaseModel):
    nomor_kamar: str = Field(min_length=1)
    status_ketersediaan: StatusKamar = Field(default="Tersedia", description="Tersedia, Dihuni, Perbaikan")
    harga_dasar: int = Field(ge=0)
    lantai: int = 1
    tipe: str = "Standar"

# Skema saat pemilik menambahkan kamar baru (POST)
class RoomCreate(RoomBase):
    pass

# Skema saat pemilik mengedit info kamar (PUT)
# Semua field dibuat opsional agar bisa update sebagian data saja
class RoomUpdate(BaseModel):
    nomor_kamar: Optional[str] = None
    status_ketersediaan: Optional[StatusKamar] = None
    harga_dasar: Optional[int] = Field(default=None, ge=0)
    lantai: Optional[int] = None
    tipe: Optional[str] = None

# Skema balikan data (Response) untuk dikirim ke Frontend
class RoomResponse(ORMModel):
    id: int
    nomor_kamar: str
    status_ketersediaan: str
    harga_dasar: int
    lantai: Optional[int] = None
    tipe: Optional[str] = None
    penghuni: Optional[PersonRef] = None
