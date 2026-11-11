<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { kendaraanApi, penghuniApi, profilKosApi } from '@/services/endpoints'
import { useUiStore } from '@/stores/ui'
import { formatDate, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import SegmentedTabs from '@/components/app/SegmentedTabs.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const route = useRoute()
const ui = useUiStore()

const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
const q = ref(search.value.trim())
const status = ref('Semua')

const rows = ref([])
const loading = ref(false)
const error = ref(null)
let reqId = 0

async function load() {
  const id = ++reqId
  loading.value = true
  error.value = null
  try {
    const result = await penghuniApi.list({ q: q.value || undefined })
    if (id === reqId) rows.value = result
  } catch (err) {
    if (id === reqId) error.value = err
  } finally {
    if (id === reqId) loading.value = false
  }
}

// Pencarian (debounce 350 ms) → parameter q
let timer = null
watch(search, (value) => {
  clearTimeout(timer)
  timer = setTimeout(() => (q.value = value.trim()), 350)
})
watch(q, load)
onBeforeUnmount(() => clearTimeout(timer))

// Ringkasan: profil kos (kode undangan) & parkir
const profil = ref(null)
const parking = ref(null)

onMounted(() => {
  load()
  profilKosApi.get().then((p) => (profil.value = p)).catch(() => {})
  kendaraanApi.summary().then((s) => (parking.value = s)).catch(() => {})
})

const counts = computed(() => {
  const c = { Semua: rows.value.length, Aktif: 0, 'Masa Tenggang': 0, 'Sudah Keluar': 0 }
  rows.value.forEach((r) => {
    const s = r.sewa?.status_sewa
    if (s in c) c[s] += 1
  })
  return c
})

const tabs = computed(() =>
  ['Semua', 'Aktif', 'Masa Tenggang', 'Sudah Keluar'].map((value) => ({
    value,
    label: value,
    count: counts.value[value],
  })),
)

const filtered = computed(() =>
  status.value === 'Semua' ? rows.value : rows.value.filter((r) => r.sewa?.status_sewa === status.value),
)

const subtitle = computed(() => {
  const active = counts.value.Aktif + counts.value['Masa Tenggang']
  const parts = [`${active} penghuni aktif`]
  if (profil.value?.kode_undangan) parts.push(`Kode undangan ${profil.value.kode_undangan}`)
  return parts.join(' · ')
})

async function copyCode() {
  const code = profil.value?.kode_undangan
  if (!code) return
  try {
    await navigator.clipboard.writeText(code)
    ui.showToast(`Kode undangan ${code} disalin.`, 'success')
  } catch {
    ui.showToast(`Kode undangan: ${code}`, 'info')
  }
}

function plates(row) {
  return (row.kendaraan ?? []).map((k) => k.nomor_polisi).join(', ')
}
</script>

<template>
  <div>
    <AppHeader title="Penghuni & Kamar" :subtitle="subtitle">
      <template v-if="profil?.kode_undangan" #actions>
        <button type="button" class="code-btn" aria-label="Salin kode undangan" @click="copyCode">
          <AppIcon name="copy" :size="18" />
        </button>
      </template>
    </AppHeader>

    <div class="app-page">
      <div class="mini-stats" aria-label="Ringkasan penghuni">
        <div class="mini-stat"><span>Aktif</span><strong>{{ counts.Aktif }}</strong></div>
        <div class="mini-stat"><span>Tenggang</span><strong class="is-warn">{{ counts['Masa Tenggang'] }}</strong></div>
        <div class="mini-stat">
          <span>Motor</span>
          <strong>{{ parking ? `${parking.motor_terpakai}/${parking.motor_kapasitas}` : '—' }}</strong>
        </div>
        <div class="mini-stat">
          <span>Mobil</span>
          <strong>{{ parking ? `${parking.mobil_terpakai}/${parking.mobil_kapasitas}` : '—' }}</strong>
        </div>
      </div>

      <label class="search">
        <span class="sr-only">Cari penghuni</span>
        <AppIcon name="search" class="search__icon" />
        <input v-model="search" type="search" class="input" placeholder="Cari nama, kamar, atau plat nomor...">
      </label>

      <SegmentedTabs v-model="status" :options="tabs" label="Filter status sewa" />

      <StateBlock
        :loading="loading"
        :error="error"
        :has-data="rows.length > 0"
        :empty="!filtered.length"
        empty-icon="users"
        :empty-title="q ? 'Tidak ditemukan' : 'Belum ada penghuni'"
        :empty-text="q ? `Tidak ada penghuni yang cocok dengan “${q}”.` : 'Tambahkan penghuni yang sudah mendaftar di aplikasi ke kamar yang tersedia.'"
        @retry="load"
      >
        <div class="card-list">
          <RouterLink
            v-for="row in filtered"
            :key="row.user.id"
            :to="{ name: 'pemilik-penghuni-detail', params: { userId: row.user.id } }"
            class="list-card tenant-card"
            :class="{ 'is-out': row.sewa?.status_sewa === 'Sudah Keluar' }"
          >
            <UserAvatar :name="row.user.nama_lengkap" :size="44" />
            <div class="tenant-card__body">
              <div class="list-card__head">
                <p class="tenant-card__name">{{ row.user.nama_lengkap }}</p>
                <StatusBadge v-if="row.sewa" :tone="statusTone(row.sewa.status_sewa)">{{ row.sewa.status_sewa }}</StatusBadge>
              </div>
              <p class="list-card__meta">
                Kamar {{ row.sewa?.kamar ?? '—' }}<template v-if="row.sewa"> · Sewa s/d {{ formatDate(row.sewa.tanggal_jatuh_tempo) }}</template>
              </p>
              <div class="tenant-card__foot">
                <span v-if="plates(row)" class="plate"><AppIcon name="vehicle" :size="13" /> {{ plates(row) }}</span>
                <span v-if="row.tagihan_bulan_ini" class="bill">
                  Tagihan: <StatusBadge :tone="statusTone(row.tagihan_bulan_ini)">{{ row.tagihan_bulan_ini }}</StatusBadge>
                </span>
              </div>
            </div>
          </RouterLink>
        </div>
      </StateBlock>
    </div>

    <RouterLink :to="{ name: 'pemilik-penghuni-tambah' }" class="fab">
      <AppIcon name="plus" :size="18" :stroke-width="2.4" /> Tambah Penghuni
    </RouterLink>
  </div>
</template>

<style scoped>
.code-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 999px;
  background: var(--mist);
  color: var(--ink);
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.mini-stat {
  display: flex;
  flex-direction: column;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 16px;
}

.mini-stat span {
  font-size: 11px;
  color: var(--slate);
}

.mini-stat strong {
  font-family: var(--font-editorial);
  font-size: 22px;
  font-weight: 400;
  white-space: nowrap;
}

.mini-stat .is-warn {
  color: var(--status-warning-text);
}

.search {
  position: relative;
}

.search .input {
  padding-left: 38px;
}

.search__icon {
  position: absolute;
  top: 50%;
  left: 14px;
  transform: translateY(-50%);
  color: var(--slate);
  pointer-events: none;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tenant-card {
  display: flex;
  gap: 12px;
}

.tenant-card.is-out {
  opacity: 0.7;
}

.tenant-card__body {
  flex: 1;
  min-width: 0;
}

.tenant-card__name {
  overflow: hidden;
  font-size: 15px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tenant-card__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--slate);
}

.plate {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 8px;
  background: var(--mist);
  font-weight: 600;
  color: var(--ink);
}

.bill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>
