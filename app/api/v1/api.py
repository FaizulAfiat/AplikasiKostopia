from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import auth, profil_kos

# Router utama versi 1 yang menggabungkan semua endpoint
api_router = APIRouter()
# Memasang endpoint autentikasi (register, login, profil) di /auth
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
