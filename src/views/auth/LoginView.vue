<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { MIN_PASSWORD_LENGTH, isValidEmail } from '@/utils/validators'
import AppIcon from '@/components/AppIcon.vue'
import AppInput from '@/components/AppInput.vue'
import BrandLogo from '@/components/BrandLogo.vue'
import PageHeader from '@/components/PageHeader.vue'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

// Panel akun contoh (data seed backend) hanya tampil saat development.
const showTestAccounts = import.meta.env.DEV

const TEST_ACCOUNTS = {
  penghuni: { email: 'fajar@sukabirus.id', password: 'rahasia123', message: 'Akun contoh Penghuni (Fajar - B02) dipilih' },
  pemilik: { email: 'budi@kostopia.id', password: 'pemilik2026', message: 'Akun contoh Pemilik (Pak Budi) dipilih' },
}

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const submitting = ref(false)

function clearErrors() {
  errors.email = ''
  errors.password = ''
}

function pickTestAccount(role) {
  const account = TEST_ACCOUNTS[role]
  form.email = account.email
  form.password = account.password
  clearErrors()
  ui.showToast(account.message)
}

function validate() {
  clearErrors()
  if (!isValidEmail(form.email)) errors.email = 'Email tidak boleh kosong dan harus berformat valid.'
  if (form.password.length < MIN_PASSWORD_LENGTH) errors.password = `Kata sandi minimal ${MIN_PASSWORD_LENGTH} karakter.`
  return !errors.email && !errors.password
}

async function onSubmit() {
  if (submitting.value || !validate()) return

  submitting.value = true
  ui.showLoading('Memverifikasi Akun', 'Menghubungkan ke server Kostopia & membaca token akses...')
  try {
    const user = await auth.login(form.email.trim().toLowerCase(), form.password)
    ui.showToast(`Berhasil masuk sebagai ${user.peran === 'Pemilik' ? 'Pemilik Kos' : 'Penghuni Kos'}`, 'success')
    router.replace({ name: auth.homeRoute })
  } catch (error) {
    if (error.isNetwork) {
      ui.showAlert('Koneksi Terputus', `${error.message} Atur alamat server lewat "Pengaturan Server" di bawah.`, 'network')
    } else {
      ui.showAlert('Gagal Masuk', error.message)
    }
  } finally {
    ui.hideLoading()
    submitting.value = false
  }
}
</script>

<template>
  <main class="screen">
    <div>
      <PageHeader :back-to="{ name: 'splash' }">
        <BrandLogo :size="32" />
        <span class="login__brand">KOSTOPIA</span>
      </PageHeader>

      <div class="login__intro">
        <span class="eyebrow">Selamat Datang Kembali</span>
        <h1 class="title-editorial login__title">Masuk ke Akun</h1>
        <p class="subtitle">Akses tagihan, kamar, perizinan, atau kelola kos Anda secara aman.</p>
      </div>

      <section v-if="showTestAccounts" class="test-accounts" aria-label="Akun contoh">
        <span class="test-accounts__icon"><AppIcon name="info" :size="14" /></span>
        <div>
          <h2 class="test-accounts__title">Akun contoh (data seed)</h2>
          <p class="test-accounts__desc">
            Peran ditentukan otomatis oleh server setelah masuk. Pilih akun contoh untuk mengisi form:
          </p>
          <div class="test-accounts__actions">
            <button type="button" class="test-accounts__btn" @click="pickTestAccount('penghuni')">🧑 Penghuni (Fajar)</button>
            <button type="button" class="test-accounts__btn test-accounts__btn--dark" @click="pickTestAccount('pemilik')">
              🏢 Pemilik (Pak Budi)
            </button>
          </div>
        </div>
      </section>

      <form class="form" novalidate @submit.prevent="onSubmit">
        <AppInput
          v-model="form.email"
          label="Alamat Email"
          type="email"
          icon="mail"
          required
          autocomplete="email"
          inputmode="email"
          placeholder="nama@email.com"
          :error="errors.email"
        />

        <AppInput
          v-model="form.password"
          label="Kata Sandi"
          type="password"
          icon="lock"
          required
          autocomplete="current-password"
          placeholder="Masukkan kata sandi Anda"
          :error="errors.password"
        >
          <template #label-action>
            <RouterLink :to="{ name: 'forgot-password' }" class="link">Lupa Sandi?</RouterLink>
          </template>
        </AppInput>

        <div class="login__options">
          <span class="login__secure">
            <AppIcon name="shield-check" :size="12" class="login__secure-icon" />
            Sesi aman dengan token JWT
          </span>
        </div>

        <button type="submit" class="btn btn-primary login__submit" :disabled="submitting">
          <span>Masuk Sekarang</span>
          <AppIcon name="arrow-right" />
        </button>
      </form>
    </div>

    <footer class="login__footer">
      <p class="login__signup">
        Belum memiliki akun terdaftar?
        <RouterLink :to="{ name: 'register' }" class="link">Daftar Akun Baru</RouterLink>
      </p>
      <p class="login__meta">
        <RouterLink :to="{ name: 'server-settings' }" class="login__meta-link">⚙ Pengaturan Server</RouterLink>
      </p>
    </footer>
  </main>
</template>

<style scoped>
.login__brand {
  font-family: var(--font-brand);
  font-size: 24px;
  letter-spacing: 0.05em;
  color: var(--maroon);
}

.login__intro {
  margin-bottom: 28px;
}

.login__title {
  margin-top: 4px;
  font-size: 30px;
}

.test-accounts {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  padding: 14px;
  background: rgba(251, 225, 209, 0.6);
  border: 1px solid var(--peach);
  border-radius: 16px;
}

.test-accounts__icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  border-radius: 999px;
  background: rgba(112, 0, 32, 0.1);
  color: var(--crimson);
}

.test-accounts__title {
  font-size: 12px;
  font-weight: 600;
  color: var(--sienna);
}

.test-accounts__desc {
  margin-top: 2px;
  font-size: 11px;
  line-height: 1.4;
  color: rgba(93, 42, 26, 0.8);
}

.test-accounts__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.test-accounts__btn {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  color: var(--ink);
}

.test-accounts__btn--dark {
  background: var(--maroon);
  border-color: var(--maroon);
  color: #fff;
}

.login__options {
  display: flex;
  justify-content: flex-end;
}

.login__secure {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(94, 81, 86, 0.7);
}

.login__secure-icon {
  color: var(--success);
}

.login__submit {
  margin-top: 12px;
}

.login__footer {
  padding-top: 24px;
  border-top: 1px solid var(--border);
  text-align: center;
}

.login__signup {
  font-size: 12px;
  color: var(--slate);
}

.login__signup .link {
  margin-left: 4px;
}

.login__meta {
  margin-top: 16px;
  font-size: 11px;
}

.login__meta-link {
  color: var(--slate);
  text-decoration: underline;
  text-underline-offset: 3px;
}
</style>
