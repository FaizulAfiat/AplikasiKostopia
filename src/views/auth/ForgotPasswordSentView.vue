<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { authApi } from '@/services/endpoints'
import AppIcon from '@/components/AppIcon.vue'

const route = useRoute()
const ui = useUiStore()

const email = computed(() => String(route.query.email ?? ''))
const resending = ref(false)

async function resend() {
  if (resending.value) return
  resending.value = true
  ui.showLoading('Mengirim Ulang', 'Menyiapkan tautan pemulihan baru...')
  try {
    await authApi.forgotPassword(email.value)
    ui.showToast('Tautan pemulihan telah dikirim ulang', 'success')
  } catch {
    ui.showAlert('Koneksi Terputus', 'Gagal mengirim ulang tautan. Coba kembali beberapa saat lagi.', 'network')
  } finally {
    ui.hideLoading()
    resending.value = false
  }
}
</script>

<template>
  <main class="screen sent">
    <div class="sent__content">
      <div class="sent__icon">
        <AppIcon name="mail" :size="40" :stroke-width="2.5" />
      </div>

      <span class="eyebrow sent__eyebrow">Tautan Terkirim</span>
      <h1 class="title-editorial sent__title">Periksa Email Anda</h1>

      <div class="sent__target">
        <p>Instruksi telah dikirim ke:</p>
        <p class="sent__email">{{ email }}</p>
      </div>

      <p class="subtitle sent__desc">
        Silakan buka tautan pada email tersebut dalam waktu 15 menit untuk membuat kata sandi baru.
      </p>

      <p class="sent__resend">
        Tidak menerima email? Periksa folder spam atau
        <button type="button" class="link" :disabled="resending" @click="resend">kirim ulang</button>.
      </p>
    </div>

    <RouterLink :to="{ name: 'login' }" class="btn btn-dark">Kembali ke Halaman Masuk</RouterLink>
  </main>
</template>

<style scoped>
.sent__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  text-align: center;
}

.sent__icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  background: var(--success-bg);
  border: 1px solid var(--success-border);
  border-radius: 999px;
  box-shadow: var(--shadow-subtle);
  color: var(--success);
}

.sent__eyebrow {
  color: #065f46;
}

.sent__title {
  margin-top: 4px;
  font-size: 24px;
}

.sent__target {
  width: 100%;
  margin: 12px 0 16px;
  padding: 14px;
  background: var(--mist);
  border-radius: var(--radius-field);
  font-size: 12px;
  color: var(--slate);
}

.sent__email {
  margin-top: 2px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-weight: 600;
  color: var(--ink);
  word-break: break-all;
}

.sent__desc {
  max-width: 320px;
  margin-top: 0;
}

.sent__resend {
  margin-top: 24px;
  font-size: 11px;
  color: rgba(94, 81, 86, 0.7);
}

.sent__resend .link {
  font-size: 11px;
  font-weight: 600;
}
</style>
