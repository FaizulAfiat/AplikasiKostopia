from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


# API Health Check: untuk mengecek apakah aplikasi berjalan normal
@router.get("/health", summary="Health Check")
async def health_check():
    return {
        "status": "ok",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
