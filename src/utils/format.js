const shortDateFormat = new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short' })
const longDateFormat = new Intl.DateTimeFormat('id-ID', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

/** "2026-11-04" → "4 Nov" */
export function formatShortDate(value) {
  return shortDateFormat.format(new Date(value)).replace('.', '')
}

/** → "Minggu, 8 November 2026" */
export function formatLongDate(value) {
  return longDateFormat.format(new Date(value))
}

/** 1000000 → "Rp 1.000.000" */
export function formatRupiah(amount) {
  return `Rp ${Number(amount).toLocaleString('id-ID')}`
}

/** 14.2 → "14,2" */
export function formatDecimal(value, digits = 1) {
  return Number(value).toLocaleString('id-ID', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}

/** "Budi Utomo" → "BU" */
export function initials(name = '') {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join('')
}

export function firstName(name = '') {
  return name.split(/\s+/)[0] ?? ''
}

/** Salam sesuai jam: pagi / siang / sore / malam */
export function timeGreeting(date = new Date()) {
  const hour = date.getHours()
  if (hour < 11) return 'Selamat pagi'
  if (hour < 15) return 'Selamat siang'
  if (hour < 18) return 'Selamat sore'
  return 'Selamat malam'
}

const dateFormat = new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
const dateTimeFormat = new Intl.DateTimeFormat('id-ID', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})
const monthYearFormat = new Intl.DateTimeFormat('id-ID', { month: 'long', year: 'numeric' })

/** "2026-11-10" → "10 Nov 2026" (string date YYYY-MM-DD dibaca sebagai tanggal lokal) */
export function formatDate(value) {
  if (!value) return '—'
  const date = /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T00:00:00`) : new Date(value)
  return dateFormat.format(date).replace(/\./g, '')
}

/** → "8 Nov 2026, 13.42" */
export function formatDateTime(value) {
  if (!value) return '—'
  return dateTimeFormat.format(new Date(value))
}

/** "2026-11" → "November 2026" */
export function formatMonth(periode) {
  if (!periode) return '—'
  return monthYearFormat.format(new Date(`${periode}-01T00:00:00`))
}

/** → "35 menit lalu", "kemarin", "3 hari lalu", atau tanggal */
export function formatRelative(value) {
  if (!value) return ''
  const diffMs = Date.now() - new Date(value).getTime()
  const minutes = Math.round(diffMs / 60000)
  if (minutes < 1) return 'baru saja'
  if (minutes < 60) return `${minutes} menit lalu`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours} jam lalu`
  const days = Math.round(hours / 24)
  if (days === 1) return 'kemarin'
  if (days < 7) return `${days} hari lalu`
  if (days < 30) return `${Math.round(days / 7)} minggu lalu`
  return formatDate(value)
}

/** 15400000 → "Rp 15,4 jt" */
export function formatRupiahShort(amount) {
  const value = Number(amount) || 0
  if (Math.abs(value) >= 1_000_000) return `Rp ${formatDecimal(value / 1_000_000)} jt`
  if (Math.abs(value) >= 1_000) return `Rp ${Math.round(value / 1_000)} rb`
  return formatRupiah(value)
}

/** Hari ini sebagai "YYYY-MM-DD" (zona waktu lokal) */
export function todayISO(offsetDays = 0) {
  const d = new Date()
  d.setDate(d.getDate() + offsetDays)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

/** Warna badge untuk setiap status dari backend */
const STATUS_TONES = {
  Lunas: 'success',
  Disetujui: 'success',
  Selesai: 'success',
  Aktif: 'success',
  Temuan: 'success',
  'Menunggu Verifikasi': 'warning',
  Menunggu: 'warning',
  Pending: 'warning',
  'Masa Tenggang': 'warning',
  'Belum Bayar': 'danger',
  Ditolak: 'danger',
  Hilang: 'danger',
  'Sedang Diproses': 'info',
  'Sudah Keluar': 'neutral',
}

export function statusTone(status) {
  return STATUS_TONES[status] ?? 'neutral'
}
