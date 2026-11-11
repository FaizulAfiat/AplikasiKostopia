<script setup>
import AppIcon from '@/components/AppIcon.vue'
import BrandLogo from '@/components/BrandLogo.vue'
</script>

<template>
  <main class="splash">
    <div class="splash__hero">
      <div class="splash__emblem">
        <BrandLogo :size="104" :radius="12" />
      </div>

      <h1 class="splash__brand">KOSTOPIA</h1>
      <div class="splash__divider" aria-hidden="true" />
      <p class="splash__tagline">Manajemen Kos Terpusat</p>

      <p class="splash__quote">Kenyamanan hunian dalam satu sentuhan praktis dan tenang.</p>
    </div>

    <RouterLink :to="{ name: 'login' }" class="btn btn-primary splash__cta">
      <span>Mulai Masuk</span>
      <AppIcon name="arrow-right" :stroke-width="2.5" />
    </RouterLink>
  </main>
</template>

<style scoped>
.splash {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 32px 32px 48px;
  background: var(--maroon);
  color: #fff;
}

.splash__hero {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.splash__emblem {
  margin-bottom: 24px;
  padding: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
}

.splash__emblem:hover {
  transform: scale(1.05);
}

.splash__brand {
  font-family: var(--font-brand);
  font-size: 48px;
  font-weight: 400;
  letter-spacing: 4px;
  line-height: 1;
}

.splash__divider {
  width: 48px;
  height: 2px;
  margin: 10px 0;
  background: var(--crimson);
}

.splash__tagline {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--peach);
}

.splash__quote {
  max-width: 240px;
  margin-top: 32px;
  font-family: var(--font-editorial);
  font-size: 14px;
  font-style: italic;
  color: rgba(255, 255, 255, 0.8);
}

.splash__cta {
  padding: 16px;
  font-size: 14px;
  letter-spacing: 0.02em;
  text-transform: none;
}
</style>
