<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { profilKosApi, tagihanApi } from '@/services/endpoints'
import { fileUrl } from '@/services/config'
import { useResource } from '@/composables/useResource'
import { useUiStore } from '@/stores/ui'
import { formatDate, formatDateTime, formatRupiah, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import PhotoPicker from '@/components/app/PhotoPicker.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

const route = useRoute()
const ui = useUiStore()

const { data: bill, loading, error, reload } = useResource(() => tagihanApi.detail(route.params.id))
// Info rekening tidak wajib: jika gagal dimuat, rincian tagihan tetap tampil.
const { data: profil } = useResource(() => profilKosApi.get().catch(() => null))

watch(() => route.params.id, (id) => id && reload())

const status = computed(() => bill.value?.status_tagihan)
const canUpload = computed(() => ['Belum Bayar', 'Ditolak'].includes(status.value))
const hasBank = computed(() => Boolean(profil.value?.bank_nomor_rekening))

const proof = ref(null)
const submitting = ref(false)
const accountInput = ref(null)

function isPdf(path) {
  return /\.pdf($|\?)/i.test(path ?? '')
}

async function copyAccount() {
  const number = profil.value?.bank_nomor_rekening
  if (!number) return
  try {
    await navigator.clipboard.writeText(number)
    ui.showToast('Nomor rekening disalin', 'success')
  } catch {
    // Cadangan: pilih teks agar bisa disalin manual
    const input = accountInput.value
    if (input) {
      input.focus()
      input.select()
      const ok = document.execCommand?.('copy')
      ui.showToast(ok ? 'Nomor rekening disalin' : 'Tekan lama nomor rekening untuk menyalin', ok ? 'success' : 'info')
    }
  }
}

async function submitProof() {
  if (!proof.value || submitting.value) return
  submitting.value = true
  try {
    await tagihanApi.uploadProof(bill.value.id, proof.value)
    proof.value = null
    ui.showToast('Bukti transfer terkirim. Menunggu verifikasi pemilik.', 'success')
    await reload()
  } catch (err) {
    ui.showError(err, 'Bukti Gagal Dikirim')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader :back="{ name: 'penghuni-tagihan' }" title="Rincian tagihan" />

    <div class="app-page app-page--plain">
      <StateBlock :loading="loading" :error="error" :has-data="Boolean(bill)" @retry="reload">
        <template v-if="bill">
          <section class="panel">
            <div class="detail__head">
              <p class="section-label">Tagihan {{ bill.periode_label }}</p>
              <StatusBadge :tone="statusTone(bill.status_tagihan)">{{ bill.status_tagihan }}</StatusBadge>
            </div>
            <p class="detail__amount">{{ formatRupiah(bill.jumlah_tagihan) }}</p>
            <p v-if="bill.kamar" class="detail__room">Kamar {{ bill.kamar }}</p>

            <dl class="detail-list detail__list">
              <div v-for="item in bill.komponen" :key="item.nama" class="detail-row">
                <dt>{{ item.nama }}</dt>
                <dd>{{ item.jumlah ? formatRupiah(item.jumlah) : 'Gratis' }}</dd>
              </div>
              <div class="detail-row detail-row--total">
                <dt>Total</dt>
                <dd>{{ formatRupiah(bill.jumlah_tagihan) }}</dd>
              </div>
              <div class="detail-row">
                <dt>Jatuh tempo</dt>
                <dd>{{ formatDate(bill.jatuh_tempo) }}</dd>
              </div>
              <div class="detail-row">
                <dt>Batas masa tenggang</dt>
                <dd>{{ formatDate(bill.batas_tenggang) }}</dd>
              </div>
            </dl>
          </section>

          <!-- Lunas -->
          <section v-if="status === 'Lunas'" class="note note--success">
            <AppIcon name="shield-check" :size="20" />
            <div>
              <p class="note__title">Pembayaran disetujui</p>
              <p>
                {{ bill.diverifikasi_at ? `Diverifikasi ${formatDateTime(bill.diverifikasi_at)}.` : 'Tagihan ini sudah lunas.' }}
                Masa sewa Anda telah diperpanjang.
              </p>
            </div>
          </section>

          <!-- Menunggu verifikasi -->
          <section v-else-if="status === 'Menunggu Verifikasi'" class="panel detail__waiting">
            <p class="section-label">Bukti transfer</p>
            <p class="detail__waiting-text">Bukti sedang diperiksa pemilik.</p>
            <p v-if="bill.tanggal_unggah" class="detail__muted">Diunggah {{ formatDateTime(bill.tanggal_unggah) }}</p>
            <a
              v-if="bill.bukti_bayar_url"
              :href="fileUrl(bill.bukti_bayar_url)"
              target="_blank"
              rel="noopener"
              class="detail__proof"
            >
              <span v-if="isPdf(bill.bukti_bayar_url)" class="detail__proof-pdf">PDF · Lihat bukti</span>
              <img v-else :src="fileUrl(bill.bukti_bayar_url)" alt="Bukti transfer yang diunggah">
            </a>
          </section>

          <!-- Rekening tujuan -->
          <section v-if="canUpload || status === 'Menunggu Verifikasi'" class="bank" aria-label="Rekening tujuan">
            <p class="section-label">Transfer ke</p>
            <template v-if="hasBank">
              <p class="bank__name">{{ profil.bank_nama }}</p>
              <input
                ref="accountInput"
                class="bank__number"
                :value="profil.bank_nomor_rekening"
                readonly
                aria-label="Nomor rekening"
              >
              <p v-if="profil.bank_atas_nama" class="bank__holder">a.n. {{ profil.bank_atas_nama }}</p>
              <button type="button" class="button button--outline button--sm bank__copy" @click="copyAccount">
                <AppIcon name="copy" :size="14" /> Salin nomor rekening
              </button>
            </template>
            <p v-else class="bank__holder">Info rekening belum diatur pemilik. Tanyakan langsung ke pemilik kos.</p>
          </section>

          <!-- Unggah bukti -->
          <section v-if="canUpload" class="panel form-stack" aria-labelledby="upload-title">
            <div v-if="status === 'Ditolak'" class="note note--danger">
              <AppIcon name="alert-circle" :size="20" />
              <div>
                <p class="note__title">Bukti sebelumnya ditolak</p>
                <p>{{ bill.alasan_tolak || 'Silakan unggah ulang bukti transfer yang jelas.' }}</p>
              </div>
            </div>
            <div>
              <h2 id="upload-title" class="panel-title detail__upload-title">Unggah bukti transfer</h2>
              <p class="panel-desc">Foto atau tangkapan layar struk transfer. Pastikan nominal dan tanggal terlihat jelas.</p>
            </div>
            <PhotoPicker v-model="proof" accept="image/*,application/pdf" label="Pilih file" />
            <button
              type="button"
              class="button button--primary button--block"
              :disabled="!proof || submitting"
              @click="submitProof"
            >
              <AppIcon name="upload" :size="16" /> {{ submitting ? 'Mengirim…' : 'Kirim Bukti' }}
            </button>
          </section>
        </template>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.detail__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.detail__amount {
  margin-top: 10px;
  font-family: var(--font-editorial);
  font-size: 38px;
  line-height: 1.1;
}

.detail__room {
  margin-top: 4px;
  font-size: 13px;
  color: var(--slate);
}

.detail__list {
  margin-top: 14px;
}

.bank {
  padding: 20px;
  background: var(--mist);
  border-radius: var(--radius-card);
}

.bank__name {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 600;
}

.bank__number {
  width: 100%;
  margin-top: 2px;
  padding: 0;
  border: 0;
  background: transparent;
  font-family: var(--font-editorial);
  font-size: 26px;
  letter-spacing: 0.03em;
  color: var(--ink);
}

.bank__number:focus {
  outline: none;
}

.bank__holder {
  margin-top: 2px;
  font-size: 13px;
  color: var(--slate);
}

.bank__copy {
  margin-top: 14px;
}

.detail__upload-title {
  font-size: 22px;
}

.detail__waiting-text {
  margin-top: 8px;
  font-family: var(--font-editorial);
  font-size: 20px;
}

.detail__muted {
  margin-top: 2px;
  font-size: 12px;
  color: var(--slate);
}

.detail__proof {
  display: block;
  width: 140px;
  margin-top: 14px;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 16px;
}

.detail__proof img {
  display: block;
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
}

.detail__proof-pdf {
  display: block;
  padding: 24px 12px;
  background: var(--mist);
  font-size: 13px;
  font-weight: 700;
  color: var(--crimson);
  text-align: center;
}

.note {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  font-size: 13px;
  line-height: 1.5;
}

.note > svg {
  flex-shrink: 0;
  margin-top: 1px;
}

.note__title {
  font-weight: 700;
}

.note--danger {
  background: var(--status-danger-bg);
  color: var(--status-danger-text);
}

.note--success {
  background: var(--status-success-bg);
  color: var(--status-success-text);
}
</style>
