<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  backTo: { type: [String, Object], required: true },
  backLabel: { type: String, default: 'Kembali' },
})
</script>

<template>
  <header class="page-header">
    <RouterLink :to="backTo" class="page-header__back" :aria-label="backLabel">
      <AppIcon name="back" :size="20" />
    </RouterLink>
    <div class="page-header__center">
      <slot />
    </div>
    <span class="page-header__spacer" aria-hidden="true" />
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-header__back {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: var(--mist);
  color: var(--ink);
  transition: background-color 0.2s ease;
}

.page-header__back:hover {
  background: #e9e3e2;
}

.page-header__center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header__spacer {
  width: 40px;
}
</style>
