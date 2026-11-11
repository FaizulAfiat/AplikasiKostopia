<script setup>
import { useRoute } from 'vue-router'
import BottomNav from '@/components/app/BottomNav.vue'

const route = useRoute()

const NAV_ITEMS = [
  { tab: 'dasbor', label: 'Dasbor', icon: 'home', to: { name: 'pemilik-beranda' } },
  { tab: 'keuangan', label: 'Keuangan', icon: 'wallet', to: { name: 'pemilik-keuangan' } },
  { tab: 'penghuni', label: 'Penghuni', icon: 'users', to: { name: 'pemilik-penghuni' } },
  { tab: 'layanan', label: 'Layanan', icon: 'chat', to: { name: 'pemilik-layanan' } },
  { tab: 'lainnya', label: 'Lainnya', icon: 'grid', to: { name: 'pemilik-lainnya' } },
]
</script>

<template>
  <div class="role-layout">
    <RouterView />
    <BottomNav v-if="!route.meta.hideNav" :items="NAV_ITEMS" />
  </div>
</template>
