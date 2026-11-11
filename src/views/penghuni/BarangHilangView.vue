<script setup>
import AppHeader from '@/components/app/AppHeader.vue'
import LostFoundPanel from '@/components/lostfound/LostFoundPanel.vue'
</script>

<template>
  <div>
    <AppHeader hero title="Barang Hilang" subtitle="Kehilangan atau menemukan barang di kos? Laporkan di sini." />
    <div class="app-page">
      <LostFoundPanel :create-route="{ name: 'penghuni-barang-hilang-baru' }" />
    </div>
  </div>
</template>
