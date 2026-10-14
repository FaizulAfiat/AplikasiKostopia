<template>
  <AuthLayout>
    <section class="auth-page welcome">
      <h1 class="auth-title">SELAMAT DATANG</h1>
      <p class="auth-subtitle welcome-subtitle">Silakan pilih peran akun Anda</p>

      <div class="role-buttons">
        <button
          id="btn-anak-kost"
          type="button"
          class="auth-btn auth-btn--dark"
          @click="selectRole('anak-kost')"
        >
          Anak Kost
        </button>
        <button
          id="btn-pengelola"
          type="button"
          class="auth-btn auth-btn--dark"
          @click="selectRole('pengelola')"
        >
          Pengelola Kost
        </button>
      </div>
    </section>
  </AuthLayout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AuthLayout from '../components/AuthLayout.vue'

const router = useRouter()

function selectRole(role) {
  router.push({ path: '/login', query: { role } })
}
</script>

<style scoped>
.welcome-subtitle { margin-top: 22px; }

.role-buttons {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 14px;
}
</style>
