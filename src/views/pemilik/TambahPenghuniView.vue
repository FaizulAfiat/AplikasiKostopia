<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { kamarApi, penghuniApi, profilKosApi } from '@/services/endpoints'
import { useUiStore } from '@/stores/ui'
import { formatRupiah, todayISO } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import AppIcon from '@/components/AppIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const router = useRouter()
const ui = useUiStore()

const users = ref([])
const rooms = ref([])
const inviteCode = ref('')
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    const [unassigned, allRooms] = await Promise.all([penghuniApi.unassigned(), kamarApi.list()])
    users.value = unassigned
    rooms.value = allRooms.filter((r) => r.status_ketersediaan === 'Tersedia')
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  profilKosApi.get().then((p) => (inviteCode.value = p?.kode_undangan ?? '')).catch(() => {})
})

const form = reactive({ userId: null, roomId: null, tanggal_mulai: todayISO(), lama_bulan: 6 })
const errors = reactive({ user: '', room: '', tanggal: '', lama: '' })
const submitting = ref(false)

const selectedRoom = computed(() => rooms.value.find((r) => r.id === form.roomId))

function validate() {
  errors.user = form.userId ? '' : 'Pilih penghuni terlebih dahulu.'
  errors.room = form.roomId ? '' : 'Pilih kamar yang tersedia.'
  errors.tanggal = form.tanggal_mulai ? '' : 'Tanggal mulai wajib diisi.'
  errors.lama = Number.isInteger(Number(form.lama_bulan)) && Number(form.lama_bulan) >= 1 ? '' : 'Lama sewa minimal 1 bulan.'
  return !errors.user && !errors.room && !errors.tanggal && !errors.lama
}

async function submit() {
  if (!validate() || submitting.value) return
  submitting.value = true
  try {
    await penghuniApi.assignRoom(form.userId, {
      room_id: form.roomId,
      tanggal_mulai: form.tanggal_mulai,
      lama_bulan: Number(form.lama_bulan),
    })
    const name = users.value.find((u) => u.id === form.userId)?.nama_lengkap ?? 'Penghuni'
    ui.showToast(`${name} ditempatkan di kamar ${selectedRoom.value?.nomor_kamar ?? ''}.`, 'success')
    router.replace({ name: 'pemilik-penghuni-detail', params: { userId: form.userId } })
  } catch (err) {
    ui.showError(err, 'Gagal Menambahkan Penghuni')
  } finally {
    submitting.value = false
  }
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText(inviteCode.value)
    ui.showToast('Kode undangan disalin.', 'success')
  } catch {
    ui.showToast(`Kode undangan: ${inviteCode.value}`, 'info')
  }
}
</script>

