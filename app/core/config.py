from pydantic_settings import BaseSettings

# Kumpulan pengaturan aplikasi (nilainya bisa ditimpa lewat file .env)
class Settings(BaseSettings):
    PROJECT_NAME: str = "Kostopia"
    PROJECT_VERSION: str = "1.0.0"
    
    
    # Alamat koneksi ke database PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:dwp@localhost:5432/kostopia"

    # Pengaturan token login (JWT): kunci rahasia, algoritma, dan masa berlaku (menit)
    SECRET_KEY: str = "rahasia_kostopia_super_aman_123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"
        extra = "ignore"

# Objek settings yang diimpor oleh file lain
settings = Settings()