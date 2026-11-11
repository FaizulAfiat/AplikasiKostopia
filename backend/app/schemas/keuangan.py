from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.schemas.common import ORMModel, UTCDateTime

KategoriPengeluaran = Literal["Listrik", "Air", "Kebersihan", "Perbaikan", "Gaji", "Lainnya"]


class RingkasanKeuangan(BaseModel):
    pemasukan: int
    pengeluaran: int
    laba_bersih: int
    tunggakan: int
    jumlah_lunas: int
    jumlah_penunggak: int


class TransaksiOut(BaseModel):
    tanggal: date
    keterangan: str
    kategori: Literal["Sewa", "Tambahan", "Pengeluaran"]
    nominal: int


class PemasukanBulanan(BaseModel):
    periode: str
    label: str
    total: int


class PengeluaranCreate(BaseModel):
    tanggal: date
    keterangan: str = Field(min_length=1)
    kategori: KategoriPengeluaran
    nominal: int = Field(gt=0)


class PengeluaranOut(ORMModel):
    id: int
    tanggal: date
    keterangan: str
    kategori: str
    nominal: int
    created_at: Optional[UTCDateTime] = None
