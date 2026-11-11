"""Kendaraan & parkir penghuni."""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.domain import PeranPengguna, User, Vehicle
from app.schemas.kendaraan import KendaraanCreate, KendaraanUpdate
from app.services.profil_kos import get_profil_atau_default


def _normalisasi_plat(plat: str) -> str:
    return " ".join(plat.upper().split())


def list_kendaraan(db: Session, user: User) -> List[Vehicle]:
    q = db.query(Vehicle)
    if user.peran != PeranPengguna.pemilik:
        q = q.filter(Vehicle.user_id == user.id)
    return q.order_by(Vehicle.jenis_kendaraan.desc(), Vehicle.slot_parkir, Vehicle.id).all()


def ringkasan(db: Session) -> dict:
    profil = get_profil_atau_default(db)
    motor = db.query(Vehicle).filter(Vehicle.jenis_kendaraan == "Motor").count()
    mobil = db.query(Vehicle).filter(Vehicle.jenis_kendaraan == "Mobil").count()
    return {
        "motor_terpakai": motor,
        "motor_kapasitas": int(profil.kapasitas_parkir_motor or 0),
        "mobil_terpakai": mobil,
        "mobil_kapasitas": int(profil.kapasitas_parkir_mobil or 0),
    }


def tambah_kendaraan(db: Session, user: User, data: KendaraanCreate) -> Vehicle:
    if user.peran != PeranPengguna.penghuni:
        raise HTTPException(status_code=403, detail="Hanya penghuni yang dapat mendaftarkan kendaraan")
    plat = _normalisasi_plat(data.nomor_polisi)
    if db.query(Vehicle).filter(Vehicle.nomor_polisi == plat).first():
        raise HTTPException(status_code=400, detail="Nomor polisi sudah terdaftar")
    r = ringkasan(db)
    if data.jenis_kendaraan == "Motor" and r["motor_terpakai"] >= r["motor_kapasitas"]:
        raise HTTPException(status_code=400, detail="Kapasitas parkir motor sudah penuh")
    if data.jenis_kendaraan == "Mobil" and r["mobil_terpakai"] >= r["mobil_kapasitas"]:
        raise HTTPException(status_code=400, detail="Kapasitas parkir mobil sudah penuh")
    kendaraan = Vehicle(
        user_id=user.id,
        nomor_polisi=plat,
        jenis_kendaraan=data.jenis_kendaraan,
        merk_warna=data.merk_warna,
    )
    db.add(kendaraan)
    db.commit()
    db.refresh(kendaraan)
    return kendaraan


def _get(db: Session, kendaraan_id: int) -> Vehicle:
    kendaraan = db.query(Vehicle).filter(Vehicle.id == kendaraan_id).first()
    if not kendaraan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kendaraan tidak ditemukan")
    return kendaraan


def ubah_kendaraan(db: Session, user: User, kendaraan_id: int, data: KendaraanUpdate) -> Vehicle:
    kendaraan = _get(db, kendaraan_id)
    perubahan = data.model_dump(exclude_unset=True)
    if user.peran == PeranPengguna.pemilik:
        if "slot_parkir" in perubahan:
            slot = (perubahan["slot_parkir"] or "").strip() or None
            if slot:
                bentrok = db.query(Vehicle).filter(Vehicle.slot_parkir == slot, Vehicle.id != kendaraan.id).first()
                if bentrok:
                    raise HTTPException(status_code=400, detail=f"Slot {slot} sudah dipakai {bentrok.nomor_polisi}")
            kendaraan.slot_parkir = slot
        if "merk_warna" in perubahan:
            kendaraan.merk_warna = perubahan["merk_warna"]
    else:
        if kendaraan.user_id != user.id:
            raise HTTPException(status_code=403, detail="Akses ditolak: ini bukan kendaraan Anda")
        # Penghuni hanya boleh mengubah merk_warna; slot_parkir diatur pemilik kos
        if "merk_warna" in perubahan:
            kendaraan.merk_warna = perubahan["merk_warna"]
    db.commit()
    db.refresh(kendaraan)
    return kendaraan


def hapus_kendaraan(db: Session, user: User, kendaraan_id: int) -> None:
    kendaraan = _get(db, kendaraan_id)
    if user.peran != PeranPengguna.pemilik and kendaraan.user_id != user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak: ini bukan kendaraan Anda")
    db.delete(kendaraan)
    db.commit()
