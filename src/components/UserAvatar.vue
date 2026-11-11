<script setup>
import { computed } from 'vue'
import { initials } from '@/utils/format'

const props = defineProps({
  name: { type: String, default: '' },
  size: { type: Number, default: 36 },
  /** crimson | maroon | soft */
  tone: { type: String, default: 'soft' },
})

const letters = computed(() => initials(props.name) || '?')
</script>

<template>
  <span
    class="avatar"
    :class="`avatar--${tone}`"
    :style="{ width: `${size}px`, height: `${size}px`, fontSize: `${Math.round(size * 0.36)}px` }"
    aria-hidden="true"
  >
    {{ letters }}
  </span>
</template>

<style scoped>
.avatar {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.avatar--crimson {
  background: var(--crimson);
  color: #fff;
}

.avatar--maroon {
  background: var(--maroon);
  color: #fff;
}

.avatar--soft {
  background: var(--mist);
  color: var(--ink);
}
</style>
