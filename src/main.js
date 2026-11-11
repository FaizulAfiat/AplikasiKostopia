import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Capacitor } from '@capacitor/core'
import { App as CapacitorApp } from '@capacitor/app'
import { StatusBar, Style } from '@capacitor/status-bar'

import App from './App.vue'
import router from './router'
import { onUnauthorized } from './services/api'
import { useAuthStore } from './stores/auth'
import { useUiStore } from './stores/ui'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const auth = useAuthStore(pinia)
const ui = useUiStore(pinia)

// Token kedaluwarsa / tidak valid → keluar & kembali ke halaman masuk.
onUnauthorized(() => {
  if (!auth.isAuthenticated) return
  auth.logout()
  ui.showAlert('Sesi Berakhir', 'Sesi Anda sudah berakhir. Silakan masuk kembali.')
  router.replace({ name: 'login' })
})

// Segarkan data akun dari server saat aplikasi dibuka (diam-diam; gagal jaringan diabaikan).
if (auth.isAuthenticated) auth.refresh().catch(() => {})

// ---------- Integrasi Android (Capacitor) ----------
if (Capacitor.isNativePlatform()) {
  StatusBar.setStyle({ style: Style.Dark }).catch(() => {})
  StatusBar.setBackgroundColor({ color: '#26020E' }).catch(() => {})

  // Tombol kembali Android: tutup dialog → kembali → keluar aplikasi di layar utama.
  CapacitorApp.addListener('backButton', ({ canGoBack }) => {
    if (ui.confirmState.visible) return ui.resolveConfirm(false)
    if (ui.alert.visible) return ui.closeAlert()
    const isRoot = ['splash', 'login', 'pemilik-beranda', 'penghuni-beranda'].includes(router.currentRoute.value.name)
    if (canGoBack && !isRoot) router.back()
    else CapacitorApp.exitApp()
  })
}

app.mount('#app')
