<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { aspirasiApi, izinApi } from '@/services/endpoints'
import { useUiStore } from '@/stores/ui'
import { formatDate, formatRelative, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import SegmentedTabs from '@/components/app/SegmentedTabs.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import BottomSheet from '@/components/app/BottomSheet.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import LostFoundPanel from '@/components/lostfound/LostFoundPanel.vue'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()

const TABS = ['aspirasi', 'izin', 'barang']
const normalizeTab = (value) => (TABS.includes(value) ? value : 'aspirasi')

const tab = ref(normalizeTab(route.query.tab))
watch(() => route.query.tab, (value) => (tab.value = normalizeTab(value)))
watch(tab, (value) => {
  if (normalizeTab(route.query.tab) !== value) router.replace({ query: { ...route.query, tab: value } })
})

// ---------- Aspirasi ----------
const aspirasi = reactive({ items: [], loading: false, error: null })

async function loadAspirasi() {
  aspirasi.loading = true
  aspirasi.error = null
  try {
    aspirasi.items = await aspirasiApi.list()
  } catch (err) {
    aspirasi.error = err
  } finally {
    aspirasi.loading = false
  }
}

const ASPIRASI_GROUPS = ['Menunggu', 'Sedang Diproses', 'Selesai']
const aspirasiGroups = computed(() =>
  ASPIRASI_GROUPS.map((status) => ({
    status,
    items: aspirasi.items.filter((a) => a.status_penanganan === status),
  })),
)
const openAspirasi = computed(() => aspirasi.items.filter((a) => a.status_penanganan !== 'Selesai').length)

// ---------- Izin ----------
const izin = reactive({ items: [], loading: false, error: null })
const izinFilter = ref('Pending')

async function loadIzin() {
  izin.loading = true
  izin.error = null
  try {
    izin.items = await izinApi.list()
  } catch (err) {
    izin.error = err
  } finally {
    izin.loading = false
  }
}

const izinCounts = computed(() => {
  const c = { Pending: 0, Disetujui: 0, Ditolak: 0 }
  izin.items.forEach((i) => {
    if (i.status_izin in c) c[i.status_izin] += 1
  })
  return c
})
const izinOptions = computed(() =>
  Object.keys(izinCounts.value).map((value) => ({ value, label: value, count: izinCounts.value[value] })),
)
const izinFiltered = computed(() => izin.items.filter((i) => i.status_izin === izinFilter.value))

// Keputusan izin
const decision = reactive({ open: false, item: null, approve: true, catatan: '', saving: false })

function openDecision(item, approve) {
  Object.assign(decision, { open: true, item, approve, catatan: '' })
}

async function submitDecision() {
  if (decision.saving) return
  decision.saving = true
  try {
    const updated = await izinApi.decide(decision.item.id, {
      status_izin: decision.approve ? 'Disetujui' : 'Ditolak',
      catatan_pemilik: decision.catatan.trim() || null,
    })
    izin.items = izin.items.map((i) => (i.id === decision.item.id ? { ...i, ...(updated ?? {}), status_izin: decision.approve ? 'Disetujui' : 'Ditolak' } : i))
    decision.open = false
    ui.showToast(decision.approve ? 'Izin disetujui.' : 'Izin ditolak.', 'success')
  } catch (err) {
    ui.showError(err, 'Gagal Menyimpan Keputusan')
  } finally {
    decision.saving = false
  }
}

const tabOptions = computed(() => [
  { value: 'aspirasi', label: 'Aspirasi', count: openAspirasi.value },
  { value: 'izin', label: 'Izin', count: izinCounts.value.Pending },
  { value: 'barang', label: 'Barang Hilang' },
])

onMounted(() => {
  loadAspirasi()
  loadIzin()
})
</script>

<template>
  <div>
    <AppHeader title="Layanan" subtitle="Aspirasi, perizinan & papan barang hilang.">
      <SegmentedTabs v-model="tab" :options="tabOptions" label="Jenis layanan" />
    </AppHeader>

    <div class="app-page">
      <!-- ================= Aspirasi ================= -->
      <template v-if="tab === 'aspirasi'">
        <StateBlock
          :loading="aspirasi.loading"
          :error="aspirasi.error"
          :has-data="aspirasi.items.length > 0"
          :empty="!aspirasi.items.length"
          empty-icon="chat"
          empty-title="Belum ada aspirasi"
          empty-text="Keluhan & saran dari penghuni akan muncul di sini."
          @retry="loadAspirasi"
        >
          <section v-for="group in aspirasiGroups" :key="group.status" class="group">
            <div class="group__head">
              <StatusBadge :tone="statusTone(group.status)">{{ group.status }}</StatusBadge>
              <span class="group__count">{{ group.items.length }}</span>
            </div>
            <p v-if="!group.items.length" class="group__empty">Tidak ada aspirasi.</p>
            <RouterLink
              v-for="item in group.items"
              :key="item.id"
              :to="{ name: 'pemilik-aspirasi-detail', params: { id: item.id } }"
              class="list-card"
            >
              <div class="list-card__head">
                <span class="chip">{{ item.kategori }}</span>
                <span class="list-card__meta">#{{ item.id }}</span>
              </div>
              <p class="list-card__title">{{ item.judul }}</p>
              <p class="list-card__meta">
                {{ item.pelapor?.nama_lengkap ?? '—' }}<template v-if="item.pelapor?.kamar"> · {{ item.pelapor.kamar }}</template> · {{ formatRelative(item.created_at) }}
              </p>
            </RouterLink>
          </section>
        </StateBlock>
      </template>

      <!-- ================= Izin ================= -->
      <template v-else-if="tab === 'izin'">
        <SegmentedTabs v-model="izinFilter" :options="izinOptions" label="Filter status izin" />
        <StateBlock
          :loading="izin.loading"
          :error="izin.error"
          :has-data="izin.items.length > 0"
          :empty="!izinFiltered.length"
          empty-icon="calendar"
          :empty-title="izinFilter === 'Pending' ? 'Tidak ada izin menunggu' : `Belum ada izin ${izinFilter.toLowerCase()}`"
          empty-text="Permohonan izin penghuni akan muncul di sini."
          @retry="loadIzin"
        >
          <div class="card-list">
            <article v-for="item in izinFiltered" :key="item.id" class="list-card izin">
              <div class="list-card__head">
                <p class="izin__type">{{ item.jenis_izin }}</p>
                <StatusBadge :tone="statusTone(item.status_izin)">{{ item.status_izin }}</StatusBadge>
              </div>
              <p class="izin__dates">
                {{ formatDate(item.tanggal_mulai) }} – {{ formatDate(item.tanggal_selesai) }}
                <span v-if="item.durasi" class="chip">{{ item.durasi }}</span>
              </p>
              <p v-if="item.alasan" class="izin__reason">“{{ item.alasan }}”</p>
              <p class="list-card__meta">
                {{ item.pemohon?.nama_lengkap ?? '—' }}<template v-if="item.pemohon?.kamar"> · Kamar {{ item.pemohon.kamar }}</template> · {{ formatRelative(item.created_at) }}
              </p>
              <p v-if="item.catatan_pemilik" class="izin__note">Catatan: {{ item.catatan_pemilik }}</p>
              <div v-if="item.status_izin === 'Pending'" class="izin__actions">
                <button type="button" class="button button--outline button--sm" @click="openDecision(item, false)">Tolak</button>
                <button type="button" class="button button--dark button--sm" @click="openDecision(item, true)">Setujui</button>
              </div>
            </article>
          </div>
        </StateBlock>
      </template>

      <!-- ================= Barang hilang (UC-15) ================= -->
      <LostFoundPanel v-else :create-route="{ name: 'pemilik-barang-hilang-baru' }" show-stats />
    </div>

    <BottomSheet
      v-model:open="decision.open"
      :title="decision.approve ? 'Setujui izin' : 'Tolak izin'"
      :description="decision.item ? `${decision.item.jenis_izin} · ${decision.item.pemohon?.nama_lengkap ?? ''}` : ''"
    >
      <form class="form-stack" @submit.prevent="submitDecision">
        <label>
          <span class="field-label">Catatan untuk penghuni <span class="field-label__hint">(opsional)</span></span>
          <textarea
            v-model="decision.catatan"
            class="textarea"
            maxlength="300"
            :placeholder="decision.approve ? 'Contoh: Hati-hati di jalan, kunci kamar dititip di pos.' : 'Contoh: Mohon ajukan ulang dengan tanggal yang jelas.'"
          />
        </label>
        <div class="form-actions">
          <button type="button" class="button button--outline" @click="decision.open = false">Batal</button>
          <button type="submit" class="button" :class="decision.approve ? 'button--dark' : 'button--primary'" :disabled="decision.saving">
            {{ decision.saving ? 'Menyimpan…' : decision.approve ? 'Setujui' : 'Tolak' }}
          </button>
        </div>
      </form>
    </BottomSheet>
  </div>
</template>

<style scoped>
.group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.group__head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.group__count {
  min-width: 24px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--mist);
  font-size: 12px;
  font-weight: 700;
  text-align: center;
}

.group__empty {
  padding: 12px 16px;
  border: 1px dashed var(--border);
  border-radius: 16px;
  font-size: 13px;
  color: var(--slate);
}

.chip {
  display: inline-flex;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--mist);
  font-size: 11px;
  font-weight: 600;
  color: var(--slate);
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.izin__type {
  font-size: 15px;
  font-weight: 600;
}

.izin__dates {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  font-size: 14px;
  font-weight: 500;
}

.izin__reason {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--ink);
}

.izin__note {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 12px;
  background: var(--fog);
  font-size: 12px;
  color: var(--slate);
}

.izin__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 12px;
}
</style>
