"""Aturan / tata tertib kos."""
from typing import List
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.domain import PeranPengguna, Rules, User
from app.schemas.aturan import AturanCreate, AturanUpdate


def list_aturan(db: Session, user: User) -> List[Rules]:
    q = db.query(Rules)
    if user.peran != PeranPengguna.pemilik:
        q = q.filter(Rules.status_aktif.is_(True))
    return q.order_by(Rules.urutan, Rules.id).all()


def _get(db: Session, aturan_id: int) -> Rules:
    r = db.query(Rules).filter(Rules.id == aturan_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Aturan tidak ditemukan")
    return r


def buat_aturan(db: Session, data: AturanCreate) -> Rules:
    urutan = (db.query(func.max(Rules.urutan)).scalar() or 0) + 1
    r = Rules(
        poin_aturan=data.judul.strip(),
        deskripsi=data.deskripsi,
        sanksi=data.sanksi,
        status_aktif=data.status_aktif,
        urutan=urutan,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def ubah_aturan(db: Session, aturan_id: int, data: AturanUpdate) -> Rules:
    r = _get(db, aturan_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if key in ("judul", "status_aktif", "urutan") and value is None:
            continue
        setattr(r, key, value)
    db.commit()
    db.refresh(r)
    return r


def hapus_aturan(db: Session, aturan_id: int) -> None:
    r = _get(db, aturan_id)
    db.delete(r)
    db.commit()
