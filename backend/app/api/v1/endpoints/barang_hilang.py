from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_validasi_user
from app.core.database import get_db
from app.schemas.barang_hilang import BarangHilangCreate, BarangHilangOut
from app.services import barang_hilang as barang_service

router = APIRouter()


@router.get("", response_model=List[BarangHilangOut])
def daftar_barang(
    status_barang: Optional[Literal["Aktif", "Selesai"]] = Query(default=None, alias="status"),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_validasi_user),
):
    return barang_service.list_barang(db, status_barang, q)


@router.post("", response_model=BarangHilangOut, status_code=status.HTTP_201_CREATED)
def lapor_barang(data: BarangHilangCreate, db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    return barang_service.buat_laporan(db, current_user, data)


@router.post("/{barang_id}/selesai", response_model=BarangHilangOut)
def tandai_selesai(barang_id: int, db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    """Hanya pelapor yang boleh menandai laporannya selesai (403 untuk pengguna lain)."""
    return barang_service.tandai_selesai(db, current_user, barang_id)
