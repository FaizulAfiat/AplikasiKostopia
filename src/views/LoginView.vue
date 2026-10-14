<template>
  <AuthLayout show-back back-to="/">
    <section class="auth-page login">
      <h1 class="auth-title">LOG IN</h1>
      <p class="auth-subtitle login-subtitle">Gunakan Akun {{ roleLabel }}</p>

      <form class="auth-form login-form" id="login-form" @submit.prevent="handleLogin">
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

        <div class="auth-field field-password">
          <input
            id="input-password"
            :type="showPassword ? 'text' : 'password'"
            v-model="formData.password"
            placeholder="Kata Sandi"
            required
            autocomplete="current-password"
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

        <a href="#" class="auth-link forgot-link" id="link-forgot-password">Lupa Kata Sandi</a>

        <p v-if="errorMsg" class="auth-error">{{ errorMsg }}</p>

        <button
          type="submit"
          class="auth-btn auth-btn--accent btn-login"
          id="btn-login-submit"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">LOG IN</span>
          <span v-else class="auth-dots"><span></span><span></span><span></span></span>
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
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AuthLayout from '../components/AuthLayout.vue'

const route = useRoute()

const formData = ref({ email: '', password: '' })
const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')

const roleLabel = computed(() =>
  route.query.role === 'pengelola' ? 'Pengelola Kost' : 'Anak Kost'
)

async function handleLogin() {
  errorMsg.value = ''
  isLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1200))
    console.log('Login:', formData.value, 'Role:', route.query.role)
  } catch {
    errorMsg.value = 'Email atau kata sandi salah. Silakan coba lagi.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-subtitle { margin-top: 26px; }

.login-form { margin-top: 10px; }

.field-password { margin-top: 20px; }

.forgot-link {
  align-self: center;
  margin-top: 10px;
}

.auth-error { margin-top: 12px; }

.btn-login { margin-top: 30px; }

.terms { margin-top: 8px; }

.divider { margin-top: 18px; }

.auth-prompt { margin-top: 18px; }
</style>
