<script setup>
const model = defineModel({ type: String, required: true })

defineProps({
  /** [{ value: 'aktif', label: 'Aktif', count?: 4 }] */
  options: { type: Array, required: true },
  /** Gaya untuk di atas latar maroon */
  dark: { type: Boolean, default: false },
  label: { type: String, default: 'Pilihan tampilan' },
})
</script>

<template>
  <div class="segmented" :class="{ 'segmented--dark': dark }" role="tablist" :aria-label="label">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      role="tab"
      class="segmented__item"
      :class="{ 'is-active': model === option.value }"
      :aria-selected="model === option.value"
      @click="model = option.value"
    >
      {{ option.label }}
      <span v-if="option.count !== undefined && option.count !== null" class="segmented__count">{{ option.count }}</span>
    </button>
  </div>
</template>

<style scoped>
.segmented {
  display: flex;
  gap: 4px;
  padding: 4px;
  overflow-x: auto;
  background: var(--mist);
  border-radius: 14px;
  scrollbar-width: none;
}

.segmented__item {
  flex: 1 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 12px;
  border: 0;
  border-radius: 11px;
  background: transparent;
  font-size: 13px;
  font-weight: 600;
  color: var(--slate);
  white-space: nowrap;
}

.segmented__item.is-active {
  background: #fff;
  color: var(--ink);
  box-shadow: 0 1px 4px rgba(38, 2, 14, 0.12);
}

.segmented__count {
  min-width: 18px;
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(94, 81, 86, 0.15);
  font-size: 11px;
}

.segmented__item.is-active .segmented__count {
  background: var(--crimson);
  color: #fff;
}

.segmented--dark {
  background: rgba(255, 255, 255, 0.1);
}

.segmented--dark .segmented__item {
  color: rgba(255, 255, 255, 0.8);
}

.segmented--dark .segmented__item.is-active {
  background: #fff;
  color: var(--ink);
}
</style>
