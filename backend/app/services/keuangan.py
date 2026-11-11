"""Laporan keuangan kos: ringkasan, transaksi, pemasukan bulanan, pengeluaran, rekap Excel."""
from datetime import date, datetime, time
from io import BytesIO
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.waktu import awal_akhir_bulan, hari_ini, label_pendek, periode_dari, tambah_bulan
from app.models.domain import Expense, Transaction, TAGIHAN_LUNAS
from app.schemas.keuangan import PengeluaranCreate
from app.services import tagihan as tagihan_service


def rentang(dari: Optional[date], sampai: Optional[date]) -> tuple[date, date]:
    awal, akhir = awal_akhir_bulan(hari_ini())
    dari = dari or awal
    sampai = sampai or akhir
    if sampai < dari:
        raise HTTPException(status_code=422, detail="Tanggal 'sampai' tidak boleh sebelum 'dari'")
    return dari, sampai


def _lunas_dalam(db: Session, dari: date, sampai: date) -> List[Transaction]:
    return db.query(Transaction).filter(
        Transaction.status_tagihan == TAGIHAN_LUNAS,
        Transaction.diverifikasi_at >= datetime.combine(dari, time.min),
        Transaction.diverifikasi_at <= datetime.combine(sampai, time.max),
    ).all()


def _pengeluaran_dalam(db: Session, dari: date, sampai: date) -> List[Expense]:
    return db.query(Expense).filter(Expense.tanggal >= dari, Expense.tanggal <= sampai).all()


def ringkasan(db: Session, dari: Optional[date] = None, sampai: Optional[date] = None) -> dict:
    tagihan_service.pastikan_tagihan_bulan_ini(db)
    dari, sampai = rentang(dari, sampai)
    lunas = _lunas_dalam(db, dari, sampai)
    pemasukan = sum(int(t.jumlah_tagihan or 0) for t in lunas)
    pengeluaran = sum(int(e.nominal or 0) for e in _pengeluaran_dalam(db, dari, sampai))
    total_tunggakan, penunggak = tagihan_service.tunggakan(db)
    return {
        "pemasukan": pemasukan,
        "pengeluaran": pengeluaran,
        "laba_bersih": pemasukan - pengeluaran,
        "tunggakan": total_tunggakan,
        "jumlah_lunas": len(lunas),
        "jumlah_penunggak": penunggak,
    }


def transaksi(db: Session, dari: Optional[date] = None, sampai: Optional[date] = None) -> List[dict]:
    dari, sampai = rentang(dari, sampai)
    hasil = []
    for t in _lunas_dalam(db, dari, sampai):
        nama = t.penghuni.nama_lengkap if t.penghuni else "-"
        for k in t.komponen:
            jumlah = int(k.get("jumlah") or 0)
            is_sewa = str(k.get("nama", "")).lower().startswith("sewa")
            if not is_sewa and jumlah <= 0:
                continue
            hasil.append({
                "tanggal": t.diverifikasi_at.date(),
                "keterangan": f"{k.get('nama')} · {nama} ({t.periode_label})",
                "kategori": "Sewa" if is_sewa else "Tambahan",
                "nominal": jumlah,
                "_urut": t.diverifikasi_at,
            })
    for e in _pengeluaran_dalam(db, dari, sampai):
        hasil.append({
            "tanggal": e.tanggal,
            "keterangan": e.keterangan,
            "kategori": "Pengeluaran",
            "nominal": -int(e.nominal or 0),
            "_urut": datetime.combine(e.tanggal, time.max),
        })
    hasil.sort(key=lambda x: x["_urut"], reverse=True)
    for h in hasil:
        h.pop("_urut")
    return hasil


def pemasukan_bulanan(db: Session, bulan: int = 6) -> List[dict]:
    bulan = max(1, min(bulan, 24))
    awal_ini = hari_ini().replace(day=1)
    hasil = []
    for i in range(bulan - 1, -1, -1):
        awal = tambah_bulan(awal_ini, -i)
        _, akhir = awal_akhir_bulan(awal)
        periode = periode_dari(awal)
        total = sum(int(t.jumlah_tagihan or 0) for t in _lunas_dalam(db, awal, akhir))
        hasil.append({"periode": periode, "label": label_pendek(periode), "total": total})
    return hasil


def list_pengeluaran(db: Session, dari: Optional[date] = None, sampai: Optional[date] = None) -> List[Expense]:
    dari, sampai = rentang(dari, sampai)
    return db.query(Expense).filter(Expense.tanggal >= dari, Expense.tanggal <= sampai) \
        .order_by(Expense.tanggal.desc(), Expense.id.desc()).all()


def tambah_pengeluaran(db: Session, data: PengeluaranCreate) -> Expense:
    e = Expense(**data.model_dump())
    e.keterangan = e.keterangan.strip()
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def hapus_pengeluaran(db: Session, pengeluaran_id: int) -> None:
    e = db.query(Expense).filter(Expense.id == pengeluaran_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Pengeluaran tidak ditemukan")
    db.delete(e)
    db.commit()


def rekap_xlsx(db: Session, dari: Optional[date] = None, sampai: Optional[date] = None,
               nama_kos: str = "Kostopia") -> bytes:
    """Membuat file Excel berisi ringkasan dan daftar transaksi dalam rentang."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    dari, sampai = rentang(dari, sampai)
    r = ringkasan(db, dari, sampai)
    wb = Workbook()
    ws = wb.active
    ws.title = "Ringkasan"
    ws.append([f"Rekap Keuangan {nama_kos}"])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append([f"Periode {dari.isoformat()} s.d. {sampai.isoformat()}"])
    ws.append([])
    for label, key in [("Pemasukan", "pemasukan"), ("Pengeluaran", "pengeluaran"),
                       ("Laba bersih", "laba_bersih"), ("Tunggakan", "tunggakan"),
                       ("Jumlah tagihan lunas", "jumlah_lunas"), ("Jumlah penunggak", "jumlah_penunggak")]:
        ws.append([label, r[key]])
    for row in ws.iter_rows(min_row=4, min_col=2, max_col=2):
        for c in row:
            c.number_format = "#,##0"
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 18

    wt = wb.create_sheet("Transaksi")
    wt.append(["Tanggal", "Keterangan", "Kategori", "Nominal (Rp)"])
    for c in wt[1]:
        c.font = Font(bold=True)
    for t in transaksi(db, dari, sampai):
        wt.append([t["tanggal"], t["keterangan"], t["kategori"], t["nominal"]])
    for row in wt.iter_rows(min_row=2):
        row[0].number_format = "yyyy-mm-dd"
        row[3].number_format = "#,##0"
    for col, w in zip("ABCD", (12, 56, 14, 16)):
        wt.column_dimensions[col].width = w

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
