import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.domain import User, PeranPengguna
from app.schemas.user import UserRegister, UserUpdateMe

logger = logging.getLogger("kostopia")

# Pengaturan enkripsi password (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Mendaftarkan akun baru (default Penghuni; Pemilik hanya jika belum ada Pemilik)
def register_user(db: Session, data: UserRegister) -> User:
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar, silakan gunakan email lain")
    if data.peran == PeranPengguna.pemilik:
        sudah_ada = db.query(User).filter(User.peran == PeranPengguna.pemilik).first()
        if sudah_ada:
            raise HTTPException(
                status_code=400,
                detail="Akun Pemilik sudah ada. Sistem hanya mendukung satu pemilik kos.",
            )
    db_user = User(
        nama_lengkap=data.nama_lengkap.strip(),
        email=data.email.lower(),
        nomor_telepon=data.nomor_telepon,
        password_hash=hash_password(data.password),
        peran=data.peran,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Kompatibilitas dengan kode lama: mendaftarkan akun pemilik
def create_pemilik(db: Session, user: UserRegister) -> User:
    user.peran = PeranPengguna.pemilik
    return register_user(db, user)


# Mengecek email & password saat login; mengembalikan user jika benar, False jika salah
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.password_hash):
        return False
    return user


# Mencari user berdasarkan alamat email (tidak peka huruf besar/kecil)
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower()).first()


def update_me(db: Session, user: User, data: UserUpdateMe) -> User:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def ganti_sandi(db: Session, user: User, sandi_lama: str, sandi_baru: str) -> None:
    if not pwd_context.verify(sandi_lama, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kata sandi lama salah")
    user.password_hash = hash_password(sandi_baru)
    db.commit()


def lupa_sandi(db: Session, email: str) -> None:
    """Belum ada pengiriman email sungguhan; permintaan hanya dicatat ke log server."""
    user = get_user_by_email(db, email)
    if user:
        logger.warning("Permintaan reset kata sandi untuk %s (user id %s)", user.email, user.id)
    else:
        logger.warning("Permintaan reset kata sandi untuk email tidak terdaftar: %s", email)
