<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dasborApi } from '@/services/endpoints'
import { useResource } from '@/composables/useResource'
import { firstName, formatDate, formatRupiah, formatShortDate, statusTone, todayISO } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import AppIcon from '@/components/AppIcon.vue'

const auth = useAuthStore()
const { data, loading, error, reload } = useResource(() => dasborApi.penghuni())

const hasRoom = computed(() => Boolean(data.value?.kamar) && data.value?.status_sewa !== 'Sudah Keluar')

const eyebrow = computed(() => {
  const parts = [data.value?.nama_kos]
  const kamar = data.value?.kamar ?? auth.user?.kamar
  if (kamar && hasRoom.value) parts.push(`Kamar ${kamar}`)
  return parts.filter(Boolean).join(' · ')
})

const bill = computed(() => data.value?.tagihan_aktif ?? null)
const billOpen = computed(() => bill.value && bill.value.status_tagihan !== 'Lunas')
const today = todayISO()
const pastDue = computed(() => billOpen.value && bill.value.jatuh_tempo < today)

const lease = computed(() => {
  const mulai = data.value?.sewa_mulai
  const sampai = data.value?.sewa_sampai
  if (!mulai || !sampai) return null
  const start = new Date(`${mulai}T00:00:00`).getTime()
  const end = new Date(`${sampai}T00:00:00`).getTime()
  const now = Date.now()
  const progress = end > start ? Math.min(1, Math.max(0, (now - start) / (end - start))) : 1
  const daysLeft = Math.ceil((end - now) / 86400000)
  return { sampai, progress: Math.round(progress * 100), daysLeft }
})

const shortcuts = computed(() => [
  { label: 'Lapor aspirasi', note: 'Keluhan & saran', icon: 'chat', to: { name: 'penghuni-aspirasi-baru' } },
  { label: 'Ajukan izin', note: 'Pulang / menginap', icon: 'calendar', to: { name: 'penghuni-izin-baru' } },
  { label: 'Beri penilaian', note: 'Bagikan pengalaman', icon: 'star', to: { name: 'penghuni-info', query: { tab: 'penilaian' } } },
  {
    label: 'Aturan kos',
    note: `${data.value?.jumlah_aturan_aktif ?? 0} aturan aktif`,
    icon: 'book',
    to: { name: 'penghuni-info', query: { tab: 'aturan' } },
  },
])

const announcement = computed(() => data.value?.pengumuman_terbaru ?? null)
const requests = computed(() => data.value?.permintaan ?? [])

function requestRoute(item) {
  return { name: 'penghuni-layanan', query: item.jenis === 'Izin' ? { tab: 'izin' } : {} }
}
</script>

