"""Aspirasi/keluhan penghuni."""
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.domain import Aspiration, PeranPengguna, User
from app.schemas.aspirasi import AspirasiCreate, AspirasiUpdate


def list_aspirasi(db: Session, user: User, status_penanganan: Optional[str] = None) -> List[Aspiration]:
    q = db.query(Aspiration)
    if user.peran != PeranPengguna.pemilik:
        q = q.filter(Aspiration.user_id == user.id)
    if status_penanganan:
        q = q.filter(Aspiration.status_penanganan == status_penanganan)
    return q.order_by(Aspiration.created_at.desc(), Aspiration.id.desc()).all()


def buat_aspirasi(db: Session, user: User, data: AspirasiCreate) -> Aspiration:
    if user.peran != PeranPengguna.penghuni:
        raise HTTPException(status_code=403, detail="Hanya penghuni yang dapat mengirim aspirasi")
    a = Aspiration(
        user_id=user.id,
        judul=data.judul,
        kategori=data.kategori,
        deskripsi_kendala=data.deskripsi_kendala,
        lampiran_foto_url=[u for u in data.lampiran_foto_urls if u],
        status_penanganan="Menunggu",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def ubah_aspirasi(db: Session, aspirasi_id: int, data: AspirasiUpdate) -> Aspiration:
    a = db.query(Aspiration).filter(Aspiration.id == aspirasi_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aspirasi tidak ditemukan")
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "status_penanganan" and value is None:
            continue
        setattr(a, key, value)
    db.commit()
    db.refresh(a)
    return a
