from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.common import ORMModel, UTCDateTime


class AturanCreate(BaseModel):
    judul: str = Field(min_length=1)
    deskripsi: Optional[str] = None
    sanksi: Optional[str] = None
    status_aktif: bool = True


class AturanUpdate(BaseModel):
    judul: Optional[str] = Field(default=None, min_length=1)
    deskripsi: Optional[str] = None
    sanksi: Optional[str] = None
    status_aktif: Optional[bool] = None
    urutan: Optional[int] = None


class AturanOut(ORMModel):
    id: int
    urutan: int
    judul: str
    deskripsi: Optional[str] = None
    sanksi: Optional[str] = None
    status_aktif: bool
    updated_at: Optional[UTCDateTime] = None
