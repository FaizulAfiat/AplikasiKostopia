from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

# Struktur dasar atribut kamar
class RoomBase(BaseModel):
    nomor_kamar: str
    status_ketersediaan: str = Field(default="Tersedia", description="Contoh: Tersedia, Dihuni, Perbaikan")
    harga_dasar: Decimal

# Skema saat pemilik menambahkan kamar baru (POST)
class RoomCreate(RoomBase):
    pass

# Skema saat pemilik mengedit info kamar (PUT)
# Semua field dibuat opsional agar bisa update sebagian data saja
class RoomUpdate(BaseModel):
    nomor_kamar: Optional[str] = None
    status_ketersediaan: Optional[str] = None
    harga_dasar: Optional[Decimal] = None

# Skema balikan data (Response) untuk dikirim ke Frontend
class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True