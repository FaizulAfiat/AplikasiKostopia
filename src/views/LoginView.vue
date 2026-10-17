<template>
  <AuthLayout show-back back-to="/">
    <section class="auth-page login">
      <h1 class="auth-title">LOG IN</h1>
      <p class="auth-subtitle login-subtitle">Gunakan Akun {{ roleLabel }}</p>

      <form class="auth-form login-form" id="login-form" novalidate @submit.prevent="handleLogin">
        <fieldset class="login-fields" :disabled="isLoading">
        <div class="auth-field" :class="{ 'has-error': fieldErrors.email }">
          <input
            id="input-email"
            type="email"
            v-model.trim="formData.email"
            placeholder="Email"
            required
            autocomplete="email"
            :aria-invalid="!!fieldErrors.email"
            aria-describedby="error-email"
            @blur="touchEmail"
            @input="onInput('email')"
          />
        </div>
        <p v-if="fieldErrors.email" id="error-email" class="auth-field-error">{{ fieldErrors.email }}</p>

        <div class="auth-field field-password" :class="{ 'has-error': fieldErrors.password }">
          <input
            id="input-password"
            :type="showPassword ? 'text' : 'password'"
            v-model="formData.password"
            placeholder="Kata Sandi"
            required
            autocomplete="current-password"
            :aria-invalid="!!fieldErrors.password"
            aria-describedby="error-password"
            @input="onInput('password')"
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
        <p v-if="fieldErrors.password" id="error-password" class="auth-field-error">{{ fieldErrors.password }}</p>
        </fieldset>

        <a href="#" class="auth-link forgot-link" id="link-forgot-password">Lupa Kata Sandi</a>

        <div v-if="errorMsg" class="auth-alert auth-alert--error" id="login-error" role="alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 7v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <circle cx="12" cy="16.5" r="1.2" fill="currentColor"/>
          </svg>
          <span>{{ errorMsg }}</span>
        </div>
        <div v-if="successMsg" class="auth-alert auth-alert--success" id="login-success" role="status">
          <span>{{ successMsg }}</span>
        </div>

        <button
          type="submit"
          class="auth-btn auth-btn--accent btn-login"
          id="btn-login-submit"
          :disabled="isLoading"
          :aria-busy="isLoading"
        >
          <span v-if="!isLoading">LOG IN</span>
          <span v-else class="auth-loading">
            <span class="auth-spinner" aria-hidden="true"></span>
            Memproses...
          </span>
        </button>

        <p class="auth-terms terms">
          Dengan melanjutkan, Anda menyetujui Ketentuan
          <a href="#" id="link-terms">Layanan</a> dan
          <a href="#" id="link-privacy">Kebijakan Privasi kami.</a>
        </p>
      </form>

      <hr class="auth-divider divider" />

      <p class="auth-prompt">
        Belum Punya Akun?
        <router-link :to="{ path: '/register', query: { role: route.query.role } }" id="link-to-register">Daftar</router-link>
      </p>
    </section>
  </AuthLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import AuthLayout from '../components/AuthLayout.vue'
import { validateEmail, validatePassword } from '../utils/validation'
import { AuthError } from '../services/auth'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const formData = ref({ email: '', password: '' })
const fieldErrors = reactive({ email: '', password: '' })
const emailTouched = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const roleLabel = computed(() =>
  route.query.role === 'pengelola' ? 'Pengelola Kost' : 'Anak Kost'
)

function touchEmail() {
  if (!formData.value.email) return
  emailTouched.value = true
  fieldErrors.email = validateEmail(formData.value.email)
}

function onInput(field) {
  errorMsg.value = ''
  // live re-check email only after the user has left the field once
  if (field === 'email' && emailTouched.value) {
    fieldErrors.email = validateEmail(formData.value.email)
  } else {
    fieldErrors[field] = ''
  }
}

function validateForm() {
  fieldErrors.email = validateEmail(formData.value.email)
  fieldErrors.password = validatePassword(formData.value.password)
  emailTouched.value = true

  const firstInvalid = fieldErrors.email ? 'input-email' : fieldErrors.password ? 'input-password' : null
  if (firstInvalid) document.getElementById(firstInvalid)?.focus()
  return !firstInvalid
}

async function handleLogin() {
  if (isLoading.value) return // prevent double submit
  errorMsg.value = ''
  successMsg.value = ''

  // Validate BEFORE sending anything to the server
  if (!validateForm()) return

  isLoading.value = true
  try {
    const res = await authStore.login({
  email: formData.value.email,
  password: formData.value.password,
  role: route.query.role === 'pengelola' ? 'pengelola' : 'anak-kost',
})

    successMsg.value = `Berhasil masuk. Selamat datang, ${res.user?.name || 'Pengguna'}!`
    // TODO: simpan token & arahkan ke dashboard saat halamannya sudah tersedia
  } catch (err) {
    if (err instanceof AuthError) {
      errorMsg.value = err.message
      if (err.fields?.email) fieldErrors.email = [].concat(err.fields.email)[0]
      if (err.fields?.password) fieldErrors.password = [].concat(err.fields.password)[0]
      if (err.code === 'INVALID_CREDENTIALS') formData.value.password = ''
    } else {
      errorMsg.value = 'Terjadi kesalahan tak terduga. Silakan coba lagi.'
      console.error(err)
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-subtitle { margin-top: 26px; }

.login-form { margin-top: 10px; }

.login-fields {
  border: none;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.login-fields:disabled { opacity: 0.75; }

.field-password { margin-top: 20px; }

.forgot-link {
  align-self: center;
  margin-top: 10px;
}

.auth-alert { margin-top: 12px; }

.btn-login { margin-top: 30px; }

.terms { margin-top: 8px; }

.divider { margin-top: 18px; }

.auth-prompt { margin-top: 18px; }
</style>
