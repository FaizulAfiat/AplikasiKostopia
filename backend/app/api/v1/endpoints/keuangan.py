from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja
from app.core.database import get_db
from app.schemas.keuangan import (
    PemasukanBulanan, PengeluaranCreate, PengeluaranOut, RingkasanKeuangan, TransaksiOut,
)
from app.services import keuangan as keuangan_service
from app.services.profil_kos import get_profil_atau_default

# Semua endpoint keuangan khusus Pemilik
router = APIRouter(dependencies=[Depends(get_pemilik_saja)])


@router.get("/ringkasan", response_model=RingkasanKeuangan)
def ringkasan(dari: Optional[date] = None, sampai: Optional[date] = None, db: Session = Depends(get_db)):
    return keuangan_service.ringkasan(db, dari, sampai)


@router.get("/transaksi", response_model=List[TransaksiOut])
def transaksi(dari: Optional[date] = None, sampai: Optional[date] = None, db: Session = Depends(get_db)):
    return keuangan_service.transaksi(db, dari, sampai)


@router.get("/pemasukan-bulanan", response_model=List[PemasukanBulanan])
def pemasukan_bulanan(bulan: int = Query(default=6, ge=1, le=24), db: Session = Depends(get_db)):
    return keuangan_service.pemasukan_bulanan(db, bulan)


@router.get("/pengeluaran", response_model=List[PengeluaranOut])
def daftar_pengeluaran(dari: Optional[date] = None, sampai: Optional[date] = None, db: Session = Depends(get_db)):
    return keuangan_service.list_pengeluaran(db, dari, sampai)


@router.post("/pengeluaran", response_model=PengeluaranOut, status_code=status.HTTP_201_CREATED)
def tambah_pengeluaran(data: PengeluaranCreate, db: Session = Depends(get_db)):
    return keuangan_service.tambah_pengeluaran(db, data)


@router.delete("/pengeluaran/{pengeluaran_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_pengeluaran(pengeluaran_id: int, db: Session = Depends(get_db)):
    keuangan_service.hapus_pengeluaran(db, pengeluaran_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/rekap.xlsx")
def rekap_excel(dari: Optional[date] = None, sampai: Optional[date] = None, db: Session = Depends(get_db)):
    dari, sampai = keuangan_service.rentang(dari, sampai)
    profil = get_profil_atau_default(db)
    isi = keuangan_service.rekap_xlsx(db, dari, sampai, profil.nama_kos)
    nama_file = f"rekap-keuangan-{dari.isoformat()}_{sampai.isoformat()}.xlsx"
    return Response(
        content=isi,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nama_file}"'},
    )
