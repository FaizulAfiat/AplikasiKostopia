from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config import settings


def buat_engine(url: str):
    """Membuat engine; SQLite (dipakai saat testing) butuh pengaturan khusus."""
    if url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}}
        if url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool
        return create_engine(url, **kwargs)
    # SQLAlchemy 2.1+ memakai driver "psycopg" (v3) untuk "postgresql://",
    # sedangkan requirements.txt memasang psycopg2 → pilih driver psycopg2 secara eksplisit.
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return create_engine(url, pool_pre_ping=True)


# Koneksi utama ke database
engine = buat_engine(settings.DATABASE_URL)

# Pembuat sesi untuk berinteraksi (query/simpan data) dengan database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Class induk untuk semua model tabel
Base = declarative_base()

# Menyediakan sesi database untuk setiap request, lalu menutupnya setelah selesai
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
