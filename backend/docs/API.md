# Kontrak API Kostopia v1

Dokumen ini adalah **sumber kebenaran** antara backend FastAPI dan aplikasi mobile (Vue + Capacitor).
Semua endpoint berawalan `/api/v1`. Semua body & respons JSON (kecuali unggah file & unduh xlsx).

## Konvensi umum

- **Auth:** header `Authorization: Bearer <access_token>`. Token didapat dari `POST /auth/login`.
- **Peran:** `"Pemilik"` atau `"Penghuni"` (nilai enum `PeranPengguna`). Tidak ada peran lain.
- **Error:** format FastAPI standar `{"detail": "pesan dalam Bahasa Indonesia"}`.
  - 400 aturan bisnis dilanggar · 401 belum login/token salah · 403 peran tidak berhak · 404 tidak ada · 422 validasi.
  - Untuk 422 dari Pydantic, `detail` berupa list; frontend menampilkan `detail[0].msg`.
  - Pesan validasi yang dibuat sendiri memakai `HTTPException(422, "…")` (string).
- **Waktu:** `datetime` dikirim ISO 8601 UTC dengan akhiran `Z` (mis. `2026-11-08T06:42:00Z`). `date` sebagai `YYYY-MM-DD`.
- **Uang:** angka bulat rupiah (`int`), bukan string/desimal. Contoh `1000000`.
- **Ringkasan orang** (`PersonRef`) yang disisipkan di banyak respons:
  ```json
  { "id": 3, "nama_lengkap": "Fajar Nugraha", "peran": "Penghuni", "kamar": "B02" }
  ```
  `kamar` = nomor kamar dari sewa aktif (status `Aktif`/`Masa Tenggang`), atau `null`.

## Status (nilai string persis)

| Entitas | Nilai |
|---|---|
| Sewa (`status_sewa`) | `Aktif`, `Masa Tenggang`, `Sudah Keluar` |
| Kamar (`status_ketersediaan`) | `Tersedia`, `Dihuni`, `Perbaikan` |
| Tagihan (`status_tagihan`) | `Belum Bayar`, `Menunggu Verifikasi`, `Lunas`, `Ditolak` |
| Aspirasi (`status_penanganan`) | `Menunggu`, `Sedang Diproses`, `Selesai` |
| Aspirasi (`kategori`) | `Kerusakan`, `Fasilitas`, `Kebersihan`, `Keamanan`, `Saran` |
| Izin (`status_izin`) | `Pending`, `Disetujui`, `Ditolak` |
| Izin (`jenis_izin`) | `Pulang Kampung`, `Menginap di Luar`, `Pulang Larut`, `Lainnya` |
| Barang hilang (`jenis`) | `Hilang`, `Temuan` |
| Barang hilang (`status_barang`) | `Aktif`, `Selesai` |
| Penilaian (`aspek`) | `Kebersihan`, `Keamanan`, `Fasilitas`, `Pelayanan`, `Umum` |
| Kendaraan (`jenis_kendaraan`) | `Motor`, `Mobil` |
| Pengeluaran (`kategori`) | `Listrik`, `Air`, `Kebersihan`, `Perbaikan`, `Gaji`, `Lainnya` |

---

## 1. Autentikasi & profil — `/auth`

### `POST /auth/register` (publik)
Body: `{ nama_lengkap, email, nomor_telepon, password (min 8), peran? }`
- `peran` default `"Penghuni"`. `"Pemilik"` hanya boleh jika belum ada akun Pemilik (sistem satu properti) → selain itu 400.
- Email duplikat → 400 `"Email sudah terdaftar, silakan gunakan email lain"`.
- Respons 201: `UserOut`.

### `POST /auth/login` (publik)
Body `{ email, password }` → 200:
```json
{ "access_token": "…", "token_type": "bearer", "role": "Penghuni", "user": UserOut }
```
Salah → 401 `"Email atau kata sandi salah"`.

### `POST /auth/lupa-sandi` (publik)
Body `{ email }` → selalu 200 `{ "message": "Jika email terdaftar, instruksi telah dikirim." }`
(Belum ada pengiriman email sungguhan; cukup dicatat ke log server.)

