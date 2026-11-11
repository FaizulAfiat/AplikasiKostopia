from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_penghuni_saja, get_validasi_user
from app.core.database import get_db
from app.schemas.penilaian import PenilaianCreate, PenilaianOut, RingkasanPenilaian
from app.services import penilaian as penilaian_service

router = APIRouter()


@router.get("", response_model=List[PenilaianOut])
def daftar_penilaian(db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    return penilaian_service.list_penilaian(db, current_user)


@router.get("/ringkasan", response_model=RingkasanPenilaian)
def ringkasan_penilaian(db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    return penilaian_service.ringkasan(db)


@router.post("", response_model=PenilaianOut, status_code=status.HTTP_201_CREATED)
def beri_penilaian(data: PenilaianCreate, db: Session = Depends(get_db), current_user=Depends(get_penghuni_saja)):
    return penilaian_service.buat_penilaian(db, current_user, data)
