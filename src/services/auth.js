// Auth service — talks to FastAPI via ./api.js.
//
// Expected FastAPI endpoints (when VITE_API_URL is set):
//   POST /auth/login     body: { email, password, role }
//                        resp: { access_token, token_type, user: { name, email, role } }
//   POST /auth/register  body: { name, email, phone, password, role }
//                        resp: { user: {...} }  (any 2xx is treated as success)
//
// If your login uses FastAPI's OAuth2PasswordRequestForm, set
//   VITE_AUTH_LOGIN_FORM=true
// and the login request is sent as form data: username=<email>&password=<password>.
//
// Without VITE_API_URL a mock backend is used. Mock account: demo@kostopia.id / password123

import { API_URL, ApiError, post } from './api'

// Views import AuthError; it is the same class as ApiError.
export { ApiError as AuthError }

const LOGIN_AS_FORM = import.meta.env.VITE_AUTH_LOGIN_FORM === 'true'

/** Normalize various FastAPI login response shapes into { token, user }. */
function normalizeLogin(data, fallbackRole) {
  const token = data?.access_token || data?.token || ''
  const user = data?.user || { email: data?.email, name: data?.name }
  return { token, user: { ...user, role: user?.role || data?.role || fallbackRole } }
}

/* ─────────── Real backend ─────────── */
async function apiLogin({ email, password, role }) {
  try {
    const data = LOGIN_AS_FORM
      ? await post('/auth/login', { username: email, password }, { form: true, auth: false })
      : await post('/auth/login', { email, password, role }, { auth: false })
    return normalizeLogin(data, role)
  } catch (err) {
    if (err instanceof ApiError) {
      if (err.status === 401) {
        err.code = 'INVALID_CREDENTIALS'
        err.message = 'Email atau kata sandi salah. Silakan coba lagi.'
      } else if (err.status === 404) {
        err.message = 'Akun dengan email ini tidak ditemukan.'
      } else if (err.status === 403 && !err.data?.detail) {
        err.message = 'Akun Anda belum aktif atau diblokir.'
      }
      // OAuth2 form uses "username"; show its error on the email field.
      if (err.fields.username && !err.fields.email) err.fields.email = err.fields.username
    }
    throw err
  }
}

async function apiRegister(payload) {
  try {
    return await post('/auth/register', payload, { auth: false })
  } catch (err) {
    if (err instanceof ApiError && err.status === 409 && !err.data?.detail) {
      err.message = 'Email sudah terdaftar. Silakan masuk.'
    }
    throw err
  }
}

/* ─────────── Mock backend (used when VITE_API_URL is not set) ─────────── */
const delay = ms => new Promise(r => setTimeout(r, ms))
const MOCK_USERS = [{ email: 'demo@kostopia.id', password: 'password123', name: 'Demo User' }]
const offlineError = () =>
  new ApiError('Tidak dapat terhubung ke server. Periksa koneksi internet Anda.', { code: 'NETWORK' })

async function mockLogin({ email, password, role }) {
  await delay(1200)
  if (!navigator.onLine) throw offlineError()
  const user = MOCK_USERS.find(u => u.email.toLowerCase() === email.toLowerCase())
  if (!user || user.password !== password) {
    throw new ApiError('Email atau kata sandi salah. Silakan coba lagi.', {
      status: 401, code: 'INVALID_CREDENTIALS',
    })
  }
  return normalizeLogin({ access_token: 'mock-token', user: { name: user.name, email: user.email } }, role)
}

async function mockRegister({ name, email, password, phone }) {
  await delay(1400)
  if (!navigator.onLine) throw offlineError()
  if (MOCK_USERS.some(u => u.email.toLowerCase() === email.toLowerCase())) {
    throw new ApiError('Email sudah terdaftar. Silakan masuk.', { status: 409, code: 'CONFLICT' })
  }
  MOCK_USERS.push({ name, email, password, phone })
  return { user: { name, email } }
}

/* ─────────── Public API ─────────── */
export function login(payload) {
  return API_URL ? apiLogin(payload) : mockLogin(payload)
}

export function register(payload) {
  return API_URL ? apiRegister(payload) : mockRegister(payload)
}
