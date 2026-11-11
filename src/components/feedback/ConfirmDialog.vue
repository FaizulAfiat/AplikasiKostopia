<script setup>
import { nextTick, ref, watch } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const confirmButton = ref(null)

watch(
  () => ui.confirmState.visible,
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
      v-if="ui.confirmState.visible"
      class="overlay confirm-overlay"
      @click.self="ui.resolveConfirm(false)"
      @keydown.esc="ui.resolveConfirm(false)"
    >
      <div class="confirm-card" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-desc">
        <h3 id="confirm-title" class="confirm-card__title">{{ ui.confirmState.title }}</h3>
        <p v-if="ui.confirmState.description" id="confirm-desc" class="confirm-card__desc">
          {{ ui.confirmState.description }}
        </p>
        <div class="confirm-card__actions">
          <button type="button" class="button button--outline" @click="ui.resolveConfirm(false)">Batal</button>
          <button
            ref="confirmButton"
            type="button"
            class="button"
            :class="ui.confirmState.tone === 'danger' ? 'button--primary' : 'button--dark'"
            @click="ui.resolveConfirm(true)"
          >
            {{ ui.confirmState.confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.confirm-overlay {
  background: rgba(0, 0, 0, 0.55);
}

.confirm-card {
  width: 100%;
  max-width: 320px;
  padding: 24px;
  background: #fff;
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-modal);
}

.confirm-card__title {
  font-family: var(--font-editorial);
  font-size: 20px;
  font-weight: 600;
}

.confirm-card__desc {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--slate);
}

.confirm-card__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 20px;
}
</style>
