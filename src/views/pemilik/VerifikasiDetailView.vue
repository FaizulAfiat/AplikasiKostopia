<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { tagihanApi } from '@/services/endpoints'
import { fileUrl } from '@/services/config'
import { useResource } from '@/composables/useResource'
import { useUiStore } from '@/stores/ui'
import { formatDate, formatDateTime, formatMonth, formatRupiah, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import BottomSheet from '@/components/app/BottomSheet.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()

const backRoute = { name: 'pemilik-keuangan' }
const { data: bill, loading, error, reload } = useResource(() => tagihanApi.detail(route.params.id))

const proofUrl = computed(() => fileUrl(bill.value?.bukti_bayar_url))
const proofIsPdf = computed(() => /\.pdf($|\?)/i.test(bill.value?.bukti_bayar_url ?? ''))
const canDecide = computed(() => bill.value?.status_tagihan === 'Menunggu Verifikasi')

const viewerOpen = ref(false)
const submitting = ref(false)

// ---------- Tolak ----------
const rejectOpen = ref(false)
const reason = ref('')
const reasonError = ref('')

function openReject() {
  reason.value = ''
  reasonError.value = ''
  rejectOpen.value = true
}

function goBack() {
  if (window.history.state?.back) router.back()
  else router.replace(backRoute)
}

async function reject() {
  reasonError.value = reason.value.trim() ? '' : 'Alasan penolakan wajib diisi.'
  if (reasonError.value || submitting.value) return
  submitting.value = true
  try {
    await tagihanApi.verify(bill.value.id, false, reason.value.trim())
    rejectOpen.value = false
    ui.showToast('Pembayaran ditolak. Penghuni akan diminta mengunggah ulang.', 'success')
    goBack()
  } catch (err) {
    ui.showError(err, 'Gagal Menolak Pembayaran')
  } finally {
    submitting.value = false
  }
}

// ---------- Setujui ----------
async function approve() {
  if (submitting.value) return
  const ok = await ui.confirm(
    'Setujui pembayaran?',
    `Tagihan ${bill.value.penghuni?.nama_lengkap ?? ''} sebesar ${formatRupiah(bill.value.jumlah_tagihan)} akan ditandai Lunas dan masa sewa diperpanjang 1 bulan.`,
    { confirmLabel: 'Setujui' },
  )
  if (!ok) return
  submitting.value = true
  try {
    await tagihanApi.verify(bill.value.id, true)
    ui.showToast('Pembayaran disetujui · tagihan Lunas.', 'success')
    goBack()
  } catch (err) {
    ui.showError(err, 'Gagal Menyetujui Pembayaran')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader :back="backRoute" title="Verifikasi Pembayaran" :subtitle="bill ? `Tagihan #${bill.id}` : ''" />

    <div class="app-page app-page--plain" :class="{ 'has-actions': canDecide }">
      <StateBlock :loading="loading" :error="error" :has-data="!!bill" @retry="reload">
        <template v-if="bill">
          <section class="panel tenant">
            <UserAvatar :name="bill.penghuni?.nama_lengkap" :size="48" tone="maroon" />
            <div class="tenant__body">
              <p class="tenant__name">{{ bill.penghuni?.nama_lengkap ?? '—' }}</p>
              <p class="tenant__meta">Kamar {{ bill.kamar ?? '—' }} · {{ bill.periode_label || formatMonth(bill.periode) }}</p>
            </div>
            <StatusBadge :tone="statusTone(bill.status_tagihan)">{{ bill.status_tagihan }}</StatusBadge>
          </section>

          <div v-if="bill.status_tagihan === 'Ditolak' && bill.alasan_tolak" class="reject-note" role="note">
            <AppIcon name="alert-circle" :size="18" />
            <div>
              <p class="reject-note__title">Alasan penolakan</p>
              <p>{{ bill.alasan_tolak }}</p>
            </div>
          </div>

          <section class="panel">
            <h2 class="panel-title">Bukti pembayaran</h2>
            <p v-if="!bill.bukti_bayar_url" class="muted">Penghuni belum mengunggah bukti pembayaran.</p>
            <a v-else-if="proofIsPdf" :href="proofUrl" target="_blank" rel="noopener" class="pdf-link">
              <AppIcon name="receipt" :size="22" />
              <span>Buka bukti (PDF)</span>
              <AppIcon name="chevron-right" :size="16" />
            </a>
            <button v-else type="button" class="proof" aria-label="Perbesar bukti pembayaran" @click="viewerOpen = true">
              <img :src="proofUrl" alt="Bukti pembayaran">
              <span class="proof__hint">Ketuk untuk memperbesar</span>
            </button>
          </section>

          <section class="panel">
            <h2 class="panel-title">Rincian tagihan</h2>
            <dl class="detail-list">
              <div class="detail-row"><dt>Periode</dt><dd>{{ bill.periode_label || formatMonth(bill.periode) }}</dd></div>
              <div v-for="(item, index) in bill.komponen" :key="index" class="detail-row">
                <dt>{{ item.nama }}</dt>
                <dd>{{ item.jumlah ? formatRupiah(item.jumlah) : 'Gratis' }}</dd>
              </div>
              <div class="detail-row detail-row--total"><dt>Total</dt><dd>{{ formatRupiah(bill.jumlah_tagihan) }}</dd></div>
              <div class="detail-row"><dt>Jatuh tempo</dt><dd>{{ formatDate(bill.jatuh_tempo) }}</dd></div>
              <div v-if="bill.batas_tenggang" class="detail-row"><dt>Batas tenggang</dt><dd>{{ formatDate(bill.batas_tenggang) }}</dd></div>
              <div class="detail-row"><dt>Tanggal unggah</dt><dd>{{ formatDateTime(bill.tanggal_unggah) }}</dd></div>
              <div v-if="bill.diverifikasi_at" class="detail-row"><dt>Diverifikasi</dt><dd>{{ formatDateTime(bill.diverifikasi_at) }}</dd></div>
            </dl>
          </section>
        </template>
      </StateBlock>
    </div>

    <div v-if="canDecide" class="decide-bar">
      <button type="button" class="button button--outline" :disabled="submitting" @click="openReject">Tolak</button>
      <button type="button" class="button button--dark" :disabled="submitting" @click="approve">
        <AppIcon name="check" :size="16" /> Setujui · tandai Lunas
      </button>
    </div>

    <BottomSheet v-model:open="rejectOpen" title="Tolak pembayaran" description="Alasan akan dikirim ke penghuni agar dapat mengunggah ulang bukti.">
      <form class="form-stack" novalidate @submit.prevent="reject">
        <label>
          <span class="field-label">Alasan penolakan <span class="req">*</span></span>
          <textarea
            v-model="reason"
            class="textarea"
            :class="{ 'is-invalid': reasonError }"
            maxlength="300"
            placeholder="Contoh: Nominal transfer tidak sesuai tagihan."
            @input="reasonError = ''"
          />
          <span v-if="reasonError" class="field-error" role="alert">{{ reasonError }}</span>
        </label>
        <div class="form-actions">
          <button type="button" class="button button--outline" @click="rejectOpen = false">Batal</button>
          <button type="submit" class="button button--primary" :disabled="submitting">{{ submitting ? 'Mengirim…' : 'Kirim Penolakan' }}</button>
        </div>
      </form>
    </BottomSheet>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="viewerOpen" class="viewer" role="dialog" aria-label="Bukti pembayaran" @click="viewerOpen = false">
          <img :src="proofUrl" alt="Bukti pembayaran ukuran penuh">
          <div class="viewer__bar">
            <a :href="proofUrl" target="_blank" rel="noopener" class="button button--outline button--sm" @click.stop>Buka di tab baru</a>
            <button type="button" class="button button--dark button--sm" @click="viewerOpen = false">Tutup</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.has-actions {
  padding-bottom: calc(110px + env(safe-area-inset-bottom));
}

.tenant {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px;
}

.tenant__body {
  flex: 1;
  min-width: 0;
}

.tenant__name {
  font-family: var(--font-editorial);
  font-size: 20px;
}

.tenant__meta {
  margin-top: 2px;
  font-size: 13px;
  color: var(--slate);
}

.reject-note {
  display: flex;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--status-danger-bg);
  color: var(--status-danger-text);
  font-size: 14px;
}

.reject-note__title {
  font-weight: 700;
}

.muted {
  margin-top: 10px;
  font-size: 13px;
  color: var(--slate);
}

.proof {
  position: relative;
  display: block;
  width: 100%;
  margin-top: 14px;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--mist);
}

.proof img {
  display: block;
  width: 100%;
  max-height: 360px;
  object-fit: contain;
}

.proof__hint {
  position: absolute;
  right: 10px;
  bottom: 10px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 11px;
}

.pdf-link {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 16px;
  background: var(--mist);
  font-weight: 600;
  color: var(--crimson);
}

.pdf-link span {
  flex: 1;
}

.decide-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  z-index: 30;
  width: min(var(--shell-width), 100%);
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 10px;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1px solid var(--border);
  transform: translateX(-50%);
}

.decide-bar .button {
  padding: 13px 10px;
}

.viewer {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px 12px;
  background: rgba(0, 0, 0, 0.88);
}

.viewer img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.viewer__bar {
  display: flex;
  gap: 10px;
}
</style>
