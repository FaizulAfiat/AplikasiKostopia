from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreatePemilik, UserResponse, UserLogin 
from app.services import user_services
from app.models.domain import User
from app.core.security import create_access_token
from app.api.v1.endpoints.deps import get_validasi_user

router = APIRouter()

# API Register: mendaftarkan akun pemilik baru (ditolak jika email sudah terdaftar)
@router.post("/register", response_model=UserResponse)
def register_pemilik(user: UserCreatePemilik, db: Session = Depends(get_db)):
    cek_email = db.query(User).filter(User.email == user.email).first()
    if cek_email:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar silahkan gunakan email lain")   

    user_baru = user_services.create_pemilik(db, user)
    return user_baru




# API Login: untuk pemilik dan penghuni, mengembalikan token akses dan peran user
@router.post("/login")
def login_universal(user_credentials: UserLogin, db: Session = Depends(get_db)):
    
    user = user_services.authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
      
        raise HTTPException(
            status_code=401, 
            detail="Email atau kata sandi salah"
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.peran.value}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.peran.value
    }

# API Profil: menampilkan data user yang sedang login (butuh token)
@router.get("/me", response_model=UserResponse)
def profil_saya(current_user: User = Depends(get_validasi_user)):
    return current_user
    