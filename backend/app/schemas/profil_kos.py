from pydantic import BaseModel
from typing import Optional
from app.schemas.common import ORMModel, UTCDateTime

# Skema untuk menerima data saat Pemilik membuat/mengedit profil (POST/PUT)
# Semua menggunakan Optional karena pemilik mungkin hanya ingin mengubah 1 atau 2 kolom saja
class ProfilKosUpdate(BaseModel):
    nama_kos: Optional[str] = None
    alamat_lengkap: Optional[str] = None
    deskripsi: Optional[str] = None
    nomor_telepon_pengelola: Optional[str] = None
    informasi_rekening: Optional[str] = None
    gmaps_url: Optional[str] = None
    bank_nama: Optional[str] = None
    bank_nomor_rekening: Optional[str] = None
    bank_atas_nama: Optional[str] = None
    tanggal_jatuh_tempo: Optional[int] = None
    masa_tenggang_hari: Optional[int] = None
    tarif_parkir_motor: Optional[int] = None
    tarif_parkir_mobil: Optional[int] = None
    kapasitas_parkir_motor: Optional[int] = None
    kapasitas_parkir_mobil: Optional[int] = None
    kode_undangan: Optional[str] = None

# Skema untuk merender data saat diminta oleh Frontend (GET)
class ProfilKosResponse(ORMModel):
    id: int
    nama_kos: str
    alamat_lengkap: str
    deskripsi: Optional[str] = None
    nomor_telepon_pengelola: Optional[str] = None
    informasi_rekening: Optional[str] = None
    gmaps_url: Optional[str] = None
    bank_nama: Optional[str] = None
    bank_nomor_rekening: Optional[str] = None
    bank_atas_nama: Optional[str] = None
    tanggal_jatuh_tempo: int = 10
    masa_tenggang_hari: int = 5
    tarif_parkir_motor: int = 0
    tarif_parkir_mobil: int = 75000
    kapasitas_parkir_motor: int = 20
    kapasitas_parkir_mobil: int = 4
    kode_undangan: Optional[str] = None
    updated_at: Optional[UTCDateTime] = None
