from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.domain import User, PeranPengguna
from app.schemas.user import UserCreatePemilik

# Pengaturan enkripsi password (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mendaftarkan akun pemilik baru: password dienkripsi lalu disimpan ke database
def create_pemilik(db: Session, user: UserCreatePemilik):

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        nama_lengkap=user.nama_lengkap,
        email=user.email,
        nomor_telepon=user.nomor_telepon,
        password_hash=hashed_password,  
        peran=PeranPengguna.pemilik
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Mengecek email & password saat login; mengembalikan user jika benar, False jika salah
def authenticate_user(db: Session, email: str, password: str):
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False 
    
    if not pwd_context.verify(password, user.password_hash):
        return False 
    

# Mencari user berdasarkan alamat email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()