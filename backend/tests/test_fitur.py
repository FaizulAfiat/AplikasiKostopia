from datetime import date, timedelta
from app.core.waktu import periode_dari, tambah_bulan
from app.models.domain import Lease, Transaction
from tests.conftest import daftar, login


# ---------- Barang hilang (UC-15) ----------

def test_barang_hilang_nama_kosong_422(client, kos):
    h = kos["fajar_h"]
    r = client.post("/api/v1/barang-hilang", headers=h, json={"jenis": "Hilang", "judul_barang": "   "})
    assert r.status_code == 422
    assert r.json()["detail"] == "Nama barang wajib diisi"
    r = client.post("/api/v1/barang-hilang", headers=h, json={"jenis": "Hilang"})
    assert r.status_code == 422
    assert r.json()["detail"] == "Nama barang wajib diisi"


def test_barang_hilang_hanya_pelapor_bisa_selesai(client, kos):
    h = kos["fajar_h"]
    r = client.post("/api/v1/barang-hilang", headers=h, json={
        "jenis": "Hilang", "judul_barang": "Payung lipat hitam", "lokasi": "Teras"})
    assert r.status_code == 201
    barang = r.json()
    assert barang["status_barang"] == "Aktif" and barang["pelapor"]["nama_lengkap"] == "Fajar Nugraha"

    # Pemilik kos (bukan pelapor) → 403
    r = client.post(f"/api/v1/barang-hilang/{barang['id']}/selesai", headers=kos["pemilik"])
    assert r.status_code == 403
    r = client.post(f"/api/v1/barang-hilang/{barang['id']}/selesai", headers=h)
    assert r.status_code == 200
    assert r.json()["status_barang"] == "Selesai" and r.json()["selesai_at"].endswith("Z")

    assert client.get("/api/v1/barang-hilang?status=Aktif", headers=h).json() == []
    assert len(client.get("/api/v1/barang-hilang?status=Selesai&q=payung", headers=h).json()) == 1


# ---------- Penghuni & tagihan ----------

def test_sewa_dan_tagihan_otomatis(client, sewa):
    p = sewa["penghuni_out"]
    assert p["sewa"]["kamar"] == "A01"
    assert p["sewa"]["status_sewa"] == "Aktif"
    assert p["user"]["kamar"] == "A01"
    assert p["tagihan_bulan_ini"] == "Belum Bayar"

    # Kamar sudah dihuni
    kamar = client.get("/api/v1/kamar", headers=sewa["pemilik"]).json()
    a01 = next(k for k in kamar if k["nomor_kamar"] == "A01")
    assert a01["status_ketersediaan"] == "Dihuni" and a01["penghuni"]["kamar"] == "A01"
    assert client.delete(f"/api/v1/kamar/{a01['id']}", headers=sewa["pemilik"]).status_code == 400

    # Tagihan bulan ini dibuat otomatis & idempoten
    t1 = client.get("/api/v1/tagihan", headers=sewa["fajar_h"]).json()
    t2 = client.get("/api/v1/tagihan", headers=sewa["fajar_h"]).json()
    assert len(t1) == 1 and len(t2) == 1
    t = t1[0]
    assert t["periode"] == periode_dari(date.today())
    assert t["jumlah_tagihan"] == 950000
    assert t["komponen"][0] == {"nama": "Sewa kamar A01", "jumlah": 950000}
    assert t["jatuh_tempo"] == max(date.today(), date.today().replace(day=10)).isoformat()
    assert t["kamar"] == "A01" and t["penghuni"]["nama_lengkap"] == "Fajar Nugraha"


