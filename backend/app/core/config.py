from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Folder root backend (satu tingkat di atas folder app/)
BASE_DIR = Path(__file__).resolve().parents[2]


# Kumpulan pengaturan aplikasi (nilainya bisa ditimpa lewat file .env)
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    PROJECT_NAME: str = "Kostopia"
    PROJECT_VERSION: str = "1.0.0"

    # Alamat koneksi ke database PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:dwp@localhost:5432/kostopia"

    # Pengaturan token login (JWT): kunci rahasia, algoritma, dan masa berlaku (menit)
    SECRET_KEY: str = "rahasia_kostopia_dev_GANTI_di_file_env_0123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Daftar origin yang diizinkan CORS, dipisah koma. "*" = semua origin.
    # Aplikasi memakai Bearer token (bukan cookie), jadi "*" aman dipakai saat development.
    CORS_ORIGINS: str = "*"

    # Folder penyimpanan file unggahan & batas ukurannya (MB)
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_MB: int = 5

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


# Objek settings yang diimpor oleh file lain
settings = Settings()
