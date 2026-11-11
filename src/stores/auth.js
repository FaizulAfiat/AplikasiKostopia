import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/services/endpoints'
import { getToken, setToken } from '@/services/api'

const USER_KEY = 'kostopia.user'

/** Peran dari backend: "Pemilik" | "Penghuni" → nama route beranda. */
export const HOME_ROUTE_BY_ROLE = {
  Pemilik: 'pemilik-beranda',
  Penghuni: 'penghuni-beranda',
}

function readCachedUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function cacheUser(user) {
  try {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
    else localStorage.removeItem(USER_KEY)
  } catch {
    // abaikan
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getToken())
  const user = ref(token.value ? readCachedUser() : null)

  const isAuthenticated = computed(() => Boolean(token.value && user.value))
  const role = computed(() => user.value?.peran ?? null)
  const isOwner = computed(() => role.value === 'Pemilik')
  const homeRoute = computed(() => HOME_ROUTE_BY_ROLE[role.value] ?? 'login')

  function setUser(next) {
    user.value = next
    cacheUser(next)
  }

  async function login(email, password) {
    const result = await authApi.login(email, password)
    token.value = result.access_token
    setToken(result.access_token)
    setUser(result.user)
    return result.user
  }

  /** Muat ulang data akun dari server (mis. setelah membuka aplikasi). */
  async function refresh() {
    if (!token.value) return null
    const fresh = await authApi.me()
    setUser(fresh)
    return fresh
  }

  async function updateProfile(data) {
    setUser(await authApi.updateMe(data))
    return user.value
  }

  function logout() {
    token.value = null
    setToken(null)
    setUser(null)
  }

  return { token, user, isAuthenticated, role, isOwner, homeRoute, login, refresh, updateProfile, logout, setUser }
})
