from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.models import domain

# Membuat semua tabel di database secara otomatis jika belum ada
Base.metadata.create_all(bind=engine)

# Objek utama aplikasi FastAPI (dicari oleh uvicorn saat server dijalankan)
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Mendaftarkan semua rute API dengan awalan /api/v1
app.include_router(api_router, prefix="/api/v1")

# Endpoint root: untuk mengecek apakah backend sudah berjalan
@app.get("/")
def read_root():
    return {"message": "Sistem Backend Kostopia Aktif!"}