def test_parkir_masuk_komponen(client, kos):
    h = kos["fajar_h"]
    for plat, jenis in (("D 1 AA", "Motor"), ("D 2 BB", "Motor"), ("D 3 CC", "Mobil")):
        r = client.post("/api/v1/kendaraan", headers=h, json={"nomor_polisi": plat, "jenis_kendaraan": jenis, "merk_warna": "X"})
        assert r.status_code == 201, r.text
    assert client.post("/api/v1/kendaraan", headers=h, json={"nomor_polisi": "d 1 aa", "jenis_kendaraan": "Motor"}).status_code == 400
    client.post(f"/api/v1/penghuni/{kos['fajar']['id']}/sewa", headers=kos["pemilik"], json={
        "room_id": kos["kamar"][0]["id"], "tanggal_mulai": date.today().isoformat(), "lama_bulan": 3})
    t = client.get("/api/v1/tagihan", headers=h).json()[0]
    # motor pertama gratis, motor kedua tarif_parkir_motor (0 default), mobil 75.000
    assert t["jumlah_tagihan"] == 950000 + 0 + 75000
    r = client.patch(f"/api/v1/kendaraan/{client.get('/api/v1/kendaraan', headers=h).json()[0]['id']}",
                     headers=kos["pemilik"], json={"slot_parkir": "M-01"})
    assert r.status_code == 200 and r.json()["slot_parkir"] == "M-01"
    ring = client.get("/api/v1/kendaraan/ringkasan", headers=kos["pemilik"]).json()
    assert ring == {"motor_terpakai": 2, "motor_kapasitas": 20, "mobil_terpakai": 1, "mobil_kapasitas": 4}


def test_unggah_bukti_dan_setujui_perpanjang_sewa(client, sewa, db):
    h, hp = sewa["fajar_h"], sewa["pemilik"]
    t = client.get("/api/v1/tagihan", headers=h).json()[0]
    lama = date.fromisoformat(sewa["penghuni_out"]["sewa"]["tanggal_jatuh_tempo"])

    # Verifikasi sebelum ada bukti → 400
    assert client.post(f"/api/v1/tagihan/{t['id']}/verifikasi", headers=hp, json={"disetujui": True}).status_code == 400

    r = client.post(f"/api/v1/tagihan/{t['id']}/bukti", headers=h, json={"bukti_bayar_url": "/uploads/bukti.jpg"})
    assert r.status_code == 200
    assert r.json()["status_tagihan"] == "Menunggu Verifikasi" and r.json()["tanggal_unggah"].endswith("Z")
    # Tidak bisa unggah lagi saat menunggu
    assert client.post(f"/api/v1/tagihan/{t['id']}/bukti", headers=h, json={"bukti_bayar_url": "/x.jpg"}).status_code == 400

    ring = client.get("/api/v1/tagihan/ringkasan-status", headers=hp).json()
    assert ring["Menunggu Verifikasi"] == 1 and set(ring) == {"Menunggu Verifikasi", "Lunas", "Ditolak", "Belum Bayar"}

    r = client.post(f"/api/v1/tagihan/{t['id']}/verifikasi", headers=hp, json={"disetujui": True})
    assert r.status_code == 200
    assert r.json()["status_tagihan"] == "Lunas" and r.json()["diverifikasi_at"].endswith("Z")

    detail = client.get(f"/api/v1/penghuni/{sewa['fajar']['id']}", headers=hp).json()
    assert detail["sewa"]["tanggal_jatuh_tempo"] == tambah_bulan(lama, 1).isoformat()
    assert detail["sewa"]["status_sewa"] == "Aktif"
    assert detail["tagihan_bulan_ini"] == "Lunas"

    ringkas = client.get("/api/v1/keuangan/ringkasan", headers=hp).json()
    assert ringkas["pemasukan"] == 950000 and ringkas["jumlah_lunas"] == 1
    trx = client.get("/api/v1/keuangan/transaksi", headers=hp).json()
    assert trx[0]["kategori"] == "Sewa" and trx[0]["nominal"] == 950000


def test_tolak_bukti_wajib_alasan(client, sewa):
    h, hp = sewa["fajar_h"], sewa["pemilik"]
    t = client.get("/api/v1/tagihan", headers=h).json()[0]
    client.post(f"/api/v1/tagihan/{t['id']}/bukti", headers=h, json={"bukti_bayar_url": "/uploads/b.jpg"})
    r = client.post(f"/api/v1/tagihan/{t['id']}/verifikasi", headers=hp, json={"disetujui": False})
    assert r.status_code == 422
    r = client.post(f"/api/v1/tagihan/{t['id']}/verifikasi", headers=hp, json={"disetujui": False, "alasan": "Nominal tidak sesuai"})
    assert r.status_code == 200
    assert r.json()["status_tagihan"] == "Ditolak" and r.json()["alasan_tolak"] == "Nominal tidak sesuai"
    # Setelah ditolak boleh unggah ulang
    r = client.post(f"/api/v1/tagihan/{t['id']}/bukti", headers=h, json={"bukti_bayar_url": "/uploads/c.jpg"})
    assert r.status_code == 200 and r.json()["alasan_tolak"] is None