### `GET /auth/me` → `UserOut`
### `PUT /auth/me` → `UserOut`
Body (semua opsional): `{ nama_lengkap, nomor_telepon, asal_kampus, kontak_darurat_nama, kontak_darurat_telepon }`

### `POST /auth/ganti-sandi`
Body `{ sandi_lama, sandi_baru (min 8) }` → 200 `{ "message": "Kata sandi berhasil diubah." }`; sandi lama salah → 400.

**`UserOut`:**
```json
{
  "id": 3, "nama_lengkap": "Fajar Nugraha", "email": "fajar@sukabirus.id",
  "nomor_telepon": "081222451274", "peran": "Penghuni",
  "asal_kampus": "Telkom University · Informatika",
  "kontak_darurat_nama": "Ibu Nugraha", "kontak_darurat_telepon": "081390012182",
  "kamar": "B02", "created_at": "…Z"
}
```

---

## 2. Unggah file — `/files`

### `POST /files` (login) — `multipart/form-data`, field `file`
- Hanya `image/jpeg`, `image/png`, `image/webp`, `application/pdf`; maks 5 MB → selain itu 422.
- Disimpan di folder `uploads/` backend, disajikan statis di **`/uploads/<nama>`** (di luar `/api/v1`).
- Respons 201: `{ "url": "/uploads/3f2a….jpg" }` (path relatif; frontend menggabungkan dengan origin server).

---

## 3. Profil kos — `/profil` (sudah ada, diperluas)

`GET /profil` (login) · `POST /profil` & `PUT /profil` (Pemilik).
Field tambahan: `bank_nama`, `bank_nomor_rekening`, `bank_atas_nama`, `tanggal_jatuh_tempo` (int, default 10),
`masa_tenggang_hari` (int, default 5), `tarif_parkir_motor` (int, default 0 = gratis 1 motor pertama),
`tarif_parkir_mobil` (int, default 75000), `kapasitas_parkir_motor` (default 20), `kapasitas_parkir_mobil` (default 4),
`kode_undangan` (string, mis. `KST-8241`).

---

## 4. Kamar — `/kamar` (sudah ada, diperluas)

`GET /kamar` (login), `POST /kamar`, `PUT /kamar/{id}`, `DELETE /kamar/{id}` (Pemilik).
Field tambahan: `lantai` (int), `tipe` (string, mis. `Standar`). Respons juga memuat `penghuni: PersonRef | null`.
Hapus kamar yang sedang dihuni → 400.

---

## 5. Penghuni & sewa — `/penghuni` (Pemilik)

### `GET /penghuni?status=&q=`
`status` ∈ status sewa; `q` mencari nama/kamar/plat nomor. Respons `PenghuniOut[]` (hanya yang punya sewa, terbaru dulu, `Sudah Keluar` di akhir).

### `GET /penghuni/{user_id}` → `PenghuniOut`
### `GET /penghuni/belum-ditempatkan` → `UserOut[]` (akun Penghuni tanpa sewa Aktif/Masa Tenggang)
### `POST /penghuni/{user_id}/sewa`
Body `{ room_id, tanggal_mulai (date), lama_bulan (int ≥1) }` → 201 `PenghuniOut`.
Kamar harus `Tersedia` → kamar jadi `Dihuni`; `tanggal_jatuh_tempo = tanggal_mulai + lama_bulan bulan`; status `Aktif`.
Langsung buat tagihan periode bulan berjalan.
### `PATCH /penghuni/{user_id}/status`
Body `{ status_sewa }`. `Sudah Keluar` → kamar kembali `Tersedia`.

**`PenghuniOut`:**
```json
{
  "user": UserOut,
  "sewa": { "id": 4, "kamar": "B02", "room_id": 12, "tanggal_mulai": "2025-02-01",
            "tanggal_jatuh_tempo": "2026-11-15", "status_sewa": "Masa Tenggang" },
  "kendaraan": [KendaraanOut],
  "tagihan_bulan_ini": "Belum Bayar"
}
```

