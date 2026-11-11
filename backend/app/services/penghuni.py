"""Manajemen penghuni & sewa (khusus Pemilik)."""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.waktu import tambah_bulan
from app.models.domain import (
    Lease, PeranPengguna, Room, User,
    KAMAR_DIHUNI, KAMAR_TERSEDIA, SEWA_AKTIF, SEWA_BERJALAN, SEWA_KELUAR,
)
from app.schemas.kendaraan import KendaraanOut
from app.schemas.penghuni import PenghuniOut, SewaCreate, SewaOut
from app.schemas.user import UserOut
from app.services import tagihan as tagihan_service


def sewa_terakhir(user: User) -> Optional[Lease]:
    """Sewa aktif jika ada; jika tidak, sewa terbaru (mis. Sudah Keluar)."""
    return user.sewa_aktif or (max(user.sewa, key=lambda s: s.id) if user.sewa else None)


def sewa_out(lease: Lease) -> SewaOut:
    return SewaOut(
        id=lease.id,
        kamar=lease.kamar.nomor_kamar if lease.kamar else None,
        room_id=lease.room_id,
        tanggal_mulai=lease.tanggal_mulai,
        tanggal_jatuh_tempo=lease.tanggal_jatuh_tempo,
        status_sewa=lease.status_sewa,
    )


def penghuni_out(db: Session, user: User) -> PenghuniOut:
    lease = sewa_terakhir(user)
    tagihan = tagihan_service.tagihan_periode_sewa(db, lease.id) if lease else None
    return PenghuniOut(
        user=UserOut.model_validate(user),
        sewa=sewa_out(lease) if lease else None,
        kendaraan=[KendaraanOut.model_validate(v) for v in sorted(user.kendaraan, key=lambda v: v.id)],
        tagihan_bulan_ini=tagihan.status_tagihan if tagihan else None,
    )


def get_penghuni_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.peran != PeranPengguna.penghuni:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Penghuni tidak ditemukan")
    return user


def list_penghuni(db: Session, status_sewa: Optional[str] = None, q: Optional[str] = None) -> List[PenghuniOut]:
    tagihan_service.pastikan_tagihan_bulan_ini(db)
    users = db.query(User).filter(User.peran == PeranPengguna.penghuni).all()
    hasil = []
    for user in users:
        lease = sewa_terakhir(user)
        if lease is None:
            continue
        if status_sewa and lease.status_sewa != status_sewa:
            continue
        if q:
            kata = q.strip().lower()
            kolom = [user.nama_lengkap or "", lease.kamar.nomor_kamar if lease.kamar else ""]
            kolom += [v.nomor_polisi or "" for v in user.kendaraan]
            if not any(kata in k.lower() for k in kolom):
                continue
        hasil.append((lease, user))
    # Terbaru dulu, yang Sudah Keluar di akhir
    hasil.sort(key=lambda x: (x[0].status_sewa == SEWA_KELUAR, -(x[0].tanggal_mulai.toordinal() if x[0].tanggal_mulai else 0), -x[0].id))
    return [penghuni_out(db, u) for _, u in hasil]


def detail_penghuni(db: Session, user_id: int) -> PenghuniOut:
    tagihan_service.pastikan_tagihan_bulan_ini(db)
    return penghuni_out(db, get_penghuni_user(db, user_id))


def belum_ditempatkan(db: Session) -> List[User]:
    users = db.query(User).filter(User.peran == PeranPengguna.penghuni).order_by(User.created_at.desc()).all()
    return [u for u in users if u.sewa_aktif is None]


def buat_sewa(db: Session, user_id: int, data: SewaCreate) -> PenghuniOut:
    user = get_penghuni_user(db, user_id)
    if user.sewa_aktif is not None:
        raise HTTPException(status_code=400, detail="Penghuni ini masih memiliki sewa aktif")
    kamar = db.query(Room).filter(Room.id == data.room_id).first()
    if not kamar:
        raise HTTPException(status_code=404, detail="Kamar tidak ditemukan.")
    if kamar.status_ketersediaan != KAMAR_TERSEDIA or kamar.sewa_aktif is not None:
        raise HTTPException(status_code=400, detail=f"Kamar {kamar.nomor_kamar} tidak tersedia")
    lease = Lease(
        user_id=user.id,
        room_id=kamar.id,
        tanggal_mulai=data.tanggal_mulai,
        tanggal_jatuh_tempo=tambah_bulan(data.tanggal_mulai, data.lama_bulan),
        status_sewa=SEWA_AKTIF,
    )
    kamar.status_ketersediaan = KAMAR_DIHUNI
    db.add(lease)
    db.commit()
    db.refresh(user)
    # Langsung buat tagihan periode bulan berjalan
    tagihan_service.pastikan_tagihan_bulan_ini(db)
    db.refresh(user)
    return penghuni_out(db, user)


def ubah_status_sewa(db: Session, user_id: int, status_baru: str) -> PenghuniOut:
    user = get_penghuni_user(db, user_id)
    lease = sewa_terakhir(user)
    if lease is None:
        raise HTTPException(status_code=404, detail="Penghuni belum memiliki sewa")
    if lease.status_sewa == SEWA_KELUAR and status_baru in SEWA_BERJALAN:
        kamar = lease.kamar
        if kamar.sewa_aktif is not None:
            raise HTTPException(status_code=400, detail=f"Kamar {kamar.nomor_kamar} sudah dihuni penghuni lain")
    lease.status_sewa = status_baru
    if status_baru == SEWA_KELUAR:
        lease.kamar.status_ketersediaan = KAMAR_TERSEDIA
    else:
        lease.kamar.status_ketersediaan = KAMAR_DIHUNI
    db.commit()
    db.refresh(user)
    return penghuni_out(db, user)
