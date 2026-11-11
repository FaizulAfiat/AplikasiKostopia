"""Pengumuman pemilik kos + penanda sudah dibaca."""
from typing import List
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.domain import (
    Announcement, AnnouncementRead, Lease, PeranPengguna, User, SEWA_BERJALAN,
)
from app.schemas.common import PersonRef
from app.schemas.pengumuman import PengumumanCreate, PengumumanOut, PengumumanUpdate


def _total_penghuni(db: Session) -> int:
    """Jumlah penghuni dengan sewa berjalan (target pembaca pengumuman)."""
    return db.query(Lease.user_id).filter(Lease.status_sewa.in_(SEWA_BERJALAN)).distinct().count()


def to_out(a: Announcement, user: User, total_penghuni: int) -> PengumumanOut:
    pembaca_ids = {r.user_id for r in a.pembaca}
    return PengumumanOut(
        id=a.id,
        judul=a.judul,
        isi_pengumuman=a.isi_pengumuman,
        disematkan=bool(a.disematkan),
        created_at=a.created_at,
        pembuat=PersonRef.model_validate(a.pembuat) if a.pembuat else None,
        dibaca_count=len(pembaca_ids),
        total_penghuni=total_penghuni,
        sudah_dibaca=user.id in pembaca_ids,
    )


def list_pengumuman(db: Session, user: User) -> List[PengumumanOut]:
    data = db.query(Announcement).order_by(
        Announcement.disematkan.desc(), Announcement.created_at.desc(), Announcement.id.desc()
    ).all()
    total = _total_penghuni(db)
    return [to_out(a, user, total) for a in data]


def _get(db: Session, pengumuman_id: int) -> Announcement:
    a = db.query(Announcement).filter(Announcement.id == pengumuman_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Pengumuman tidak ditemukan")
    return a


def buat_pengumuman(db: Session, user: User, data: PengumumanCreate) -> PengumumanOut:
    a = Announcement(user_id=user.id, **data.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return to_out(a, user, _total_penghuni(db))


def ubah_pengumuman(db: Session, user: User, pengumuman_id: int, data: PengumumanUpdate) -> PengumumanOut:
    a = _get(db, pengumuman_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(a, key, value)
    db.commit()
    db.refresh(a)
    return to_out(a, user, _total_penghuni(db))


def hapus_pengumuman(db: Session, pengumuman_id: int) -> None:
    a = _get(db, pengumuman_id)
    db.delete(a)
    db.commit()


def tandai_dibaca(db: Session, user: User, pengumuman_id: int) -> PengumumanOut:
    if user.peran != PeranPengguna.penghuni:
        raise HTTPException(status_code=403, detail="Hanya penghuni yang dapat menandai pengumuman")
    a = _get(db, pengumuman_id)
    sudah = db.query(AnnouncementRead).filter(
        AnnouncementRead.announcement_id == a.id, AnnouncementRead.user_id == user.id
    ).first()
    if not sudah:
        db.add(AnnouncementRead(announcement_id=a.id, user_id=user.id))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
        db.refresh(a)
    return to_out(a, user, _total_penghuni(db))
