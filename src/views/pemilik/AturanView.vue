<script setup>
import { computed, reactive, ref } from 'vue'
import { aturanApi } from '@/services/endpoints'
import { useResource } from '@/composables/useResource'
import { useUiStore } from '@/stores/ui'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import BottomSheet from '@/components/app/BottomSheet.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const ui = useUiStore()
const { data, loading, error, reload } = useResource(() => aturanApi.list(), { initial: [] })
const rules = computed(() => [...(data.value ?? [])].sort((a, b) => a.urutan - b.urutan))
const activeCount = computed(() => rules.value.filter((r) => r.status_aktif).length)

const number = (index) => String(index + 1).padStart(2, '0')
const sanctionTone = (s) => (/denda|keluar|sp/i.test(s ?? '') ? 'danger' : 'warning')

// ---------- Toggle aktif ----------
const togglingId = ref(null)

async function toggle(rule) {
  if (togglingId.value) return
  togglingId.value = rule.id
  try {
    const updated = await aturanApi.update(rule.id, { status_aktif: !rule.status_aktif })
    data.value = data.value.map((r) => (r.id === rule.id ? { ...r, ...(updated ?? { status_aktif: !rule.status_aktif }) } : r))
    ui.showToast(rule.status_aktif ? 'Aturan dinonaktifkan.' : 'Aturan diaktifkan.', 'success')
  } catch (err) {
    ui.showError(err, 'Gagal Mengubah Aturan')
  } finally {
    togglingId.value = null
  }
}

// ---------- Form tambah / ubah ----------
const sheetOpen = ref(false)
const editing = ref(null)
const form = reactive({ judul: '', deskripsi: '', sanksi: '', status_aktif: true })
const judulError = ref('')
const saving = ref(false)
const SANKSI_PRESETS = ['Teguran', 'Teguran tertulis', 'Denda Rp 50.000', 'Denda Rp 100.000']

function openForm(rule = null) {
  editing.value = rule
  Object.assign(form, {
    judul: rule?.judul ?? '',
    deskripsi: rule?.deskripsi ?? '',
    sanksi: rule?.sanksi ?? '',
    status_aktif: rule?.status_aktif ?? true,
  })
  judulError.value = ''
  sheetOpen.value = true
}

async function save() {
  judulError.value = form.judul.trim() ? '' : 'Judul aturan wajib diisi.'
  if (judulError.value || saving.value) return
  saving.value = true
  const body = {
    judul: form.judul.trim(),
    deskripsi: form.deskripsi.trim() || null,
    sanksi: form.sanksi.trim() || null,
    status_aktif: form.status_aktif,
  }
  try {
    if (editing.value) await aturanApi.update(editing.value.id, body)
    else await aturanApi.create(body)
    sheetOpen.value = false
    ui.showToast(editing.value ? 'Aturan diperbarui.' : 'Aturan ditambahkan.', 'success')
    reload()
  } catch (err) {
    ui.showError(err, 'Gagal Menyimpan Aturan')
  } finally {
    saving.value = false
  }
}

