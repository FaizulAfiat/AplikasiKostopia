from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import ProfilKos
from app.schemas.profil_kos import ProfilKosResponse, ProfilKosUpdate
# Sesuaikan path impor deps di bawah ini dengan letak file deps.py kamu
from app.api.v1.endpoints.deps import get_validasi_user, get_pemilik_saja 

router = APIRouter()

@router.get("/", response_model=ProfilKosResponse)
def ambil_profil_kos(db: Session = Depends(get_db), current_user = Depends(get_validasi_user)):
    """Semua pengguna yang sudah login (Pemilik/Penghuni) bisa melihat biodata kos"""
    profil = db.query(ProfilKos).filter(ProfilKos.id == 1).first()
    if not profil:
        raise HTTPException(status_code=404, detail="Profil kos belum diatur")
    return profil

@router.put("/", response_model=ProfilKosResponse)
def edit_profil_kos(
    data_baru: ProfilKosUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_pemilik_saja) # Hanya pemilik yang lolos!
):
    """Hanya Pemilik yang bisa mengubah biodata kos"""
    profil = db.query(ProfilKos).filter(ProfilKos.id == 1).first()
    if not profil:
        raise HTTPException(status_code=404, detail="Profil kos belum diatur")
    
    # exclude_unset=True memastikan hanya kolom yang dikirim frontend yang diubah
    update_data = data_baru.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profil, key, value)
    
    db.commit()
    db.refresh(profil)
    return profil