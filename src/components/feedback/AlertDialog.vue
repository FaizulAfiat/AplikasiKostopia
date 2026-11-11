<script setup>
import { nextTick, ref, watch } from 'vue'
import { useUiStore } from '@/stores/ui'
import AppIcon from '@/components/AppIcon.vue'

const ui = useUiStore()
const confirmButton = ref(null)

watch(
  () => ui.alert.visible,
  async (visible) => {
    if (visible) {
      await nextTick()
      confirmButton.value?.focus()
    }
  },
)
</script>

<template>
  <Transition name="fade">
    <div
      v-if="ui.alert.visible"
      class="overlay alert-overlay"
      @click.self="ui.closeAlert()"
      @keydown.esc="ui.closeAlert()"
    >
      <div
        class="alert-card"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="alert-title"
        aria-describedby="alert-desc"
      >
        <div class="alert-card__icon" :class="`alert-card__icon--${ui.alert.variant}`">
          <AppIcon :name="ui.alert.variant === 'network' ? 'wifi-off' : 'warning'" :size="24" />
        </div>
        <h3 id="alert-title" class="title-editorial alert-card__title">{{ ui.alert.title }}</h3>
        <p id="alert-desc" class="alert-card__desc">{{ ui.alert.description }}</p>
        <button ref="confirmButton" type="button" class="btn btn-primary alert-card__btn" @click="ui.closeAlert()">
          Coba Lagi
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.alert-overlay {
  background: rgba(0, 0, 0, 0.6);
}

.alert-card {
  width: 100%;
  max-width: 310px;
  padding: 24px;
  background: #fff;
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-modal);
  text-align: center;
}

.alert-card__icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  border-radius: 999px;
}

.alert-card__icon--error {
  background: var(--danger-bg);
  color: var(--crimson);
}

.alert-card__icon--network {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.alert-card__title {
  font-size: 18px;
}

.alert-card__desc {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--slate);
}

.alert-card__btn {
  margin-top: 20px;
  padding: 10px 16px;
  text-transform: none;
  letter-spacing: 0;
}
</style>
