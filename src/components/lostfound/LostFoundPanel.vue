<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { barangHilangApi } from '@/services/endpoints'
import AppIcon from '@/components/AppIcon.vue'
import SegmentedTabs from '@/components/app/SegmentedTabs.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import LostFoundCard from './LostFoundCard.vue'

/**
 * Papan informasi Barang Hilang (UC-15) — dipakai Penghuni & Pemilik.
 * Langkah 1–2: pengguna membuka menu → sistem menampilkan laporan yang masih aktif.
 */
const props = defineProps({
  /** Route form "Buat laporan" */
  createRoute: { type: Object, required: true },
  showStats: { type: Boolean, default: false },
})

const tab = ref('Aktif')
const query = ref('')
const active = ref([])
const done = ref([])
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    const [aktif, selesai] = await Promise.all([
      barangHilangApi.list({ status: 'Aktif' }),
      barangHilangApi.list({ status: 'Selesai' }),
    ])
    active.value = aktif
    done.value = selesai
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

onMounted(load)

const stats = computed(() => ({
  active: active.value.length,
  lost: active.value.filter((r) => r.jenis === 'Hilang').length,
  found: active.value.filter((r) => r.jenis === 'Temuan').length,
  done: done.value.length,
}))

const tabs = computed(() => [
  { value: 'Aktif', label: 'Aktif', count: stats.value.active },
  { value: 'Selesai', label: 'Selesai', count: stats.value.done },
])

const items = computed(() => {
  const source = tab.value === 'Aktif' ? active.value : done.value
  const keyword = query.value.trim().toLowerCase()
  if (!keyword) return source
  return source.filter((r) =>
    [r.judul_barang, r.lokasi, r.deskripsi, r.pelapor?.nama_lengkap].some((t) => t?.toLowerCase().includes(keyword)),
  )
})

function onResolved(updated) {
  active.value = active.value.filter((r) => r.id !== updated.id)
  done.value = [updated, ...done.value]
}

watch(tab, () => (query.value = ''))

defineExpose({ reload: load })
</script>

<template>
  <div class="lf-panel">
    <div v-if="showStats" class="lf-panel__stats" aria-label="Ringkasan laporan">
      <div class="lf-stat"><span>Aktif</span><strong>{{ stats.active }}</strong></div>
      <div class="lf-stat"><span>Hilang</span><strong class="is-lost">{{ stats.lost }}</strong></div>
      <div class="lf-stat"><span>Temuan</span><strong class="is-found">{{ stats.found }}</strong></div>
      <div class="lf-stat"><span>Selesai</span><strong>{{ stats.done }}</strong></div>
    </div>

    <SegmentedTabs v-model="tab" :options="tabs" label="Filter laporan" />

    <label class="lf-panel__search">
      <span class="sr-only">Cari barang</span>
      <AppIcon name="search" class="lf-panel__search-icon" />
      <input v-model="query" type="search" class="input" placeholder="Cari nama barang atau lokasi...">
    </label>

    <StateBlock
      :loading="loading"
      :error="error"
      :has-data="active.length + done.length > 0"
      :empty="!items.length"
      :empty-title="query ? 'Tidak ditemukan' : tab === 'Aktif' ? 'Belum ada laporan aktif' : 'Belum ada laporan selesai'"
      :empty-text="query ? `Tidak ada laporan yang cocok dengan “${query}”.` : 'Laporan barang hilang & temuan akan tampil di sini.'"
      @retry="load"
    >
      <TransitionGroup name="list" tag="div" class="lf-panel__list">
        <LostFoundCard v-for="report in items" :key="report.id" :report="report" @resolved="onResolved" />
      </TransitionGroup>
    </StateBlock>

    <RouterLink :to="props.createRoute" class="fab">
      <AppIcon name="plus" :size="18" :stroke-width="2.4" /> Buat laporan
    </RouterLink>
  </div>
</template>

<style scoped>
.lf-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lf-panel__stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.lf-stat {
  display: flex;
  flex-direction: column;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 16px;
}

.lf-stat span {
  font-size: 11px;
  color: var(--slate);
}

.lf-stat strong {
  font-family: var(--font-editorial);
  font-size: 24px;
  font-weight: 400;
}

.lf-stat .is-lost {
  color: var(--crimson);
}

.lf-stat .is-found {
  color: var(--status-success-text);
}

.lf-panel__search {
  position: relative;
}

.lf-panel__search .input {
  padding-left: 38px;
}

.lf-panel__search-icon {
  position: absolute;
  top: 50%;
  left: 14px;
  transform: translateY(-50%);
  color: var(--slate);
  pointer-events: none;
}

.lf-panel__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-enter-active,
.list-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