def test_tagihan_penghuni_lain_403(client, sewa):
    daftar(client, "Andi", "andi@sukabirus.id")
    ha = login(client, "andi@sukabirus.id")
    t = client.get("/api/v1/tagihan", headers=sewa["fajar_h"]).json()[0]
    assert client.get(f"/api/v1/tagihan/{t['id']}", headers=ha).status_code == 403
    assert client.get("/api/v1/tagihan", headers=ha).json() == []


def test_lewat_jatuh_tempo_jadi_masa_tenggang(client, sewa, db):
    # Buat tagihan bulan lalu yang belum dibayar → sewa otomatis Masa Tenggang
    lease = db.query(Lease).first()
    lalu = tambah_bulan(date.today(), -1)
    db.add(Transaction(lease_id=lease.id, periode=periode_dari(lalu), jumlah_tagihan=950000,
                       komponen_biaya=[{"nama": "Sewa kamar A01", "jumlah": 950000}],
                       jatuh_tempo=lalu.replace(day=10), batas_tenggang=lalu.replace(day=15),
                       status_tagihan="Belum Bayar"))
    db.commit()
    detail = client.get(f"/api/v1/penghuni/{sewa['fajar']['id']}", headers=sewa["pemilik"]).json()
    assert detail["sewa"]["status_sewa"] == "Masa Tenggang"
    ring = client.get("/api/v1/keuangan/ringkasan", headers=sewa["pemilik"]).json()
    assert ring["tunggakan"] >= 950000 and ring["jumlah_penunggak"] == 1


def test_penghuni_keluar_kamar_tersedia(client, sewa):
    hp = sewa["pemilik"]
    r = client.patch(f"/api/v1/penghuni/{sewa['fajar']['id']}/status", headers=hp, json={"status_sewa": "Sudah Keluar"})
    assert r.status_code == 200 and r.json()["sewa"]["status_sewa"] == "Sudah Keluar"
    kamar = client.get("/api/v1/kamar", headers=hp).json()
    assert next(k for k in kamar if k["nomor_kamar"] == "A01")["status_ketersediaan"] == "Tersedia"
    belum = client.get("/api/v1/penghuni/belum-ditempatkan", headers=hp).json()
    assert [u["email"] for u in belum] == ["fajar@sukabirus.id"]
    lst = client.get("/api/v1/penghuni?status=Sudah Keluar", headers=hp).json()
    assert len(lst) == 1


# ---------- Aspirasi & izin ----------

def test_aspirasi_buat_dan_tanggapi(client, kos):
    h, hp = kos["fajar_h"], kos["pemilik"]
    r = client.post("/api/v1/aspirasi", headers=h, json={
        "judul": " ", "kategori": "Kerusakan", "deskripsi_kendala": "Bocor"})
    assert r.status_code == 422
    r = client.post("/api/v1/aspirasi", headers=h, json={
        "judul": "Keran bocor", "kategori": "Kerusakan", "deskripsi_kendala": "Keran kamar mandi bocor",
        "lampiran_foto_urls": ["/uploads/a.jpg"]})
    assert r.status_code == 201
    a = r.json()
    assert a["status_penanganan"] == "Menunggu" and a["lampiran_foto_urls"] == ["/uploads/a.jpg"]
    assert client.post("/api/v1/aspirasi", headers=hp, json={
        "judul": "x", "kategori": "Saran", "deskripsi_kendala": "y"}).status_code == 403
    assert client.patch(f"/api/v1/aspirasi/{a['id']}", headers=h, json={"status_penanganan": "Selesai"}).status_code == 403
    r = client.patch(f"/api/v1/aspirasi/{a['id']}", headers=hp, json={
        "status_penanganan": "Sedang Diproses", "tanggapan_pemilik": "Tukang datang besok"})
    assert r.status_code == 200
    assert r.json()["status_penanganan"] == "Sedang Diproses"
    assert len(client.get("/api/v1/aspirasi?status=Sedang Diproses", headers=h).json()) == 1


