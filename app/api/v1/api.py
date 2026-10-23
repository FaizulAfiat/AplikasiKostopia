from fastapi import APIRouter
from app.api.v1.endpoints import auth, profil_kos, kamar

# Router utama versi 1 yang menggabungkan semua endpoint
api_router = APIRouter()
# Memasang endpoint autentikasi (register, login, profil) di /auth
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(kamar.router, prefix="/kamar", tags=["kamar"])
api_router.include_router(profil_kos.router, prefix="/profil", tags=["profil"])