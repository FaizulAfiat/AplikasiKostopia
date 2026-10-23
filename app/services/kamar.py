from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.domain import Room
from app.schemas.kamar import RoomCreate, RoomUpdate

def get_all_kamar(db: Session) -> List[Room]:
    """Mengambil semua daftar kamar kos."""
    return db.query(Room).all()

def get_kamar_by_id(db: Session, kamar_id: int) -> Room:
    """Mengambil satu kamar berdasarkan ID atau raise 404 jika tidak ditemukan."""
    kamar = db.query(Room).filter(Room.id == kamar_id).first()
    if not kamar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Kamar tidak ditemukan."
        )
    return kamar

def create_kamar(db: Session, kamar_in: RoomCreate) -> Room:
    """Menambahkan kamar baru dengan pengecekan duplikasi nomor kamar."""
    kamar_ada = db.query(Room).filter(Room.nomor_kamar == kamar_in.nomor_kamar).first()
    if kamar_ada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Nomor kamar sudah terdaftar."
        )
    
    kamar_baru = Room(**kamar_in.model_dump())
    db.add(kamar_baru)
    db.commit()
    db.refresh(kamar_baru)
    return kamar_baru

def update_kamar(db: Session, kamar_id: int, kamar_in: RoomUpdate) -> Room:
    """Memperbarui informasi kamar berdasarkan ID."""
    kamar = get_kamar_by_id(db, kamar_id)
    
    update_data = kamar_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kamar, key, value)
        
    db.commit()
    db.refresh(kamar)
    return kamar

def delete_kamar(db: Session, kamar_id: int) -> None:
    """Menghapus kamar berdasarkan ID."""
    kamar = get_kamar_by_id(db, kamar_id)
    
    db.delete(kamar)
    db.commit()
    return None
