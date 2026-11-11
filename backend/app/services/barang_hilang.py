"""Barang hilang & temuan (UC-15)."""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.waktu import sekarang
from app.models.domain import LostFound, User
from app.schemas.barang_hilang import BarangHilangCreate


def list_barang(db: Session, status_barang: Optional[str] = None, q: Optional[str] = None) -> List[LostFound]:
    query = db.query(LostFound)
    if status_barang:
        query = query.filter(LostFound.status_barang == status_barang)
    if q and q.strip():
        pola = f"%{q.strip()}%"
        query = query.filter(or_(
            LostFound.judul_barang.ilike(pola),
            LostFound.deskripsi.ilike(pola),
            LostFound.lokasi.ilike(pola),
        ))
    if status_barang == "Selesai":
        return query.order_by(LostFound.selesai_at.desc(), LostFound.id.desc()).all()
    # Aktif (atau semua): yang aktif dulu, terbaru dulu
    hasil = query.order_by(LostFound.created_at.desc(), LostFound.id.desc()).all()
    return sorted(hasil, key=lambda b: b.status_barang != "Aktif")


def buat_laporan(db: Session, user: User, data: BarangHilangCreate) -> LostFound:
    # Skenario alternatif 6a: nama barang kosong
    if not data.judul_barang or not data.judul_barang.strip():
        raise HTTPException(status_code=422, detail="Nama barang wajib diisi")
    barang = LostFound(
        user_id=user.id,
        jenis=data.jenis,
        judul_barang=data.judul_barang.strip(),
        deskripsi=data.deskripsi,
        lokasi=data.lokasi,
        foto_url=data.foto_url,
        status_barang="Aktif",
    )
    db.add(barang)
    db.commit()
    db.refresh(barang)
    return barang


def tandai_selesai(db: Session, user: User, barang_id: int) -> LostFound:
    barang = db.query(LostFound).filter(LostFound.id == barang_id).first()
    if not barang:
        raise HTTPException(status_code=404, detail="Laporan barang tidak ditemukan")
    if barang.user_id != user.id:
        raise HTTPException(status_code=403, detail="Hanya pelapor yang dapat menandai laporan ini selesai")
    if barang.status_barang != "Selesai":
        barang.status_barang = "Selesai"
        barang.selesai_at = sekarang()
        db.commit()
        db.refresh(barang)
    return barang
