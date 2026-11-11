from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.domain import PeranPengguna
from app.schemas.common import ORMModel, UTCDateTime

# Data dasar yang dimiliki semua user (email otomatis divalidasi formatnya)
class UserBase(BaseModel):
    nama_lengkap: str = Field(min_length=1)
    email: EmailStr
    nomor_telepon: Optional[str] = None


# Data dari form register (peran default Penghuni)
class UserRegister(UserBase):
    password: str = Field(min_length=8)
    peran: PeranPengguna = PeranPengguna.penghuni


# Alias lama agar kode tim yang memakai nama ini tetap berjalan
UserCreatePemilik = UserRegister
UserCreatePenghuni = UserRegister


# Data dari form login (email & password)
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class LupaSandiIn(BaseModel):
    email: EmailStr


class GantiSandiIn(BaseModel):
    sandi_lama: str
    sandi_baru: str = Field(min_length=8)


# Data profil yang boleh diubah pengguna sendiri (PUT /auth/me)
class UserUpdateMe(BaseModel):
    nama_lengkap: Optional[str] = Field(default=None, min_length=1)
    nomor_telepon: Optional[str] = None
    asal_kampus: Optional[str] = None
    kontak_darurat_nama: Optional[str] = None
    kontak_darurat_telepon: Optional[str] = None


# Data user yang dikirim kembali ke frontend (tanpa password)
class UserOut(ORMModel):
    id: int
    nama_lengkap: str
    email: str
    nomor_telepon: Optional[str] = None
    peran: PeranPengguna
    asal_kampus: Optional[str] = None
    kontak_darurat_nama: Optional[str] = None
    kontak_darurat_telepon: Optional[str] = None
    kamar: Optional[str] = None
    created_at: UTCDateTime


UserResponse = UserOut


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: PeranPengguna
    user: UserOut
