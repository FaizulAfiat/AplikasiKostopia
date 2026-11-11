<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { authApi } from '@/services/endpoints'
import { isValidEmail } from '@/utils/validators'
import AppIcon from '@/components/AppIcon.vue'
import AppInput from '@/components/AppInput.vue'
import BrandLogo from '@/components/BrandLogo.vue'
import PageHeader from '@/components/PageHeader.vue'

const router = useRouter()
const ui = useUiStore()

const email = ref('')
const error = ref('')
const submitting = ref(false)

async function onSubmit() {
  error.value = isValidEmail(email.value) ? '' : 'Masukkan alamat email yang valid.'
  if (error.value || submitting.value) return

  submitting.value = true
  ui.showLoading('Mengirim Tautan', 'Menyiapkan instruksi pemulihan kata sandi...')
  try {
    const target = email.value.trim()
    await authApi.forgotPassword(target)
    router.push({ name: 'forgot-password-sent', query: { email: target } })
  } catch {
    ui.showAlert(
      'Koneksi Terputus',
      'Gagal menghubungi server Kostopia. Pastikan perangkat Anda terhubung ke jaringan internet dan coba kembali.',
      'network',
    )
  } finally {
    ui.hideLoading()
    submitting.value = false
  }
}
</script>

<template>
  <main class="screen">
    <div>
      <PageHeader :back-to="{ name: 'login' }">
        <span class="overline">Pemulihan Akun</span>
      </PageHeader>

      <div class="forgot__emblem">
        <BrandLogo :size="52" :radius="12" />
      </div>

      <h1 class="title-editorial forgot__title">Lupa Kata Sandi?</h1>
      <p class="subtitle forgot__desc">
        Masukkan alamat email yang terdaftar di Kostopia. Kami akan mengirimkan tautan instruksi
        pengaturan ulang kata sandi ke kotak masuk Anda.
      </p>

      <form class="form forgot__form" novalidate @submit.prevent="onSubmit">
        <AppInput
          v-model="email"
          label="Alamat Email Terdaftar"
          type="email"
          icon="mail"
          required
          autocomplete="email"
          placeholder="nama@email.com"
          :error="error"
        />

        <button type="submit" class="btn btn-primary forgot__submit" :disabled="submitting">
          <span>Kirim Tautan Pemulihan</span>
          <AppIcon name="send" />
        </button>
      </form>
    </div>

    <footer class="forgot__footer">
      <RouterLink :to="{ name: 'login' }" class="forgot__back">
        <AppIcon name="arrow-left" />
        <span>Kembali ke Halaman Masuk</span>
      </RouterLink>
    </footer>
  </main>
</template>

<style scoped>
.forgot__emblem {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 8px 0 20px;
  background: rgba(251, 225, 209, 0.4);
  border: 1px solid rgba(251, 225, 209, 0.8);
  border-radius: 16px;
  box-shadow: var(--shadow-subtle);
}

.forgot__title {
  font-size: 24px;
}

.forgot__desc {
  margin-top: 8px;
}

.forgot__form {
  margin-top: 24px;
}

.forgot__submit {
  margin-top: 8px;
}

.forgot__footer {
  text-align: center;
}

.forgot__back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--slate);
}

.forgot__back:hover {
  color: var(--ink);
}
</style>