def test_izin_buat_dan_putuskan(client, kos):
    h, hp = kos["fajar_h"], kos["pemilik"]
    hari = date.today()
    r = client.post("/api/v1/izin", headers=h, json={
        "jenis_izin": "Pulang Kampung", "tanggal_mulai": hari.isoformat(),
        "tanggal_selesai": (hari - timedelta(days=1)).isoformat(), "alasan": "Lebaran"})
    assert r.status_code == 422
    r = client.post("/api/v1/izin", headers=h, json={
        "jenis_izin": "Pulang Kampung", "tanggal_mulai": hari.isoformat(),
        "tanggal_selesai": (hari + timedelta(days=4)).isoformat(), "alasan": "Acara keluarga"})
    assert r.status_code == 201
    izin = r.json()
    assert izin["durasi"] == "5 hari" and izin["status_izin"] == "Pending"
    r = client.post("/api/v1/izin", headers=h, json={
        "jenis_izin": "Pulang Larut", "tanggal_mulai": hari.isoformat(),
        "tanggal_selesai": hari.isoformat(), "alasan": "Kerja kelompok"})
    assert r.json()["durasi"] == "1 malam"

    r = client.patch(f"/api/v1/izin/{izin['id']}", headers=hp, json={"status_izin": "Disetujui", "catatan_pemilik": "Hati-hati"})
    assert r.status_code == 200 and r.json()["status_izin"] == "Disetujui"
    assert client.patch(f"/api/v1/izin/{izin['id']}", headers=hp, json={"status_izin": "Ditolak"}).status_code == 400


# ---------- Pengumuman, aturan, penilaian ----------

def test_pengumuman_baca_aturan_penilaian(client, sewa):
    h, hp = sewa["fajar_h"], sewa["pemilik"]
    client.post("/api/v1/pengumuman", headers=hp, json={"judul": "Biasa", "isi_pengumuman": "isi", "disematkan": False})
    r = client.post("/api/v1/pengumuman", headers=hp, json={"judul": "Penting", "isi_pengumuman": "isi", "disematkan": True})
    assert r.status_code == 201
    daftar_p = client.get("/api/v1/pengumuman", headers=h).json()
    assert daftar_p[0]["judul"] == "Penting" and daftar_p[0]["sudah_dibaca"] is False
    assert daftar_p[0]["total_penghuni"] == 1
    for _ in range(2):
        r = client.post(f"/api/v1/pengumuman/{daftar_p[0]['id']}/baca", headers=h)
        assert r.status_code == 200
    assert r.json()["dibaca_count"] == 1 and r.json()["sudah_dibaca"] is True

    r = client.post("/api/v1/aturan", headers=hp, json={"judul": "Jam malam 23.00", "deskripsi": "…", "sanksi": "Teguran", "status_aktif": True})
    assert r.status_code == 201 and r.json()["urutan"] == 1
    r2 = client.post("/api/v1/aturan", headers=hp, json={"judul": "Nonaktif", "status_aktif": False})
    assert r2.json()["urutan"] == 2
    assert len(client.get("/api/v1/aturan", headers=h).json()) == 1
    assert len(client.get("/api/v1/aturan", headers=hp).json()) == 2
    r = client.put(f"/api/v1/aturan/{r2.json()['id']}", headers=hp, json={"judul": "Aktif lagi", "status_aktif": True})
    assert r.status_code == 200 and r.json()["judul"] == "Aktif lagi"

    assert client.post("/api/v1/penilaian", headers=h, json={"skor_bintang": 6, "aspek": "Umum"}).status_code == 422
    for skor, aspek in ((5, "Kebersihan"), (4, "Keamanan")):
        assert client.post("/api/v1/penilaian", headers=h, json={"skor_bintang": skor, "aspek": aspek, "ulasan_feedback": "ok"}).status_code == 201
    ring = client.get("/api/v1/penilaian/ringkasan", headers=h).json()
    assert ring["rata_rata"] == 4.5 and ring["jumlah"] == 2
    assert ring["distribusi"] == {"1": 0, "2": 0, "3": 0, "4": 1, "5": 1}
    assert {a["aspek"] for a in ring["per_aspek"]} == {"Kebersihan", "Keamanan", "Fasilitas", "Pelayanan", "Umum"}


