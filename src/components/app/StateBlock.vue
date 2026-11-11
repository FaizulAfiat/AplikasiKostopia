<script setup>
import AppIcon from '@/components/AppIcon.vue'

/**
 * Satu komponen untuk 3 keadaan daftar/halaman:
 *   <StateBlock :loading="loading" :error="error" :empty="!items.length" empty-text="…" @retry="reload">
 *     …konten…
 *   </StateBlock>
 */
defineProps({
  loading: { type: Boolean, default: false },
  error: { type: [Object, Error, null], default: null },
  empty: { type: Boolean, default: false },
  emptyTitle: { type: String, default: 'Belum ada data' },
  emptyText: { type: String, default: '' },
  emptyIcon: { type: String, default: 'box' },
  /** Jika data lama sudah ada, jangan tutupi konten saat memuat ulang */
  hasData: { type: Boolean, default: false },
})

defineEmits(['retry'])
</script>

<template>
  <div v-if="loading && !hasData" class="state state--loading" aria-busy="true">
    <div class="state__skeleton" />
    <div class="state__skeleton" />
    <div class="state__skeleton state__skeleton--short" />
  </div>

  <div v-else-if="error && !hasData" class="state" role="alert">
    <span class="state__icon state__icon--error"><AppIcon :name="error.isNetwork ? 'wifi-off' : 'warning'" :size="26" /></span>
    <p class="state__title">{{ error.isNetwork ? 'Tidak dapat terhubung' : 'Gagal memuat data' }}</p>
    <p class="state__text">{{ error.message }}</p>
    <button type="button" class="button button--outline button--sm" @click="$emit('retry')">
      <AppIcon name="refresh" :size="14" /> Coba lagi
    </button>
  </div>

  <div v-else-if="empty" class="state">
    <span class="state__icon"><AppIcon :name="emptyIcon" :size="26" :stroke-width="1.6" /></span>
    <p class="state__title">{{ emptyTitle }}</p>
    <p v-if="emptyText" class="state__text">{{ emptyText }}</p>
    <slot name="empty-action" />
  </div>

  <slot v-else />
</template>

<style scoped>
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 36px 20px;
  text-align: center;
}

.state__icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
  border-radius: 999px;
  background: var(--mist);
  color: var(--slate);
}

.state__icon--error {
  background: var(--status-danger-bg);
  color: var(--crimson);
}

.state__title {
  font-size: 15px;
  font-weight: 600;
}

.state__text {
  max-width: 280px;
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--slate);
}

.state--loading {
  align-items: stretch;
  gap: 12px;
  padding: 4px 0;
}

.state__skeleton {
  height: 84px;
  border-radius: 20px;
  background: linear-gradient(90deg, var(--mist) 25%, #faf6f5 50%, var(--mist) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.3s infinite;
}

.state__skeleton--short {
  width: 60%;
  height: 56px;
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}
</style>
