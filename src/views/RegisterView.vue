<template>
  <AuthLayout show-back :back-to="{ path: '/login', query: { role } }">
    <section class="auth-page register">
      <h1 class="auth-title">DAFTAR</h1>
      <p class="auth-subtitle register-subtitle">Buat Akun {{ roleLabel }}</p>

      <form class="auth-form register-form" id="register-form" @submit.prevent="handleRegister">
        <div class="auth-field">
          <input
            id="input-name"
            type="text"
            v-model="formData.name"
            placeholder="Nama Lengkap"
            required
            autocomplete="name"
          />
        </div>

        <div class="auth-field">
          <input
            id="input-email"
            type="email"
            v-model="formData.email"
            placeholder="Email"
            required
            autocomplete="email"
          />
        </div>

        <div v-if="role === 'pengelola'" class="auth-field">
          <input
            id="input-phone"
            type="tel"
            v-model="formData.phone"
            placeholder="Nomor Telepon"
            required
            autocomplete="tel"
          />
        </div>

        <div class="auth-field">
          <input
            id="input-password"
            :type="showPassword ? 'text' : 'password'"
            v-model="formData.password"
            placeholder="Kata Sandi"
            required
            minlength="8"
            autocomplete="new-password"
          />
          <button
            v-if="formData.password"
            type="button"
            class="auth-eye"
            id="btn-toggle-password"
            tabindex="-1"
            :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
            @click="showPassword = !showPassword"
          >
            <svg v-if="!showPassword" width="16" height="16" fill="none" viewBox="0 0 24 24">
              <path d="M1 12S5 4 12 4s11 8 11 8-4 8-11 8S1 12 1 12Z" stroke="currentColor" stroke-width="2"/>
              <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            </svg>
            <svg v-else width="16" height="16" fill="none" viewBox="0 0 24 24">
              <path d="M17.94 17.94A10 10 0 0 1 12 20C5 20 1 12 1 12a18.5 18.5 0 0 1 4.06-6.94M9.9 4.24A9 9 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.29 4.23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <div class="auth-field" :class="{ 'has-error': passwordMismatch }">
          <input
            id="input-confirm-password"
            :type="showPassword ? 'text' : 'password'"
            v-model="formData.confirmPassword"
            placeholder="Konfirmasi Kata Sandi"
            required
            autocomplete="new-password"
          />
        </div>

        <p v-if="passwordMismatch" class="auth-error">Kata sandi tidak cocok</p>
        <p v-if="errorMsg" class="auth-error">{{ errorMsg }}</p>

        <button
          type="submit"
          class="auth-btn auth-btn--accent btn-register"
          id="btn-register-submit"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">DAFTAR</span>
          <span v-else class="auth-dots"><span></span><span></span><span></span></span>
        </button>

        <p class="auth-terms terms">
          Dengan mendaftar, Anda menyetujui Ketentuan
          <a href="#" id="link-terms">Layanan</a> dan
          <a href="#" id="link-privacy">Kebijakan Privasi kami.</a>
        </p>
      </form>

      <hr class="auth-divider divider" />

      <p class="auth-prompt">
        Sudah Punya Akun?
        <router-link :to="{ path: '/login', query: { role } }" id="link-to-login">Log In</router-link>
      </p>
    </section>
  </AuthLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AuthLayout from '../components/AuthLayout.vue'

const route = useRoute()

const role = computed(() => (route.query.role === 'pengelola' ? 'pengelola' : 'anak-kost'))
const roleLabel = computed(() => (role.value === 'pengelola' ? 'Pengelola Kost' : 'Anak Kost'))

const formData = ref({
  name: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')

const passwordMismatch = computed(() =>
  formData.value.confirmPassword.length > 0 &&
  formData.value.password !== formData.value.confirmPassword
)

async function handleRegister() {
  if (passwordMismatch.value) return
  errorMsg.value = ''
  isLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1400))
    console.log('Register:', { ...formData.value, role: role.value })
  } catch {
    errorMsg.value = 'Pendaftaran gagal. Silakan coba lagi.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-subtitle { margin-top: 22px; }

.register-form {
  margin-top: 10px;
  gap: 14px;
}

.btn-register { margin-top: 14px; }

.terms { margin-top: -6px; }

.divider { margin-top: 18px; }

.auth-prompt { margin-top: 18px; }
</style>
