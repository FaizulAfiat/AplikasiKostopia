<script setup>
import { computed, reactive, ref } from 'vue'
import { kamarApi } from '@/services/endpoints'
import { useResource } from '@/composables/useResource'
import { useUiStore } from '@/stores/ui'
import { formatRupiah } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import BottomSheet from '@/components/app/BottomSheet.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const ui = useUiStore()
const { data, loading, error, reload } = useResource(() => kamarApi.list(), { initial: [] })
const rooms = computed(() => data.value ?? [])

const STATUS = ['Tersedia', 'Dihuni', 'Perbaikan']
const STATUS_TONE = { Tersedia: 'success', Dihuni: 'info', Perbaikan: 'warning' }

const floors = computed(() => {
  const map = new Map()
  rooms.value.forEach((r) => {
    const key = r.lantai ?? 0
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(r)
  })
  return [...map.entries()]
    .sort(([a], [b]) => a - b)
    .map(([lantai, list]) => ({ lantai, rooms: list.sort((a, b) => a.nomor_kamar.localeCompare(b.nomor_kamar, 'id', { numeric: true })) }))
})

const counts = computed(() => {
  const c = { Tersedia: 0, Dihuni: 0, Perbaikan: 0 }
  rooms.value.forEach((r) => (c[r.status_ketersediaan] = (c[r.status_ketersediaan] ?? 0) + 1))
  return c
})

// ---------- Form ----------
const sheetOpen = ref(false)
const editing = ref(null)
const form = reactive({ nomor_kamar: '', lantai: 1, tipe: 'Standar', harga_dasar: null, status_ketersediaan: 'Tersedia' })
const errors = reactive({ nomor: '', harga: '', lantai: '' })
const saving = ref(false)

function openForm(room = null) {
  editing.value = room
  Object.assign(form, {
    nomor_kamar: room?.nomor_kamar ?? '',
    lantai: room?.lantai ?? (floors.value.at(-1)?.lantai || 1),
    tipe: room?.tipe ?? 'Standar',
    harga_dasar: room?.harga_dasar ?? null,
    status_ketersediaan: room?.status_ketersediaan ?? 'Tersedia',
  })
  Object.assign(errors, { nomor: '', harga: '', lantai: '' })
  sheetOpen.value = true
}

async function save() {
  errors.nomor = form.nomor_kamar.trim() ? '' : 'Nomor kamar wajib diisi.'
  errors.harga = form.harga_dasar !== null && form.harga_dasar !== '' && Number(form.harga_dasar) >= 0 ? '' : 'Harga sewa wajib diisi.'
  errors.lantai = Number.isInteger(Number(form.lantai)) && Number(form.lantai) >= 0 ? '' : 'Lantai harus berupa angka.'
  if (errors.nomor || errors.harga || errors.lantai || saving.value) return

  saving.value = true
  const body = {
    nomor_kamar: form.nomor_kamar.trim().toUpperCase(),
    lantai: Number(form.lantai),
    tipe: form.tipe.trim() || 'Standar',
    harga_dasar: Math.round(Number(form.harga_dasar)),
    status_ketersediaan: form.status_ketersediaan,
  }
  try {
    if (editing.value) await kamarApi.update(editing.value.id, body)
    else await kamarApi.create(body)
    sheetOpen.value = false
    ui.showToast(editing.value ? `Kamar ${body.nomor_kamar} diperbarui.` : `Kamar ${body.nomor_kamar} ditambahkan.`, 'success')
    reload()
  } catch (err) {
    ui.showError(err, 'Gagal Menyimpan Kamar')
  } finally {
    saving.value = false
  }
}

