from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja, get_validasi_user
from app.core.database import get_db
from app.schemas.kendaraan import KendaraanCreate, KendaraanOut, KendaraanUpdate, RingkasanParkir
from app.services import kendaraan as kendaraan_service

router = APIRouter()


@router.get("", response_model=List[KendaraanOut])
def daftar_kendaraan(db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    return kendaraan_service.list_kendaraan(db, current_user)


@router.get("/ringkasan", response_model=RingkasanParkir)
def ringkasan_parkir(db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    return kendaraan_service.ringkasan(db)


@router.post("", response_model=KendaraanOut, status_code=status.HTTP_201_CREATED)
def tambah_kendaraan(data: KendaraanCreate, db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    return kendaraan_service.tambah_kendaraan(db, current_user, data)


@router.patch("/{kendaraan_id}", response_model=KendaraanOut)
def ubah_kendaraan(
    kendaraan_id: int, data: KendaraanUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_validasi_user),
):
    return kendaraan_service.ubah_kendaraan(db, current_user, kendaraan_id, data)


@router.delete("/{kendaraan_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_kendaraan(kendaraan_id: int, db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    kendaraan_service.hapus_kendaraan(db, current_user, kendaraan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
