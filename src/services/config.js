import { Capacitor } from '@capacitor/core'

const STORAGE_KEY = 'kostopia.serverUrl'

/**
 * Alamat server backend (tanpa /api/v1).
 * - Browser (npm run dev): http://localhost:8000
 * - Emulator Android: http://10.0.2.2:8000 (alias localhost komputer)
 * - HP sungguhan: http://<IP-laptop>:8000 — atur lewat layar "Pengaturan Server".
 */
export function defaultServerUrl() {
  if (import.meta.env.VITE_SERVER_URL) return import.meta.env.VITE_SERVER_URL
  return Capacitor.getPlatform() === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000'
}

export function getServerUrl() {
  try {
    return localStorage.getItem(STORAGE_KEY) || defaultServerUrl()
  } catch {
    return defaultServerUrl()
  }
}

export function setServerUrl(url) {
  const clean = url.trim().replace(/\/+$/, '')
  try {
    if (clean) localStorage.setItem(STORAGE_KEY, clean)
    else localStorage.removeItem(STORAGE_KEY)
  } catch {
    // penyimpanan tidak tersedia
  }
}

export const apiBaseUrl = () => `${getServerUrl()}/api/v1`

/** Ubah path file dari backend (mis. "/uploads/x.jpg") jadi URL lengkap. */
export function fileUrl(path) {
  if (!path) return null
  if (/^(https?:|data:|blob:)/.test(path)) return path
  return `${getServerUrl()}${path.startsWith('/') ? '' : '/'}${path}`
}
