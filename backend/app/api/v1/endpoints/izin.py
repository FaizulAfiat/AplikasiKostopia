from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja, get_penghuni_saja, get_validasi_user
from app.core.database import get_db
from app.schemas.izin import IzinCreate, IzinOut, IzinUpdate
from app.services import izin as izin_service

router = APIRouter()


@router.get("", response_model=List[IzinOut])
def daftar_izin(
    status_izin: Optional[Literal["Pending", "Disetujui", "Ditolak"]] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_validasi_user),
):
    return izin_service.list_izin(db, current_user, status_izin)


@router.post("", response_model=IzinOut, status_code=status.HTTP_201_CREATED)
def ajukan_izin(data: IzinCreate, db: Session = Depends(get_db), current_user=Depends(get_penghuni_saja)):
    return izin_service.buat_izin(db, current_user, data)


@router.patch("/{izin_id}", response_model=IzinOut)
def putuskan_izin(
    izin_id: int, data: IzinUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja),
):
    return izin_service.putuskan_izin(db, izin_id, data)