---

## 6. Kendaraan & parkir — `/kendaraan`

- `GET /kendaraan` — Penghuni: miliknya; Pemilik: semua (+ `pemilik: PersonRef`).
- `POST /kendaraan` — Penghuni (untuk dirinya). Body `{ nomor_polisi, jenis_kendaraan, merk_warna }`. Plat duplikat → 400. Kapasitas parkir penuh → 400.
- `PATCH /kendaraan/{id}` — Pemilik: `{ slot_parkir }`; Penghuni pemilik kendaraan: `{ merk_warna }`.
- `DELETE /kendaraan/{id}` — pemilik kendaraan atau Pemilik kos.
- `GET /kendaraan/ringkasan` (Pemilik) → `{ motor_terpakai, motor_kapasitas, mobil_terpakai, mobil_kapasitas }`

**`KendaraanOut`:** `{ id, nomor_polisi, jenis_kendaraan, merk_warna, slot_parkir, pemilik: PersonRef }`

---

## 7. Tagihan & pembayaran — `/tagihan`

**Pembuatan otomatis:** setiap kali endpoint tagihan/dasbor dipanggil, backend memastikan setiap sewa `Aktif`/`Masa Tenggang`
punya tagihan untuk periode bulan berjalan (idempoten, unik per `lease_id + periode`). Komponen:
`Sewa kamar <nomor>` = harga kamar; parkir: motor pertama gratis (`tarif_parkir_motor` untuk motor berikutnya), tiap mobil `tarif_parkir_mobil`.
`jatuh_tempo` = tanggal `tanggal_jatuh_tempo` di bulan itu; `batas_tenggang` = jatuh_tempo + `masa_tenggang_hari`.
(Jika sewa baru dimulai setelah tanggal itu di bulan yang sama, tagihan pertama jatuh tempo pada `tanggal_mulai`.)
Jika lewat jatuh tempo dan belum lunas, sewa otomatis menjadi `Masa Tenggang`.
"Belum lunas" di sini (dan untuk `tunggakan`/`jumlah_penunggak`) = status `Belum Bayar` atau `Ditolak`;
tagihan `Menunggu Verifikasi` tidak dihitung menunggak karena penghuni sudah mengunggah bukti.

- `GET /tagihan?status=&periode=YYYY-MM` — Penghuni: miliknya (terbaru dulu); Pemilik: semua.
- `GET /tagihan/{id}`
- `POST /tagihan/{id}/bukti` (Penghuni pemilik tagihan) Body `{ bukti_bayar_url }`. Hanya jika status `Belum Bayar`/`Ditolak` → jadi `Menunggu Verifikasi`.
- `POST /tagihan/{id}/verifikasi` (Pemilik) Body `{ disetujui: bool, alasan?: string }`.
  - Setuju: `Lunas`, `diverifikasi_at`; sewa diperpanjang 1 bulan dari `tanggal_jatuh_tempo` lama dan status `Aktif`.
  - Tolak: `alasan` wajib (422) → `Ditolak`, `alasan_tolak`.
  - Hanya dari status `Menunggu Verifikasi` → selain itu 400.
- `GET /tagihan/ringkasan-status` (Pemilik) → `{ "Menunggu Verifikasi": 3, "Lunas": 15, "Ditolak": 1, "Belum Bayar": 2 }` untuk `periode` (default bulan ini).

**`TagihanOut`:**
```json
{
  "id": 21, "periode": "2026-11", "periode_label": "November 2026",
  "jumlah_tagihan": 1000000,
  "komponen": [ { "nama": "Sewa kamar B02", "jumlah": 950000 }, { "nama": "Parkir motor", "jumlah": 0 } ],
  "jatuh_tempo": "2026-11-10", "batas_tenggang": "2026-11-15",
  "status_tagihan": "Belum Bayar", "bukti_bayar_url": null, "alasan_tolak": null,
  "tanggal_unggah": null, "diverifikasi_at": null,
  "penghuni": PersonRef, "kamar": "B02"
}
```

---

## 8. Keuangan — `/keuangan` (Pemilik)

