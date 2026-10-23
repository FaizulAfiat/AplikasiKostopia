from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.profil_kos import ProfilKosResponse, ProfilKosUpdate
from app.api.v1.endpoints.deps import get_validasi_user, get_pemilik_saja 
from app.services import profil_kos as profil_kos_service

router = APIRouter()

@router.get("/", response_model=ProfilKosResponse)
def ambil_profil_kos(
    db: Session = Depends(get_db), 
    current_user = Depends(get_validasi_user)
):
    """Semua pengguna yang sudah login (Pemilik/Penghuni) bisa melihat biodata kos"""
    return profil_kos_service.get_profil_kos(db)

@router.post("/profil", response_model=ProfilKosResponse, status_code=status.HTTP_201_CREATED)
def buat_profil_baru(
    data_baru: ProfilKosUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_pemilik_saja)
):
    return profil_kos_service.create_profil_kos(db, data_baru)

@router.put("/", response_model=ProfilKosResponse)
def edit_profil_kos(
    data_baru: ProfilKosUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_pemilik_saja)
):
    """Hanya Pemilik yang bisa mengubah biodata kos"""
    return profil_kos_service.update_profil_kos(db, data_baru)