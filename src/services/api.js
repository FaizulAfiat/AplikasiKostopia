// =========================================================
// Klien HTTP untuk backend FastAPI Kostopia (lihat docs/API.md di branch backend)
// =========================================================
import { apiBaseUrl } from './config'

const TOKEN_KEY = 'kostopia.token'

export class ApiError extends Error {
  constructor(message, status, detail) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }

  get isNetwork() {
    return this.status === 0
  }
}

let unauthorizedHandler = null

/** Dipanggil saat token kedaluwarsa / tidak valid (401). */
export function onUnauthorized(handler) {
  unauthorizedHandler = handler
}

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // abaikan
  }
}

function extractMessage(detail, status) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length) {
    const msg = detail[0]?.msg ?? 'Data tidak valid.'
    return msg.replace(/^Value error, /, '')
  }
  if (status >= 500) return 'Terjadi kesalahan di server. Coba lagi beberapa saat.'
  return 'Permintaan tidak dapat diproses.'
}

function buildUrl(path, query) {
  const url = new URL(`${apiBaseUrl()}${path}`)
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value)
    })
  }
  return url.toString()
}

/**
 * @param {string} method
 * @param {string} path  mis. "/tagihan"
 * @param {{ body?: any, query?: Record<string, any>, form?: FormData, raw?: boolean }} [options]
 */
export async function request(method, path, { body, query, form, raw = false } = {}) {
  const headers = { Accept: 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let payload
  if (form) {
    payload = form
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }

  let response
  try {
    response = await fetch(buildUrl(path, query), { method, headers, body: payload })
  } catch {
    throw new ApiError(
      'Tidak dapat terhubung ke server Kostopia. Periksa koneksi internet atau alamat server.',
      0,
    )
  }

  if (raw && response.ok) return response

  let data = null
  const text = await response.text()
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!response.ok) {
    if (response.status === 401 && token && unauthorizedHandler) unauthorizedHandler()
    const detail = data?.detail ?? data
    throw new ApiError(extractMessage(detail, response.status), response.status, detail)
  }

  return data
}

export const api = {
  get: (path, query) => request('GET', path, { query }),
  post: (path, body) => request('POST', path, { body }),
  put: (path, body) => request('PUT', path, { body }),
  patch: (path, body) => request('PATCH', path, { body }),
  delete: (path) => request('DELETE', path),
  upload: (path, form) => request('POST', path, { form }),
  download: (path, query) => request('GET', path, { query, raw: true }),
}
