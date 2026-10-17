// HTTP client for the FastAPI backend.
//
// Configure in .env (project root):
//   VITE_API_URL=http://localhost:8000
//
// Usage:
//   import { post } from '@/services/api'
//   const data = await post('/auth/login', { email, password })
//   const data = await post('/auth/token', { username, password }, { form: true })

export const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')
const DEFAULT_TIMEOUT_MS = 15000

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'UNKNOWN', fields = {}, data = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.fields = fields // { fieldName: 'pesan error' }
    this.data = data // raw response body
  }
}

/* ─────────── Auth token (Bearer) ─────────── */
let authToken = ''
export function setAuthToken(token) {
  authToken = token || ''
}

/* ─────────── FastAPI error parsing ─────────── */

/**
 * FastAPI returns errors as:
 *   HTTPException      -> { "detail": "Pesan error" }
 *   Validation (422)   -> { "detail": [{ "loc": ["body", "email"], "msg": "...", "type": "..." }] }
 */
function parseFastApiError(data) {
  const detail = data?.detail
  if (typeof detail === 'string') return { message: detail, fields: {} }

  if (Array.isArray(detail)) {
    const fields = {}
    for (const item of detail) {
      const loc = Array.isArray(item?.loc) ? item.loc.filter(p => p !== 'body') : []
      const key = loc.length ? String(loc[loc.length - 1]) : '_'
      if (!fields[key]) fields[key] = item?.msg || 'Nilai tidak valid'
    }
    return { message: detail[0]?.msg || '', fields }
  }

  return { message: data?.message || '', fields: {} }
}

const STATUS_DEFAULTS = {
  400: ['VALIDATION', 'Permintaan tidak valid.'],
  401: ['UNAUTHORIZED', 'Sesi Anda tidak valid. Silakan masuk kembali.'],
  403: ['FORBIDDEN', 'Anda tidak memiliki akses.'],
  404: ['NOT_FOUND', 'Data tidak ditemukan.'],
  409: ['CONFLICT', 'Data sudah ada.'],
  422: ['VALIDATION', 'Data yang dikirim tidak valid. Periksa kembali isian Anda.'],
  429: ['RATE_LIMITED', 'Terlalu banyak percobaan. Tunggu beberapa saat lalu coba lagi.'],
}

function errorFromResponse(status, data) {
  const { message, fields } = parseFastApiError(data)
  if (status >= 500) {
    return new ApiError('Server sedang bermasalah. Silakan coba lagi nanti.', {
      status, code: 'SERVER', data,
    })
  }
  const [code, fallback] = STATUS_DEFAULTS[status] || ['UNKNOWN', 'Terjadi kesalahan. Silakan coba lagi.']
  // 422 messages from Pydantic are in English and technical; prefer the friendly fallback.
  const msg = status === 422 ? fallback : message || fallback
  return new ApiError(msg, { status, code, fields, data })
}

/* ─────────── Core request ─────────── */

/**
 * @param {string} method
 * @param {string} path      e.g. '/auth/login'
 * @param {object} [body]
 * @param {object} [opts]
 * @param {boolean} [opts.form=false]  send as application/x-www-form-urlencoded
 *                                     (needed for FastAPI OAuth2PasswordRequestForm)
 * @param {boolean} [opts.auth=true]   attach Authorization: Bearer <token> if available
 * @param {number}  [opts.timeout]     ms, default 15000
 * @param {object}  [opts.headers]     extra headers
 * @param {AbortSignal} [opts.signal]  external cancel signal
 */
export async function request(method, path, body, opts = {}) {
  const { form = false, auth = true, timeout = DEFAULT_TIMEOUT_MS, headers = {}, signal } = opts

  if (!API_URL) {
    throw new ApiError('VITE_API_URL belum diatur.', { code: 'CONFIG' })
  }

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort('timeout'), timeout)
  signal?.addEventListener('abort', () => controller.abort('cancel'), { once: true })

  const finalHeaders = { Accept: 'application/json', ...headers }
  let payload
  if (body !== undefined) {
    if (form) {
      finalHeaders['Content-Type'] = 'application/x-www-form-urlencoded'
      payload = new URLSearchParams(
        Object.entries(body).filter(([, v]) => v !== undefined && v !== null)
      ).toString()
    } else {
      finalHeaders['Content-Type'] = 'application/json'
      payload = JSON.stringify(body)
    }
  }
  if (auth && authToken) finalHeaders.Authorization = `Bearer ${authToken}`

  let res
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers: finalHeaders,
      body: payload,
      signal: controller.signal,
    })
  } catch (err) {
    if (err?.name === 'AbortError') {
      if (controller.signal.reason === 'cancel') {
        throw new ApiError('Permintaan dibatalkan.', { code: 'CANCELLED' })
      }
      throw new ApiError('Permintaan terlalu lama. Periksa koneksi Anda lalu coba lagi.', { code: 'TIMEOUT' })
    }
    // Also thrown when the server is down or CORS is not configured on FastAPI.
    throw new ApiError('Tidak dapat terhubung ke server. Periksa koneksi internet Anda.', { code: 'NETWORK' })
  } finally {
    clearTimeout(timer)
  }

  const data = res.status === 204 ? null : await res.json().catch(() => null)
  if (!res.ok) throw errorFromResponse(res.status, data)
  return data
}

export const post = (path, body, opts) => request('POST', path, body, opts)
export const get = (path, opts) => request('GET', path, undefined, opts)
