from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja, get_validasi_user
from app.core.database import get_db
from app.schemas.aturan import AturanCreate, AturanOut, AturanUpdate
from app.services import aturan as aturan_service

router = APIRouter()


@router.get("", response_model=List[AturanOut])
def daftar_aturan(db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    return aturan_service.list_aturan(db, current_user)


@router.post("", response_model=AturanOut, status_code=status.HTTP_201_CREATED)
def tambah_aturan(data: AturanCreate, db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    return aturan_service.buat_aturan(db, data)


@router.put("/{aturan_id}", response_model=AturanOut)
def ubah_aturan(aturan_id: int, data: AturanUpdate, db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    return aturan_service.ubah_aturan(db, aturan_id, data)


@router.delete("/{aturan_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_aturan(aturan_id: int, db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    aturan_service.hapus_aturan(db, aturan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
