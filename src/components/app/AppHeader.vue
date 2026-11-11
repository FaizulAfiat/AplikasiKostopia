<script setup>
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
  title: { type: String, required: true },
  /** Teks kecil di atas judul (mis. "KOS GRIYA SUKABIRUS · B02") */
  eyebrow: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  /** Tampilkan tombol kembali. `true` = riwayat sebelumnya, atau objek route tujuan. */
  back: { type: [Boolean, Object, String], default: false },
  /** Header maroon besar ala desain (untuk layar utama tiap tab). */
  hero: { type: Boolean, default: false },
})

const router = useRouter()

function goBack() {
  if (typeof props.back === 'object' || typeof props.back === 'string') router.push(props.back)
  else if (window.history.state?.back) router.back()
  else router.push('/')
}
</script>

<template>
  <header class="app-header" :class="{ 'app-header--hero': hero }">
    <div class="app-header__bar">
      <button v-if="back" type="button" class="app-header__back" aria-label="Kembali" @click="goBack">
        <AppIcon name="back" :size="20" />
      </button>
      <div class="app-header__titles">
        <p v-if="eyebrow" class="app-header__eyebrow">{{ eyebrow }}</p>
        <h1 class="app-header__title">{{ title }}</h1>
        <p v-if="subtitle" class="app-header__subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="app-header__actions">
        <slot name="actions" />
      </div>
    </div>
    <div v-if="$slots.default" class="app-header__extra">
      <slot />
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 20;
  padding: calc(12px + env(safe-area-inset-top)) 16px 12px;
  background: rgba(250, 248, 247, 0.96);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.app-header--hero {
  position: relative;
  padding-bottom: 20px;
  background: var(--maroon);
  border-bottom: 0;
  color: #fff;
}

.app-header__bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-header__back {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 999px;
  background: var(--mist);
  color: var(--ink);
}

.app-header--hero .app-header__back {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.app-header__titles {
  flex: 1;
  min-width: 0;
}

.app-header__eyebrow {
  margin-bottom: 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--slate);
}

.app-header--hero .app-header__eyebrow {
  color: rgba(255, 255, 255, 0.7);
}

.app-header__title {
  overflow: hidden;
  font-family: var(--font-editorial);
  font-size: 22px;
  font-weight: 600;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-header--hero .app-header__title {
  font-size: 30px;
  font-weight: 400;
  white-space: normal;
}

.app-header__subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: var(--slate);
}

.app-header--hero .app-header__subtitle {
  color: rgba(255, 255, 255, 0.75);
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-header__extra {
  margin-top: 14px;
}
</style>
