<template>
  <AuthLayout show-back :back-to="{ path: '/login', query: { role } }">
    <section class="auth-page register">
      <h1 class="auth-title reg-title">KOSTOPIA</h1>
      <p class="reg-tagline">{{ tagline }}</p>

      <form class="auth-form register-form" id="register-form" @submit.prevent="handleRegister" novalidate>
        <fieldset class="reg-fields" :disabled="isLoading">
        <div class="reg-group">
          <label for="input-name" class="reg-label">Nama Lengkap</label>
          <div class="reg-field" :class="{ 'has-error': fieldErrors.name }">
            <input
              id="input-name"
              type="text"
              v-model.trim="formData.name"
              placeholder="Budi Utomo"
              required
              autocomplete="name"
              :aria-invalid="!!fieldErrors.name"
              @input="clearError('name')"
            />
          </div>
          <p v-if="fieldErrors.name" class="auth-field-error">{{ fieldErrors.name }}</p>
        </div>

        <div class="reg-group">
          <label for="input-email" class="reg-label">Email</label>
          <div class="reg-field" :class="{ 'has-error': fieldErrors.email }">
            <input
              id="input-email"
              type="email"
              v-model.trim="formData.email"
              placeholder="Budiutomo22@gmail.com"
              required
              autocomplete="email"
              :aria-invalid="!!fieldErrors.email"
              @blur="touchEmail"
              @input="onEmailInput"
            />
          </div>
          <p v-if="fieldErrors.email" class="auth-field-error">{{ fieldErrors.email }}</p>
        </div>

        <div class="reg-group">
          <label for="input-phone" class="reg-label">Nomor Telepon</label>
          <div class="reg-field" :class="{ 'has-error': fieldErrors.phone }">
            <input
              id="input-phone"
              type="tel"
              inputmode="numeric"
              v-model.trim="formData.phone"
              placeholder="081445765777"
              required
              autocomplete="tel"
              :aria-invalid="!!fieldErrors.phone"
              @input="clearError('phone')"
            />
          </div>
          <p v-if="fieldErrors.phone" class="auth-field-error">{{ fieldErrors.phone }}</p>
        </div>

        <div class="reg-group">
          <label for="input-password" class="reg-label">Kata Sandi</label>
          <div class="reg-field" :class="{ 'has-error': fieldErrors.password }">
            <input
              id="input-password"
              :type="showPassword ? 'text' : 'password'"
              v-model="formData.password"
              placeholder="••••••••••"
              required
              minlength="8"
              autocomplete="new-password"
              :aria-invalid="!!fieldErrors.password"
              @input="clearError('password')"
            />
            <button
              type="button"
              class="reg-eye"
              id="btn-toggle-password"
              tabindex="-1"
              :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
              @click="showPassword = !showPassword"
            >
              <svg v-if="!showPassword" width="15" height="15" fill="none" viewBox="0 0 24 24">
                <path d="M1 12S5 4 12 4s11 8 11 8-4 8-11 8S1 12 1 12Z" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
              </svg>
              <svg v-else width="15" height="15" fill="none" viewBox="0 0 24 24">
                <path d="M17.94 17.94A10 10 0 0 1 12 20C5 20 1 12 1 12a18.5 18.5 0 0 1 4.06-6.94M9.9 4.24A9 9 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.29 4.23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <p v-if="fieldErrors.password" class="auth-field-error">{{ fieldErrors.password }}</p>
        </div>
        </fieldset>

        <div v-if="errorMsg" class="auth-alert auth-alert--error" id="register-error" role="alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 7v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <circle cx="12" cy="16.5" r="1.2" fill="currentColor"/>
          </svg>
          <span>{{ errorMsg }}</span>
        </div>
        <div v-if="successMsg" class="auth-alert auth-alert--success" id="register-success" role="status">
          <span>{{ successMsg }}</span>
        </div>

        <button
          type="submit"
          class="auth-btn auth-btn--accent btn-register"
          id="btn-register-submit"
          :disabled="isLoading"
          :aria-busy="isLoading"
        >
          <span v-if="!isLoading" class="btn-register-text">Daftar Sekarang</span>
          <span v-else class="auth-loading">
            <span class="auth-spinner" aria-hidden="true"></span>
            Memproses...
          </span>
        </button>

        <p class="auth-terms terms">
          Dengan melanjutkan, Anda menyetujui Ketentuan<br />
          <a href="#" id="link-terms">Layanan</a> dan
          <a href="#" id="link-privacy">Kebijakan Privasi kami.</a>
        </p>
      </form>

      <hr class="reg-divider" />

      <p class="auth-prompt">
        Sudah punya akun?
        <router-link :to="{ path: '/login', query: { role } }" id="link-to-login">Masuk</router-link>
      </p>
    </section>
  </AuthLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthLayout from '../components/AuthLayout.vue'
import { validateEmail, validatePassword, validatePhone, validateRequired } from '../utils/validation'
import { register, AuthError } from '../services/auth'

