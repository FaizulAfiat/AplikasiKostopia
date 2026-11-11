from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.models import domain  # noqa: F401  (mendaftarkan semua model ke Base)
from app.services.files import upload_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Membuat semua tabel di database secara otomatis jika belum ada (saat server start).
    # Catatan: create_all tidak mengubah tabel lama → reset dengan `python -m app.seed --reset`.
    Base.metadata.create_all(bind=engine)
    yield


# Objek utama aplikasi FastAPI (dicari oleh uvicorn saat server dijalankan)
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

# CORS: aplikasi memakai Bearer token (bukan cookie), sehingga allow_credentials=False
# dan origin "*" aman. Origin WebView Capacitor Android adalah http://localhost.
origins = settings.cors_origins_list or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Mendaftarkan semua rute API dengan awalan /api/v1
app.include_router(api_router, prefix="/api/v1")

# File unggahan disajikan statis di /uploads/<nama>
app.mount("/uploads", StaticFiles(directory=str(upload_dir())), name="uploads")


# Endpoint root: untuk mengecek apakah backend sudah berjalan
@app.get("/")
def read_root():
    return {"message": "Sistem Backend Kostopia Aktif!"}
