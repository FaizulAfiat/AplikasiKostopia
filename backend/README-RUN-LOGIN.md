# Kostopia Backend — cara menjalankan, mengisi data contoh, dan login

Kontrak API lengkap (sumber kebenaran untuk frontend): [`docs/API.md`](docs/API.md).
Dokumentasi interaktif tersedia di `http://127.0.0.1:8000/docs` setelah server berjalan.

## 1. Persiapan database PostgreSQL
1. Pastikan PostgreSQL aktif (service `postgresql-x64-16` di Windows).
2. Buat database bernama `kostopia`, misalnya lewat pgAdmin (Databases → Create → Database) atau terminal:
   ```powershell
   & "C:\Program Files\PostgreSQL\16\bin\createdb.exe" -U postgres kostopia
   ```
3. Salin `.env.example` menjadi `.env` di folder backend, lalu isi:
   - `DATABASE_URL` sesuai username/password PostgreSQL lokal, contoh
     `postgresql://postgres:PASSWORD_ANDA@localhost:5432/kostopia`
   - `SECRET_KEY` dengan string acak panjang:
     `python -c "import secrets; print(secrets.token_urlsafe(48))"`
   - `CORS_ORIGINS` biarkan `*` (aplikasi memakai Bearer token, bukan cookie).
4. Jangan pernah membagikan / meng-commit file `.env`.

## 2. Instal dependensi
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Jika PowerShell memblokir aktivasi, gunakan Command Prompt: `.venv\Scripts\activate.bat`.

## 3. Isi data contoh (seed)
```powershell
python -m app.seed --reset   # hapus semua tabel, buat ulang, isi data contoh
python -m app.seed           # hanya mengisi jika database masih kosong (aman dijalankan berulang)
```
> **PENTING untuk database tim yang sudah ada:** skema tabel berubah (kolom baru di hampir semua tabel).
> `Base.metadata.create_all()` hanya membuat tabel yang belum ada dan **tidak** memigrasi tabel lama,
> jadi jalankan `python -m app.seed --reset` sekali. Perintah ini **menghapus semua data** di database `kostopia`.

Data contoh memakai tanggal relatif terhadap hari ini (tagihan 6 bulan terakhir, tagihan bulan berjalan, dll.).

| Peran | Email | Sandi | Keterangan |
|---|---|---|---|
| Pemilik | `budi@kostopia.id` | `pemilik2026` | Budi Utomo, Kos Griya Sukabirus |
| Penghuni | `fajar@sukabirus.id` | `rahasia123` | Fajar Nugraha, kamar B02, Masa Tenggang, tagihan bulan ini belum dibayar |
| Penghuni | `andi@`, `rizky@`, `nadia@`, `dimas@`, `salsa@`, `laras@`, `yoga@` … `@sukabirus.id` | `rahasia123` | A01, A03, A07, B04, B06, B07, B10 |
| Penghuni | `sinta@sukabirus.id` | `rahasia123` | Belum ditempatkan di kamar |

## 4. Jalankan server
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Untuk diakses dari HP / emulator Android di jaringan yang sama gunakan `--host 0.0.0.0`
(lalu arahkan frontend ke `http://IP_LAPTOP:8000/api/v1`; emulator Android: `http://10.0.2.2:8000/api/v1`).

Cek cepat:
- `http://127.0.0.1:8000/` → `{"message": "Sistem Backend Kostopia Aktif!"}`
- `http://127.0.0.1:8000/api/v1/health` → `{"status": "ok", "version": "1.0.0"}`
- `http://127.0.0.1:8000/docs` → Swagger UI. Login memakai body JSON lewat `POST /api/v1/auth/login`;
  untuk endpoint lain kirim header `Authorization: Bearer <access_token>` (mis. lewat Postman/curl).

File unggahan (`POST /api/v1/files`) disimpan di folder `uploads/` (diabaikan git) dan disajikan di `/uploads/<nama>`.

## 5. Menjalankan test
```powershell
pytest -q
```
Test memakai SQLite in-memory, jadi tidak membutuhkan PostgreSQL.

## Catatan
- Pembuatan tagihan bulanan otomatis: setiap kali endpoint tagihan/dasbor dipanggil, backend memastikan setiap sewa aktif
  punya tagihan bulan berjalan; tagihan yang lewat jatuh tempo dan masih `Belum Bayar`/`Ditolak` membuat sewa menjadi `Masa Tenggang`.
- Ini setup development lokal, bukan konfigurasi produksi. Sebelum deployment gunakan HTTPS, secret yang aman,
  pembatasan percobaan login, CORS yang dibatasi, dan mekanisme migrasi database (mis. Alembic).
