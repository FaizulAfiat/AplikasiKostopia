<script setup>
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useLogout } from '@/composables/useLogout'
import AppHeader from '@/components/app/AppHeader.vue'
import AppIcon from '@/components/AppIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const auth = useAuthStore()
const ui = useUiStore()
const logout = useLogout()

const GROUPS = [
  {
    label: 'Kelola kos',
    items: [
      { label: 'Pengumuman', desc: 'Kirim info ke semua penghuni', icon: 'bell', to: { name: 'pemilik-pengumuman' } },
      { label: 'Aturan Kos', desc: 'Tata tertib & sanksi', icon: 'book', to: { name: 'pemilik-aturan' } },
      { label: 'Penilaian', desc: 'Rating & ulasan penghuni', icon: 'star', to: { name: 'pemilik-penilaian' } },
      { label: 'Kamar & Tarif', desc: 'Daftar kamar dan harga sewa', icon: 'door', to: { name: 'pemilik-kamar' } },
      { label: 'Profil Kos', desc: 'Alamat, rekening, jatuh tempo, parkir', icon: 'home', to: { name: 'pemilik-profil-kos' } },
    ],
  },
  {
    label: 'Akun & aplikasi',
    items: [
      { label: 'Akun Saya', desc: 'Data diri & kata sandi', icon: 'user', to: { name: 'pemilik-akun' } },
      { label: 'Pengaturan Server', desc: 'Alamat server backend', icon: 'settings', to: { name: 'server-settings' } },
    ],
  },
]

async function onLogout() {
  const ok = await ui.confirm('Keluar dari akun?', 'Anda perlu masuk kembali untuk mengelola kos.', { confirmLabel: 'Keluar', tone: 'danger' })
  if (ok) logout()
}
</script>

<template>
  <div>
    <AppHeader title="Lainnya" />

    <div class="app-page">
      <section class="panel profile">
        <UserAvatar :name="auth.user?.nama_lengkap" :size="56" tone="maroon" />
        <div class="profile__body">
          <p class="profile__name">{{ auth.user?.nama_lengkap ?? 'Pemilik' }}</p>
          <p class="profile__role">Pemilik Kos</p>
          <p class="profile__email">{{ auth.user?.email }}</p>
        </div>
      </section>

      <section v-for="group in GROUPS" :key="group.label" class="menu">
        <h2 class="section-label">{{ group.label }}</h2>
        <ul class="menu__list">
          <li v-for="item in group.items" :key="item.label">
            <RouterLink :to="item.to" class="menu__item">
              <span class="menu__icon"><AppIcon :name="item.icon" :size="20" /></span>
              <span class="menu__text">
                <span class="menu__label">{{ item.label }}</span>
                <span class="menu__desc">{{ item.desc }}</span>
              </span>
              <AppIcon name="chevron-right" :size="18" class="menu__chev" />
            </RouterLink>
          </li>
        </ul>
      </section>

      <button type="button" class="button button--danger-outline button--block logout" @click="onLogout">
        <AppIcon name="logout" :size="18" /> Keluar
      </button>
    </div>
  </div>
</template>

<style scoped>
.profile {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
}

.profile__body {
  min-width: 0;
}

.profile__name {
  font-family: var(--font-editorial);
  font-size: 22px;
}

.profile__role {
  margin-top: 2px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--crimson);
}

.profile__email {
  overflow: hidden;
  margin-top: 2px;
  font-size: 13px;
  color: var(--slate);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu__list {
  margin: 0;
  padding: 0;
  overflow: hidden;
  list-style: none;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
}

.menu__list li + li {
  border-top: 1px solid var(--border);
}

.menu__item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
}

.menu__item:active {
  background: var(--fog);
}

.menu__icon {
  width: 40px;
  height: 40px;
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--mist);
  color: var(--maroon);
}

.menu__text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.menu__label {
  font-size: 15px;
  font-weight: 600;
}

.menu__desc {
  font-size: 12px;
  color: var(--slate);
}

.menu__chev {
  color: var(--slate);
}

.logout {
  margin-top: 6px;
  padding: 13px;
}
</style>
