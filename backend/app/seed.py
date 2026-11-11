"""Data contoh Kostopia.

Pemakaian (dari folder root backend):
    python -m app.seed           # isi data contoh jika database masih kosong (idempoten)
    python -m app.seed --reset   # HAPUS semua tabel, buat ulang, lalu isi data contoh

Semua tanggal dibuat relatif terhadap hari ini sehingga data selalu terlihat "terkini".
"""
import argparse
import random
import sys
from datetime import date, datetime, time, timedelta

from app.core.database import Base, SessionLocal, engine
from app.core.waktu import NAMA_BULAN, awal_akhir_bulan, periode_dari, sekarang, tambah_bulan, tanggal_di_periode
from app.models.domain import (
    Announcement, AnnouncementRead, Aspiration, Expense, Lease, LostFound, PeranPengguna, Permission,
    ProfilKos, Rating, Room, Rules, Transaction, User, Vehicle,
    KAMAR_DIHUNI, KAMAR_PERBAIKAN, KAMAR_TERSEDIA, SEWA_AKTIF, SEWA_KELUAR, SEWA_TENGGANG,
    TAGIHAN_BELUM, TAGIHAN_DITOLAK, TAGIHAN_LUNAS, TAGIHAN_MENUNGGU,
)
from app.services.tagihan import hitung_komponen
from app.services.user_services import hash_password

SANDI_PENGHUNI = "rahasia123"
SANDI_PEMILIK = "pemilik2026"

# (nama, email, kamar, telepon, kampus, bulan_sewa_lalu, status tagihan bulan ini)
PENGHUNI = [
    ("Andi Saputra", "andi", "A01", "081234560101", "Telkom University · Teknik Telekomunikasi", 14, TAGIHAN_LUNAS),
    ("Putri Lestari", "putri", "A02", "081234560102", "Telkom University · Desain Komunikasi Visual", 9, TAGIHAN_LUNAS),
    ("Rizky Aditya", "rizky", "A03", "081234560103", "Telkom University · Sistem Informasi", 11, TAGIHAN_MENUNGGU),
    ("Bagas Wicaksono", "bagas", "A04", "081234560104", "Telkom University · Teknik Industri", 7, TAGIHAN_LUNAS),
    ("Galih Ramadhan", "galih", "A05", "081234560105", "Telkom University · Teknik Elektro", 4, TAGIHAN_LUNAS),
    ("Intan Permata", "intan", "A06", "081234560106", "Telkom University · Manajemen Bisnis", 16, TAGIHAN_LUNAS),
    ("Nadia Putri", "nadia", "A07", "081234560107", "Telkom University · Akuntansi", 8, TAGIHAN_LUNAS),
    ("Reza Maulana", "reza", "A08", "081234560108", "Telkom University · Informatika", 5, TAGIHAN_LUNAS),
    ("Citra Anggraini", "citra", "A10", "081234560110", "Telkom University · Ilmu Komunikasi", 12, TAGIHAN_LUNAS),
    ("Hendra Gunawan", "hendra", "B01", "081234560201", "Telkom University · Teknik Fisika", 18, TAGIHAN_LUNAS),
    ("Fajar Nugraha", "fajar", "B02", "081222451274", "Telkom University · Informatika", 21, TAGIHAN_BELUM),
    ("Ayu Wulandari", "ayu", "B03", "081234560203", "Telkom University · Sistem Informasi", 6, TAGIHAN_LUNAS),
    ("Dimas Pratama", "dimas", "B04", "081234560204", "Telkom University · Teknik Komputer", 10, TAGIHAN_MENUNGGU),
    ("Farhan Akbar", "farhan", "B05", "081234560205", "Telkom University · Teknik Logistik", 3, TAGIHAN_LUNAS),
    ("Salsa Nabila", "salsa", "B06", "081234560206", "Telkom University · Desain Interior", 13, TAGIHAN_LUNAS),
    ("Laras Ayu", "laras", "B07", "081234560207", "Telkom University · Administrasi Bisnis", 15, TAGIHAN_MENUNGGU),
    ("Tiara Kusuma", "tiara", "B08", "081234560208", "Telkom University · Teknologi Informasi", 2, TAGIHAN_LUNAS),
    ("Yoga Firmansyah", "yoga", "B10", "081234560210", "Telkom University · Teknik Elektro", 19, TAGIHAN_DITOLAK),
]

