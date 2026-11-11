"""Fixture pytest: database SQLite in-memory + TestClient dengan get_db di-override."""
import os
import tempfile

# Harus di-set sebelum app diimpor agar engine bawaan tidak menunjuk PostgreSQL
os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("UPLOAD_DIR", tempfile.mkdtemp(prefix="kostopia-uploads-"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import domain  # noqa: F401

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def bersihkan_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db():
    s = TestingSessionLocal()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def client():
    return TestClient(app)


def daftar(client, nama, email, peran=None, password="rahasia123"):
    body = {"nama_lengkap": nama, "email": email, "nomor_telepon": "0812", "password": password}
    if peran:
        body["peran"] = peran
    r = client.post("/api/v1/auth/register", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def login(client, email, password="rahasia123"):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def pemilik(client):
    daftar(client, "Budi Utomo", "budi@kostopia.id", "Pemilik", "pemilik2026")
    return login(client, "budi@kostopia.id", "pemilik2026")


@pytest.fixture
def kos(client, pemilik):
    """Profil kos + 2 kamar + satu penghuni (Fajar) yang ditempatkan di A01."""
    r = client.post("/api/v1/profil", headers=pemilik, json={
        "nama_kos": "Kos Griya Sukabirus", "alamat_lengkap": "Jl. Sukabirus No. 12",
        "tanggal_jatuh_tempo": 10, "masa_tenggang_hari": 5,
    })
    assert r.status_code == 201, r.text
    kamar = []
    for nomor in ("A01", "A02"):
        r = client.post("/api/v1/kamar", headers=pemilik, json={"nomor_kamar": nomor, "harga_dasar": 950000, "lantai": 1})
        assert r.status_code == 201, r.text
        kamar.append(r.json())
    fajar = daftar(client, "Fajar Nugraha", "fajar@sukabirus.id")
    fajar_h = login(client, "fajar@sukabirus.id")
    return {"pemilik": pemilik, "kamar": kamar, "fajar": fajar, "fajar_h": fajar_h}


@pytest.fixture
def sewa(client, kos):
    from datetime import date
    r = client.post(f"/api/v1/penghuni/{kos['fajar']['id']}/sewa", headers=kos["pemilik"], json={
        "room_id": kos["kamar"][0]["id"], "tanggal_mulai": date.today().isoformat(), "lama_bulan": 1,
    })
    assert r.status_code == 201, r.text
    kos["penghuni_out"] = r.json()
    return kos
