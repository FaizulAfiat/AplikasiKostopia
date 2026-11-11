from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja, get_penghuni_saja, get_validasi_user
from app.core.database import get_db
from app.schemas.aspirasi import AspirasiCreate, AspirasiOut, AspirasiUpdate, StatusAspirasi
from app.services import aspirasi as aspirasi_service

router = APIRouter()


@router.get("", response_model=List[AspirasiOut])
def daftar_aspirasi(
    status_penanganan: Optional[StatusAspirasi] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_validasi_user),
):
    return aspirasi_service.list_aspirasi(db, current_user, status_penanganan)


@router.post("", response_model=AspirasiOut, status_code=status.HTTP_201_CREATED)
def kirim_aspirasi(data: AspirasiCreate, db: Session = Depends(get_db), current_user=Depends(get_penghuni_saja)):
    return aspirasi_service.buat_aspirasi(db, current_user, data)


@router.patch("/{aspirasi_id}", response_model=AspirasiOut)
def tanggapi_aspirasi(
    aspirasi_id: int, data: AspirasiUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja),
):
    return aspirasi_service.ubah_aspirasi(db, aspirasi_id, data)
