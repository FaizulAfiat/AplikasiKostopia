<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { dasborApi, penghuniApi } from '@/services/endpoints'
import { useResource } from '@/composables/useResource'
import {
  firstName,
  formatDecimal,
  formatLongDate,
  formatRelative,
  formatRupiah,
  formatRupiahShort,
  timeGreeting,
} from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const router = useRouter()
const auth = useAuthStore()
const { data, loading, error, reload } = useResource(() => dasborApi.pemilik())

const greeting = computed(() => `${timeGreeting()}, ${firstName(auth.user?.nama_lengkap ?? '') || 'Pemilik'}`)
const today = formatLongDate(new Date())

const pending = computed(() => {
  const p = data.value?.perlu_tindakan
  if (!p) return 0
  return p.bukti_menunggu + p.izin_pending + p.aspirasi_baru + p.sewa_berakhir_7_hari
})

const subtitle = computed(() =>
  data.value
    ? `Ringkasan kos hari ini — ada ${pending.value} hal yang menunggu keputusan Anda.`
    : 'Ringkasan kos hari ini.',
)

const occupancy = computed(() => {
  const d = data.value
  if (!d?.total_kamar) return 0
  return Math.round((d.kamar_terisi / d.total_kamar) * 100)
})

const actions = computed(() => {
  const p = data.value?.perlu_tindakan
  if (!p) return []
  return [
    { label: 'Bukti bayar menunggu verifikasi', count: p.bukti_menunggu, to: { name: 'pemilik-keuangan' } },
    { label: 'Permohonan izin pending', count: p.izin_pending, to: { name: 'pemilik-layanan', query: { tab: 'izin' } } },
    { label: 'Aspirasi baru', count: p.aspirasi_baru, to: { name: 'pemilik-layanan', query: { tab: 'aspirasi' } } },
    { label: 'Sewa berakhir dalam 7 hari', count: p.sewa_berakhir_7_hari, to: { name: 'pemilik-penghuni' } },
  ]
})

const bars = computed(() => {
  const rows = data.value?.pemasukan_6_bulan ?? []
  const max = Math.max(1, ...rows.map((r) => r.total))
  return rows.map((r, i) => ({
    ...r,
    height: Math.max(4, Math.round((r.total / max) * 100)),
    last: i === rows.length - 1,
  }))
})

const TILE_CLASS = {
  Lunas: 'tile--paid',
  'Belum Bayar': 'tile--unpaid',
  'Masa Tenggang': 'tile--grace',
  Menunggu: 'tile--waiting',
  Kosong: 'tile--empty',
}

const LEGEND = [
  { label: 'Lunas', cls: 'tile--paid' },
  { label: 'Belum Bayar', cls: 'tile--unpaid' },
  { label: 'Masa Tenggang', cls: 'tile--grace' },
  { label: 'Menunggu', cls: 'tile--waiting' },
  { label: 'Kosong', cls: 'tile--empty' },
]

const ACTIVITY_TONE = {
  Aspirasi: 'warning',
  Izin: 'info',
  Lunas: 'success',
  Ulasan: 'neutral',
  'Barang Hilang': 'danger',
}

// Peta kamar hanya memuat nama penghuni (tanpa user id) → cari lewat daftar penghuni.
async function openRoom(room) {
  if (room.status === 'Kosong' || !room.penghuni) return
  try {
    const rows = await penghuniApi.list({ q: room.nomor })
    const match = rows.find((r) => r.sewa?.kamar === room.nomor && r.sewa?.status_sewa !== 'Sudah Keluar')
    if (match) return router.push({ name: 'pemilik-penghuni-detail', params: { userId: match.user.id } })
  } catch {
    // jatuh ke daftar penghuni
  }
  router.push({ name: 'pemilik-penghuni', query: { q: room.nomor } })
}
</script>

