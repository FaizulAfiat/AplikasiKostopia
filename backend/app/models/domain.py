from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, Enum, JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base
from app.core.waktu import sekarang, periode_label
import enum

# Pilihan peran pengguna: Pemilik kos atau Penghuni
class PeranPengguna(str, enum.Enum):
    pemilik = "Pemilik"
    penghuni = "Penghuni"


# Nilai status (string persis sesuai kontrak docs/API.md)
SEWA_AKTIF = "Aktif"
SEWA_TENGGANG = "Masa Tenggang"
SEWA_KELUAR = "Sudah Keluar"
SEWA_BERJALAN = (SEWA_AKTIF, SEWA_TENGGANG)

KAMAR_TERSEDIA = "Tersedia"
KAMAR_DIHUNI = "Dihuni"
KAMAR_PERBAIKAN = "Perbaikan"

TAGIHAN_BELUM = "Belum Bayar"
TAGIHAN_MENUNGGU = "Menunggu Verifikasi"
TAGIHAN_LUNAS = "Lunas"
TAGIHAN_DITOLAK = "Ditolak"


# Tabel pengguna (pemilik & penghuni) beserta relasinya ke tabel lain
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nomor_telepon = Column(String)
    peran = Column(Enum(PeranPengguna), default=PeranPengguna.penghuni)
    asal_kampus = Column(String, nullable=True)
    kontak_darurat_nama = Column(String, nullable=True)
    kontak_darurat_telepon = Column(String, nullable=True)
    created_at = Column(DateTime, default=sekarang)

    kendaraan = relationship("Vehicle", back_populates="pemilik")
    lost_found = relationship("LostFound", back_populates="pelapor")
    perizinan = relationship("Permission", back_populates="pemohon")
    penilaian = relationship("Rating", back_populates="pengguna")
    aspirasi = relationship("Aspiration", back_populates="pelapor")
    pengumuman = relationship("Announcement", back_populates="pembuat")
    sewa = relationship("Lease", back_populates="penyewa", order_by="Lease.id")

    @property
    def sewa_aktif(self):
        """Sewa berstatus Aktif/Masa Tenggang (terbaru), atau None."""
        aktif = [s for s in self.sewa if s.status_sewa in SEWA_BERJALAN]
        return aktif[-1] if aktif else None

    @property
    def kamar(self):
        """Nomor kamar dari sewa aktif (dipakai PersonRef & UserOut)."""
        sewa = self.sewa_aktif
        return sewa.kamar.nomor_kamar if sewa and sewa.kamar else None


# Tabel aturan/tata tertib kos
class Rules(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True, index=True)
    poin_aturan = Column(Text)  # menyimpan judul aturan
    deskripsi = Column(Text, nullable=True)
    sanksi = Column(String, nullable=True)
    urutan = Column(Integer, default=0)
    status_aktif = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=sekarang, onupdate=sekarang)

    # Nama field di API adalah `judul`
    judul = synonym("poin_aturan")


# Tabel kamar kos (nomor, status ketersediaan, harga)
class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    nomor_kamar = Column(String, unique=True, index=True)
    status_ketersediaan = Column(String, default=KAMAR_TERSEDIA)
    harga_dasar = Column(Integer)  # rupiah bulat
    lantai = Column(Integer, default=1)
    tipe = Column(String, default="Standar")

    sewa = relationship("Lease", back_populates="kamar")

    @property
    def sewa_aktif(self):
        aktif = [s for s in self.sewa if s.status_sewa in SEWA_BERJALAN]
        return max(aktif, key=lambda s: s.id) if aktif else None

    @property
    def penghuni(self):
        sewa = self.sewa_aktif
        return sewa.penyewa if sewa else None


# Tabel kendaraan milik pengguna
class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    nomor_polisi = Column(String, unique=True)
    jenis_kendaraan = Column(String)  # Motor / Mobil
    merk_warna = Column(String)
    slot_parkir = Column(String, nullable=True)

    pemilik = relationship("User", back_populates="kendaraan")


# Tabel laporan barang hilang/ditemukan
class LostFound(Base):
    __tablename__ = "lost_found"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    jenis = Column(String, default="Hilang")  # Hilang / Temuan
    judul_barang = Column(String)
    deskripsi = Column(Text)
    foto_url = Column(String, nullable=True)
    lokasi = Column(String)
    status_barang = Column(String, default="Aktif")
    created_at = Column(DateTime, default=sekarang)
    selesai_at = Column(DateTime, nullable=True)

    pelapor = relationship("User", back_populates="lost_found")


# Tabel pengajuan izin penghuni (disetujui/ditolak oleh pemilik)
class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    jenis_izin = Column(String)
    tanggal_mulai = Column(Date)
    tanggal_selesai = Column(Date)
    durasi = Column(String)
    alasan = Column(Text)
    status_izin = Column(String, default="Pending")
    catatan_pemilik = Column(Text, nullable=True)
    created_at = Column(DateTime, default=sekarang)

    pemohon = relationship("User", back_populates="perizinan")


