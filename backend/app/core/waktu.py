"""Fungsi bantu tanggal/waktu yang dipakai banyak service."""
import calendar
from datetime import date, datetime, timezone

NAMA_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
              "Agustus", "September", "Oktober", "November", "Desember"]
NAMA_BULAN_PENDEK = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul",
                     "Agu", "Sep", "Okt", "Nov", "Des"]


def sekarang() -> datetime:
    """Waktu sekarang dalam UTC tanpa tzinfo (format penyimpanan di database)."""
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


def hari_ini() -> date:
    return date.today()


def tambah_bulan(tgl: date, n: int) -> date:
    """Menambah n bulan; tanggal disesuaikan jika bulan tujuan lebih pendek."""
    bulan = tgl.month - 1 + n
    tahun = tgl.year + bulan // 12
    bulan = bulan % 12 + 1
    hari = min(tgl.day, calendar.monthrange(tahun, bulan)[1])
    return date(tahun, bulan, hari)


def periode_dari(tgl: date) -> str:
    return f"{tgl.year:04d}-{tgl.month:02d}"


def periode_label(periode: str) -> str:
    tahun, bulan = periode.split("-")
    return f"{NAMA_BULAN[int(bulan) - 1]} {tahun}"


def label_pendek(periode: str) -> str:
    return NAMA_BULAN_PENDEK[int(periode.split("-")[1]) - 1]


def tanggal_di_periode(periode: str, hari: int) -> date:
    """Tanggal ke-`hari` di bulan `periode`, dibatasi jumlah hari bulan itu."""
    tahun, bulan = (int(x) for x in periode.split("-"))
    return date(tahun, bulan, min(hari, calendar.monthrange(tahun, bulan)[1]))


def awal_akhir_bulan(tgl: date) -> tuple[date, date]:
    return tgl.replace(day=1), tgl.replace(day=calendar.monthrange(tgl.year, tgl.month)[1])


def format_utc(dt: datetime | None) -> str | None:
    """Datetime → ISO 8601 UTC berakhiran Z (mis. 2026-11-08T06:42:00Z)."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.replace(microsecond=0).isoformat() + "Z"
