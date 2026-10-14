from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Koneksi utama ke database
engine = create_engine(settings.DATABASE_URL)

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