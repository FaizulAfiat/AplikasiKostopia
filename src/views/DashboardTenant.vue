<template>
  <div class="dashboard-tenant">
    <h1>Dashboard Penghuni Kost</h1>
    <p>Selamat datang, {{ user?.name || 'Penghuni' }}! Ini halaman dashboard untuk melihat kamar Anda.</p>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
const user = authStore.user
</script>

<style scoped>
.dashboard-tenant {
  padding: 2rem;
  background: linear-gradient(135deg, hsl(150, 30%, 95%), hsl(150, 20%, 90%));
  min-height: 80vh;
}
.dashboard-tenant h1 {
  font-family: 'Inter', sans-serif;
  font-size: 2.5rem;
  color: hsl(150, 40%, 20%);
}
</style>
