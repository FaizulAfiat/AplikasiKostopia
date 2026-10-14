from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.domain import PeranPengguna

# Data dasar yang dimiliki semua user (email otomatis divalidasi formatnya)
class UserBase(BaseModel):
    nama_lengkap: str
    email: EmailStr
    nomor_telepon: Optional[str] = None


# Data dari form register pemilik
class UserCreatePemilik(UserBase):
    password: str


# Data dari form login (email & password)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Data dari form tambah penghuni
class UserCreatePenghuni(UserBase):
    password: str

# Data user yang dikirim kembali ke frontend (tanpa password)
class UserResponse(UserBase):
    id: int
    peran: PeranPengguna
    created_at: datetime

    class Config:
        from_attributes = True