# (email, plat, jenis, merk_warna, slot)
KENDARAAN = [
    ("andi", "D 3412 AFQ", "Motor", "Honda Vario · Merah", "M-01"),
    ("putri", "D 5520 UJK", "Motor", "Honda Scoopy · Krem", "M-02"),
    ("rizky", "B 1876 KZT", "Mobil", "Toyota Agya · Putih", "C-01"),
    ("rizky", "D 2208 RAD", "Motor", "Yamaha NMAX · Hitam", "M-03"),
    ("bagas", "D 6731 BGW", "Motor", "Honda Beat · Biru", "M-04"),
    ("intan", "D 1190 IPM", "Motor", "Yamaha Fazzio · Hijau", "M-05"),
    ("reza", "F 4415 RM", "Motor", "Suzuki Satria · Hitam", "M-06"),
    ("fajar", "D 4521 FNG", "Motor", "Honda Beat · Hitam", "M-07"),
    ("dimas", "D 1733 DPR", "Mobil", "Honda Brio · Abu-abu", "C-02"),
    ("dimas", "D 8890 DMS", "Motor", "Kawasaki KLX · Hijau", "M-08"),
    ("salsa", "D 2765 SNB", "Motor", "Honda Genio · Putih", "M-09"),
    ("laras", "E 5512 LA", "Motor", "Yamaha Mio · Pink", "M-10"),
    ("yoga", "D 3098 YF", "Motor", "Honda CBR150 · Merah", "M-11"),
    ("hendra", "D 7654 HG", "Motor", "Yamaha Aerox · Biru", None),
]


def _dt(tgl: date, jam: int, menit: int = 0) -> datetime:
    """Datetime UTC (naif) pada tanggal tertentu, tidak melebihi waktu sekarang."""
    hasil = datetime.combine(tgl, time(jam % 24, menit))
    batas = sekarang() - timedelta(minutes=5)
    return min(hasil, batas)


def _sudah_ada_data(db) -> bool:
    return db.query(User).filter(User.email == "budi@kostopia.id").first() is not None


