# Kostopia — Aplikasi Mobile (Vue 3 + Capacitor)

Aplikasi Android untuk Pemilik Kos dan Penghuni Kos. Tampilan dibuat dengan Vue 3, dibungkus menjadi APK dengan Capacitor, dan terhubung ke backend FastAPI + PostgreSQL di folder [`backend/`](backend/) (kontrak API: [`backend/docs/API.md`](backend/docs/API.md)).

## Prasyarat

| Kebutuhan | Versi |
|---|---|
| Node.js | 22 LTS atau lebih baru |
| Backend Kostopia | sudah berjalan di port 8000 — klik dua kali `backend\jalankan-server.bat` (persiapan awal: [`backend/README-RUN-LOGIN.md`](backend/README-RUN-LOGIN.md)) |
| Untuk membuat APK | Java JDK 21 + Android SDK (platform 35, build-tools 35) |

## 1. Menjalankan di browser (paling cepat untuk mencoba)

```powershell
npm install
npm run dev
```

Buka `http://localhost:5173`, lalu tekan F12 → Ctrl+Shift+M untuk tampilan HP.
Aplikasi otomatis memakai backend di `http://localhost:8000`.

Akun contoh (dari `python -m app.seed` di backend):

| Peran | Email | Kata sandi |
|---|---|---|
| Pemilik | budi@kostopia.id | pemilik2026 |
| Penghuni | fajar@sukabirus.id | rahasia123 |

## 2. Membuat APK Android

```powershell
npm run build          # bangun versi web ke folder dist/
npx cap sync android   # salin ke proyek Android
cd android
.\gradlew.bat assembleDebug
```

Hasilnya ada di `android\app\build\outputs\apk\debug\app-debug.apk`. Salin file itu ke HP lalu instal (izinkan "Instal dari sumber tidak dikenal").

## 3. Menghubungkan HP ke backend

Di HP, `localhost` berarti HP itu sendiri, jadi aplikasi perlu alamat laptop yang menjalankan backend:

1. Pastikan HP dan laptop terhubung ke **Wi-Fi yang sama**.
2. Cari IP laptop: jalankan `ipconfig`, lalu lihat **IPv4 Address** (mis. `192.168.1.10`).
3. Backend harus dijalankan dengan `--host 0.0.0.0` (sudah diatur di `jalankan-server.bat`).
4. Di aplikasi, buka **Masuk → ⚙ Pengaturan Server**, isi `http://192.168.1.10:8000`, tekan **Uji koneksi**, lalu **Simpan**.
5. Jika uji koneksi gagal, izinkan Python di **Windows Defender Firewall** untuk jaringan *Private*.

Emulator Android otomatis memakai `http://10.0.2.2:8000` (alamat laptop dari dalam emulator).

## Struktur kode

```
backend/         Backend FastAPI + PostgreSQL (app/, tests/, docs/API.md, jalankan-server.bat)
src/
  services/      api.js (klien HTTP + token), endpoints.js (satu fungsi per endpoint), config.js (alamat server)
  stores/        auth.js (sesi login), ui.js (toast, dialog, konfirmasi)
  components/
    app/         AppHeader, BottomNav, SegmentedTabs, StateBlock, BottomSheet, PhotoPicker
    lostfound/   Papan & kartu Barang Hilang (UC-15)
    layout/      PemilikLayout, PenghuniLayout (menu bawah)
  views/
    auth/        Splash, Masuk, Daftar, Lupa sandi, Pengaturan server
    pemilik/     Dasbor, Keuangan & verifikasi, Penghuni & kamar, Layanan, Pengumuman, Aturan, Penilaian, Kamar, Profil kos
    penghuni/    Beranda, Tagihan & unggah bukti, Aspirasi & izin, Barang hilang, Info kos
    shared/      Akun (data diri, kendaraan, ganti sandi), Form barang hilang
android/         Proyek Android dari Capacitor
```