# Tabel penilaian bintang dan ulasan dari pengguna
class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skor_bintang = Column(Integer)
    aspek = Column(String, default="Umum")
    ulasan_feedback = Column(Text)
    created_at = Column(DateTime, default=sekarang)

    pengguna = relationship("User", back_populates="penilaian")


# Tabel aspirasi/keluhan penghuni beserta tanggapan pemilik
class Aspiration(Base):
    __tablename__ = "aspirations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    judul = Column(String)
    kategori = Column(String)
    deskripsi_kendala = Column(Text)
    lampiran_foto_url = Column(JSON, default=list)  # list URL foto (maks 3)
    status_penanganan = Column(String, default="Menunggu")
    tanggapan_pemilik = Column(Text, nullable=True)
    created_at = Column(DateTime, default=sekarang)
    updated_at = Column(DateTime, default=sekarang, onupdate=sekarang)

    pelapor = relationship("User", back_populates="aspirasi")

    @property
    def lampiran_foto_urls(self):
        return list(self.lampiran_foto_url or [])


# Tabel pengumuman yang dibuat oleh pemilik
class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    judul = Column(String)
    isi_pengumuman = Column(Text)
    disematkan = Column(Boolean, default=False)
    created_at = Column(DateTime, default=sekarang)

    pembuat = relationship("User", back_populates="pengumuman")
    pembaca = relationship("AnnouncementRead", back_populates="pengumuman",
                           cascade="all, delete-orphan")


# Tabel penanda pengumuman yang sudah dibaca penghuni
class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"
    __table_args__ = (UniqueConstraint("announcement_id", "user_id", name="uq_baca_pengumuman"),)
    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    dibaca_at = Column(DateTime, default=sekarang)

    pengumuman = relationship("Announcement", back_populates="pembaca")


# Tabel sewa: menghubungkan penghuni dengan kamar beserta jatuh tempo
class Lease(Base):
    __tablename__ = "leases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    tanggal_mulai = Column(Date)
    tanggal_jatuh_tempo = Column(Date)
    status_sewa = Column(String, default=SEWA_AKTIF)

    penyewa = relationship("User", back_populates="sewa")
    kamar = relationship("Room", back_populates="sewa")
    transaksi = relationship("Transaction", back_populates="sewa")


# Tabel tagihan/pembayaran dari setiap sewa (satu tagihan per sewa per bulan)
class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("lease_id", "periode", name="uq_tagihan_sewa_periode"),)
    id = Column(Integer, primary_key=True, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"))
    periode = Column(String(7), index=True)  # "YYYY-MM"
    jumlah_tagihan = Column(Integer)  # rupiah bulat
    komponen_biaya = Column(JSON, default=list)  # [{"nama": ..., "jumlah": ...}]
    jatuh_tempo = Column(Date)
    batas_tenggang = Column(Date)
    bukti_bayar_url = Column(String, nullable=True)
    status_tagihan = Column(String, default=TAGIHAN_BELUM)
    alasan_tolak = Column(Text, nullable=True)
    tanggal_unggah = Column(DateTime, nullable=True)
    diverifikasi_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=sekarang)
    updated_at = Column(DateTime, default=sekarang, onupdate=sekarang)

    sewa = relationship("Lease", back_populates="transaksi")

    @property
    def komponen(self):
        return list(self.komponen_biaya or [])

    @property
    def periode_label(self):
        return periode_label(self.periode)

    @property
    def penghuni(self):
        return self.sewa.penyewa if self.sewa else None

    @property
    def kamar(self):
        return self.sewa.kamar.nomor_kamar if self.sewa and self.sewa.kamar else None


# Tabel pengeluaran operasional kos (dicatat pemilik)
class Expense(Base):
    __tablename__ = "pengeluaran"
    id = Column(Integer, primary_key=True, index=True)
    tanggal = Column(Date)
    keterangan = Column(String)
    kategori = Column(String)
    nominal = Column(Integer)
    created_at = Column(DateTime, default=sekarang)


# Tabel profil kos (Sistem Single-Property, hanya akan berisi 1 baris data)
class ProfilKos(Base):
    __tablename__ = "profil_kos"

    id = Column(Integer, primary_key=True, index=True)
    nama_kos = Column(String, nullable=False, default="Kostopia")
    alamat_lengkap = Column(Text, nullable=False, default="")
    deskripsi = Column(Text, nullable=True)
    nomor_telepon_pengelola = Column(String, nullable=True)
    informasi_rekening = Column(String, nullable=True)
    gmaps_url = Column(String, nullable=True)
    bank_nama = Column(String, nullable=True)
    bank_nomor_rekening = Column(String, nullable=True)
    bank_atas_nama = Column(String, nullable=True)
    tanggal_jatuh_tempo = Column(Integer, default=10)
    masa_tenggang_hari = Column(Integer, default=5)
    tarif_parkir_motor = Column(Integer, default=0)
    tarif_parkir_mobil = Column(Integer, default=75000)
    kapasitas_parkir_motor = Column(Integer, default=20)
    kapasitas_parkir_mobil = Column(Integer, default=4)
    kode_undangan = Column(String, nullable=True)
    updated_at = Column(DateTime, default=sekarang, onupdate=sekarang)