<template>
  <div>
    <AppHeader hero :eyebrow="eyebrow || 'Kostopia'" :title="`Halo, ${firstName(auth.user?.nama_lengkap) || 'Penghuni'}`">
      <template #actions>
        <StatusBadge v-if="data?.status_sewa && hasRoom" :tone="statusTone(data.status_sewa)">{{ data.status_sewa }}</StatusBadge>
        <RouterLink :to="{ name: 'penghuni-profil' }" class="beranda__avatar" aria-label="Profil saya">
          <UserAvatar :name="auth.user?.nama_lengkap" :size="40" tone="crimson" />
        </RouterLink>
      </template>
      <div class="beranda__hero-spacer" aria-hidden="true" />
    </AppHeader>

    <div class="app-page app-page--overlap">
      <StateBlock :loading="loading" :error="error" :has-data="Boolean(data)" @retry="reload">
        <template v-if="data">
          <!-- Belum ditempatkan di kamar -->
          <section v-if="!hasRoom" class="panel beranda__lifted beranda__noroom">
            <span class="beranda__noroom-icon"><AppIcon name="door" :size="26" /></span>
            <h2 class="panel-title">Anda belum menempati kamar</h2>
            <p class="panel-desc">
              Akun Anda sudah terdaftar. Pemilik kos perlu menempatkan Anda di kamar terlebih dahulu —
              setelah itu tagihan dan masa sewa akan tampil di sini.
            </p>
            <button type="button" class="button button--outline button--sm" :disabled="loading" @click="reload">
              <AppIcon name="refresh" :size="14" /> {{ loading ? 'Memeriksa…' : 'Periksa lagi' }}
            </button>
          </section>

          <template v-else>
            <!-- Tagihan -->
            <section class="panel beranda__lifted" aria-labelledby="bill-title">
              <template v-if="bill">
                <div class="beranda__bill-head">
                  <p id="bill-title" class="section-label">Tagihan {{ bill.periode_label }}</p>
                  <StatusBadge :tone="statusTone(bill.status_tagihan)">{{ bill.status_tagihan }}</StatusBadge>
                </div>
                <p class="beranda__amount">{{ formatRupiah(bill.jumlah_tagihan) }}</p>
                <p v-if="billOpen" class="beranda__due">
                  Jatuh tempo {{ formatShortDate(bill.jatuh_tempo) }} ·
                  <span :class="{ 'is-urgent': pastDue }">masa tenggang berakhir {{ formatDate(bill.batas_tenggang) }}</span>
                </p>
                <p v-else class="beranda__due">
                  Lunas{{ bill.diverifikasi_at ? ` · disetujui ${formatDate(bill.diverifikasi_at)}` : '' }}. Terima kasih!
                </p>
                <div class="beranda__bill-actions">
                  <RouterLink :to="{ name: 'penghuni-tagihan-detail', params: { id: bill.id } }" class="button button--outline">
                    Lihat rincian
                  </RouterLink>
                  <RouterLink
                    v-if="['Belum Bayar', 'Ditolak'].includes(bill.status_tagihan)"
                    :to="{ name: 'penghuni-tagihan-detail', params: { id: bill.id } }"
                    class="button button--primary"
                  >
                    Bayar &amp; Unggah Bukti
                  </RouterLink>
                </div>
              </template>
              <div v-else class="beranda__nobill">
                <p id="bill-title" class="section-label">Tagihan</p>
                <p class="beranda__nobill-text">Tidak ada tagihan aktif 🎉</p>
              </div>
            </section>

            <!-- Masa sewa -->
            <section v-if="lease" class="panel" aria-label="Masa sewa">
              <p class="section-label">Masa sewa</p>
              <p class="beranda__lease">s/d {{ formatDate(lease.sampai) }}</p>
              <div class="beranda__progress" role="progressbar" :aria-valuenow="lease.progress" aria-valuemin="0" aria-valuemax="100">
                <span :style="{ width: `${lease.progress}%` }" />
              </div>
              <p class="beranda__lease-note">
                <template v-if="lease.daysLeft > 0">Sisa {{ lease.daysLeft }} hari · </template>
                <template v-else>Masa sewa sudah berakhir · </template>
                Diperpanjang otomatis 1 bulan setelah pembayaran disetujui.
              </p>
            </section>
          </template>

          <!-- Pintasan -->
          <nav class="beranda__shortcuts" aria-label="Pintasan">
            <RouterLink v-for="item in shortcuts" :key="item.label" :to="item.to" class="beranda__tile">
              <span class="beranda__tile-icon"><AppIcon :name="item.icon" :size="20" /></span>
              <span class="beranda__tile-label">{{ item.label }}</span>
              <span class="beranda__tile-note">{{ item.note }}</span>
            </RouterLink>
          </nav>

          <!-- Pengumuman terbaru (satu-satunya kartu peach) -->
          <RouterLink v-if="announcement" :to="{ name: 'penghuni-info' }" class="beranda__announce">
            <div class="beranda__announce-head">
              <p class="beranda__announce-label">Pengumuman terbaru</p>
              <time :datetime="announcement.created_at">{{ formatDate(announcement.created_at) }}</time>
            </div>
            <h2 class="beranda__announce-title">{{ announcement.judul }}</h2>
            <p class="beranda__announce-body">{{ announcement.isi_pengumuman }}</p>
            <span class="beranda__announce-link">Semua pengumuman →</span>
          </RouterLink>

          <!-- Permintaan saya -->
          <section aria-labelledby="req-title">
            <div class="section-title">
              <h2 id="req-title" class="section-label">Permintaan saya</h2>
              <RouterLink :to="{ name: 'penghuni-layanan' }" class="text-link">Riwayat →</RouterLink>
            </div>
            <p v-if="!requests.length" class="beranda__empty">Belum ada aspirasi atau izin yang Anda ajukan.</p>
            <ul v-else class="beranda__requests">
              <li v-for="item in requests" :key="`${item.jenis}-${item.id}`">
                <RouterLink :to="requestRoute(item)" class="list-card beranda__request">
                  <div class="list-card__head">
                    <span class="beranda__chip">{{ item.jenis }}</span>
                    <StatusBadge :tone="statusTone(item.status)">{{ item.status }}</StatusBadge>
                  </div>
                  <p class="list-card__title">{{ item.judul }}</p>
                  <p class="list-card__meta">{{ formatDate(item.created_at) }}</p>
                </RouterLink>
              </li>
            </ul>
          </section>
        </template>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.beranda__hero-spacer {
  height: 28px;
}

