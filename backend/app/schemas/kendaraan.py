from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.schemas.common import ORMModel, PersonRef

JenisKendaraan = Literal["Motor", "Mobil"]


class KendaraanCreate(BaseModel):
    nomor_polisi: str = Field(min_length=1)
    jenis_kendaraan: JenisKendaraan
    merk_warna: Optional[str] = None


# Pemilik kos mengatur slot_parkir; penghuni pemilik kendaraan mengubah merk_warna
class KendaraanUpdate(BaseModel):
    slot_parkir: Optional[str] = None
    merk_warna: Optional[str] = None


class KendaraanOut(ORMModel):
    id: int
    nomor_polisi: str
    jenis_kendaraan: str
    merk_warna: Optional[str] = None
    slot_parkir: Optional[str] = None
    pemilik: PersonRef


class RingkasanParkir(BaseModel):
    motor_terpakai: int
    motor_kapasitas: int
    mobil_terpakai: int
    mobil_kapasitas: int
