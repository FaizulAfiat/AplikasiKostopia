<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { barangHilangApi } from '@/services/endpoints'
import { fileUrl } from '@/services/config'
import { formatShortDate } from '@/utils/format'
import StatusBadge from '@/components/StatusBadge.vue'

const props = defineProps({
  /** BarangHilangOut dari API */
  report: { type: Object, required: true },
})

const emit = defineEmits(['resolved'])

const auth = useAuthStore()
const ui = useUiStore()

const isMine = computed(() => auth.user?.id === props.report.pelapor?.id)
const isActive = computed(() => props.report.status_barang === 'Aktif')
const isLost = computed(() => props.report.jenis === 'Hilang')

const reporterLabel = computed(() => {
  const pelapor = props.report.pelapor ?? {}
  if (isMine.value) return auth.isOwner ? 'Anda (Pemilik)' : 'Anda'
  if (pelapor.peran === 'Pemilik') return `${pelapor.nama_lengkap} · Pemilik`
  return [pelapor.nama_lengkap, pelapor.kamar].filter(Boolean).join(' · ')
})

const resolving = ref(false)

// UC-15 langkah 7–8: pelapor menandai Selesai → laporan pindah dari daftar aktif
async function resolve() {
  const ok = await ui.confirm(
    'Tandai laporan selesai?',
    isLost.value
      ? 'Pastikan barang sudah ketemu dan sudah Anda ambil.'
      : 'Pastikan barang sudah diambil oleh pemiliknya.',
    { confirmLabel: 'Tandai Selesai' },
  )
  if (!ok) return

  resolving.value = true
  try {
    const updated = await barangHilangApi.markDone(props.report.id)
    ui.showToast('Laporan ditandai Selesai dan dipindahkan dari daftar aktif.', 'success')
    emit('resolved', updated)
  } catch (error) {
    ui.showError(error, 'Gagal Memperbarui')
  } finally {
    resolving.value = false
  }
}
</script>

<template>
  <article class="lf-card" :class="{ 'lf-card--done': !isActive }">
    <div class="lf-card__photo">
      <img v-if="report.foto_url" :src="fileUrl(report.foto_url)" :alt="`Foto ${report.judul_barang}`" loading="lazy">
      <span v-else>Foto barang</span>
    </div>

    <div class="lf-card__body">
      <div class="lf-card__meta">
        <div class="lf-card__badges">
          <StatusBadge :tone="isLost ? 'danger' : 'success'">{{ isLost ? 'Hilang' : 'Ditemukan' }}</StatusBadge>
          <StatusBadge v-if="!isActive" tone="neutral">Selesai</StatusBadge>
        </div>
        <time :datetime="report.created_at">{{ formatShortDate(report.created_at) }}</time>
      </div>

      <h3 class="lf-card__title">{{ report.judul_barang }}</h3>
      <p v-if="report.deskripsi" class="lf-card__desc">{{ report.deskripsi }}</p>
      <p class="lf-card__where">{{ [report.lokasi, reporterLabel].filter(Boolean).join(' · ') }}</p>

      <div v-if="isActive && isMine" class="lf-card__resolve">
        <p>{{ isLost ? 'Barang sudah ketemu dan diambil?' : 'Barang sudah diambil oleh pemiliknya?' }}</p>
        <button type="button" class="button button--outline button--sm" :disabled="resolving" @click="resolve">
          {{ resolving ? 'Menyimpan…' : 'Tandai Selesai' }}
        </button>
      </div>

      <p v-else-if="!isActive && report.selesai_at" class="lf-card__resolved">
        Ditandai selesai {{ formatShortDate(report.selesai_at) }}
      </p>
    </div>
  </article>
</template>

<style scoped>
.lf-card {
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 22px;
}

.lf-card__photo {
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: repeating-linear-gradient(135deg, #f3efee 0 14px, #ebe4e3 14px 28px);
  font-size: 12px;
  color: var(--slate);
}

.lf-card__photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lf-card--done .lf-card__photo {
  opacity: 0.6;
}

.lf-card__body {
  padding: 14px 16px 16px;
}

.lf-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: var(--slate);
}

.lf-card__badges {
  display: flex;
  gap: 6px;
}

.lf-card__title {
  margin-top: 10px;
  font-size: 16px;
  font-weight: 600;
}

.lf-card__desc {
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.5;
}

.lf-card__where {
  margin-top: 6px;
  font-size: 12px;
  color: var(--slate);
}

.lf-card__resolve,
.lf-card__resolved {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  font-size: 12px;
}

.lf-card__resolve {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--slate);
}

.lf-card__resolved {
  color: var(--status-success-text);
}
</style>