<template>
  <div>
    <AppHeader :back="{ name: 'pemilik-penghuni' }" title="Tambah Penghuni" subtitle="Tempatkan penghuni terdaftar ke kamar." />

    <form class="app-page app-page--plain" novalidate @submit.prevent="submit">
      <section class="panel panel--mist intro">
        <AppIcon name="info" :size="20" />
        <div>
          <p>Penghuni perlu <strong>mendaftar akun di aplikasi Kostopia</strong> terlebih dahulu. Setelah itu namanya muncul di daftar di bawah.</p>
          <button v-if="inviteCode" type="button" class="code" @click="copyCode">
            Kode undangan <strong>{{ inviteCode }}</strong> <AppIcon name="copy" :size="14" />
          </button>
        </div>
      </section>

      <StateBlock :loading="loading" :error="error" :has-data="users.length + rooms.length > 0" @retry="load">
        <section class="block">
          <h2 class="section-label">1 · Pilih penghuni</h2>
          <div v-if="!users.length" class="empty-state">
            Belum ada akun penghuni yang menunggu ditempatkan. Minta calon penghuni mendaftar di aplikasi{{ inviteCode ? ` dengan kode ${inviteCode}` : '' }}, lalu muat ulang halaman ini.
            <div><button type="button" class="button button--outline button--sm reload" @click="load"><AppIcon name="refresh" :size="14" /> Muat ulang</button></div>
          </div>
          <div v-else class="choices" role="radiogroup" aria-label="Penghuni">
            <label v-for="u in users" :key="u.id" class="choice" :class="{ 'is-selected': form.userId === u.id }">
              <input v-model="form.userId" type="radio" name="penghuni" :value="u.id" class="sr-only" @change="errors.user = ''">
              <UserAvatar :name="u.nama_lengkap" :size="40" />
              <span class="choice__body">
                <span class="choice__title">{{ u.nama_lengkap }}</span>
                <span class="choice__meta">{{ u.email }}<template v-if="u.nomor_telepon"> · {{ u.nomor_telepon }}</template></span>
              </span>
              <span class="choice__radio" aria-hidden="true" />
            </label>
          </div>
          <p v-if="errors.user" class="field-error" role="alert">{{ errors.user }}</p>
        </section>

        <section class="block">
          <h2 class="section-label">2 · Pilih kamar</h2>
          <div v-if="!rooms.length" class="empty-state">
            Tidak ada kamar berstatus Tersedia.
            <RouterLink :to="{ name: 'pemilik-kamar' }" class="text-link">Kelola kamar</RouterLink>
          </div>
          <div v-else class="rooms" role="radiogroup" aria-label="Kamar">
            <label v-for="r in rooms" :key="r.id" class="room" :class="{ 'is-selected': form.roomId === r.id }">
              <input v-model="form.roomId" type="radio" name="kamar" :value="r.id" class="sr-only" @change="errors.room = ''">
              <span class="room__no">{{ r.nomor_kamar }}</span>
              <span class="room__meta">{{ r.tipe || 'Standar' }} · Lt {{ r.lantai ?? '—' }}</span>
              <span class="room__price">{{ formatRupiah(r.harga_dasar) }}</span>
            </label>
          </div>
          <p v-if="errors.room" class="field-error" role="alert">{{ errors.room }}</p>
        </section>

        <section class="block form-row">
          <label>
            <span class="field-label">Tanggal mulai <span class="req">*</span></span>
            <input v-model="form.tanggal_mulai" type="date" class="input" :class="{ 'is-invalid': errors.tanggal }">
            <span v-if="errors.tanggal" class="field-error">{{ errors.tanggal }}</span>
          </label>
          <label>
            <span class="field-label">Lama sewa (bulan) <span class="req">*</span></span>
            <input v-model.number="form.lama_bulan" type="number" min="1" max="60" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.lama }">
            <span v-if="errors.lama" class="field-error">{{ errors.lama }}</span>
          </label>
        </section>

        <p v-if="selectedRoom" class="summary">
          Tagihan pertama sebesar <strong>{{ formatRupiah(selectedRoom.harga_dasar) }}</strong> (belum termasuk parkir) dibuat otomatis untuk bulan berjalan.
        </p>

        <button type="submit" class="button button--primary button--block submit" :disabled="submitting || !users.length || !rooms.length">
          {{ submitting ? 'Menyimpan…' : 'Tempatkan Penghuni' }}
        </button>
      </StateBlock>
    </form>
  </div>
</template>

<style scoped>
.panel--mist {
  background: var(--mist);
  border-color: transparent;
}

.intro {
  display: flex;
  gap: 12px;
  padding: 16px 18px;
  font-size: 14px;
  line-height: 1.5;
}

.intro > svg {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--crimson);
}

.code {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 6px 12px;
  border: 1px dashed var(--slate);
  border-radius: 10px;
  background: #fff;
  font-size: 13px;
}

.block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 14px;
}

.reload {
  margin-top: 12px;
}

.choices {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.choice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 18px;
  cursor: pointer;
}

.choice.is-selected,
.room.is-selected {
  border-color: var(--crimson);
  box-shadow: 0 0 0 2px rgba(112, 0, 32, 0.12);
}

.choice__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.choice__title {
  font-weight: 600;
}

.choice__meta {
  overflow: hidden;
  font-size: 12px;
  color: var(--slate);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.choice__radio {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border);
  border-radius: 999px;
}

.choice.is-selected .choice__radio {
  border: 6px solid var(--crimson);
}

.rooms {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.room {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 16px;
  cursor: pointer;
}

.room__no {
  font-family: var(--font-editorial);
  font-size: 20px;
}

.room__meta {
  font-size: 11px;
  color: var(--slate);
}

.room__price {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 600;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.summary {
  margin-bottom: 14px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--slate);
}

.submit {
  padding: 14px;
}
</style>