async function remove() {
  const room = editing.value
  if (!room) return
  const ok = await ui.confirm(`Hapus kamar ${room.nomor_kamar}?`, 'Kamar akan dihapus dari daftar. Kamar yang sedang dihuni tidak dapat dihapus.', {
    confirmLabel: 'Hapus',
    tone: 'danger',
  })
  if (!ok) return
  saving.value = true
  try {
    await kamarApi.remove(room.id)
    sheetOpen.value = false
    data.value = rooms.value.filter((r) => r.id !== room.id)
    ui.showToast(`Kamar ${room.nomor_kamar} dihapus.`, 'success')
  } catch (err) {
    ui.showError(err, 'Kamar Tidak Dapat Dihapus')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader
      :back="{ name: 'pemilik-lainnya' }"
      title="Kamar & Tarif"
      :subtitle="rooms.length ? `${rooms.length} kamar · ${counts.Tersedia} tersedia · ${counts.Dihuni} dihuni` : ''"
    >
      <template #actions>
        <button type="button" class="button button--primary button--sm" @click="openForm()">
          <AppIcon name="plus" :size="14" /> Tambah kamar
        </button>
      </template>
    </AppHeader>

    <div class="app-page app-page--plain">
      <StateBlock
        :loading="loading"
        :error="error"
        :has-data="rooms.length > 0"
        :empty="!rooms.length"
        empty-icon="door"
        empty-title="Belum ada kamar"
        empty-text="Tambahkan kamar beserta harga sewanya agar bisa ditempati penghuni."
        @retry="reload"
      >
        <template #empty-action>
          <button type="button" class="button button--primary button--sm" @click="openForm()">+ Tambah kamar</button>
        </template>

        <section v-for="floor in floors" :key="floor.lantai" class="floor">
          <h2 class="section-label">{{ floor.lantai ? `Lantai ${floor.lantai}` : 'Tanpa lantai' }} · {{ floor.rooms.length }} kamar</h2>
          <button v-for="room in floor.rooms" :key="room.id" type="button" class="list-card room" @click="openForm(room)">
            <span class="room__no">{{ room.nomor_kamar }}</span>
            <span class="room__body">
              <span class="room__type">{{ room.tipe || 'Standar' }}</span>
              <span class="room__price">{{ formatRupiah(room.harga_dasar) }}<small>/bulan</small></span>
              <span v-if="room.penghuni" class="room__tenant"><AppIcon name="user" :size="12" /> {{ room.penghuni.nama_lengkap }}</span>
            </span>
            <StatusBadge :tone="STATUS_TONE[room.status_ketersediaan] ?? 'neutral'">{{ room.status_ketersediaan }}</StatusBadge>
          </button>
        </section>
      </StateBlock>
    </div>

    <BottomSheet v-model:open="sheetOpen" :title="editing ? `Ubah kamar ${editing.nomor_kamar}` : 'Tambah kamar'">
      <form class="form-stack" novalidate @submit.prevent="save">
        <div class="row">
          <label>
            <span class="field-label">Nomor kamar <span class="req">*</span></span>
            <input v-model="form.nomor_kamar" type="text" class="input" :class="{ 'is-invalid': errors.nomor }" maxlength="10" placeholder="A01">
            <span v-if="errors.nomor" class="field-error">{{ errors.nomor }}</span>
          </label>
          <label>
            <span class="field-label">Lantai</span>
            <input v-model.number="form.lantai" type="number" min="0" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.lantai }">
            <span v-if="errors.lantai" class="field-error">{{ errors.lantai }}</span>
          </label>
        </div>
        <label>
          <span class="field-label">Tipe</span>
          <input v-model="form.tipe" type="text" class="input" maxlength="40" placeholder="Standar / Kamar mandi dalam / AC" list="tipe-kamar">
          <datalist id="tipe-kamar">
            <option value="Standar" />
            <option value="Kamar mandi dalam" />
            <option value="AC" />
            <option value="Deluxe" />
          </datalist>
        </label>
        <label>
          <span class="field-label">Harga sewa per bulan (Rp) <span class="req">*</span></span>
          <input v-model.number="form.harga_dasar" type="number" min="0" step="1000" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.harga }" placeholder="950000">
          <span v-if="errors.harga" class="field-error">{{ errors.harga }}</span>
        </label>
        <label>
          <span class="field-label">Status</span>
          <select v-model="form.status_ketersediaan" class="select">
            <option v-for="s in STATUS" :key="s" :value="s">{{ s }}</option>
          </select>
          <span v-if="editing?.penghuni" class="hint">Dihuni oleh {{ editing.penghuni.nama_lengkap }}. Status sewa diatur dari menu Penghuni.</span>
        </label>
        <div class="form-actions">
          <button v-if="editing" type="button" class="button button--danger-outline" :disabled="saving" @click="remove">
            <AppIcon name="trash" :size="16" /> Hapus
          </button>
          <button v-else type="button" class="button button--outline" @click="sheetOpen = false">Batal</button>
          <button type="submit" class="button button--primary" :disabled="saving">{{ saving ? 'Menyimpan…' : 'Simpan' }}</button>
        </div>
      </form>
    </BottomSheet>
  </div>
</template>

<style scoped>
.floor {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
}

.room {
  display: flex;
  align-items: center;
  gap: 14px;
}

.room__no {
  min-width: 54px;
  font-family: var(--font-editorial);
  font-size: 24px;
  color: var(--maroon);
}

.room__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.room__type {
  font-size: 12px;
  color: var(--slate);
}

.room__price {
  font-size: 15px;
  font-weight: 600;
}

.room__price small {
  margin-left: 2px;
  font-size: 11px;
  font-weight: 400;
  color: var(--slate);
}

.room__tenant {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  overflow: hidden;
  font-size: 12px;
  color: var(--slate);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 10px;
}

.hint {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--slate);
}
</style>
