from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.common import PersonRef, UTCDateTime


class PengumumanCreate(BaseModel):
    judul: str = Field(min_length=1)
    isi_pengumuman: str = Field(min_length=1)
    disematkan: bool = False


class PengumumanUpdate(BaseModel):
    judul: Optional[str] = Field(default=None, min_length=1)
    isi_pengumuman: Optional[str] = Field(default=None, min_length=1)
    disematkan: Optional[bool] = None


class PengumumanOut(BaseModel):
    id: int
    judul: str
    isi_pengumuman: str
    disematkan: bool
    created_at: UTCDateTime
    pembuat: Optional[PersonRef] = None
    dibaca_count: int
    total_penghuni: int
    sudah_dibaca: bool
