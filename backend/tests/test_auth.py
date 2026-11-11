from tests.conftest import daftar, login


def test_register_default_penghuni_dan_login(client):
    u = daftar(client, "Andi Saputra", "andi@sukabirus.id")
    assert u["peran"] == "Penghuni"
    assert u["kamar"] is None
    assert u["created_at"].endswith("Z")

    r = client.post("/api/v1/auth/login", json={"email": "andi@sukabirus.id", "password": "rahasia123"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "Penghuni"
    assert body["user"]["email"] == "andi@sukabirus.id"


def test_login_salah(client):
    daftar(client, "Andi", "andi@sukabirus.id")
    r = client.post("/api/v1/auth/login", json={"email": "andi@sukabirus.id", "password": "salahsalah"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Email atau kata sandi salah"


def test_register_email_duplikat_dan_pemilik_kedua(client):
    daftar(client, "Budi", "budi@kostopia.id", "Pemilik")
    r = client.post("/api/v1/auth/register", json={
        "nama_lengkap": "Budi", "email": "budi@kostopia.id", "password": "rahasia123"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Email sudah terdaftar, silakan gunakan email lain"
    r = client.post("/api/v1/auth/register", json={
        "nama_lengkap": "Pemilik 2", "email": "lain@kostopia.id", "password": "rahasia123", "peran": "Pemilik"})
    assert r.status_code == 400


def test_register_password_pendek(client):
    r = client.post("/api/v1/auth/register", json={
        "nama_lengkap": "X", "email": "x@x.id", "password": "123"})
    assert r.status_code == 422


def test_me_get_put_dan_ganti_sandi(client):
    daftar(client, "Fajar", "fajar@sukabirus.id")
    h = login(client, "fajar@sukabirus.id")
    r = client.get("/api/v1/auth/me", headers=h)
    assert r.status_code == 200 and r.json()["nama_lengkap"] == "Fajar"

    r = client.put("/api/v1/auth/me", headers=h, json={
        "nama_lengkap": "Fajar Nugraha", "asal_kampus": "Telkom University · Informatika",
        "kontak_darurat_nama": "Ibu Nugraha", "kontak_darurat_telepon": "081390012182"})
    assert r.status_code == 200
    assert r.json()["asal_kampus"] == "Telkom University · Informatika"
    assert r.json()["kontak_darurat_nama"] == "Ibu Nugraha"

    r = client.post("/api/v1/auth/ganti-sandi", headers=h, json={"sandi_lama": "salah123", "sandi_baru": "barubaru1"})
    assert r.status_code == 400
    r = client.post("/api/v1/auth/ganti-sandi", headers=h, json={"sandi_lama": "rahasia123", "sandi_baru": "barubaru1"})
    assert r.status_code == 200 and r.json()["message"] == "Kata sandi berhasil diubah."
    login(client, "fajar@sukabirus.id", "barubaru1")


def test_lupa_sandi_selalu_200(client):
    r = client.post("/api/v1/auth/lupa-sandi", json={"email": "tidakada@x.id"})
    assert r.status_code == 200
    assert r.json()["message"] == "Jika email terdaftar, instruksi telah dikirim."


def test_tanpa_token_401_dan_role_guard_403(client, pemilik):
    assert client.get("/api/v1/auth/me").status_code == 401
    daftar(client, "Andi", "andi@sukabirus.id")
    h = login(client, "andi@sukabirus.id")
    assert client.get("/api/v1/penghuni", headers=h).status_code == 403
    assert client.get("/api/v1/dasbor/pemilik", headers=h).status_code == 403
    assert client.post("/api/v1/kamar", headers=h, json={"nomor_kamar": "Z1", "harga_dasar": 1}).status_code == 403
    assert client.get("/api/v1/keuangan/ringkasan", headers=h).status_code == 403
    assert client.get("/api/v1/dasbor/penghuni", headers=pemilik).status_code == 403
    assert client.get("/api/v1/penghuni", headers=pemilik).status_code == 200
