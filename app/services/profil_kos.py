from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.domain import ProfilKos
from app.schemas.profil_kos import ProfilKosUpdate

def get_profil_kos(db: Session) -> ProfilKos:
    """Mengambil biodata/profil kos (id=1) atau raise 404 jika belum diatur."""
    profil = db.query(ProfilKos).filter(ProfilKos.id == 1).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profil kos belum diatur"
        )
    return profil

def create_profil_kos(db: Session, data_baru: ProfilKosUpdate) -> ProfilKos:
    """Membuat profil kos baru dengan pengecekan pencegahan duplikasi."""
    # 1. CEK PENCEGAHAN DUPLIKAT
    profil_lama = db.query(ProfilKos).first()
    if profil_lama:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Profil Kos sudah ada! Silakan gunakan fitur Edit (PUT)."
        )
    
    # 2. BUNGKUS DATA BARU
    profil_baru = ProfilKos(**data_baru.model_dump())
    
    # 3. SIMPAN KE DATABASE
    db.add(profil_baru)
    db.commit()
    db.refresh(profil_baru)
    return profil_baru

def update_profil_kos(db: Session, data_baru: ProfilKosUpdate) -> ProfilKos:
    """Mengubah biodata/profil kos (id=1)."""
    profil = get_profil_kos(db)
    
    # exclude_unset=True memastikan hanya kolom yang dikirim frontend yang diubah
    update_data = data_baru.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profil, key, value)
    
    db.commit()
    db.refresh(profil)
    return profil
