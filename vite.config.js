import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
// Catatan: vite-plugin-vue-devtools sengaja tidak dipakai — tombol melayangnya
// menutupi tombol aksi & menu bawah di tampilan aplikasi HP.
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    // Bisa diakses dari HP di jaringan Wi-Fi yang sama
    host: true,
  },
})
