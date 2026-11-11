<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/services/api'
import { aspirasiApi } from '@/services/endpoints'
import { fileUrl } from '@/services/config'
import { useUiStore } from '@/stores/ui'
import { formatDateTime, formatRelative, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()
const backRoute = { name: 'pemilik-layanan', query: { tab: 'aspirasi' } }

const item = ref(null)
const loading = ref(false)
const error = ref(null)
const form = reactive({ status: 'Menunggu', tanggapan: '' })
const saving = ref(false)

// Tidak ada GET /aspirasi/{id} → ambil daftar lalu cari berdasarkan id.
async function load() {
  loading.value = true
  error.value = null
  try {
    const list = await aspirasiApi.list()
    const found = list.find((a) => String(a.id) === String(route.params.id))
    if (!found) throw new ApiError('Aspirasi tidak ditemukan atau sudah dihapus.', 404)
    item.value = found
    form.status = found.status_penanganan
    form.tanggapan = found.tanggapan_pemilik ?? ''
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

onMounted(load)

const STATUS = ['Menunggu', 'Sedang Diproses', 'Selesai']
const photos = computed(() => item.value?.lampiran_foto_urls ?? [])
const unchanged = computed(
  () => item.value && form.status === item.value.status_penanganan && form.tanggapan.trim() === (item.value.tanggapan_pemilik ?? ''),
)

async function save() {
  if (saving.value || unchanged.value) return
  saving.value = true
  try {
    const updated = await aspirasiApi.update(item.value.id, {
      status_penanganan: form.status,
      tanggapan_pemilik: form.tanggapan.trim() || null,
    })
    item.value = { ...item.value, ...(updated ?? {}) }
    ui.showToast('Tanggapan terkirim ke penghuni.', 'success')
    router.replace(backRoute)
  } catch (err) {
    ui.showError(err, 'Gagal Menyimpan Tanggapan')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader :back="backRoute" title="Detail Aspirasi" />

    <div class="app-page app-page--plain">
      <StateBlock :loading="loading" :error="error" :has-data="!!item" @retry="load">
        <template v-if="item">
          <section class="panel">
            <div class="head">
              <p class="eyebrow">Tiket #{{ item.id }} · {{ item.kategori }}</p>
              <StatusBadge :tone="statusTone(item.status_penanganan)">{{ item.status_penanganan }}</StatusBadge>
            </div>
            <h2 class="title">{{ item.judul }}</h2>
            <div class="reporter">
              <UserAvatar :name="item.pelapor?.nama_lengkap" :size="36" />
              <div>
                <p class="reporter__name">{{ item.pelapor?.nama_lengkap ?? '—' }}</p>
                <p class="reporter__meta">
                  <template v-if="item.pelapor?.kamar">Kamar {{ item.pelapor.kamar }} · </template>{{ formatRelative(item.created_at) }}
                </p>
              </div>
            </div>
            <p class="desc">{{ item.deskripsi_kendala }}</p>

            <div v-if="photos.length" class="photos">
              <a v-for="path in photos" :key="path" :href="fileUrl(path)" target="_blank" rel="noopener" class="photo">
                <img :src="fileUrl(path)" alt="Lampiran aspirasi">
              </a>
            </div>
            <p class="stamp">Dibuat {{ formatDateTime(item.created_at) }}<template v-if="item.updated_at && item.updated_at !== item.created_at"> · Diperbarui {{ formatDateTime(item.updated_at) }}</template></p>
          </section>

          <form class="panel form-stack" @submit.prevent="save">
            <h3 class="panel-title">Tindak lanjut</h3>
            <label>
              <span class="field-label">Status penanganan</span>
              <select v-model="form.status" class="select">
                <option v-for="s in STATUS" :key="s" :value="s">{{ s }}</option>
              </select>
            </label>
            <label>
              <span class="field-label">Tanggapan untuk penghuni</span>
              <textarea
                v-model="form.tanggapan"
                class="textarea"
                maxlength="1000"
                placeholder="Contoh: Teknisi akan datang besok pukul 10.00 untuk memperbaiki keran."
              />
            </label>
            <button type="submit" class="button button--dark button--block" :disabled="saving || unchanged">
              {{ saving ? 'Mengirim…' : 'Simpan & Kirim Tanggapan' }}
            </button>
          </form>
        </template>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.panel {
  padding: 20px;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.title {
  margin-top: 10px;
  font-family: var(--font-editorial);
  font-size: 26px;
  font-weight: 400;
  line-height: 1.2;
}

.reporter {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
}

.reporter__name {
  font-size: 14px;
  font-weight: 600;
}

.reporter__meta {
  font-size: 12px;
  color: var(--slate);
}

.desc {
  margin-top: 14px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-line;
}

.photos {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 14px;
}

.photo {
  aspect-ratio: 1;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 14px;
}

.photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stamp {
  margin-top: 14px;
  font-size: 11px;
  color: var(--slate);
}

.panel-title {
  font-size: 20px;
}
</style>
