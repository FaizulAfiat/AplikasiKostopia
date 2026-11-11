import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

export function useLogout() {
  const router = useRouter()
  const auth = useAuthStore()
  const ui = useUiStore()

  return function logout() {
    auth.logout()
    ui.showToast('Anda telah keluar dari akun')
    router.replace({ name: 'login' })
  }
}
