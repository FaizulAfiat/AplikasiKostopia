# Kostopia — menjalankan login & registrasi pemilik

## 1. Persiapan database PostgreSQL
1. Pastikan PostgreSQL aktif.
2. Buat database bernama `kostopia` (misalnya melalui pgAdmin: Databases → Create → Database).
3. Salin `.env.example` menjadi `.env` di folder backend, lalu isi `DATABASE_URL` sesuai username/password PostgreSQL lokal.
4. Ganti `SECRET_KEY` dengan nilai acak yang panjang. Jangan bagikan file `.env`.

Contoh format URL (ganti kredensial sesuai komputer sendiri):
`postgresql://postgres:PASSWORD_ANDA@localhost:5432/kostopia`

## 2. Jalankan backend (terminal pertama)
Buka folder `kostopia-backend` (folder backend di dalam paket perbaikan).:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Jika PowerShell memblokir aktivasi, gunakan Command Prompt:
```cmd
.venv\Scripts\activate.bat
```
Tes backend:
- `http://127.0.0.1:8000/`
- Dokumentasi API: `http://127.0.0.1:8000/docs`

## 3. Jalankan frontend (terminal kedua)
Buka folder `kostopia-frontend`:
```powershell
npm install
npm run dev
```
Buka URL Vite yang tampil di terminal, biasanya `http://localhost:5173`.

Frontend sudah dikonfigurasi menggunakan `VITE_API_URL=http://127.0.0.1:8000/api/v1` pada `.env`. Restart Vite jika mengubah file `.env`.

## 4. Uji alur pemilik
1. Buka halaman daftar dengan parameter role pemilik: `http://localhost:5173/register?role=pengelola`.
2. Isi nama, email, nomor telepon, dan kata sandi minimal 8 karakter.
3. Setelah registrasi berhasil, masuk lewat `http://localhost:5173/login?role=pengelola`.
4. Login memakai email dan kata sandi yang baru dibuat. Seharusnya diarahkan ke `/dashboard/pemilik`.
5. Di Swagger (`/docs`), endpoint tersedia di `/api/v1/auth/register`, `/api/v1/auth/login`, dan `/api/v1/auth/me`.

## Catatan
- Backend memakai PostgreSQL; aplikasi tidak akan start jika database tidak bisa dihubungi.
- `Base.metadata.create_all()` membuat tabel yang belum ada, tetapi tidak melakukan migrasi terhadap skema tabel lama.
- Ini setup development lokal, bukan konfigurasi produksi. Sebelum deployment, gunakan HTTPS, secret yang aman, pembatasan percobaan login, dan mekanisme migrasi database.
