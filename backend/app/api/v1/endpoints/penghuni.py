from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja
from app.core.database import get_db
from app.schemas.penghuni import PenghuniOut, SewaCreate, SewaStatusUpdate, StatusSewa
from app.schemas.user import UserOut
from app.services import penghuni as penghuni_service

router = APIRouter()


@router.get("", response_model=List[PenghuniOut])
def daftar_penghuni(
    status_sewa: Optional[StatusSewa] = Query(default=None, alias="status"),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_pemilik_saja),
):
    return penghuni_service.list_penghuni(db, status_sewa, q)


@router.get("/belum-ditempatkan", response_model=List[UserOut])
def penghuni_belum_ditempatkan(db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    return penghuni_service.belum_ditempatkan(db)


@router.get("/{user_id}", response_model=PenghuniOut)
def detail_penghuni(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    return penghuni_service.detail_penghuni(db, user_id)


@router.post("/{user_id}/sewa", response_model=PenghuniOut, status_code=status.HTTP_201_CREATED)
def tempatkan_penghuni(
    user_id: int, data: SewaCreate,
    db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja),
):
    return penghuni_service.buat_sewa(db, user_id, data)


@router.patch("/{user_id}/status", response_model=PenghuniOut)
def ubah_status_sewa(
    user_id: int, data: SewaStatusUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja),
):
    return penghuni_service.ubah_status_sewa(db, user_id, data.status_sewa)
