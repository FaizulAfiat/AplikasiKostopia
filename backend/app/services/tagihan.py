"""Logika tagihan bulanan: pembuatan otomatis, masa tenggang, unggah bukti, verifikasi."""
from datetime import timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.waktu import hari_ini, periode_dari, sekarang, tambah_bulan, tanggal_di_periode, awal_akhir_bulan
from app.models.domain import (
    Lease, PeranPengguna, ProfilKos, Transaction, User,
    SEWA_AKTIF, SEWA_BERJALAN, SEWA_KELUAR, SEWA_TENGGANG,
    TAGIHAN_BELUM, TAGIHAN_DITOLAK, TAGIHAN_LUNAS, TAGIHAN_MENUNGGU,
)
from app.services.profil_kos import get_profil_atau_default

SEMUA_STATUS_TAGIHAN = [TAGIHAN_MENUNGGU, TAGIHAN_LUNAS, TAGIHAN_DITOLAK, TAGIHAN_BELUM]
# Tagihan yang dianggap menunggak bila lewat jatuh tempo. "Menunggu Verifikasi" tidak termasuk
# karena penghuni sudah membayar dan tinggal menunggu pemeriksaan pemilik.
STATUS_TERTUNGGAK = (TAGIHAN_BELUM, TAGIHAN_DITOLAK)


def hitung_komponen(lease: Lease, profil: ProfilKos) -> list[dict]:
    """Komponen tagihan: sewa kamar + parkir (motor pertama gratis, tiap mobil berbayar)."""
    kamar = lease.kamar
    komponen = [{"nama": f"Sewa kamar {kamar.nomor_kamar}", "jumlah": int(kamar.harga_dasar or 0)}]
    kendaraan = sorted(lease.penyewa.kendaraan if lease.penyewa else [], key=lambda v: v.id)
    motor = [v for v in kendaraan if v.jenis_kendaraan == "Motor"]
    mobil = [v for v in kendaraan if v.jenis_kendaraan == "Mobil"]
    if motor:
        tambahan = (len(motor) - 1) * int(profil.tarif_parkir_motor or 0)
        nama = "Parkir motor" if len(motor) == 1 else f"Parkir motor ({len(motor)})"
        komponen.append({"nama": nama, "jumlah": tambahan})
    if mobil:
        nama = "Parkir mobil" if len(mobil) == 1 else f"Parkir mobil ({len(mobil)})"
        komponen.append({"nama": nama, "jumlah": len(mobil) * int(profil.tarif_parkir_mobil or 0)})
    return komponen


def buat_tagihan(db: Session, lease: Lease, periode: str, profil: ProfilKos) -> Transaction:
    """Membuat objek tagihan untuk satu sewa & periode (belum di-commit)."""
    komponen = hitung_komponen(lease, profil)
    jatuh_tempo = tanggal_di_periode(periode, int(profil.tanggal_jatuh_tempo or 10))
    # Sewa yang baru mulai setelah tanggal jatuh tempo: tagihan pertama jatuh tempo di hari mulai
    if lease.tanggal_mulai and periode_dari(lease.tanggal_mulai) == periode and lease.tanggal_mulai > jatuh_tempo:
        jatuh_tempo = lease.tanggal_mulai
    tagihan = Transaction(
        lease_id=lease.id,
        periode=periode,
        komponen_biaya=komponen,
        jumlah_tagihan=sum(k["jumlah"] for k in komponen),
        jatuh_tempo=jatuh_tempo,
        batas_tenggang=jatuh_tempo + timedelta(days=int(profil.masa_tenggang_hari or 0)),
        status_tagihan=TAGIHAN_BELUM,
    )
    db.add(tagihan)
    return tagihan


def pastikan_tagihan_bulan_ini(db: Session) -> None:
    """Idempoten: setiap sewa Aktif/Masa Tenggang punya tagihan periode bulan berjalan,
    lalu sewa yang punya tagihan lewat jatuh tempo & belum lunas menjadi Masa Tenggang."""
    today = hari_ini()
    periode = periode_dari(today)
    _, akhir_bulan = awal_akhir_bulan(today)
    profil = get_profil_atau_default(db)

    leases = db.query(Lease).filter(Lease.status_sewa.in_(SEWA_BERJALAN)).all()
    sudah_ada = {
        lid for (lid,) in db.query(Transaction.lease_id).filter(Transaction.periode == periode).all()
    }
    berubah = False
    for lease in leases:
        if lease.id in sudah_ada or lease.kamar is None:
            continue
        if lease.tanggal_mulai and lease.tanggal_mulai > akhir_bulan:
            continue  # sewa baru mulai bulan depan
        buat_tagihan(db, lease, periode, profil)
        berubah = True
    if berubah:
        try:
            db.commit()
        except IntegrityError:
            # Request lain sudah membuat tagihan yang sama (unik lease_id + periode)
            db.rollback()

    # Perbarui status sewa menjadi Masa Tenggang jika ada tagihan lewat jatuh tempo
    terlambat = {
        lid for (lid,) in db.query(Transaction.lease_id).filter(
            Transaction.status_tagihan.in_(STATUS_TERTUNGGAK),
            Transaction.jatuh_tempo < today,
        ).all()
    }
    berubah = False
    for lease in leases:
        if lease.status_sewa == SEWA_AKTIF and lease.id in terlambat:
            lease.status_sewa = SEWA_TENGGANG
            berubah = True
    if berubah:
        db.commit()