def isi_data(db) -> None:
    rnd = random.Random(2026)
    today = date.today()
    periode_ini = periode_dari(today)
    awal_bulan_ini, _ = awal_akhir_bulan(today)

    # ---------- Profil kos ----------
    profil = ProfilKos(
        nama_kos="Kos Griya Sukabirus",
        alamat_lengkap="Jl. Sukabirus No. 27, Citeureup, Dayeuhkolot, Kabupaten Bandung, Jawa Barat 40257",
        deskripsi="Kos campur dekat kampus Telkom University. Kamar bersih, Wi-Fi 100 Mbps, dapur bersama, dan parkir luas.",
        nomor_telepon_pengelola="081311220044",
        informasi_rekening="BCA 4410 2041 88 a.n. Budi Utomo",
        gmaps_url="https://maps.google.com/?q=Jl.+Sukabirus+Dayeuhkolot+Bandung",
        bank_nama="BCA",
        bank_nomor_rekening="4410 2041 88",
        bank_atas_nama="Budi Utomo",
        tanggal_jatuh_tempo=10,
        masa_tenggang_hari=5,
        tarif_parkir_motor=50000,
        tarif_parkir_mobil=75000,
        kapasitas_parkir_motor=20,
        kapasitas_parkir_mobil=4,
        kode_undangan="KST-8241",
    )
    db.add(profil)

    # ---------- Pemilik ----------
    budi = User(
        nama_lengkap="Budi Utomo", email="budi@kostopia.id", password_hash=hash_password(SANDI_PEMILIK),
        nomor_telepon="081311220044", peran=PeranPengguna.pemilik,
        created_at=_dt(tambah_bulan(today, -30), 2),
    )
    db.add(budi)

    # ---------- Kamar ----------
    kamar = {}
    for lantai, huruf in ((1, "A"), (2, "B")):
        for i in range(1, 11):
            nomor = f"{huruf}{i:02d}"
            if huruf == "A":
                harga = 850000 + (i % 3) * 50000           # 850rb – 950rb
                tipe = "Standar"
            else:
                harga = 950000 + (i % 3) * 50000           # 950rb – 1,05jt
                tipe = "Kamar Mandi Dalam"
            status = KAMAR_TERSEDIA
            if nomor == "B09":
                status = KAMAR_PERBAIKAN
            kamar[nomor] = Room(nomor_kamar=nomor, harga_dasar=harga, lantai=lantai, tipe=tipe,
                                status_ketersediaan=status)
            db.add(kamar[nomor])
    kamar["B02"].harga_dasar = 950000
    db.flush()

    # ---------- Penghuni ----------
    users = {}
    for nama, kode, nomor, telp, kampus, bulan_lalu, _ in PENGHUNI:
        u = User(
            nama_lengkap=nama, email=f"{kode}@sukabirus.id", password_hash=hash_password(SANDI_PENGHUNI),
            nomor_telepon=telp, peran=PeranPengguna.penghuni, asal_kampus=kampus,
            kontak_darurat_nama=f"Ibu {nama.split()[-1]}",
            kontak_darurat_telepon=f"0813900{rnd.randint(10000, 99999)}",
            created_at=_dt(tambah_bulan(awal_bulan_ini, -bulan_lalu) - timedelta(days=3), 3),
        )
        users[kode] = u
        db.add(u)
    # Akun penghuni yang belum ditempatkan & mantan penghuni
    sinta = User(nama_lengkap="Sinta Maharani", email="sinta@sukabirus.id", password_hash=hash_password(SANDI_PENGHUNI),
                 nomor_telepon="081234560301", peran=PeranPengguna.penghuni,
                 asal_kampus="Telkom University · Informatika", created_at=_dt(today - timedelta(days=2), 4))
    kevin = User(nama_lengkap="Kevin Halim", email="kevin@sukabirus.id", password_hash=hash_password(SANDI_PENGHUNI),
                 nomor_telepon="081234560302", peran=PeranPengguna.penghuni,
                 asal_kampus="Telkom University · Teknik Industri", created_at=_dt(tambah_bulan(today, -14), 4))
    users["sinta"], users["kevin"] = sinta, kevin
    db.add_all([sinta, kevin])
    db.flush()

    # ---------- Kendaraan ----------
    for kode, plat, jenis, merk, slot in KENDARAAN:
        db.add(Vehicle(user_id=users[kode].id, nomor_polisi=plat, jenis_kendaraan=jenis, merk_warna=merk, slot_parkir=slot))
    db.flush()

    # ---------- Sewa & tagihan ----------
    jt_hari = profil.tanggal_jatuh_tempo
    lewat_jt_bulan_ini = today > tanggal_di_periode(periode_ini, jt_hari)
    for idx, (nama, kode, nomor, _, _, bulan_lalu, status_ini) in enumerate(PENGHUNI):
        u = users[kode]
        room = kamar[nomor]
        mulai = tambah_bulan(awal_bulan_ini, -bulan_lalu)
        lease = Lease(user_id=u.id, room_id=room.id, tanggal_mulai=mulai, status_sewa=SEWA_AKTIF)
        room.status_ketersediaan = KAMAR_DIHUNI
        db.add(lease)
        db.flush()
        db.refresh(lease)
        komponen = hitung_komponen(lease, profil)
        total = sum(k["jumlah"] for k in komponen)

        def tagihan(periode, status, **kw):
            jt = tanggal_di_periode(periode, jt_hari)
            t = Transaction(lease_id=lease.id, periode=periode, komponen_biaya=komponen, jumlah_tagihan=total,
                            jatuh_tempo=jt, batas_tenggang=jt + timedelta(days=profil.masa_tenggang_hari),
                            status_tagihan=status, created_at=_dt(tanggal_di_periode(periode, 1), 0), **kw)
            db.add(t)
            return t

        # 6 bulan terakhir (sebelum bulan ini) lunas, sejak sewa dimulai
        for k in range(6, 0, -1):
            awal = tambah_bulan(awal_bulan_ini, -k)
            if awal < mulai:
                continue
            periode = periode_dari(awal)
            # Fajar: jika hari ini belum lewat jatuh tempo, tagihan bulan lalu dibiarkan belum bayar
            if kode == "fajar" and k == 1 and not lewat_jt_bulan_ini:
                tagihan(periode, TAGIHAN_BELUM)
                continue
            hari_unggah = 3 + (idx + k) % 7
            unggah = _dt(awal.replace(day=hari_unggah), 1 + idx % 12, (idx * 7) % 60)
            tagihan(periode, TAGIHAN_LUNAS, bukti_bayar_url=f"/uploads/contoh-bukti-{kode}-{periode}.jpg",
                    tanggal_unggah=unggah, diverifikasi_at=unggah + timedelta(hours=5 + idx % 5))

        # Tagihan bulan ini
        jt_ini = tanggal_di_periode(periode_ini, jt_hari)
        if status_ini == TAGIHAN_LUNAS:
            hari = min(today.day, 2 + idx % 8)
            unggah = _dt(awal_bulan_ini.replace(day=hari), 1 + idx % 10, (idx * 11) % 60)
            tagihan(periode_ini, TAGIHAN_LUNAS, bukti_bayar_url=f"/uploads/contoh-bukti-{kode}-{periode_ini}.jpg",
                    tanggal_unggah=unggah, diverifikasi_at=unggah + timedelta(hours=3))
            lease.tanggal_jatuh_tempo = tambah_bulan(jt_ini, 1)
        elif status_ini == TAGIHAN_MENUNGGU:
            unggah = _dt(today - timedelta(days=idx % 2), 2 + idx % 6, 20)
            tagihan(periode_ini, TAGIHAN_MENUNGGU, bukti_bayar_url=f"/uploads/contoh-bukti-{kode}-{periode_ini}.jpg",
                    tanggal_unggah=unggah)
            lease.tanggal_jatuh_tempo = jt_ini
        elif status_ini == TAGIHAN_DITOLAK:
            unggah = _dt(today - timedelta(days=2), 4, 5)
            tagihan(periode_ini, TAGIHAN_DITOLAK, bukti_bayar_url=f"/uploads/contoh-bukti-{kode}-{periode_ini}.jpg",
                    tanggal_unggah=unggah, alasan_tolak="Nominal transfer kurang Rp 50.000 dari total tagihan.")
            lease.tanggal_jatuh_tempo = jt_ini
            if lewat_jt_bulan_ini:
                lease.status_sewa = SEWA_TENGGANG
        else:  # Belum Bayar (Fajar)
            tagihan(periode_ini, TAGIHAN_BELUM)
            lease.tanggal_jatuh_tempo = jt_ini + timedelta(days=profil.masa_tenggang_hari)
            lease.status_sewa = SEWA_TENGGANG

    # Mantan penghuni di A09 (riwayat sewa, kamar kini tersedia)
    db.add(Lease(user_id=kevin.id, room_id=kamar["A09"].id, tanggal_mulai=tambah_bulan(awal_bulan_ini, -14),
                 tanggal_jatuh_tempo=tambah_bulan(awal_bulan_ini, -2), status_sewa=SEWA_KELUAR))
    db.flush()

    # ---------- Pengeluaran ----------
    for k in range(6, -1, -1):
        awal = tambah_bulan(awal_bulan_ini, -k)
        label = NAMA_BULAN[awal.month - 1]
        daftar = [
            (2, f"Token listrik bersama {label}", "Listrik", 1350000 + rnd.randint(0, 6) * 25000),
            (4, f"Tagihan PDAM {label}", "Air", 420000 + rnd.randint(0, 5) * 10000),
            (5, f"Gaji petugas kebersihan {label}", "Gaji", 1200000),
            (12, "Sabun, pel & kantong sampah", "Kebersihan", 185000 + rnd.randint(0, 4) * 15000),
        ]
        if k % 2 == 0:
            daftar.append((18, rnd.choice(["Servis pompa air", "Ganti lampu koridor lantai 2",
                                            "Perbaikan keran dapur", "Cat ulang pagar depan"]),
                           "Perbaikan", 250000 + rnd.randint(0, 10) * 25000))
        if k == 3:
            daftar.append((20, "Perpanjangan langganan Wi-Fi 100 Mbps", "Lainnya", 650000))
        for hari, ket, kat, nominal in daftar:
            tgl = awal.replace(day=hari)
            if tgl > today:
                continue
            db.add(Expense(tanggal=tgl, keterangan=ket, kategori=kat, nominal=nominal, created_at=_dt(tgl, 6)))

    # ---------- Pengumuman ----------
    bulan_depan = NAMA_BULAN[tambah_bulan(awal_bulan_ini, 1).month - 1]
    pengumuman = [
        (f"Pembayaran sewa {bulan_depan}", True, 1,
         f"Halo teman-teman, pembayaran sewa bulan {bulan_depan} paling lambat tanggal {jt_hari}. "
         f"Transfer ke BCA 4410 2041 88 a.n. Budi Utomo lalu unggah bukti di aplikasi Kostopia. Terima kasih!"),
        ("Pemadaman listrik terjadwal", False, 3,
         "PLN akan melakukan pemeliharaan jaringan hari Sabtu pukul 09.00–13.00. Mohon simpan pekerjaan dan cabut perangkat elektronik."),
        ("Kerja bakti bulanan", False, 9,
         "Kerja bakti membersihkan dapur dan area jemur hari Minggu pukul 07.30. Sarapan disediakan pengelola."),
        ("Fogging nyamuk area kos", False, 20,
         "Akan dilakukan fogging di seluruh area kos. Harap tutup jendela dan simpan makanan di wadah tertutup."),
    ]
    penghuni_aktif = [users[p[1]] for p in PENGHUNI]
    for idx, (judul, pin, hari_lalu, isi) in enumerate(pengumuman):
        a = Announcement(user_id=budi.id, judul=judul, isi_pengumuman=isi, disematkan=pin,
                         created_at=_dt(today - timedelta(days=hari_lalu), 2 + idx))
        db.add(a)
        db.flush()
        jumlah_baca = {0: 11, 1: 15, 2: 17, 3: 18}[idx]
        for u in penghuni_aktif[:jumlah_baca]:
            if u.email == "fajar@sukabirus.id" and idx == 0:
                continue  # Fajar belum membaca pengumuman yang disematkan
            db.add(AnnouncementRead(announcement_id=a.id, user_id=u.id, dibaca_at=a.created_at + timedelta(hours=2)))

    # ---------- Aturan ----------
    aturan = [
        ("Jam malam pukul 23.00", "Gerbang utama dikunci pukul 23.00. Penghuni yang pulang lebih larut wajib mengajukan izin Pulang Larut di aplikasi.", "Teguran"),
        ("Tamu lawan jenis dilarang masuk kamar", "Tamu lawan jenis hanya boleh berada di ruang tamu lantai 1 sampai pukul 21.00.", "Denda Rp 50.000"),
        ("Jaga kebersihan dapur bersama", "Cuci peralatan masak setelah dipakai dan buang sampah pada tempatnya.", "Teguran"),
        ("Parkir sesuai slot", "Kendaraan wajib diparkir di slot yang sudah ditentukan pengelola.", "Denda Rp 25.000"),
    ]
    for i, (judul, desk, sanksi) in enumerate(aturan, start=1):
        db.add(Rules(poin_aturan=judul, deskripsi=desk, sanksi=sanksi, urutan=i, status_aktif=True,
                     updated_at=_dt(today - timedelta(days=40 - i), 3)))

    # ---------- Aspirasi ----------
    aspirasi = [
        ("fajar", "Keran kamar mandi bocor", "Kerusakan", "Keran di kamar mandi B02 terus menetes walaupun sudah ditutup rapat.", "Menunggu", None, 1),
        ("salsa", "Lampu koridor lantai 2 mati", "Fasilitas", "Lampu di depan kamar B05–B07 mati sejak dua hari lalu, gelap saat malam.", "Menunggu", None, 2),
        ("andi", "Wi-Fi sering terputus malam hari", "Fasilitas", "Mulai pukul 20.00 koneksi Wi-Fi sering putus, padahal sedang kuliah daring.", "Menunggu", None, 3),
        ("nadia", "Tempat sampah dapur penuh", "Kebersihan", "Tempat sampah dapur sudah penuh sejak kemarin dan mulai bau.", "Menunggu", None, 0),
        ("dimas", "Pintu gerbang sulit dikunci", "Keamanan", "Gembok gerbang samping macet sehingga sering dibiarkan terbuka.", "Sedang Diproses", "Sudah dipesan gembok baru, dipasang besok sore.", 5),
        ("laras", "Mesin cuci bersama bergetar keras", "Kerusakan", "Mesin cuci di area jemur bergetar keras dan berisik saat proses pengeringan.", "Sedang Diproses", "Teknisi dijadwalkan datang Kamis ini.", 7),
        ("rizky", "Tambah rak sepatu di depan", "Saran", "Usul ditambah rak sepatu di teras karena sepatu sering berserakan.", "Selesai", "Rak sepatu baru sudah dipasang di teras. Terima kasih sarannya!", 15),
        ("fajar", "AC kamar kurang dingin", "Kerusakan", "AC di kamar B02 kurang dingin, mungkin perlu dicuci.", "Selesai", "AC sudah diservis dan freon ditambah.", 25),
    ]
    for kode, judul, kat, desk, status, tanggapan, hari_lalu in aspirasi:
        dibuat = _dt(today - timedelta(days=hari_lalu), 1 + hari_lalu % 10, 15)
        db.add(Aspiration(user_id=users[kode].id, judul=judul, kategori=kat, deskripsi_kendala=desk,
                          lampiran_foto_url=[], status_penanganan=status, tanggapan_pemilik=tanggapan,
                          created_at=dibuat, updated_at=dibuat + timedelta(days=1 if tanggapan else 0)))

    # ---------- Perizinan ----------
    izin = [
        ("fajar", "Pulang Kampung", 3, 7, "Acara keluarga di Garut.", "Pending", None, 0),
        ("tiara", "Menginap di Luar", 1, 2, "Mengerjakan tugas besar di rumah teman.", "Pending", None, 1),
        ("andi", "Pulang Larut", 0, 0, "Rapat himpunan sampai pukul 00.30.", "Disetujui", "Hati-hati di jalan.", 4),
        ("salsa", "Pulang Kampung", -10, -6, "Libur semester singkat.", "Disetujui", None, 14),
        ("yoga", "Lainnya", -20, -19, "Lomba robotik di Surabaya.", "Disetujui", "Semoga juara!", 24),
        ("reza", "Menginap di Luar", -5, -4, "Menginap di rumah saudara.", "Ditolak", "Tanggal bentrok dengan kerja bakti, silakan ajukan ulang.", 8),
    ]
    from app.services.izin import hitung_durasi
    for kode, jenis, mulai_d, selesai_d, alasan, status, catatan, hari_lalu in izin:
        mulai = today + timedelta(days=mulai_d)
        selesai = today + timedelta(days=selesai_d)
        db.add(Permission(user_id=users[kode].id, jenis_izin=jenis, tanggal_mulai=mulai, tanggal_selesai=selesai,
                          durasi=hitung_durasi(jenis, mulai, selesai), alasan=alasan, status_izin=status,
                          catatan_pemilik=catatan, created_at=_dt(today - timedelta(days=hari_lalu), 2 + hari_lalu % 9, 40)))

    # ---------- Penilaian (rata-rata ±4,6 dari 32 ulasan) ----------
    skor = [5] * 22 + [4] * 8 + [3] * 2
    rnd.shuffle(skor)
    aspek_list = ["Kebersihan", "Keamanan", "Fasilitas", "Pelayanan", "Umum"]
    ulasan = {
        5: ["Kos nyaman dan bersih, pengelola ramah.", "Lokasi dekat kampus, Wi-Fi kencang.", "Aman, ada CCTV dan gerbang terkunci.",
            "Respons pengelola cepat kalau ada kerusakan.", "Harga sepadan dengan fasilitas."],
        4: ["Secara umum bagus, dapur kadang kurang rapi.", "Parkir cukup luas, tapi lampu koridor perlu dicek.",
            "Nyaman, semoga Wi-Fi malam hari lebih stabil."],
        3: ["Air kadang kecil saat pagi.", "Mesin cuci bersama sering antre."],
    }
    for i, s in enumerate(skor):
        kode = PENGHUNI[i % len(PENGHUNI)][1]
        db.add(Rating(user_id=users[kode].id, skor_bintang=s, aspek=aspek_list[i % len(aspek_list)],
                      ulasan_feedback=rnd.choice(ulasan[s]),
                      created_at=_dt(today - timedelta(days=2 + i * 5), 1 + i % 12, (i * 13) % 60)))

    # ---------- Barang hilang & temuan ----------
    barang = [
        ("fajar", "Hilang", "Payung lipat hitam", "Payung lipat merek Fibrella warna hitam, gagang ada stiker bintang.", "Teras lantai 1", "Aktif", 1),
        ("andi", "Temuan", "Kunci motor gantungan biru", "Ditemukan kunci motor Honda dengan gantungan karet biru.", "Area parkir motor", "Aktif", 2),
        ("salsa", "Hilang", "Kartu mahasiswa", "KTM Telkom University atas nama Salsa Nabila.", "Dapur bersama", "Aktif", 3),
        (None, "Temuan", "Charger laptop USB-C", "Charger 65W warna putih tertinggal di ruang tamu.", "Ruang tamu", "Aktif", 4),
        ("nadia", "Hilang", "Tumbler hijau", "Tumbler stainless hijau tosca 500 ml.", "Area jemur", "Selesai", 12),
    ]
    for kode, jenis, judul, desk, lokasi, status, hari_lalu in barang:
        pelapor = users[kode] if kode else budi
        dibuat = _dt(today - timedelta(days=hari_lalu), 3 + hari_lalu, 10)
        db.add(LostFound(user_id=pelapor.id, jenis=jenis, judul_barang=judul, deskripsi=desk, lokasi=lokasi,
                         status_barang=status, created_at=dibuat,
                         selesai_at=dibuat + timedelta(days=2) if status == "Selesai" else None))

    db.commit()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Isi database Kostopia dengan data contoh.")
    parser.add_argument("--reset", action="store_true", help="hapus & buat ulang semua tabel sebelum mengisi data")
    args = parser.parse_args(argv)

    if args.reset:
        print("Menghapus semua tabel...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if _sudah_ada_data(db):
            print("Data contoh sudah ada (akun budi@kostopia.id ditemukan), tidak ada yang diubah.")
            print("Gunakan `python -m app.seed --reset` untuk mengulang dari awal.")
            return 0
        isi_data(db)
        print("Data contoh berhasil dibuat.")
        print(f"  Pemilik : budi@kostopia.id / {SANDI_PEMILIK}")
        print(f"  Penghuni: fajar@sukabirus.id / {SANDI_PENGHUNI} (B02, masa tenggang)")
        print(f"  Penghuni lain: andi@, salsa@, nadia@, dimas@ ... @sukabirus.id / {SANDI_PENGHUNI}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
