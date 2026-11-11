<script setup>
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

const ICONS = { success: '✓', error: '⚠', info: 'ℹ' }
const icon = computed(() => ICONS[ui.toast.type] ?? ICONS.info)
</script>

<template>
  <div class="toast-region" role="status" aria-live="polite">
    <Transition name="toast">
      <div v-if="ui.toast.visible" class="toast" :class="`toast--${ui.toast.type}`">
        <div class="toast__body">
          <span class="toast__icon" aria-hidden="true">{{ icon }}</span>
          <span>{{ ui.toast.message }}</span>
        </div>
        <button type="button" class="toast__close" aria-label="Tutup notifikasi" @click="ui.hideToast()">
          ✕
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.toast-region {
  position: fixed;
  top: 16px;
  left: 50%;
  z-index: 60;
  width: calc(min(var(--shell-width), 100vw) - 32px);
  transform: translateX(-50%);
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: var(--ink);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-field);
  box-shadow: var(--shadow-toast);
  font-size: 12px;
  pointer-events: auto;
}

.toast__body {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toast__icon {
  font-weight: 700;
}

.toast--success .toast__icon {
  color: #6ee7b7;
}

.toast--error .toast__icon {
  color: #fda4af;
}

.toast__close {
  padding: 0;
  border: 0;
  background: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.toast__close:hover {
  color: #fff;
}

.toast-enter-active,
.toast-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-120%);
}
</style>