.beranda__avatar {
  display: inline-flex;
  border-radius: 999px;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.35);
}

.beranda__lifted {
  box-shadow: 0 14px 30px -14px rgba(38, 2, 14, 0.35);
}

.beranda__bill-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.beranda__amount {
  margin-top: 10px;
  font-family: var(--font-editorial);
  font-size: 38px;
  font-weight: 400;
  line-height: 1.1;
}

.beranda__due {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--slate);
}

.beranda__due .is-urgent {
  font-weight: 600;
  color: var(--crimson);
}

.beranda__bill-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.beranda__bill-actions .button {
  padding: 12px 14px;
  white-space: normal;
  text-align: center;
}

.beranda__nobill-text {
  margin-top: 8px;
  font-family: var(--font-editorial);
  font-size: 22px;
}

.beranda__noroom {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.beranda__noroom .panel-desc {
  margin-bottom: 8px;
  line-height: 1.5;
}

.beranda__noroom-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: var(--mist);
  color: var(--crimson);
}

.beranda__lease {
  margin-top: 8px;
  font-family: var(--font-editorial);
  font-size: 26px;
}

.beranda__progress {
  height: 8px;
  margin-top: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--mist);
}

.beranda__progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--crimson);
}

.beranda__lease-note {
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--slate);
}

.beranda__shortcuts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.beranda__tile {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-height: 112px;
  padding: 16px;
  background: var(--mist);
  border-radius: 20px;
}

.beranda__tile:active {
  background: #ebe5e4;
}

.beranda__tile-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: auto;
  border-radius: 12px;
  background: #fff;
  color: var(--crimson);
}

.beranda__tile-label {
  margin-top: 12px;
  font-size: 14px;
  font-weight: 600;
}

.beranda__tile-note {
  font-size: 12px;
  color: var(--slate);
}

.beranda__announce {
  display: block;
  padding: 22px;
  background: var(--peach);
  border: 1px solid var(--peach-border);
  border-radius: var(--radius-card);
  color: var(--sienna);
}

.beranda__announce-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
}

.beranda__announce-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.beranda__announce-title {
  margin-top: 10px;
  font-family: var(--font-editorial);
  font-size: 22px;
  font-weight: 400;
  line-height: 1.25;
  color: var(--ink);
}

.beranda__announce-body {
  display: -webkit-box;
  margin-top: 6px;
  overflow: hidden;
  font-size: 14px;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.beranda__announce-link {
  display: inline-block;
  margin-top: 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--crimson);
}

.beranda__requests {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.beranda__chip {
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--mist);
  font-size: 11px;
  font-weight: 600;
  color: var(--slate);
}

.beranda__empty {
  margin-top: 10px;
  padding: 18px;
  border: 1px dashed var(--border);
  border-radius: 20px;
  font-size: 13px;
  color: var(--slate);
  text-align: center;
}
</style>
