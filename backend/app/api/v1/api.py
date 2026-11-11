from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.endpoints import (
    auth, profil_kos, kamar, files, penghuni, kendaraan, tagihan, keuangan,
    aspirasi, izin, pengumuman, aturan, penilaian, barang_hilang, dasbor,
)

# Router utama versi 1 yang menggabungkan semua endpoint
api_router = APIRouter()


# Cek kesehatan server (dipakai frontend untuk mengetes koneksi)
@api_router.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": settings.PROJECT_VERSION}


# Memasang endpoint autentikasi (register, login, profil) di /auth
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(profil_kos.router, prefix="/profil", tags=["profil"])
api_router.include_router(kamar.router, prefix="/kamar", tags=["kamar"])
api_router.include_router(penghuni.router, prefix="/penghuni", tags=["penghuni"])
api_router.include_router(kendaraan.router, prefix="/kendaraan", tags=["kendaraan"])
api_router.include_router(tagihan.router, prefix="/tagihan", tags=["tagihan"])
api_router.include_router(keuangan.router, prefix="/keuangan", tags=["keuangan"])
api_router.include_router(aspirasi.router, prefix="/aspirasi", tags=["aspirasi"])
api_router.include_router(izin.router, prefix="/izin", tags=["izin"])
api_router.include_router(pengumuman.router, prefix="/pengumuman", tags=["pengumuman"])
api_router.include_router(aturan.router, prefix="/aturan", tags=["aturan"])
api_router.include_router(penilaian.router, prefix="/penilaian", tags=["penilaian"])
api_router.include_router(barang_hilang.router, prefix="/barang-hilang", tags=["barang-hilang"])
api_router.include_router(dasbor.router, prefix="/dasbor", tags=["dasbor"])