Parameter rentang: `dari`, `sampai` (date, default awal–akhir bulan berjalan).
- `GET /keuangan/ringkasan` → `{ pemasukan, pengeluaran, laba_bersih, tunggakan, jumlah_lunas, jumlah_penunggak }`
  (pemasukan = tagihan `Lunas` yang `diverifikasi_at` dalam rentang; tunggakan = tagihan belum lunas yang sudah lewat jatuh tempo).
- `GET /keuangan/transaksi` → `[{ tanggal, keterangan, kategori: "Sewa"|"Tambahan"|"Pengeluaran", nominal }]` (pengeluaran bernilai negatif; terbaru dulu).
  Tagihan lunas dipecah: komponen sewa → `Sewa`, komponen lain dengan nominal > 0 → `Tambahan`.
- `GET /keuangan/pemasukan-bulanan?bulan=6` → `[{ periode: "2026-06", label: "Jun", total }]` (lama → baru).
- `POST /keuangan/pengeluaran` Body `{ tanggal, keterangan, kategori, nominal (>0) }` → 201 `PengeluaranOut`.
- `GET /keuangan/pengeluaran` → `PengeluaranOut[]` · `DELETE /keuangan/pengeluaran/{id}`.
- `GET /keuangan/rekap.xlsx` → file Excel (`openpyxl`) berisi ringkasan + daftar transaksi rentang tersebut.

---

## 9. Aspirasi — `/aspirasi`

- `GET /aspirasi?status=` — Penghuni: miliknya; Pemilik: semua. Terbaru dulu.
- `POST /aspirasi` (Penghuni) Body `{ judul, kategori, deskripsi_kendala, lampiran_foto_urls: [≤3] }`. Judul/deskripsi kosong → 422.
- `PATCH /aspirasi/{id}` (Pemilik) Body `{ status_penanganan?, tanggapan_pemilik? }`.

**`AspirasiOut`:** `{ id, judul, kategori, deskripsi_kendala, lampiran_foto_urls, status_penanganan, tanggapan_pemilik, created_at, updated_at, pelapor: PersonRef }`

---

## 10. Perizinan — `/izin`

- `GET /izin?status=` — Penghuni: miliknya; Pemilik: semua.
- `POST /izin` (Penghuni) Body `{ jenis_izin, tanggal_mulai, tanggal_selesai, alasan }`. `tanggal_selesai < tanggal_mulai` → 422. `durasi` dihitung (mis. `"5 hari"`, `"1 malam"` untuk Pulang Larut).
- `PATCH /izin/{id}` (Pemilik) Body `{ status_izin: "Disetujui"|"Ditolak", catatan_pemilik? }`. Hanya dari `Pending`.

**`IzinOut`:** `{ id, jenis_izin, tanggal_mulai, tanggal_selesai, durasi, alasan, status_izin, catatan_pemilik, created_at, pemohon: PersonRef }`

---

## 11. Pengumuman — `/pengumuman`

- `GET /pengumuman` (login) — disematkan dulu, lalu terbaru.
- `POST /pengumuman` (Pemilik) Body `{ judul, isi_pengumuman, disematkan: bool }` → 201.
- `PATCH /pengumuman/{id}` (Pemilik) Body `{ judul?, isi_pengumuman?, disematkan? }` · `DELETE /pengumuman/{id}` (Pemilik).
- `POST /pengumuman/{id}/baca` (Penghuni) → tandai sudah dibaca (idempoten).

**`PengumumanOut`:** `{ id, judul, isi_pengumuman, disematkan, created_at, pembuat: PersonRef, dibaca_count, total_penghuni, sudah_dibaca }`

---

## 12. Aturan kos — `/aturan`

- `GET /aturan` — Penghuni: hanya aktif; Pemilik: semua. Urut `urutan`.
- `POST /aturan` · `PUT /aturan/{id}` · `DELETE /aturan/{id}` (Pemilik). Body `{ judul, deskripsi, sanksi, status_aktif }`.

