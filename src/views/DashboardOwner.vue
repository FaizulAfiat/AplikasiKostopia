<template>
  <div class="dashboard-owner">
    <h1>Dashboard Pemilik Kost</h1>
    <p>Selamat datang, {{ user?.name || 'Pemilik' }}! Ini halaman dashboard untuk mengelola kost Anda.</p>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
const user = authStore.user
</script>

<style scoped>
.dashboard-owner {
  padding: 2rem;
  background: linear-gradient(135deg, hsl(210, 30%, 95%), hsl(210, 20%, 90%));
  min-height: 80vh;
}
.dashboard-owner h1 {
  font-family: 'Inter', sans-serif;
  font-size: 2.5rem;
  color: hsl(210, 40%, 20%);
}
</style>
