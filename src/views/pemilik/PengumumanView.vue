<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { pengumumanApi, penghuniApi } from '@/services/endpoints'
import { useResource } from '@/composables/useResource'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const ui = useUiStore()
const { data, loading, error, reload } = useResource(() => pengumumanApi.list(), { initial: [] })
const items = computed(() => data.value ?? [])

// Jumlah penerima: dari arsip (total_penghuni) atau hitung penghuni aktif.
const activeCount = ref(null)
onMounted(() => {
  penghuniApi
    .list()
    .then((rows) => (activeCount.value = rows.filter((r) => r.sewa && r.sewa.status_sewa !== 'Sudah Keluar').length))
    .catch(() => {})
})
const recipients = computed(() => activeCount.value ?? items.value[0]?.total_penghuni ?? null)

// ---------- Form ----------
const form = reactive({ judul: '', isi: '', disematkan: false })
const errors = reactive({ judul: '', isi: '' })
const sending = ref(false)

async function send() {
  errors.judul = form.judul.trim() ? '' : 'Judul wajib diisi.'
  errors.isi = form.isi.trim() ? '' : 'Isi pengumuman wajib diisi.'
  if (errors.judul || errors.isi || sending.value) return
  sending.value = true
  try {
    await pengumumanApi.create({ judul: form.judul.trim(), isi_pengumuman: form.isi.trim(), disematkan: form.disematkan })
    Object.assign(form, { judul: '', isi: '', disematkan: false })
    ui.showToast('Pengumuman terkirim ke penghuni.', 'success')
    reload()
  } catch (err) {
    ui.showError(err, 'Pengumuman Gagal Dikirim')
  } finally {
    sending.value = false
  }
}

// ---------- Aksi arsip ----------
const busyId = ref(null)

async function togglePin(item) {
  if (busyId.value) return
  busyId.value = item.id
  try {
    await pengumumanApi.update(item.id, { disematkan: !item.disematkan })
    ui.showToast(item.disematkan ? 'Pengumuman dilepas dari beranda.' : 'Pengumuman disematkan di beranda.', 'success')
    await reload()
  } catch (err) {
    ui.showError(err, 'Gagal Mengubah Pengumuman')
  } finally {
    busyId.value = null
  }
}

async function remove(item) {
  if (busyId.value) return
  const ok = await ui.confirm('Hapus pengumuman?', `“${item.judul}” akan dihapus untuk semua penghuni. Tindakan ini tidak dapat dibatalkan.`, {
    confirmLabel: 'Hapus',
    tone: 'danger',
  })
  if (!ok) return
  busyId.value = item.id
  try {
    await pengumumanApi.remove(item.id)
    data.value = items.value.filter((i) => i.id !== item.id)
    ui.showToast('Pengumuman dihapus.', 'success')
  } catch (err) {
    ui.showError(err, 'Gagal Menghapus Pengumuman')
  } finally {
    busyId.value = null
  }
}
</script>

<template>
  <div>
    <AppHeader :back="{ name: 'pemilik-lainnya' }" title="Pengumuman" />

    <div class="app-page app-page--plain">
      <form class="panel form-stack" novalidate @submit.prevent="send">
        <div>
          <h2 class="panel-title">Buat pengumuman</h2>
          <p class="panel-desc">{{ recipients !== null ? `Dikirim ke ${recipients} penghuni aktif` : 'Dikirim ke semua penghuni aktif' }}</p>
        </div>
        <label>
          <span class="field-label">Judul <span class="req">*</span></span>
          <input v-model="form.judul" type="text" class="input" :class="{ 'is-invalid': errors.judul }" maxlength="120" placeholder="Contoh: Pemadaman air Sabtu pagi" @input="errors.judul = ''">
          <span v-if="errors.judul" class="field-error">{{ errors.judul }}</span>
        </label>
        <label>
          <span class="field-label">Isi pengumuman <span class="req">*</span></span>
          <textarea v-model="form.isi" class="textarea" :class="{ 'is-invalid': errors.isi }" maxlength="2000" placeholder="Tulis informasi untuk penghuni..." @input="errors.isi = ''" />
          <span v-if="errors.isi" class="field-error">{{ errors.isi }}</span>
        </label>
        <label class="checkbox">
          <input v-model="form.disematkan" type="checkbox">
          <span>Sematkan di beranda penghuni</span>
        </label>
        <button type="submit" class="button button--primary button--block" :disabled="sending">
          <AppIcon name="send" :size="16" /> {{ sending ? 'Mengirim…' : 'Kirim Pengumuman' }}
        </button>
      </form>

      <h2 class="section-label archive-label">Arsip pengumuman</h2>
      <StateBlock
        :loading="loading"
        :error="error"
        :has-data="items.length > 0"
        :empty="!items.length"
        empty-icon="bell"
        empty-title="Belum ada pengumuman"
        empty-text="Pengumuman yang Anda kirim akan tersimpan di sini."
        @retry="reload"
      >
        <div class="list">
          <article v-for="item in items" :key="item.id" class="list-card ann" :class="{ 'is-pinned': item.disematkan }">
            <div class="list-card__head">
              <span class="list-card__meta">{{ formatDate(item.created_at) }}</span>
              <StatusBadge :tone="item.disematkan ? 'info' : 'neutral'">{{ item.disematkan ? 'Disematkan' : 'Umum' }}</StatusBadge>
            </div>
            <h3 class="ann__title">{{ item.judul }}</h3>
            <p class="ann__body">{{ item.isi_pengumuman }}</p>
            <div class="ann__foot">
              <span class="list-card__meta">Dibaca {{ item.dibaca_count }}/{{ item.total_penghuni }} penghuni</span>
              <div class="ann__actions">
                <button type="button" class="icon-btn" :disabled="busyId === item.id" :aria-label="item.disematkan ? 'Lepas sematan' : 'Sematkan'" @click="togglePin(item)">
                  <AppIcon name="pin" :size="16" /> {{ item.disematkan ? 'Lepas' : 'Sematkan' }}
                </button>
                <button type="button" class="icon-btn icon-btn--danger" :disabled="busyId === item.id" aria-label="Hapus pengumuman" @click="remove(item)">
                  <AppIcon name="trash" :size="16" />
                </button>
              </div>
            </div>
          </article>
        </div>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.archive-label {
  margin-top: 8px;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ann.is-pinned {
  border-color: var(--maroon);
}

.ann__title {
  margin-top: 8px;
  font-family: var(--font-editorial);
  font-size: 20px;
  font-weight: 400;
  line-height: 1.25;
}

.ann__body {
  margin-top: 6px;
  font-size: 14px;
  line-height: 1.55;
  color: var(--ink);
  white-space: pre-line;
}

.ann__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}

.ann__actions {
  display: flex;
  gap: 6px;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 7px 10px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
}

.icon-btn--danger {
  color: var(--crimson);
}

.icon-btn:disabled {
  opacity: 0.5;
}
</style>