**`AturanOut`:** `{ id, urutan, judul, deskripsi, sanksi, status_aktif, updated_at }` (`sanksi` contoh `"Teguran"`, `"Denda Rp 50.000"`).

---

## 13. Penilaian — `/penilaian`

- `POST /penilaian` (Penghuni) Body `{ skor_bintang (1–5), aspek, ulasan_feedback? }` → 201.
- `GET /penilaian` — Pemilik: semua; Penghuni: miliknya.
- `GET /penilaian/ringkasan` (login) → `{ rata_rata, jumlah, distribusi: {"1":0,…,"5":12}, per_aspek: [{ aspek, rata_rata, jumlah }] }`

**`PenilaianOut`:** `{ id, skor_bintang, aspek, ulasan_feedback, created_at, pengguna: PersonRef }`

---

## 14. Barang hilang (UC-15) — `/barang-hilang`

- `GET /barang-hilang?status=Aktif|Selesai&q=` (login). Aktif: terbaru dulu; Selesai: `selesai_at` terbaru dulu.
- `POST /barang-hilang` (login) Body `{ jenis, judul_barang, deskripsi?, lokasi?, foto_url? }`.
  Nama barang kosong → **422 `"Nama barang wajib diisi"`** (skenario alternatif 6a).
- `POST /barang-hilang/{id}/selesai` — **hanya pelapor** (403 selain pelapor) → `Selesai`, `selesai_at`.

**`BarangHilangOut`:** `{ id, jenis, judul_barang, deskripsi, lokasi, foto_url, status_barang, created_at, selesai_at, pelapor: PersonRef }`

---

## 15. Dasbor — `/dasbor`

### `GET /dasbor/pemilik`
```json
{
  "nama_kos": "Kos Griya Sukabirus", "total_kamar": 20, "kamar_terisi": 18,
  "pemasukan_bulan_ini": 15400000, "tagihan_lunas": 15, "total_tagihan": 18,
  "tunggakan": 2100000, "jumlah_penunggak": 3, "jumlah_tenggang": 1,
  "rating_rata": 4.6, "jumlah_ulasan": 32,
  "perlu_tindakan": { "bukti_menunggu": 3, "izin_pending": 2, "aspirasi_baru": 4, "sewa_berakhir_7_hari": 2 },
  "pemasukan_6_bulan": [ { "periode": "2026-06", "label": "Jun", "total": 14200000 } ],
  "peta_kamar": [ { "lantai": 1, "kamar": [ { "id": 1, "nomor": "A01", "status": "Lunas", "penghuni": "Andi Saputra" } ] } ],
  "menunggu_verifikasi": [TagihanOut],
  "aktivitas": [ { "jenis": "Aspirasi"|"Izin"|"Lunas"|"Ulasan"|"Barang Hilang", "judul": "…", "nama": "…", "kamar": "B02", "waktu": "…Z" } ]
}
```
`peta_kamar[].kamar[].status` ∈ `Lunas`, `Belum Bayar`, `Menunggu`, `Masa Tenggang`, `Kosong`.

### `GET /dasbor/penghuni`
```json
{
  "nama_kos": "Kos Griya Sukabirus", "kamar": "B02", "status_sewa": "Masa Tenggang",
  "sewa_mulai": "2025-02-01", "sewa_sampai": "2026-11-15",
  "tagihan_aktif": TagihanOut | null,
  "pengumuman_terbaru": PengumumanOut | null,
  "permintaan": [ { "jenis": "Aspirasi"|"Izin", "id": 5, "judul": "…", "status": "Menunggu", "created_at": "…Z" } ],
  "jumlah_aturan_aktif": 4
}
```

---

## Data contoh (seed)

`python -m app.seed` (idempoten) — `python -m app.seed --reset` menghapus & membuat ulang semua tabel.

| Peran | Email | Sandi |
|---|---|---|
| Pemilik | `budi@kostopia.id` | `pemilik2026` |
| Penghuni (B02, masa tenggang) | `fajar@sukabirus.id` | `rahasia123` |
| Penghuni lain | `andi@sukabirus.id`, `salsa@sukabirus.id`, … | `rahasia123` |
