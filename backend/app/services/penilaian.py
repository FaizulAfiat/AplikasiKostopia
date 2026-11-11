"""Penilaian (rating bintang) & ulasan penghuni."""
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.domain import PeranPengguna, Rating, User
from app.schemas.penilaian import PenilaianCreate

DAFTAR_ASPEK = ["Kebersihan", "Keamanan", "Fasilitas", "Pelayanan", "Umum"]


def list_penilaian(db: Session, user: User) -> List[Rating]:
    q = db.query(Rating)
    if user.peran != PeranPengguna.pemilik:
        q = q.filter(Rating.user_id == user.id)
    return q.order_by(Rating.created_at.desc(), Rating.id.desc()).all()


def buat_penilaian(db: Session, user: User, data: PenilaianCreate) -> Rating:
    if user.peran != PeranPengguna.penghuni:
        raise HTTPException(status_code=403, detail="Hanya penghuni yang dapat memberi penilaian")
    r = Rating(user_id=user.id, **data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def _rata(skor: list[int]) -> float:
    return round(sum(skor) / len(skor), 1) if skor else 0.0


def ringkasan(db: Session) -> dict:
    semua = db.query(Rating).all()
    skor = [int(r.skor_bintang) for r in semua]
    distribusi = {str(i): 0 for i in range(1, 6)}
    for s in skor:
        distribusi[str(s)] = distribusi.get(str(s), 0) + 1
    per_aspek = []
    for aspek in DAFTAR_ASPEK:
        s = [int(r.skor_bintang) for r in semua if (r.aspek or "Umum") == aspek]
        per_aspek.append({"aspek": aspek, "rata_rata": _rata(s), "jumlah": len(s)})
    return {"rata_rata": _rata(skor), "jumlah": len(skor), "distribusi": distribusi, "per_aspek": per_aspek}
