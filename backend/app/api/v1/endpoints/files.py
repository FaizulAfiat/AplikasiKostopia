from fastapi import APIRouter, Depends, File, UploadFile, status
from app.api.v1.endpoints.deps import get_validasi_user
from app.services import files as files_service

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def unggah_file(file: UploadFile = File(...), current_user=Depends(get_validasi_user)):
    """Unggah gambar (JPG/PNG/WEBP) atau PDF maks 5 MB; dikembalikan URL relatif /uploads/…"""
    url = await files_service.simpan_file(file)
    return {"url": url}
