from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.kamar import RoomCreate, RoomUpdate, RoomResponse
from app.api.v1.endpoints.deps import get_pemilik_saja, get_validasi_user
from app.core.database import get_db
from app.services import kamar as kamar_service

router = APIRouter()

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def tambah_kamar(
    kamar_in: RoomCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_pemilik_saja) # Proteksi RBAC: Hanya Pemilik
):
    return kamar_service.create_kamar(db, kamar_in)

@router.get("/", response_model=List[RoomResponse])
def ambil_semua_kamar(
    db: Session = Depends(get_db),
    current_user = Depends(get_validasi_user) # Pemilik & Penghuni bisa melihat list kamar
):
    return kamar_service.get_all_kamar(db)

@router.put("/{kamar_id}", response_model=RoomResponse)
def ubah_data_kamar(
    kamar_id: int, 
    kamar_in: RoomUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_pemilik_saja) # Proteksi RBAC: Hanya Pemilik
):
    return kamar_service.update_kamar(db, kamar_id, kamar_in)

@router.delete("/{kamar_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_kamar(
    kamar_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_pemilik_saja) # Proteksi RBAC: Hanya Pemilik
):
    return kamar_service.delete_kamar(db, kamar_id)