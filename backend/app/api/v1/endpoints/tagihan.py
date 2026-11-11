from typing import Dict, List, Literal, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja, get_validasi_user
from app.core.database import get_db
from app.schemas.tagihan import BuktiBayarIn, TagihanOut, VerifikasiIn
from app.services import tagihan as tagihan_service

router = APIRouter()

StatusTagihan = Literal["Belum Bayar", "Menunggu Verifikasi", "Lunas", "Ditolak"]
POLA_PERIODE = r"^\d{4}-(0[1-9]|1[0-2])$"


@router.get("", response_model=List[TagihanOut])
def daftar_tagihan(
    status_tagihan: Optional[StatusTagihan] = Query(default=None, alias="status"),
    periode: Optional[str] = Query(default=None, pattern=POLA_PERIODE),
    db: Session = Depends(get_db),
    current_user=Depends(get_validasi_user),
):
    return tagihan_service.list_tagihan(db, current_user, status_tagihan, periode)


@router.get("/ringkasan-status", response_model=Dict[str, int])
def ringkasan_status(
    periode: Optional[str] = Query(default=None, pattern=POLA_PERIODE),
    db: Session = Depends(get_db),
    current_user=Depends(get_pemilik_saja),
):
    return tagihan_service.ringkasan_status(db, periode)


@router.get("/{tagihan_id}", response_model=TagihanOut)
def detail_tagihan(tagihan_id: int, db: Session = Depends(get_db), current_user=Depends(get_validasi_user)):
    tagihan_service.pastikan_tagihan_bulan_ini(db)
    return tagihan_service.get_tagihan(db, tagihan_id, current_user)


@router.post("/{tagihan_id}/bukti", response_model=TagihanOut)
def unggah_bukti(
    tagihan_id: int, data: BuktiBayarIn,
    db: Session = Depends(get_db), current_user=Depends(get_validasi_user),
):
    return tagihan_service.unggah_bukti(db, tagihan_id, current_user, data.bukti_bayar_url)


@router.post("/{tagihan_id}/verifikasi", response_model=TagihanOut)
def verifikasi_tagihan(
    tagihan_id: int, data: VerifikasiIn,
    db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja),
):
    return tagihan_service.verifikasi(db, tagihan_id, current_user, data.disetujui, data.alasan)
