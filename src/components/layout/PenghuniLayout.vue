<script setup>
import { useRoute } from 'vue-router'
import BottomNav from '@/components/app/BottomNav.vue'

const route = useRoute()

const NAV_ITEMS = [
  { tab: 'beranda', label: 'Beranda', icon: 'home', to: { name: 'penghuni-beranda' } },
  { tab: 'tagihan', label: 'Tagihan', icon: 'receipt', to: { name: 'penghuni-tagihan' } },
  { tab: 'layanan', label: 'Layanan', icon: 'chat', to: { name: 'penghuni-layanan' } },
  { tab: 'barang', label: 'Barang', icon: 'box', to: { name: 'penghuni-barang-hilang' } },
  { tab: 'info', label: 'Info Kos', icon: 'book', to: { name: 'penghuni-info' } },
]
</script>

<template>
  <div class="role-layout">
    <RouterView />
    <BottomNav v-if="!route.meta.hideNav" :items="NAV_ITEMS" />
  </div>
</template>
