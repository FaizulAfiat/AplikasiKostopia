"""Data ringkasan untuk dasbor Pemilik dan Penghuni."""
from datetime import datetime, time, timedelta
from sqlalchemy.orm import Session
from app.core.waktu import hari_ini, periode_dari
from app.models.domain import (
    Aspiration, Lease, LostFound, Permission, Rating, Room, Rules, Transaction, User,
    KAMAR_DIHUNI, SEWA_BERJALAN, SEWA_TENGGANG,
    TAGIHAN_LUNAS, TAGIHAN_MENUNGGU,
)
from app.schemas.tagihan import TagihanOut
from app.services import keuangan as keuangan_service
from app.services import penilaian as penilaian_service
from app.services import pengumuman as pengumuman_service
from app.services import tagihan as tagihan_service
from app.services.profil_kos import get_profil_atau_default

STATUS_PETA = {
    "Lunas": "Lunas",
    "Menunggu Verifikasi": "Menunggu",
    "Belum Bayar": "Belum Bayar",
    "Ditolak": "Belum Bayar",
}


def _status_peta(room: Room, tagihan_ini: dict) -> str:
    lease = room.sewa_aktif
    if lease is None:
        return "Kosong"
    if lease.status_sewa == SEWA_TENGGANG:
        return "Masa Tenggang"
    t = tagihan_ini.get(lease.id)
    return STATUS_PETA.get(t.status_tagihan, "Belum Bayar") if t else "Belum Bayar"


def _aktivitas(db: Session, batas: int = 10) -> list[dict]:
    hasil = []

    def orang(u: User):
        return (u.nama_lengkap, u.kamar) if u else (None, None)

    for a in db.query(Aspiration).order_by(Aspiration.created_at.desc()).limit(batas).all():
        nama, kamar = orang(a.pelapor)
        hasil.append({"jenis": "Aspirasi", "judul": a.judul or "Aspirasi baru", "nama": nama, "kamar": kamar, "waktu": a.created_at})
    for i in db.query(Permission).order_by(Permission.created_at.desc()).limit(batas).all():
        nama, kamar = orang(i.pemohon)
        hasil.append({"jenis": "Izin", "judul": f"Izin {i.jenis_izin} · {i.durasi}", "nama": nama, "kamar": kamar, "waktu": i.created_at})
    for t in db.query(Transaction).filter(Transaction.status_tagihan == TAGIHAN_LUNAS,
                                          Transaction.diverifikasi_at.isnot(None)) \
            .order_by(Transaction.diverifikasi_at.desc()).limit(batas).all():
        nama, kamar = orang(t.penghuni)
        hasil.append({"jenis": "Lunas", "judul": f"Pembayaran {t.periode_label} lunas", "nama": nama,
                      "kamar": t.kamar or kamar, "waktu": t.diverifikasi_at})
    for r in db.query(Rating).order_by(Rating.created_at.desc()).limit(batas).all():
        nama, kamar = orang(r.pengguna)
        hasil.append({"jenis": "Ulasan", "judul": f"Memberi {r.skor_bintang} bintang · {r.aspek}", "nama": nama, "kamar": kamar, "waktu": r.created_at})
    for b in db.query(LostFound).order_by(LostFound.created_at.desc()).limit(batas).all():
        nama, kamar = orang(b.pelapor)
        hasil.append({"jenis": "Barang Hilang", "judul": f"{b.jenis}: {b.judul_barang}", "nama": nama, "kamar": kamar, "waktu": b.created_at})
    hasil = [h for h in hasil if h["waktu"] is not None]
    hasil.sort(key=lambda h: h["waktu"], reverse=True)
    return hasil[:batas]


