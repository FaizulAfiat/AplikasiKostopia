// =========================================================
// Pembungkus semua endpoint backend — satu fungsi per endpoint.
// Bentuk data persis mengikuti docs/API.md (branch backend).
// =========================================================
import { api } from './api'
import { compressImageToBlob } from '@/utils/image'

// ---------- Auth & akun ----------
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (email, password) => api.post('/auth/login', { email, password }),
  forgotPassword: (email) => api.post('/auth/lupa-sandi', { email }),
  me: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
  changePassword: (sandiLama, sandiBaru) =>
    api.post('/auth/ganti-sandi', { sandi_lama: sandiLama, sandi_baru: sandiBaru }),
}

// ---------- File ----------
const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
export const MAX_UPLOAD_MB = 5

/**
 * Unggah satu file (foto dikompres dulu). Mengembalikan path, mis. "/uploads/abc.jpg".
 * @param {File} file
 */
export async function uploadFile(file) {
  let blob = file
  let name = file.name || 'upload'
  if (IMAGE_TYPES.includes(file.type) || file.type.startsWith('image/')) {
    blob = await compressImageToBlob(file)
    name = name.replace(/\.[^.]+$/, '') + '.jpg'
  } else if (file.type !== 'application/pdf') {
    throw new Error('Format file harus JPG, PNG, WEBP, atau PDF.')
  }
  if (blob.size > MAX_UPLOAD_MB * 1024 * 1024) {
    throw new Error(`Ukuran file maksimal ${MAX_UPLOAD_MB} MB.`)
  }
  const form = new FormData()
  form.append('file', blob, name)
  const { url } = await api.upload('/files', form)
  return url
}

// ---------- Profil kos & kamar ----------
export const profilKosApi = {
  get: () => api.get('/profil'),
  create: (data) => api.post('/profil', data),
  update: (data) => api.put('/profil', data),
}

export const kamarApi = {
  list: () => api.get('/kamar'),
  create: (data) => api.post('/kamar', data),
  update: (id, data) => api.put(`/kamar/${id}`, data),
  remove: (id) => api.delete(`/kamar/${id}`),
}

// ---------- Penghuni & sewa (Pemilik) ----------
export const penghuniApi = {
  list: (query) => api.get('/penghuni', query),
  detail: (userId) => api.get(`/penghuni/${userId}`),
  unassigned: () => api.get('/penghuni/belum-ditempatkan'),
  assignRoom: (userId, data) => api.post(`/penghuni/${userId}/sewa`, data),
  setStatus: (userId, statusSewa) => api.patch(`/penghuni/${userId}/status`, { status_sewa: statusSewa }),
}

// ---------- Kendaraan ----------
export const kendaraanApi = {
  list: () => api.get('/kendaraan'),
  create: (data) => api.post('/kendaraan', data),
  update: (id, data) => api.patch(`/kendaraan/${id}`, data),
  remove: (id) => api.delete(`/kendaraan/${id}`),
  summary: () => api.get('/kendaraan/ringkasan'),
}

// ---------- Tagihan ----------
export const tagihanApi = {
  list: (query) => api.get('/tagihan', query),
  detail: (id) => api.get(`/tagihan/${id}`),
  uploadProof: (id, buktiBayarUrl) => api.post(`/tagihan/${id}/bukti`, { bukti_bayar_url: buktiBayarUrl }),
  verify: (id, disetujui, alasan) => api.post(`/tagihan/${id}/verifikasi`, { disetujui, alasan }),
  statusSummary: (periode) => api.get('/tagihan/ringkasan-status', { periode }),
}

// ---------- Keuangan (Pemilik) ----------
export const keuanganApi = {
  summary: (range) => api.get('/keuangan/ringkasan', range),
  transactions: (range) => api.get('/keuangan/transaksi', range),
  monthlyIncome: (bulan = 6) => api.get('/keuangan/pemasukan-bulanan', { bulan }),
  expenses: () => api.get('/keuangan/pengeluaran'),
  addExpense: (data) => api.post('/keuangan/pengeluaran', data),
  removeExpense: (id) => api.delete(`/keuangan/pengeluaran/${id}`),
  /** @returns {Promise<Blob>} */
  downloadRecap: async (range) => (await api.download('/keuangan/rekap.xlsx', range)).blob(),
}

// ---------- Aspirasi ----------
export const aspirasiApi = {
  list: (query) => api.get('/aspirasi', query),
  create: (data) => api.post('/aspirasi', data),
  update: (id, data) => api.patch(`/aspirasi/${id}`, data),
}

// ---------- Izin ----------
export const izinApi = {
  list: (query) => api.get('/izin', query),
  create: (data) => api.post('/izin', data),
  decide: (id, data) => api.patch(`/izin/${id}`, data),
}

// ---------- Pengumuman ----------
export const pengumumanApi = {
  list: () => api.get('/pengumuman'),
  create: (data) => api.post('/pengumuman', data),
  update: (id, data) => api.patch(`/pengumuman/${id}`, data),
  remove: (id) => api.delete(`/pengumuman/${id}`),
  markRead: (id) => api.post(`/pengumuman/${id}/baca`),
}

// ---------- Aturan ----------
export const aturanApi = {
  list: () => api.get('/aturan'),
  create: (data) => api.post('/aturan', data),
  update: (id, data) => api.put(`/aturan/${id}`, data),
  remove: (id) => api.delete(`/aturan/${id}`),
}

// ---------- Penilaian ----------
export const penilaianApi = {
  list: () => api.get('/penilaian'),
  create: (data) => api.post('/penilaian', data),
  summary: () => api.get('/penilaian/ringkasan'),
}

// ---------- Barang hilang (UC-15) ----------
export const barangHilangApi = {
  list: (query) => api.get('/barang-hilang', query),
  create: (data) => api.post('/barang-hilang', data),
  markDone: (id) => api.post(`/barang-hilang/${id}/selesai`),
}

// ---------- Dasbor ----------
export const dasborApi = {
  pemilik: () => api.get('/dasbor/pemilik'),
  penghuni: () => api.get('/dasbor/penghuni'),
}