def tagihan_periode_sewa(db: Session, lease_id: int, periode: Optional[str] = None) -> Optional[Transaction]:
    periode = periode or periode_dari(hari_ini())
    return db.query(Transaction).filter(
        Transaction.lease_id == lease_id, Transaction.periode == periode
    ).first()


def list_tagihan(db: Session, user: User, status_tagihan: Optional[str] = None,
                 periode: Optional[str] = None) -> List[Transaction]:
    pastikan_tagihan_bulan_ini(db)
    q = db.query(Transaction).join(Lease, Transaction.lease_id == Lease.id)
    if user.peran != PeranPengguna.pemilik:
        q = q.filter(Lease.user_id == user.id)
    if status_tagihan:
        q = q.filter(Transaction.status_tagihan == status_tagihan)
    if periode:
        q = q.filter(Transaction.periode == periode)
    return q.order_by(Transaction.periode.desc(), Transaction.id.desc()).all()


def get_tagihan(db: Session, tagihan_id: int, user: User) -> Transaction:
    tagihan = db.query(Transaction).filter(Transaction.id == tagihan_id).first()
    if not tagihan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tagihan tidak ditemukan")
    if user.peran != PeranPengguna.pemilik and tagihan.sewa.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak: ini bukan tagihan Anda")
    return tagihan


def unggah_bukti(db: Session, tagihan_id: int, user: User, bukti_url: str) -> Transaction:
    if user.peran == PeranPengguna.pemilik:
        raise HTTPException(status_code=403, detail="Hanya penghuni pemilik tagihan yang dapat mengunggah bukti")
    tagihan = get_tagihan(db, tagihan_id, user)
    if tagihan.status_tagihan not in (TAGIHAN_BELUM, TAGIHAN_DITOLAK):
        raise HTTPException(status_code=400, detail=f"Tagihan berstatus {tagihan.status_tagihan}, bukti tidak dapat diunggah")
    if not bukti_url or not bukti_url.strip():
        raise HTTPException(status_code=422, detail="Bukti pembayaran wajib diunggah")
    tagihan.bukti_bayar_url = bukti_url.strip()
    tagihan.tanggal_unggah = sekarang()
    tagihan.status_tagihan = TAGIHAN_MENUNGGU
    tagihan.alasan_tolak = None
    db.commit()
    db.refresh(tagihan)
    return tagihan


def verifikasi(db: Session, tagihan_id: int, user: User, disetujui: bool, alasan: Optional[str]) -> Transaction:
    tagihan = get_tagihan(db, tagihan_id, user)
    if tagihan.status_tagihan != TAGIHAN_MENUNGGU:
        raise HTTPException(status_code=400, detail="Hanya tagihan berstatus Menunggu Verifikasi yang dapat diverifikasi")
    if disetujui:
        tagihan.status_tagihan = TAGIHAN_LUNAS
        tagihan.diverifikasi_at = sekarang()
        tagihan.alasan_tolak = None
        lease = tagihan.sewa
        if lease.tanggal_jatuh_tempo:
            lease.tanggal_jatuh_tempo = tambah_bulan(lease.tanggal_jatuh_tempo, 1)
        if lease.status_sewa != SEWA_KELUAR:
            lease.status_sewa = SEWA_AKTIF
    else:
        if not alasan or not alasan.strip():
            raise HTTPException(status_code=422, detail="Alasan penolakan wajib diisi")
        tagihan.status_tagihan = TAGIHAN_DITOLAK
        tagihan.alasan_tolak = alasan.strip()
    db.commit()
    db.refresh(tagihan)
    return tagihan


def ringkasan_status(db: Session, periode: Optional[str] = None) -> dict:
    pastikan_tagihan_bulan_ini(db)
    periode = periode or periode_dari(hari_ini())
    hasil = {s: 0 for s in SEMUA_STATUS_TAGIHAN}
    for (st,) in db.query(Transaction.status_tagihan).filter(Transaction.periode == periode).all():
        hasil[st] = hasil.get(st, 0) + 1
    return hasil


def tunggakan(db: Session) -> tuple[int, int]:
    """(total nominal, jumlah sewa penunggak) dari tagihan Belum Bayar/Ditolak yang lewat jatuh tempo."""
    rows = db.query(Transaction).filter(
        Transaction.status_tagihan.in_(STATUS_TERTUNGGAK),
        Transaction.jatuh_tempo < hari_ini(),
    ).all()
    return sum(int(t.jumlah_tagihan or 0) for t in rows), len({t.lease_id for t in rows})
