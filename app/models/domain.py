from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime
import enum

# Pilihan peran pengguna: Pemilik kos atau Penghuni
class PeranPengguna(str, enum.Enum):
    pemilik = "Pemilik"
    penghuni = "Penghuni"

# Tabel pengguna (pemilik & penghuni) beserta relasinya ke tabel lain
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nomor_telepon = Column(String)
    peran = Column(Enum(PeranPengguna), default=PeranPengguna.penghuni)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    kendaraan = relationship("Vehicle", back_populates="pemilik")
    lost_found = relationship("LostFound", back_populates="pelapor")
    perizinan = relationship("Permission", back_populates="pemohon")
    penilaian = relationship("Rating", back_populates="pengguna")
    aspirasi = relationship("Aspiration", back_populates="pelapor")
    pengumuman = relationship("Announcement", back_populates="pembuat")
    sewa = relationship("Lease", back_populates="penyewa")

# Tabel aturan/tata tertib kos
class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True, index=True)
    poin_aturan = Column(Text)
    status_aktif = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Tabel kamar kos (nomor, status ketersediaan, harga)
class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    nomor_kamar = Column(String, unique=True, index=True)
    status_ketersediaan = Column(String)
    harga_dasar = Column(Numeric)

    sewa = relationship("Lease", back_populates="kamar")

# Tabel kendaraan milik pengguna
class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    nomor_polisi = Column(String, unique=True)
    jenis_kendaraan = Column(String)
    merk_warna = Column(String)

    pemilik = relationship("User", back_populates="kendaraan")

# Tabel laporan barang hilang/ditemukan
class LostFound(Base):
    __tablename__ = "lost_found"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    judul_barang = Column(String)
    deskripsi = Column(Text)
    foto_url = Column(String, nullable=True)
    lokasi = Column(String)
    status_barang = Column(String, default="Aktif")

    pelapor = relationship("User", back_populates="lost_found")

# Tabel pengajuan izin penghuni (disetujui/ditolak oleh pemilik)
class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    jenis_izin = Column(String)
    tanggal_mulai = Column(Date)
    durasi = Column(String)
    alasan = Column(Text)
    status_izin = Column(String, default="Pending")
    catatan_pemilik = Column(Text, nullable=True)

    pemohon = relationship("User", back_populates="perizinan")

# Tabel penilaian bintang dan ulasan dari pengguna
class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skor_bintang = Column(Integer)
    ulasan_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    pengguna = relationship("User", back_populates="penilaian")

# Tabel aspirasi/keluhan penghuni beserta tanggapan pemilik
class Aspiration(Base):
    __tablename__ = "aspirations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    deskripsi_kendala = Column(Text)
    lampiran_foto_url = Column(String, nullable=True)
    status_penanganan = Column(String, default="Menunggu")
    tanggapan_pemilik = Column(Text, nullable=True)

    pelapor = relationship("User", back_populates="aspirasi")

# Tabel pengumuman yang dibuat oleh pemilik
class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    judul = Column(String)
    isi_pengumuman = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    pembuat = relationship("User", back_populates="pengumuman")

# Tabel sewa: menghubungkan penghuni dengan kamar beserta jatuh tempo
class Lease(Base):
    __tablename__ = "leases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    tanggal_mulai = Column(Date)
    tanggal_jatuh_tempo = Column(Date)
    status_sewa = Column(String)

    penyewa = relationship("User", back_populates="sewa")
    kamar = relationship("Room", back_populates="sewa")
    transaksi = relationship("Transaction", back_populates="sewa")

# Tabel tagihan/pembayaran dari setiap sewa
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"))
    jumlah_tagihan = Column(Numeric)
    komponen_biaya = Column(String)
    bukti_bayar_url = Column(String, nullable=True)
    status_tagihan = Column(String, default="Belum Bayar")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    sewa = relationship("Lease", back_populates="transaksi")

# Tabel profil kos (Sistem Single-Property, hanya akan berisi 1 baris data)
class ProfilKos(Base):
    __tablename__ = "profil_kos"
    
    id = Column(Integer, primary_key=True, index=True)
    nama_kos = Column(String, nullable=False, default="Kostopia")
    alamat_lengkap = Column(Text, nullable=False)
    deskripsi = Column(Text, nullable=True)
    nomor_telepon_pengelola = Column(String, nullable=True)
    informasi_rekening = Column(String, nullable=True) 
    gmaps_url = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)