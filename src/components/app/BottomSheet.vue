<script setup>
import { onBeforeUnmount, watch } from 'vue'

const open = defineModel('open', { type: Boolean, default: false })

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})

// Kunci scroll halaman saat sheet terbuka
watch(open, (value) => {
  document.body.style.overflow = value ? 'hidden' : ''
})

onBeforeUnmount(() => {
  if (open.value) document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="open" class="sheet-backdrop" @click.self="open = false" @keydown.esc="open = false">
        <section class="sheet" role="dialog" aria-modal="true" :aria-label="title">
          <div class="sheet__grip" aria-hidden="true" />
          <header class="sheet__head">
            <div>
              <h2 class="sheet__title">{{ title }}</h2>
              <p v-if="description" class="sheet__desc">{{ description }}</p>
            </div>
            <button type="button" class="sheet__close" aria-label="Tutup" @click="open = false">✕</button>
          </header>
          <div class="sheet__body">
            <slot />
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.sheet-backdrop {
  position: fixed;
  inset: 0;
  z-index: 45;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
}

.sheet {
  width: min(var(--shell-width), 100%);
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  padding: 8px 20px calc(20px + env(safe-area-inset-bottom));
  background: #fff;
  border-radius: 24px 24px 0 0;
  box-shadow: var(--shadow-modal);
}

.sheet__grip {
  width: 40px;
  height: 4px;
  margin: 0 auto 12px;
  border-radius: 999px;
  background: var(--border);
}

.sheet__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.sheet__title {
  font-family: var(--font-editorial);
  font-size: 22px;
  font-weight: 600;
}

.sheet__desc {
  margin-top: 4px;
  font-size: 13px;
  color: var(--slate);
}

.sheet__close {
  padding: 4px 8px;
  border: 0;
  border-radius: 8px;
  background: var(--mist);
  color: var(--slate);
}

.sheet__body {
  overflow-y: auto;
}

.sheet-enter-active,
.sheet-leave-active {
  transition: opacity 0.25s ease;
}

.sheet-enter-active .sheet,
.sheet-leave-active .sheet {
  transition: transform 0.25s ease;
}

.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
}

.sheet-enter-from .sheet,
.sheet-leave-to .sheet {
  transform: translateY(100%);
}
</style>