def dasbor_pemilik(db: Session) -> dict:
    tagihan_service.pastikan_tagihan_bulan_ini(db)
    today = hari_ini()
    periode = periode_dari(today)
    profil = get_profil_atau_default(db)

    rooms = db.query(Room).order_by(Room.lantai, Room.nomor_kamar).all()
    tagihan_bulan_ini = db.query(Transaction).filter(Transaction.periode == periode).all()
    per_lease = {t.lease_id: t for t in tagihan_bulan_ini}
    ringkas = keuangan_service.ringkasan(db)
    rating = penilaian_service.ringkasan(db)

    lantai_map: dict[int, list] = {}
    for room in rooms:
        penghuni = room.penghuni
        lantai_map.setdefault(room.lantai or 1, []).append({
            "id": room.id,
            "nomor": room.nomor_kamar,
            "status": _status_peta(room, per_lease),
            "penghuni": penghuni.nama_lengkap if penghuni else None,
        })

    leases_berjalan = db.query(Lease).filter(Lease.status_sewa.in_(SEWA_BERJALAN)).all()
    menunggu = db.query(Transaction).filter(Transaction.status_tagihan == TAGIHAN_MENUNGGU) \
        .order_by(Transaction.tanggal_unggah.desc(), Transaction.id.desc()).all()

    return {
        "nama_kos": profil.nama_kos,
        "total_kamar": len(rooms),
        "kamar_terisi": sum(1 for r in rooms if r.sewa_aktif is not None or r.status_ketersediaan == KAMAR_DIHUNI),
        "pemasukan_bulan_ini": ringkas["pemasukan"],
        "tagihan_lunas": sum(1 for t in tagihan_bulan_ini if t.status_tagihan == TAGIHAN_LUNAS),
        "total_tagihan": len(tagihan_bulan_ini),
        "tunggakan": ringkas["tunggakan"],
        "jumlah_penunggak": ringkas["jumlah_penunggak"],
        "jumlah_tenggang": sum(1 for l in leases_berjalan if l.status_sewa == SEWA_TENGGANG),
        "rating_rata": rating["rata_rata"],
        "jumlah_ulasan": rating["jumlah"],
        "perlu_tindakan": {
            "bukti_menunggu": len(menunggu),
            "izin_pending": db.query(Permission).filter(Permission.status_izin == "Pending").count(),
            "aspirasi_baru": db.query(Aspiration).filter(Aspiration.status_penanganan == "Menunggu").count(),
            "sewa_berakhir_7_hari": sum(
                1 for l in leases_berjalan
                if l.tanggal_jatuh_tempo and today <= l.tanggal_jatuh_tempo <= today + timedelta(days=7)
            ),
        },
        "pemasukan_6_bulan": keuangan_service.pemasukan_bulanan(db, 6),
        "peta_kamar": [{"lantai": k, "kamar": v} for k, v in sorted(lantai_map.items())],
        "menunggu_verifikasi": [TagihanOut.model_validate(t) for t in menunggu],
        "aktivitas": _aktivitas(db),
    }


def dasbor_penghuni(db: Session, user: User) -> dict:
    tagihan_service.pastikan_tagihan_bulan_ini(db)
    db.refresh(user)
    profil = get_profil_atau_default(db)
    lease = user.sewa_aktif or (max(user.sewa, key=lambda s: s.id) if user.sewa else None)

    tagihan_aktif = None
    if lease:
        tagihan_milik = db.query(Transaction).filter(Transaction.lease_id == lease.id) \
            .order_by(Transaction.periode.desc(), Transaction.id.desc()).all()
        belum_lunas = [t for t in tagihan_milik if t.status_tagihan != TAGIHAN_LUNAS]
        if belum_lunas:
            tagihan_aktif = belum_lunas[-1]  # tagihan belum lunas paling lama dulu
        elif tagihan_milik:
            tagihan_aktif = tagihan_milik[0]

    pengumuman = pengumuman_service.list_pengumuman(db, user)

    permintaan = []
    for a in db.query(Aspiration).filter(Aspiration.user_id == user.id).all():
        permintaan.append({"jenis": "Aspirasi", "id": a.id, "judul": a.judul or "Aspirasi",
                           "status": a.status_penanganan, "created_at": a.created_at})
    for i in db.query(Permission).filter(Permission.user_id == user.id).all():
        permintaan.append({"jenis": "Izin", "id": i.id, "judul": f"Izin {i.jenis_izin} · {i.durasi}",
                           "status": i.status_izin, "created_at": i.created_at})
    permintaan.sort(key=lambda p: p["created_at"] or datetime.combine(hari_ini(), time.min), reverse=True)

    return {
        "nama_kos": profil.nama_kos,
        "kamar": lease.kamar.nomor_kamar if lease and lease.kamar else None,
        "status_sewa": lease.status_sewa if lease else None,
        "sewa_mulai": lease.tanggal_mulai if lease else None,
        "sewa_sampai": lease.tanggal_jatuh_tempo if lease else None,
        "tagihan_aktif": TagihanOut.model_validate(tagihan_aktif) if tagihan_aktif else None,
        "pengumuman_terbaru": pengumuman[0] if pengumuman else None,
        "permintaan": permintaan[:5],
        "jumlah_aturan_aktif": db.query(Rules).filter(Rules.status_aktif.is_(True)).count(),
    }
