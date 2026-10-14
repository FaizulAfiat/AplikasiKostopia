from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Skema untuk menerima data saat Pemilik melakukan edit (PUT)
# Semua menggunakan Optional karena pemilik mungkin hanya ingin mengubah 1 atau 2 kolom saja
class ProfilKosUpdate(BaseModel):
    nama_kos: Optional[str] = None
    alamat_lengkap: Optional[str] = None
    deskripsi: Optional[str] = None
    nomor_telepon_pengelola: Optional[str] = None
    informasi_rekening: Optional[str] = None
    gmaps_url: Optional[str] = None

# Skema untuk merender data saat diminta oleh Frontend (GET)
class ProfilKosResponse(BaseModel):
    id: int
    nama_kos: str
    alamat_lengkap: str
    deskripsi: Optional[str] = None
    nomor_telepon_pengelola: Optional[str] = None
    informasi_rekening: Optional[str] = None
    gmaps_url: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Mengizinkan Pydantic membaca objek SQLAlchemy langsung