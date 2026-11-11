<script setup>
import AppToast from '@/components/feedback/AppToast.vue'
import AlertDialog from '@/components/feedback/AlertDialog.vue'
import ConfirmDialog from '@/components/feedback/ConfirmDialog.vue'
import LoadingOverlay from '@/components/feedback/LoadingOverlay.vue'
</script>

<template>
  <!-- Aplikasi mobile: di HP tampil penuh layar, di laptop tampil seperti ponsel di tengah -->
  <div class="auth-stage">
    <div class="app-shell">
      <RouterView />
    </div>
  </div>

  <AppToast />
  <LoadingOverlay />
  <AlertDialog />
  <ConfirmDialog />
</template>
