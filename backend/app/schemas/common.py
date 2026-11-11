"""Tipe & skema yang dipakai bersama oleh banyak endpoint."""
from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, PlainSerializer
from app.core.waktu import format_utc
from app.models.domain import PeranPengguna

# Datetime yang selalu dikirim sebagai ISO 8601 UTC berakhiran "Z"
UTCDateTime = Annotated[datetime, PlainSerializer(format_utc, return_type=str)]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Ringkasan orang yang disisipkan di banyak respons
class PersonRef(ORMModel):
    id: int
    nama_lengkap: str
    peran: PeranPengguna
    kamar: Optional[str] = None


class MessageOut(BaseModel):
    message: str