<template>
  <div>
    <AppHeader hero :eyebrow="today" :title="greeting" :subtitle="subtitle" />

    <div class="app-page">
      <StateBlock :loading="loading" :error="error" :has-data="!!data" @retry="reload">
        <template v-if="data">
          <!-- Statistik -->
          <section class="dash-stats" aria-label="Ringkasan">
            <div class="stat-card dash-stat">
              <p class="section-label">Kamar terisi</p>
              <p class="stat-card__value">{{ data.kamar_terisi }}<span class="stat-card__unit">/{{ data.total_kamar }}</span></p>
              <p class="stat-card__note">Okupansi {{ occupancy }}%</p>
            </div>
            <div class="stat-card dash-stat">
              <p class="section-label">Pemasukan bulan ini</p>
              <p class="stat-card__value dash-stat__money">{{ formatRupiahShort(data.pemasukan_bulan_ini) }}</p>
              <p class="stat-card__note">{{ data.tagihan_lunas }} dari {{ data.total_tagihan }} tagihan lunas</p>
            </div>
            <div class="stat-card dash-stat">
              <p class="section-label">Tunggakan</p>
              <p class="stat-card__value dash-stat__money is-crimson">{{ formatRupiahShort(data.tunggakan) }}</p>
              <p class="stat-card__note">{{ data.jumlah_penunggak }} penghuni · {{ data.jumlah_tenggang }} masa tenggang</p>
            </div>
            <RouterLink :to="{ name: 'pemilik-penilaian' }" class="stat-card dash-stat">
              <p class="section-label">Rating</p>
              <p class="stat-card__value">{{ formatDecimal(data.rating_rata) }}<span class="stat-card__unit">/5</span></p>
              <p class="stat-card__note">{{ data.jumlah_ulasan }} ulasan</p>
            </RouterLink>
          </section>

          <!-- Perlu tindakan (satu-satunya kartu peach) -->
          <section class="dash-action">
            <div class="section-title">
              <h2 class="panel-title dash-action__title">Perlu tindakan</h2>
              <span class="dash-action__total">{{ pending }}</span>
            </div>
            <ul class="dash-action__list">
              <li v-for="item in actions" :key="item.label">
                <RouterLink :to="item.to" class="dash-action__row">
                  <span class="dash-action__count" :class="{ 'is-zero': !item.count }">{{ item.count }}</span>
                  <span class="dash-action__label">{{ item.label }}</span>
                  <AppIcon name="chevron-right" :size="16" />
                </RouterLink>
              </li>
            </ul>
          </section>

          <div class="dash-quick">
            <RouterLink :to="{ name: 'pemilik-keuangan' }" class="button button--dark">Verifikasi Pembayaran</RouterLink>
            <RouterLink :to="{ name: 'pemilik-pengumuman' }" class="button button--outline">Buat Pengumuman</RouterLink>
          </div>

          <!-- Grafik pemasukan -->
          <section class="panel">
            <div class="section-title">
              <h2 class="panel-title">Pemasukan 6 bulan</h2>
              <RouterLink :to="{ name: 'pemilik-keuangan', query: { tab: 'laporan' } }" class="text-link">Laporan</RouterLink>
            </div>
            <p v-if="!bars.length" class="dash-muted">Belum ada data pemasukan.</p>
            <div v-else class="chart" role="img" :aria-label="`Grafik pemasukan ${bars.length} bulan terakhir`">
              <div v-for="bar in bars" :key="bar.periode" class="chart__col">
                <span class="chart__value">{{ formatRupiahShort(bar.total).replace('Rp ', '') }}</span>
                <div class="chart__track">
                  <div class="chart__bar" :class="{ 'is-last': bar.last }" :style="{ height: `${bar.height}%` }" :title="formatRupiah(bar.total)" />
                </div>
                <span class="chart__label" :class="{ 'is-last': bar.last }">{{ bar.label }}</span>
              </div>
            </div>
          </section>

          <!-- Peta kamar -->
          <section class="panel">
            <h2 class="panel-title">Peta kamar</h2>
            <p v-if="!data.peta_kamar.length" class="dash-muted">Belum ada kamar. Tambahkan lewat menu Kamar &amp; Tarif.</p>
            <div v-for="floor in data.peta_kamar" :key="floor.lantai" class="floor">
              <p class="section-label">Lantai {{ floor.lantai }}</p>
              <div class="floor__grid">
                <button
                  v-for="room in floor.kamar"
                  :key="room.id"
                  type="button"
                  class="tile"
                  :class="TILE_CLASS[room.status] ?? 'tile--empty'"
                  :disabled="room.status === 'Kosong' || !room.penghuni"
                  :aria-label="`Kamar ${room.nomor}: ${room.status}${room.penghuni ? ', ' + room.penghuni : ''}`"
                  @click="openRoom(room)"
                >
                  {{ room.nomor }}
                </button>
              </div>
            </div>
            <ul class="legend">
              <li v-for="item in LEGEND" :key="item.label"><span class="legend__dot tile" :class="item.cls" />{{ item.label }}</li>
            </ul>
          </section>

          <!-- Menunggu verifikasi -->
          <section class="panel">
            <div class="section-title">
              <h2 class="panel-title">Menunggu verifikasi</h2>
              <RouterLink :to="{ name: 'pemilik-keuangan' }" class="text-link">Semua</RouterLink>
            </div>
            <p v-if="!data.menunggu_verifikasi.length" class="dash-muted">Tidak ada bukti bayar yang menunggu.</p>
            <ul v-else class="dash-rows">
              <li v-for="bill in data.menunggu_verifikasi" :key="bill.id" class="dash-row">
                <UserAvatar :name="bill.penghuni?.nama_lengkap" :size="40" />
                <div class="dash-row__body">
                  <p class="dash-row__name">{{ bill.penghuni?.nama_lengkap }}</p>
                  <p class="dash-row__meta">Kamar {{ bill.kamar ?? '—' }} · {{ formatRupiah(bill.jumlah_tagihan) }}</p>
                </div>
                <RouterLink :to="{ name: 'pemilik-tagihan-detail', params: { id: bill.id } }" class="button button--outline button--sm">Periksa</RouterLink>
              </li>
            </ul>
          </section>

          <!-- Aktivitas -->
          <section class="panel">
            <h2 class="panel-title">Aktivitas terbaru</h2>
            <p v-if="!data.aktivitas.length" class="dash-muted">Belum ada aktivitas.</p>
            <ul v-else class="dash-rows">
              <li v-for="(item, index) in data.aktivitas" :key="index" class="dash-activity">
                <StatusBadge :tone="ACTIVITY_TONE[item.jenis] ?? 'neutral'">{{ item.jenis }}</StatusBadge>
                <p class="dash-activity__title">{{ item.judul }}</p>
                <p class="dash-row__meta">
                  <template v-if="item.nama">{{ item.nama }}<template v-if="item.kamar"> · {{ item.kamar }}</template> · </template>{{ formatRelative(item.waktu) }}
                </p>
              </li>
            </ul>
          </section>
        </template>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.dash-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.dash-stat {
  padding: 16px;
  color: inherit;
}

