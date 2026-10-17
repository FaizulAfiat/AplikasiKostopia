// src/stores/auth.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { login as loginService } from '../services/auth'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref('')
  const user = ref(null)
  const role = ref('') // 'pengelola' or 'anak-kost'
  const isAuthenticated = computed(() => !!token.value)

  const router = useRouter()

  async function login(payload) {
    const res = await loginService(payload)
    token.value = res.token || ''
    user.value = res.user || null
    role.value = payload.role
    // redirect based on role
    if (role.value === 'pengelola') {
      router.replace({ path: '/dashboard/pemilik' })
    } else {
      router.replace({ path: '/dashboard/penghuni' })
    }
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    role.value = ''
    router.replace({ path: '/' })
  }

  return { token, user, role, isAuthenticated, login, logout }
})
