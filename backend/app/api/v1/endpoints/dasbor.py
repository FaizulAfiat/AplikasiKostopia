from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.endpoints.deps import get_pemilik_saja, get_penghuni_saja
from app.core.database import get_db
from app.schemas.dasbor import DasborPemilik, DasborPenghuni
from app.services import dasbor as dasbor_service

router = APIRouter()


@router.get("/pemilik", response_model=DasborPemilik)
def dasbor_pemilik(db: Session = Depends(get_db), current_user=Depends(get_pemilik_saja)):
    return dasbor_service.dasbor_pemilik(db)


@router.get("/penghuni", response_model=DasborPenghuni)
def dasbor_penghuni(db: Session = Depends(get_db), current_user=Depends(get_penghuni_saja)):
    return dasbor_service.dasbor_penghuni(db, current_user)
