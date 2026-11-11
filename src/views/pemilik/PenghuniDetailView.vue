<script setup>
import { computed, ref, shallowRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import { kendaraanApi, penghuniApi } from '@/services/endpoints'
import { useUiStore } from '@/stores/ui'
import { formatDate, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import BottomSheet from '@/components/app/BottomSheet.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const route = useRoute()
const ui = useUiStore()

const data = shallowRef(null)
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    data.value = await penghuniApi.detail(route.params.userId)
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

watch(() => route.params.userId, (id) => id && load(), { immediate: true })

const user = computed(() => data.value?.user)
const sewa = computed(() => data.value?.sewa)

const monthYear = new Intl.DateTimeFormat('id-ID', { month: 'short', year: 'numeric' })
const sinceLabel = computed(() => {
  if (!sewa.value) return 'Belum ditempatkan di kamar'
  const since = monthYear.format(new Date(`${sewa.value.tanggal_mulai}T00:00:00`)).replace('.', '')
  return `Kamar ${sewa.value.kamar ?? '—'} · sejak ${since}`
})

const telLink = (phone) => `tel:${String(phone).replace(/[^\d+]/g, '')}`

// ---------- Ubah status ----------
const STATUS_OPTIONS = ['Aktif', 'Masa Tenggang', 'Sudah Keluar']
const savingStatus = ref(false)

async function changeStatus(next) {
  if (!sewa.value || next === sewa.value.status_sewa || savingStatus.value) return
  const name = user.value.nama_lengkap
  const ok =
    next === 'Sudah Keluar'
      ? await ui.confirm(
          'Tandai sudah keluar?',
          `${name} akan dicatat keluar dan kamar ${sewa.value.kamar ?? ''} kembali tersedia. Tindakan ini tidak dapat dibatalkan.`,
          { confirmLabel: 'Ya, sudah keluar', tone: 'danger' },
        )
      : await ui.confirm(`Ubah status menjadi ${next}?`, `Status sewa ${name} akan diperbarui.`, { confirmLabel: 'Ubah status' })
  if (!ok) return

  savingStatus.value = true
  try {
    const result = await penghuniApi.setStatus(user.value.id, next)
    if (result?.user) data.value = result
    else await load()
    ui.showToast(`Status sewa diubah menjadi ${next}.`, 'success')
  } catch (err) {
    ui.showError(err, 'Gagal Mengubah Status')
  } finally {
    savingStatus.value = false
  }
}

// ---------- Slot parkir ----------
const slotOpen = ref(false)
const slotVehicle = ref(null)
const slotValue = ref('')
const savingSlot = ref(false)

function openSlot(vehicle) {
  slotVehicle.value = vehicle
  slotValue.value = vehicle.slot_parkir ?? ''
  slotOpen.value = true
}

async function saveSlot() {
  if (savingSlot.value) return
  savingSlot.value = true
  try {
    const updated = await kendaraanApi.update(slotVehicle.value.id, { slot_parkir: slotValue.value.trim() || null })
    data.value = {
      ...data.value,
      kendaraan: data.value.kendaraan.map((k) => (k.id === updated.id ? { ...k, ...updated } : k)),
    }
    slotOpen.value = false
    ui.showToast('Slot parkir disimpan.', 'success')
  } catch (err) {
    ui.showError(err, 'Gagal Menyimpan Slot')
  } finally {
    savingSlot.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader :back="{ name: 'pemilik-penghuni' }" title="Detail Penghuni" />

    <div class="app-page app-page--plain">
      <StateBlock :loading="loading" :error="error" :has-data="!!data" @retry="load">
        <template v-if="user">
          <section class="profile">
            <UserAvatar :name="user.nama_lengkap" :size="72" tone="maroon" />
            <h2 class="profile__name">{{ user.nama_lengkap }}</h2>
            <p class="profile__meta">{{ sinceLabel }}</p>
            <StatusBadge v-if="sewa" :tone="statusTone(sewa.status_sewa)">{{ sewa.status_sewa }}</StatusBadge>
          </section>

          <section class="panel">
            <h3 class="panel-title">Biodata</h3>
            <dl class="detail-list">
              <div class="detail-row">
                <dt>Telepon</dt>
                <dd><a v-if="user.nomor_telepon" :href="telLink(user.nomor_telepon)" class="text-link">{{ user.nomor_telepon }}</a><template v-else>—</template></dd>
              </div>
              <div class="detail-row"><dt>Email</dt><dd class="break">{{ user.email }}</dd></div>
              <div class="detail-row"><dt>Asal / kampus</dt><dd>{{ user.asal_kampus || '—' }}</dd></div>
              <div v-if="sewa" class="detail-row">
                <dt>Masa sewa</dt>
                <dd>{{ formatDate(sewa.tanggal_mulai) }} – {{ formatDate(sewa.tanggal_jatuh_tempo) }}</dd>
              </div>
              <div v-if="data.tagihan_bulan_ini" class="detail-row">
                <dt>Tagihan bulan ini</dt>
                <dd><StatusBadge :tone="statusTone(data.tagihan_bulan_ini)">{{ data.tagihan_bulan_ini }}</StatusBadge></dd>
              </div>
            </dl>
            <RouterLink
              :to="{ name: 'pemilik-keuangan', query: { penghuni: user.id, nama: user.nama_lengkap } }"
              class="text-link tagihan-link"
            >
              Lihat riwayat tagihan
            </RouterLink>
          </section>

          <section class="panel panel--mist">
            <h3 class="panel-title">Kontak darurat</h3>
            <p v-if="!user.kontak_darurat_nama && !user.kontak_darurat_telepon" class="muted">Belum diisi oleh penghuni.</p>
            <dl v-else class="detail-list">
              <div class="detail-row"><dt>Nama</dt><dd>{{ user.kontak_darurat_nama || '—' }}</dd></div>
              <div class="detail-row">
                <dt>Telepon</dt>
                <dd>
                  <a v-if="user.kontak_darurat_telepon" :href="telLink(user.kontak_darurat_telepon)" class="text-link">{{ user.kontak_darurat_telepon }}</a>
                  <template v-else>—</template>
                </dd>
              </div>
            </dl>
          </section>

          <section class="panel">
            <h3 class="panel-title">Kendaraan</h3>
            <p v-if="!data.kendaraan?.length" class="muted">Penghuni belum mendaftarkan kendaraan.</p>
            <div v-else class="vehicles">
              <div v-for="v in data.kendaraan" :key="v.id" class="vehicle">
                <span class="vehicle__icon"><AppIcon name="vehicle" :size="20" /></span>
                <div class="vehicle__body">
                  <p class="vehicle__plate">{{ v.nomor_polisi }}</p>
                  <p class="vehicle__meta">{{ v.jenis_kendaraan }}<template v-if="v.merk_warna"> · {{ v.merk_warna }}</template></p>
                  <p class="vehicle__meta">Slot: <strong>{{ v.slot_parkir || 'Belum diatur' }}</strong></p>
                </div>
                <button type="button" class="button button--outline button--sm" @click="openSlot(v)">Atur slot</button>
              </div>
            </div>
          </section>

          <section v-if="sewa" class="panel">
            <h3 class="panel-title">Ubah status penghuni</h3>
            <p class="panel-desc">Status saat ini: {{ sewa.status_sewa }}</p>
            <div class="status-seg" role="radiogroup" aria-label="Status sewa">
              <button
                v-for="option in STATUS_OPTIONS"
                :key="option"
                type="button"
                role="radio"
                class="status-seg__item"
                :class="{ 'is-active': sewa.status_sewa === option, 'is-danger': option === 'Sudah Keluar' }"
                :aria-checked="sewa.status_sewa === option"
                :disabled="savingStatus || sewa.status_sewa === 'Sudah Keluar'"
                @click="changeStatus(option)"
              >
                {{ option }}
              </button>
            </div>
            <p v-if="sewa.status_sewa === 'Sudah Keluar'" class="muted">Sewa sudah berakhir. Tempatkan ulang lewat menu Tambah Penghuni.</p>
          </section>
        </template>
      </StateBlock>
    </div>

    <BottomSheet v-model:open="slotOpen" title="Atur slot parkir" :description="slotVehicle ? `${slotVehicle.jenis_kendaraan} · ${slotVehicle.nomor_polisi}` : ''">
      <form class="form-stack" @submit.prevent="saveSlot">
        <label>
          <span class="field-label">Slot parkir</span>
          <input v-model="slotValue" type="text" class="input" maxlength="20" placeholder="Contoh: M-07">
        </label>
        <div class="form-actions">
          <button type="button" class="button button--outline" @click="slotOpen = false">Batal</button>
          <button type="submit" class="button button--primary" :disabled="savingSlot">{{ savingSlot ? 'Menyimpan…' : 'Simpan' }}</button>
        </div>
      </form>
    </BottomSheet>
  </div>
</template>

<style scoped>
.profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 0 4px;
  text-align: center;
}

.profile__name {
  margin-top: 6px;
  font-family: var(--font-editorial);
  font-size: 28px;
  font-weight: 400;
}

.profile__meta {
  margin-bottom: 4px;
  font-size: 14px;
  color: var(--slate);
}

.panel {
  padding: 20px;
}

.panel .panel-title {
  margin-bottom: 6px;
  font-size: 20px;
}

.panel--mist {
  background: var(--mist);
  border-color: transparent;
}

.panel--mist .detail-row {
  border-color: rgba(94, 81, 86, 0.15);
}

.break {
  word-break: break-all;
}

.muted {
  margin-top: 8px;
  font-size: 13px;
  color: var(--slate);
}

.tagihan-link {
  display: inline-block;
  margin-top: 10px;
}

.vehicles {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

.vehicle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 16px;
}

.vehicle__icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--mist);
}

.vehicle__body {
  flex: 1;
  min-width: 0;
}

.vehicle__plate {
  font-weight: 700;
  letter-spacing: 0.04em;
}

.vehicle__meta {
  margin-top: 2px;
  font-size: 12px;
  color: var(--slate);
}

.status-seg {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4px;
  margin-top: 12px;
  padding: 4px;
  border-radius: 14px;
  background: var(--mist);
}

.status-seg__item {
  padding: 10px 4px;
  border: 0;
  border-radius: 11px;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: var(--slate);
}

.status-seg__item.is-active {
  background: var(--maroon);
  color: #fff;
}

.status-seg__item.is-danger:not(.is-active) {
  color: var(--crimson);
}

.status-seg__item:disabled {
  cursor: not-allowed;
}
</style>
