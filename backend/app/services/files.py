"""Penyimpanan file unggahan (foto bukti bayar, lampiran aspirasi, foto barang)."""
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from app.core.config import settings

# Tipe file yang diizinkan beserta ekstensi penyimpanannya
TIPE_DIIZINKAN = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}

# Tanda awal (magic bytes) tiap tipe, untuk mencegah file palsu
MAGIC = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
    "application/pdf": [b"%PDF"],
}


def upload_dir() -> Path:
    path = Path(settings.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def simpan_file(file: UploadFile) -> str:
    tipe = (file.content_type or "").lower()
    if tipe not in TIPE_DIIZINKAN:
        raise HTTPException(status_code=422, detail="Tipe file tidak didukung. Gunakan JPG, PNG, WEBP, atau PDF.")
    batas = settings.MAX_UPLOAD_MB * 1024 * 1024
    isi = await file.read(batas + 1)
    if len(isi) > batas:
        raise HTTPException(status_code=422, detail=f"Ukuran file maksimal {settings.MAX_UPLOAD_MB} MB")
    if not isi:
        raise HTTPException(status_code=422, detail="File kosong")
    if not any(isi.startswith(m) for m in MAGIC[tipe]) or (tipe == "image/webp" and isi[8:12] != b"WEBP"):
        raise HTTPException(status_code=422, detail="Isi file tidak sesuai dengan tipenya")
    nama = uuid.uuid4().hex + TIPE_DIIZINKAN[tipe]
    (upload_dir() / nama).write_bytes(isi)
    return f"/uploads/{nama}"