.dash-stat .section-label {
  font-size: 11px;
}

.dash-stat .stat-card__value {
  font-size: 30px;
}

.dash-stat__money {
  font-size: 24px !important;
}

.is-crimson {
  color: var(--crimson);
}

.dash-action {
  padding: 20px;
  background: var(--peach);
  border: 1px solid var(--peach-border);
  border-radius: var(--radius-card);
  color: var(--sienna);
}

.dash-action__title {
  color: var(--sienna);
}

.dash-action__total {
  min-width: 32px;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--crimson);
  color: #fff;
  font-weight: 700;
  text-align: center;
}

.dash-action__list {
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
}

.dash-action__row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid var(--peach-border);
}

.dash-action__count {
  min-width: 34px;
  font-family: var(--font-editorial);
  font-size: 24px;
  color: var(--crimson);
}

.dash-action__count.is-zero {
  color: rgba(93, 42, 26, 0.45);
}

.dash-action__label {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.dash-quick {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.dash-quick .button {
  padding: 12px 8px;
  font-size: 13px;
  white-space: normal;
  text-align: center;
}

.dash-muted {
  margin-top: 10px;
  font-size: 13px;
  color: var(--slate);
}

.chart {
  display: grid;
  grid-auto-columns: 1fr;
  grid-auto-flow: column;
  gap: 8px;
  margin-top: 16px;
}

.chart__col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.chart__value {
  font-size: 10px;
  color: var(--slate);
  white-space: nowrap;
}

.chart__track {
  width: 100%;
  height: 120px;
  display: flex;
  align-items: flex-end;
}

.chart__bar {
  width: 100%;
  border-radius: 8px 8px 4px 4px;
  background: var(--mist);
  border: 1px solid var(--border);
}

.chart__bar.is-last {
  background: var(--crimson);
  border-color: var(--crimson);
}

.chart__label {
  font-size: 12px;
  color: var(--slate);
}

.chart__label.is-last {
  font-weight: 700;
  color: var(--crimson);
}

.floor {
  margin-top: 16px;
}

.floor__grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-top: 8px;
}

.tile {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}

.tile:disabled {
  cursor: default;
}

.tile--paid {
  background: var(--maroon);
  color: #fff;
}

.tile--unpaid {
  background: var(--peach);
  border-color: var(--peach-border);
  color: var(--sienna);
}

.tile--grace {
  background: #f2c46d;
  color: #5a3a00;
}

.tile--waiting {
  background: #fff;
  border: 2px solid #e0a43a;
  color: #7a4e00;
}

.tile--empty {
  background: #fff;
  border: 1px dashed #cdbfbc;
  color: var(--slate);
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
  font-size: 11px;
  color: var(--slate);
}

.legend li {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend__dot {
  width: 12px;
  height: 12px;
  aspect-ratio: auto;
  border-radius: 4px;
}

.dash-rows {
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}

.dash-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.dash-row:last-child,
.dash-activity:last-child {
  border-bottom: 0;
}

.dash-row__body {
  flex: 1;
  min-width: 0;
}

.dash-row__name {
  font-size: 14px;
  font-weight: 600;
}

.dash-row__meta {
  margin-top: 2px;
  font-size: 12px;
  color: var(--slate);
}

.dash-activity {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.dash-activity__title {
  margin-top: 6px;
  font-size: 14px;
  font-weight: 500;
}
</style>