async function remove() {
  const rule = editing.value
  if (!rule) return
  const ok = await ui.confirm('Hapus aturan?', `“${rule.judul}” akan dihapus dari daftar aturan kos.`, { confirmLabel: 'Hapus', tone: 'danger' })
  if (!ok) return
  saving.value = true
  try {
    await aturanApi.remove(rule.id)
    sheetOpen.value = false
    data.value = data.value.filter((r) => r.id !== rule.id)
    ui.showToast('Aturan dihapus.', 'success')
  } catch (err) {
    ui.showError(err, 'Gagal Menghapus Aturan')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader :back="{ name: 'pemilik-lainnya' }" title="Aturan Kos" :subtitle="rules.length ? `${activeCount} dari ${rules.length} aturan aktif` : ''">
      <template #actions>
        <button type="button" class="button button--primary button--sm" @click="openForm()">
          <AppIcon name="plus" :size="14" /> Tambah
        </button>
      </template>
    </AppHeader>

    <div class="app-page app-page--plain">
      <StateBlock
        :loading="loading"
        :error="error"
        :has-data="rules.length > 0"
        :empty="!rules.length"
        empty-icon="book"
        empty-title="Belum ada aturan"
        empty-text="Tulis tata tertib kos agar penghuni tahu hak & kewajibannya."
        @retry="reload"
      >
        <template #empty-action>
          <button type="button" class="button button--primary button--sm" @click="openForm()">Tambah aturan</button>
        </template>

        <ol class="rules">
          <li v-for="(rule, index) in rules" :key="rule.id" class="rule" :class="{ 'is-off': !rule.status_aktif }">
            <span class="rule__no">{{ number(index) }}</span>
            <button type="button" class="rule__body" @click="openForm(rule)">
              <span class="rule__title">{{ rule.judul }}</span>
              <span v-if="rule.deskripsi" class="rule__desc">{{ rule.deskripsi }}</span>
              <span class="rule__tags">
                <StatusBadge v-if="rule.sanksi" :tone="sanctionTone(rule.sanksi)">Sanksi: {{ rule.sanksi }}</StatusBadge>
                <StatusBadge v-if="!rule.status_aktif" tone="neutral">Nonaktif</StatusBadge>
              </span>
            </button>
            <label class="switch" :title="rule.status_aktif ? 'Nonaktifkan' : 'Aktifkan'">
              <input type="checkbox" :checked="rule.status_aktif" :disabled="togglingId === rule.id" :aria-label="`Aturan ${rule.judul} aktif`" @click.prevent="toggle(rule)">
              <span class="switch__track" />
            </label>
          </li>
        </ol>
      </StateBlock>
    </div>

    <BottomSheet v-model:open="sheetOpen" :title="editing ? 'Ubah aturan' : 'Tambah aturan'">
      <form class="form-stack" novalidate @submit.prevent="save">
        <label>
          <span class="field-label">Judul aturan <span class="req">*</span></span>
          <input v-model="form.judul" type="text" class="input" :class="{ 'is-invalid': judulError }" maxlength="120" placeholder="Contoh: Jam malam pukul 22.00" @input="judulError = ''">
          <span v-if="judulError" class="field-error">{{ judulError }}</span>
        </label>
        <label>
          <span class="field-label">Deskripsi</span>
          <textarea v-model="form.deskripsi" class="textarea" maxlength="500" placeholder="Penjelasan aturan..." />
        </label>
        <div>
          <label for="rule-sanksi" class="field-label">Sanksi</label>
          <input id="rule-sanksi" v-model="form.sanksi" type="text" class="input" maxlength="80" placeholder="Contoh: Denda Rp 50.000">
          <div class="presets">
            <button v-for="p in SANKSI_PRESETS" :key="p" type="button" class="pill" :class="{ 'is-active': form.sanksi === p }" @click="form.sanksi = p">{{ p }}</button>
          </div>
        </div>
        <label class="checkbox">
          <input v-model="form.status_aktif" type="checkbox">
          <span>Aturan aktif (tampil untuk penghuni)</span>
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
.rules {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.rule {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 20px;
}

.rule.is-off {
  background: var(--fog);
}

.rule.is-off .rule__no,
.rule.is-off .rule__title {
  color: var(--slate);
}

.rule__no {
  min-width: 32px;
  font-family: var(--font-editorial);
  font-size: 26px;
  line-height: 1;
  color: var(--crimson);
}

.rule__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0;
  border: 0;
  background: none;
  text-align: left;
}

.rule__title {
  font-size: 15px;
  font-weight: 600;
}

.rule__desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--slate);
}

.rule__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.switch {
  position: relative;
  flex-shrink: 0;
  width: 44px;
  height: 26px;
  cursor: pointer;
}

.switch input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.switch__track {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: #d9cfcc;
  transition: background-color 0.2s ease;
  pointer-events: none;
}

.switch__track::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}

.switch input:checked + .switch__track {
  background: var(--maroon);
}

.switch input:checked + .switch__track::after {
  transform: translateX(18px);
}

.switch input:focus-visible + .switch__track {
  outline: 2px solid var(--crimson);
  outline-offset: 2px;
}

.presets {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.presets .pill {
  padding: 5px 12px;
  font-size: 12px;
}
</style>