# ---------- Keuangan ----------

def test_pengeluaran_dan_xlsx(client, kos):
    hp = kos["pemilik"]
    r = client.post("/api/v1/keuangan/pengeluaran", headers=hp, json={
        "tanggal": date.today().isoformat(), "keterangan": "Token listrik", "kategori": "Listrik", "nominal": 500000})
    assert r.status_code == 201
    assert client.post("/api/v1/keuangan/pengeluaran", headers=hp, json={
        "tanggal": date.today().isoformat(), "keterangan": "x", "kategori": "Listrik", "nominal": 0}).status_code == 422
    trx = client.get("/api/v1/keuangan/transaksi", headers=hp).json()
    assert trx[0]["kategori"] == "Pengeluaran" and trx[0]["nominal"] == -500000
    ring = client.get("/api/v1/keuangan/ringkasan", headers=hp).json()
    assert ring["pengeluaran"] == 500000 and ring["laba_bersih"] == -500000
    bulanan = client.get("/api/v1/keuangan/pemasukan-bulanan?bulan=6", headers=hp).json()
    assert len(bulanan) == 6 and bulanan[-1]["periode"] == periode_dari(date.today())
    r = client.get("/api/v1/keuangan/rekap.xlsx", headers=hp)
    assert r.status_code == 200 and r.content[:2] == b"PK"
    pid = client.get("/api/v1/keuangan/pengeluaran", headers=hp).json()[0]["id"]
    assert client.delete(f"/api/v1/keuangan/pengeluaran/{pid}", headers=hp).status_code == 204


# ---------- Unggah file ----------

def test_unggah_file(client, kos):
    h = kos["fajar_h"]
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 100
    r = client.post("/api/v1/files", headers=h, files={"file": ("a.png", png, "image/png")})
    assert r.status_code == 201
    url = r.json()["url"]
    assert url.startswith("/uploads/") and url.endswith(".png")
    assert client.get(url).status_code == 200
    r = client.post("/api/v1/files", headers=h, files={"file": ("a.txt", b"halo", "text/plain")})
    assert r.status_code == 422
    besar = b"%PDF" + b"0" * (5 * 1024 * 1024 + 1)
    r = client.post("/api/v1/files", headers=h, files={"file": ("a.pdf", besar, "application/pdf")})
    assert r.status_code == 422


# ---------- Dasbor ----------

def test_dasbor_pemilik_dan_penghuni(client, sewa):
    r = client.get("/api/v1/dasbor/pemilik", headers=sewa["pemilik"])
    assert r.status_code == 200, r.text
    d = r.json()
    for key in ("nama_kos", "total_kamar", "kamar_terisi", "pemasukan_bulan_ini", "tagihan_lunas", "total_tagihan",
                "tunggakan", "jumlah_penunggak", "jumlah_tenggang", "rating_rata", "jumlah_ulasan",
                "perlu_tindakan", "pemasukan_6_bulan", "peta_kamar", "menunggu_verifikasi", "aktivitas"):
        assert key in d
    assert set(d["perlu_tindakan"]) == {"bukti_menunggu", "izin_pending", "aspirasi_baru", "sewa_berakhir_7_hari"}
    assert d["nama_kos"] == "Kos Griya Sukabirus"
    assert d["total_kamar"] == 2 and d["kamar_terisi"] == 1 and d["total_tagihan"] == 1
    assert len(d["pemasukan_6_bulan"]) == 6
    peta = d["peta_kamar"][0]
    assert peta["lantai"] == 1
    status = {k["nomor"]: k["status"] for k in peta["kamar"]}
    assert status["A02"] == "Kosong" and status["A01"] in ("Belum Bayar", "Masa Tenggang")

    r = client.get("/api/v1/dasbor/penghuni", headers=sewa["fajar_h"])
    assert r.status_code == 200, r.text
    d = r.json()
    for key in ("nama_kos", "kamar", "status_sewa", "sewa_mulai", "sewa_sampai", "tagihan_aktif",
                "pengumuman_terbaru", "permintaan", "jumlah_aturan_aktif"):
        assert key in d
    assert d["kamar"] == "A01" and d["tagihan_aktif"]["status_tagihan"] == "Belum Bayar"
