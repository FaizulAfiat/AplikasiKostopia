from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.common import MessageOut
from app.schemas.user import (
    GantiSandiIn, LoginOut, LupaSandiIn, UserLogin, UserOut, UserRegister, UserUpdateMe,
)
from app.services import user_services
from app.models.domain import User
from app.core.security import create_access_token
from app.api.v1.endpoints.deps import get_validasi_user

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Registrasi akun. Default Penghuni; Pemilik hanya jika belum ada akun Pemilik."""
    return user_services.register_user(db, user)


@router.post("/login", response_model=LoginOut)
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
        "role": user.peran.value,
        "user": user,
    }


@router.post("/lupa-sandi", response_model=MessageOut)
def lupa_sandi(data: LupaSandiIn, db: Session = Depends(get_db)):
    user_services.lupa_sandi(db, data.email)
    return {"message": "Jika email terdaftar, instruksi telah dikirim."}


@router.get("/me", response_model=UserOut)
def profil_saya(current_user: User = Depends(get_validasi_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def ubah_profil_saya(
    data: UserUpdateMe,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_validasi_user),
):
    return user_services.update_me(db, current_user, data)


@router.post("/ganti-sandi", response_model=MessageOut)
def ganti_sandi(
    data: GantiSandiIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_validasi_user),
):
    user_services.ganti_sandi(db, current_user, data.sandi_lama, data.sandi_baru)
    return {"message": "Kata sandi berhasil diubah."}
