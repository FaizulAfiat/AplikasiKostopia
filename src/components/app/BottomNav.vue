<script setup>
import { useRoute } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  /** [{ tab: 'beranda', label: 'Beranda', icon: 'home', to: { name: '…' }, badge?: number }] */
  items: { type: Array, required: true },
})

const route = useRoute()
</script>

<template>
  <nav class="bottom-nav" aria-label="Navigasi utama">
    <RouterLink
      v-for="item in items"
      :key="item.tab"
      :to="item.to"
      class="bottom-nav__item"
      :class="{ 'is-active': route.meta.tab === item.tab }"
      :aria-current="route.meta.tab === item.tab ? 'page' : undefined"
    >
      <span class="bottom-nav__icon">
        <AppIcon :name="item.icon" :size="22" :stroke-width="route.meta.tab === item.tab ? 2.2 : 1.7" />
        <span v-if="item.badge" class="bottom-nav__badge">{{ item.badge > 99 ? '99+' : item.badge }}</span>
      </span>
      <span class="bottom-nav__label">{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  z-index: 30;
  width: min(var(--shell-width), 100%);
  display: grid;
  grid-auto-columns: 1fr;
  grid-auto-flow: column;
  padding: 6px 4px calc(6px + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1px solid var(--border);
  box-shadow: 0 -6px 20px -12px rgba(38, 2, 14, 0.2);
  transform: translateX(-50%);
}

.bottom-nav__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 2px;
  border-radius: 12px;
  color: var(--slate);
  font-size: 11px;
  font-weight: 500;
  -webkit-tap-highlight-color: transparent;
}

.bottom-nav__item.is-active {
  color: var(--crimson);
  font-weight: 700;
}

.bottom-nav__icon {
  position: relative;
  display: flex;
  padding: 3px 14px;
  border-radius: 999px;
  transition: background-color 0.2s ease;
}

.bottom-nav__item.is-active .bottom-nav__icon {
  background: rgba(112, 0, 32, 0.08);
}

.bottom-nav__badge {
  position: absolute;
  top: -2px;
  right: 4px;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border-radius: 999px;
  background: var(--crimson);
  color: #fff;
  font-size: 9px;
  font-weight: 700;
}

.bottom-nav__label {
  white-space: nowrap;
}
</style>
