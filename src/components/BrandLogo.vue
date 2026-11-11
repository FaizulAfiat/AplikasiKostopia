<script setup>
// Logo Kostopia (rumah + huruf K-T) — diambil dari KostopiaLogo.vue milik tim (branch frontend).
defineProps({
  size: { type: Number, default: 32 },
  radius: { type: Number, default: 8 },
  /** light = ubin putih logo maroon · dark = ubin maroon logo putih */
  variant: { type: String, default: 'light' },
})
</script>

<template>
  <span
    class="brand-logo"
    :class="`brand-logo--${variant}`"
    :style="{ width: `${size}px`, height: `${size}px`, borderRadius: `${radius}px` }"
    role="img"
    aria-label="Logo Kostopia"
  >
    <svg viewBox="0 0 100 88" fill="none" aria-hidden="true">
      <rect x="15" y="2" width="10.5" height="24" rx="2.2" fill="currentColor" />
      <path d="M5 30L50 5L95 30" stroke="currentColor" stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round" />
      <rect x="15" y="36" width="11" height="50" rx="2.2" fill="currentColor" />
      <path d="M22 60L39 41" stroke="currentColor" stroke-width="9.5" stroke-linecap="round" />
      <path d="M27 62L44 81" stroke="currentColor" stroke-width="9.5" stroke-linecap="round" />
      <rect x="34" y="36" width="50" height="9" rx="2.2" fill="currentColor" />
      <rect x="65" y="36" width="11" height="50" rx="2.2" fill="currentColor" />
      <rect x="48" y="49" width="6.4" height="6.4" rx="1.2" fill="currentColor" />
      <rect x="56" y="49" width="6.4" height="6.4" rx="1.2" fill="currentColor" />
      <rect x="48" y="57" width="6.4" height="6.4" rx="1.2" fill="currentColor" />
      <rect x="56" y="57" width="6.4" height="6.4" rx="1.2" fill="currentColor" />
    </svg>
  </span>
</template>

<style scoped>
.brand-logo {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 16%;
}

.brand-logo--light {
  background: #fff;
  color: var(--maroon);
  box-shadow: inset 0 0 0 1px var(--border);
}

.brand-logo--dark {
  background: var(--crimson);
  color: #fff;
}

.brand-logo svg {
  width: 100%;
  height: 100%;
}
</style>
