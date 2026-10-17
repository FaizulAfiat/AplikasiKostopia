<template>
  <div class="auth-layout">
    <!-- Logo top-left (on top of photo) -->
    <router-link to="/" class="logo" id="logo-home" aria-label="Kostopia - Beranda">
      <KostopiaLogo class="logo-icon" />
      <span class="logo-text">KOSTOPIA</span>
    </router-link>

    <!-- Spacer that reveals the photo on the left -->
    <div class="photo-area" aria-hidden="true"></div>

    <!-- Right cream panel -->
    <main class="panel">
      <!-- Panel background shape: slanted tab (top) + solid filler (rest) -->
      <div class="panel-bg" aria-hidden="true">
        <svg class="panel-tab" viewBox="0 0 654 260" preserveAspectRatio="none">
          <path
            d="M654 0 L460 0 L24 128 Q2 136 10 154 Q14 160 22 164 L112 208 Q140 222 140 250 L140 260 L654 260 Z"
            fill="currentColor"
          />
        </svg>
        <div class="panel-fill"></div>
      </div>

      <!-- Help button -->
      <button class="help-btn" id="help-btn" type="button" aria-label="Bantuan">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.6"/>
          <path d="M9.3 9.2a2.8 2.8 0 0 1 5.4 1c0 1.9-2.7 2.4-2.7 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          <circle cx="12" cy="17.4" r="0.9" fill="currentColor"/>
        </svg>
      </button>

      <!-- Page content -->
      <div class="panel-content">
        <slot />
      </div>

      <!-- Back button (bottom-left of panel) -->
      <button
        v-if="showBack"
        class="btn-back"
        id="btn-back"
        type="button"
        aria-label="Kembali"
        @click="goBack"
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
          <path d="M3 12L10 5.5V9.5H20.5V14.5H10V18.5L3 12Z" fill="currentColor"/>
        </svg>
      </button>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import KostopiaLogo from './KostopiaLogo.vue'

const props = defineProps({
  showBack: { type: Boolean, default: false },
  backTo: { type: [String, Object], default: '/' },
})

const router = useRouter()

function goBack() {
  router.push(props.backTo)
}
</script>

<style scoped>
/* ─── Layout ─── */
.auth-layout {
  --panel-left: 49.8%;
  --tab-width: 63.9%;

  position: relative;
  display: flex;
  min-height: 100vh;
  background:
    url('/kostopia-house.png') left center / cover no-repeat fixed,
    #3a3a3a;
}

.photo-area {
  width: var(--panel-left);
  flex-shrink: 0;
}

/* ─── Logo ─── */
.logo {
  position: absolute;
  top: 26px;
  left: 30px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #fff;
  filter: drop-shadow(0 1px 4px rgba(0, 0, 0, 0.45));
  transition: transform 0.25s ease;
}

.logo:hover { transform: scale(1.05); }

.logo-icon { width: 42px; height: auto; }

.logo-text {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1.4px;
}

/* ─── Cream panel ─── */
.panel {
  position: relative;
  flex: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 90px 40px 100px;
}

/* Background shape. The tab is 127.3% of the panel width
   (63.9% of screen ÷ 50.2% panel) and right-aligned, so its tip
   reaches over the photo while the area above the diagonal stays
   transparent (photo visible) – exactly like the mockup. */
.panel-bg {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  pointer-events: none;
  z-index: 0;
  color: var(--color-bg);
}

.panel-tab {
  display: block;
  width: 127.3%;
  margin-left: -27.3%;
  aspect-ratio: 654 / 260;
  height: auto;
  flex-shrink: 0;
}

.panel-fill {
  flex: 1;
  margin-top: -1px;
  background: var(--color-bg);
  border-bottom-left-radius: 22px;
}

.panel-content {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 272px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ─── Help button ─── */
.help-btn {
  position: absolute;
  top: 22px;
  right: 22px;
  z-index: 5;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--color-text-dark);
  transition: var(--transition);
}

.help-btn:hover {
  background: var(--color-primary-dark);
  color: #fff;
}

/* ─── Back button ─── */
.btn-back {
  position: absolute;
  left: 26px;
  bottom: 26px;
  z-index: 5;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2.5px solid var(--color-primary-dark);
  background: transparent;
  color: var(--color-primary-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.btn-back:hover {
  background: var(--color-primary-dark);
  color: var(--color-bg);
  transform: translateX(-3px);
}

/* ─── Responsive ─── */
@media (min-width: 1280px) {
  .panel-content { max-width: 340px; }
  .logo-icon { width: 50px; }
  .logo-text { font-size: 10.5px; }
}

@media (max-width: 900px) {
  .auth-layout {
    flex-direction: column;
    background-attachment: scroll;
    background-size: 100% 260px;
    background-position: top center;
  }
  .photo-area { width: 100%; height: 230px; }
  .panel {
    min-height: auto;
    flex: 1;
    background: var(--color-bg);
    border-radius: 24px 24px 0 0;
    margin-top: -24px;
    padding: 64px 28px 96px;
  }
  .panel-bg { display: none; }
  .panel-content { max-width: 360px; }
}
</style>
