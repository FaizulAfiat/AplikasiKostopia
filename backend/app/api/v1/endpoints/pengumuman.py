from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja, get_penghuni_saja, get_validasi_user
from app.core.database import get_db
from app.schemas.pengumuman import PengumumanCreate, PengumumanOut, PengumumanUpdate
from app.services import pengumuman as pengumuman_service

router = APIRouter()


@router.get("", response_model=List[PengumumanOut])
def daftar_pengumuman(db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    return pengumuman_service.list_pengumuman(db, current_user)


@router.post("", response_model=PengumumanOut, status_code=status.HTTP_201_CREATED)
def buat_pengumuman(data: PengumumanCreate, db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    return pengumuman_service.buat_pengumuman(db, current_user, data)


@router.patch("/{pengumuman_id}", response_model=PengumumanOut)
def ubah_pengumuman(
    pengumuman_id: int, data: PengumumanUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja),
):
    return pengumuman_service.ubah_pengumuman(db, current_user, pengumuman_id, data)


@router.delete("/{pengumuman_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_pengumuman(pengumuman_id: int, db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    pengumuman_service.hapus_pengumuman(db, pengumuman_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{pengumuman_id}/baca", response_model=PengumumanOut)
def tandai_dibaca(pengumuman_id: int, db: Session = Depends(get_db), current_user=Depends(get_penghuni_saja)):
    return pengumuman_service.tandai_dibaca(db, current_user, pengumuman_id)
