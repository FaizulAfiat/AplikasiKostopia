<script setup>
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
</script>

<template>
  <Transition name="fade">
    <div v-if="ui.loading.visible" class="overlay loading-overlay" role="alert" aria-busy="true">
      <div class="loading-card">
        <div class="spinner" aria-hidden="true" />
        <h4 class="loading-card__title">{{ ui.loading.title }}</h4>
        <p v-if="ui.loading.description" class="loading-card__desc">{{ ui.loading.description }}</p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.loading-overlay {
  background: rgba(38, 2, 14, 0.7);
}

.loading-card {
  width: 100%;
  max-width: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background: #fff;
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-modal);
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  border: 4px solid var(--mist);
  border-top-color: var(--crimson);
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

.loading-card__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
}

.loading-card__desc {
  margin-top: 4px;
  font-size: 11px;
  line-height: 1.4;
  color: var(--slate);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation-duration: 2s;
  }
}
</style>
