from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.domain import ProfilKos
from app.schemas.profil_kos import ProfilKosUpdate


def get_profil_kos(db: Session) -> ProfilKos:
    """Mengambil biodata/profil kos (baris pertama) atau raise 404 jika belum diatur."""
    profil = db.query(ProfilKos).order_by(ProfilKos.id).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil kos belum diatur"
        )
    return profil


def get_profil_atau_default(db: Session) -> ProfilKos:
    """Profil kos untuk perhitungan (tagihan/parkir); objek default jika belum diatur."""
    profil = db.query(ProfilKos).order_by(ProfilKos.id).first()
    if profil:
        return profil
    return ProfilKos(
        nama_kos="Kostopia", alamat_lengkap="", tanggal_jatuh_tempo=10, masa_tenggang_hari=5,
        tarif_parkir_motor=0, tarif_parkir_mobil=75000,
        kapasitas_parkir_motor=20, kapasitas_parkir_mobil=4,
    )


def create_profil_kos(db: Session, data_baru: ProfilKosUpdate) -> ProfilKos:
    """Membuat profil kos baru dengan pengecekan pencegahan duplikasi."""
    # 1. CEK PENCEGAHAN DUPLIKAT
    profil_lama = db.query(ProfilKos).first()
    if profil_lama:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil Kos sudah ada! Silakan gunakan fitur Edit (PUT)."
        )

    # 2. BUNGKUS DATA BARU (kolom yang tidak dikirim memakai nilai default model)
    data = data_baru.model_dump(exclude_none=True)
    if not data.get("nama_kos"):
        raise HTTPException(status_code=422, detail="Nama kos wajib diisi")
    data.setdefault("alamat_lengkap", "")
    profil_baru = ProfilKos(**data)

    # 3. SIMPAN KE DATABASE
    db.add(profil_baru)
    db.commit()
    db.refresh(profil_baru)
    return profil_baru


def update_profil_kos(db: Session, data_baru: ProfilKosUpdate) -> ProfilKos:
    """Mengubah biodata/profil kos."""
    profil = get_profil_kos(db)

    # exclude_unset=True memastikan hanya kolom yang dikirim frontend yang diubah
    update_data = data_baru.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ("nama_kos", "alamat_lengkap") and value is None:
            continue  # kolom wajib tidak boleh dikosongkan
        setattr(profil, key, value)

    db.commit()
    db.refresh(profil)
    return profil
