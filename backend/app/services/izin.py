"""Perizinan penghuni (pulang kampung, menginap di luar, dll)."""
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.domain import PeranPengguna, Permission, User
from app.schemas.izin import IzinCreate, IzinUpdate


def hitung_durasi(jenis_izin: str, mulai, selesai) -> str:
    """Durasi izin dalam teks, mis. "5 hari"; Pulang Larut dihitung per malam."""
    hari = (selesai - mulai).days + 1
    if jenis_izin == "Pulang Larut":
        return f"{hari} malam"
    return f"{hari} hari"


def list_izin(db: Session, user: User, status_izin: Optional[str] = None) -> List[Permission]:
    q = db.query(Permission)
    if user.peran != PeranPengguna.pemilik:
        q = q.filter(Permission.user_id == user.id)
    if status_izin:
        q = q.filter(Permission.status_izin == status_izin)
    return q.order_by(Permission.created_at.desc(), Permission.id.desc()).all()


def buat_izin(db: Session, user: User, data: IzinCreate) -> Permission:
    if user.peran != PeranPengguna.penghuni:
        raise HTTPException(status_code=403, detail="Hanya penghuni yang dapat mengajukan izin")
    izin = Permission(
        user_id=user.id,
        jenis_izin=data.jenis_izin,
        tanggal_mulai=data.tanggal_mulai,
        tanggal_selesai=data.tanggal_selesai,
        durasi=hitung_durasi(data.jenis_izin, data.tanggal_mulai, data.tanggal_selesai),
        alasan=data.alasan,
        status_izin="Pending",
    )
    db.add(izin)
    db.commit()
    db.refresh(izin)
    return izin


def putuskan_izin(db: Session, izin_id: int, data: IzinUpdate) -> Permission:
    izin = db.query(Permission).filter(Permission.id == izin_id).first()
    if not izin:
        raise HTTPException(status_code=404, detail="Pengajuan izin tidak ditemukan")
    if izin.status_izin != "Pending":
        raise HTTPException(status_code=400, detail="Izin ini sudah diputuskan sebelumnya")
    izin.status_izin = data.status_izin
    if data.catatan_pemilik is not None:
        izin.catatan_pemilik = data.catatan_pemilik
    db.commit()
    db.refresh(izin)
    return izin
