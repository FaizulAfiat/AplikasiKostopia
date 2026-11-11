<script setup>
defineProps({
  /** success | warning | danger | info | neutral */
  tone: { type: String, default: 'neutral' },
})
</script>

<template>
  <span class="status" :class="`status--${tone}`"><slot /></span>
</template>