const route = useRoute()
const router = useRouter()

const role = computed(() => (route.query.role === 'pengelola' ? 'pengelola' : 'anak-kost'))
const tagline = computed(() =>
  role.value === 'pengelola' ? 'Mulai Kelola Kos Anda' : 'Mulai Cari Kos Impian Anda'
)

const formData = ref({
  name: '',
  email: '',
  phone: '',
  password: '',
})

const fieldErrors = reactive({ name: '', email: '', phone: '', password: '' })
const emailTouched = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

function clearError(field) {
  fieldErrors[field] = ''
  errorMsg.value = ''
}

function touchEmail() {
  if (!formData.value.email) return
  emailTouched.value = true
  fieldErrors.email = validateEmail(formData.value.email)
}

function onEmailInput() {
  errorMsg.value = ''
  fieldErrors.email = emailTouched.value ? validateEmail(formData.value.email) : ''
}

function validateForm() {
  const { name, email, phone, password } = formData.value
  fieldErrors.name = validateRequired(name, 'Nama lengkap')
  fieldErrors.email = validateEmail(email)
  fieldErrors.phone = validatePhone(phone)
  fieldErrors.password = validatePassword(password, { minLength: 8 })
  emailTouched.value = true

  const firstInvalid = ['name', 'email', 'phone', 'password'].find(f => fieldErrors[f])
  if (firstInvalid) document.getElementById(`input-${firstInvalid}`)?.focus()
  return !firstInvalid
}

async function handleRegister() {
  if (isLoading.value) return // prevent double submit
  errorMsg.value = ''
  successMsg.value = ''

  // Validate BEFORE sending anything to the server
  if (!validateForm()) return

  isLoading.value = true
  try {
    await register({ ...formData.value, role: role.value })
    successMsg.value = 'Pendaftaran berhasil! Mengarahkan ke halaman masuk...'
    setTimeout(() => router.push({ path: '/login', query: { role: role.value } }), 1500)
  } catch (err) {
    if (err instanceof AuthError) {
      errorMsg.value = err.message
      if (err.code === 'CONFLICT') fieldErrors.email = 'Email ini sudah terdaftar.'
      for (const f of Object.keys(fieldErrors)) {
        if (err.fields?.[f]) fieldErrors[f] = [].concat(err.fields[f])[0]
      }
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
.reg-title {
  letter-spacing: 3px;
}

.reg-tagline {
  margin-top: 2px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--color-accent);
  text-align: center;
}

.register-form {
  margin-top: 18px;
}

.reg-fields {
  border: none;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reg-fields:disabled { opacity: 0.75; }

.auth-alert { margin-top: 14px; }

/* Label + field */
.reg-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reg-label {
  padding-left: 10px;
  font-size: 10.5px;
  font-weight: 500;
  letter-spacing: 0.6px;
  color: var(--color-text-dark);
}

.reg-field {
  position: relative;
  display: flex;
  align-items: center;
  height: 38px;
  padding: 0 14px;
  background: var(--color-input-bg);
  border-radius: var(--radius-field);
  border: 2px solid transparent;
  transition: var(--transition);
}

/* thin underline inside the field, like the mockup */
.reg-field::after {
  content: '';
  position: absolute;
  left: 12px;
  right: 18px;
  bottom: 8px;
  height: 1px;
  background: rgba(255, 255, 255, 0.55);
  transition: var(--transition);
}

.reg-field:focus-within {
  border-color: var(--color-accent-hover);
  box-shadow: 0 0 0 3px rgba(110, 10, 36, 0.18);
}

.reg-field.has-error { border-color: #d6455c; }

.reg-field:focus-within::after {
  background: #fff;
}

.reg-field input {
  width: 100%;
  height: 100%;
  padding: 0 24px 2px 0;
  background: transparent;
  color: #fff;
  font-size: 11.5px;
  font-weight: 500;
  letter-spacing: 0.6px;
}

.reg-field input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.reg-field input:-webkit-autofill {
  -webkit-text-fill-color: #fff;
  -webkit-box-shadow: 0 0 0 40px var(--color-input-bg) inset;
  caret-color: #fff;
}

.reg-eye {
  position: absolute;
  right: 14px;
  display: flex;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  transition: var(--transition);
}

.reg-eye:hover { color: #fff; }

/* Submit */
.btn-register {
  margin-top: 18px;
  height: 42px;
  letter-spacing: 1px;
}

.btn-register-text {
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-thickness: 1px;
}

.terms { margin-top: 6px; }

.reg-divider {
  width: 100%;
  height: 2px;
  margin-top: 16px;
  border: none;
  background: rgba(17, 17, 17, 0.35);
}

.auth-prompt { margin-top: 10px; }

@media (min-width: 1280px) {
  .reg-label { font-size: 12px; }
  .reg-tagline { font-size: 13.5px; }
  .reg-field { height: 44px; }
  .reg-field input { font-size: 13px; }
  .btn-register { height: 50px; }
}
</style>
