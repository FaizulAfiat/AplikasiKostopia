<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Capacitor } from '@capacitor/core'
import { keuanganApi, tagihanApi } from '@/services/endpoints'
import { useUiStore } from '@/stores/ui'
import { formatDate, formatMonth, formatRelative, formatRupiah, statusTone, todayISO } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import SegmentedTabs from '@/components/app/SegmentedTabs.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import BottomSheet from '@/components/app/BottomSheet.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()

// ---------- Tab ----------
const tab = ref(route.query.tab === 'laporan' ? 'laporan' : 'verifikasi')
const tabOptions = [
  { value: 'verifikasi', label: 'Verifikasi' },
  { value: 'laporan', label: 'Laporan' },
]

watch(
  () => route.query.tab,
  (value) => (tab.value = value === 'laporan' ? 'laporan' : 'verifikasi'),
)
watch(tab, (value) => {
  if ((route.query.tab ?? 'verifikasi') !== value) {
    router.replace({ query: { ...route.query, tab: value === 'verifikasi' ? undefined : value } })
  }
  if (value === 'laporan' && !report.loaded) loadReport()
})

// =========================================================
// Verifikasi
// =========================================================
const STATUSES = ['Menunggu Verifikasi', 'Lunas', 'Ditolak', 'Belum Bayar']

function periodeOf(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

const monthOptions = (() => {
  const now = new Date()
  return Array.from({ length: 6 }, (_, i) => {
    const value = periodeOf(new Date(now.getFullYear(), now.getMonth() - i, 1))
    return { value, label: formatMonth(value) }
  })
})()

/** Filter per penghuni (dari layar detail penghuni): ?penghuni=<id>&nama=<nama> */
const tenantId = computed(() => (route.query.penghuni ? Number(route.query.penghuni) : null))
const tenantName = computed(() => route.query.nama || 'penghuni ini')

const statusFilter = ref(tenantId.value ? '' : 'Menunggu Verifikasi')
const periode = ref(tenantId.value ? '' : monthOptions[0].value)

const bills = ref([])
const counts = ref({})
const billsLoading = ref(false)
const billsError = ref(null)
let billsReq = 0

async function loadBills() {
  const id = ++billsReq
  billsLoading.value = true
  billsError.value = null
  try {
    const [list, summary] = await Promise.all([
      tagihanApi.list({ status: statusFilter.value || undefined, periode: periode.value || undefined }),
      tagihanApi.statusSummary(periode.value || undefined).catch(() => null),
    ])
    if (id !== billsReq) return
    bills.value = tenantId.value ? list.filter((b) => b.penghuni?.id === tenantId.value) : list
    if (summary) counts.value = summary
  } catch (err) {
    if (id === billsReq) billsError.value = err
  } finally {
    if (id === billsReq) billsLoading.value = false
  }
}

watch([statusFilter, periode, tenantId], loadBills, { immediate: true })

const statusPills = computed(() => [
  ...(tenantId.value ? [{ value: '', label: 'Semua', count: null }] : []),
  ...STATUSES.map((s) => ({ value: s, label: s === 'Menunggu Verifikasi' ? 'Menunggu' : s, count: tenantId.value ? null : counts.value[s] ?? 0 })),
])

function clearTenant() {
  const { penghuni, nama, ...rest } = route.query
  router.replace({ query: rest })
  statusFilter.value = 'Menunggu Verifikasi'
  periode.value = monthOptions[0].value
}

function billMeta(bill) {
  const parts = [`Kamar ${bill.kamar ?? '—'}`, bill.periode_label || formatMonth(bill.periode)]
  if (bill.tanggal_unggah) parts.push(formatRelative(bill.tanggal_unggah))
  return parts.join(' · ')
}

// =========================================================
// Laporan
// =========================================================
function monthRange() {
  const now = new Date()
  const last = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  const pad = (n) => String(n).padStart(2, '0')
  return {
    dari: `${now.getFullYear()}-${pad(now.getMonth() + 1)}-01`,
    sampai: `${last.getFullYear()}-${pad(last.getMonth() + 1)}-${pad(last.getDate())}`,
  }
}

const range = reactive(monthRange())
const report = reactive({ summary: null, transactions: [], loading: false, error: null, loaded: false })
let reportReq = 0

const rangeInvalid = computed(() => range.dari && range.sampai && range.dari > range.sampai)

async function loadReport() {
  if (rangeInvalid.value || !range.dari || !range.sampai) return
  const id = ++reportReq
  report.loading = true
  report.error = null
  try {
    const [summary, transactions] = await Promise.all([
      keuanganApi.summary({ ...range }),
      keuanganApi.transactions({ ...range }),
    ])
    if (id !== reportReq) return
    report.summary = summary
    report.transactions = transactions
    report.loaded = true
  } catch (err) {
    if (id === reportReq) report.error = err
  } finally {
    if (id === reportReq) report.loading = false
  }
}

watch(() => [range.dari, range.sampai], () => tab.value === 'laporan' && loadReport())
if (tab.value === 'laporan') loadReport()

const KATEGORI_TONE = { Sewa: 'success', Tambahan: 'info', Pengeluaran: 'danger' }

// ---------- Catat pengeluaran ----------
const KATEGORI_PENGELUARAN = ['Listrik', 'Air', 'Kebersihan', 'Perbaikan', 'Gaji', 'Lainnya']
const expenseOpen = ref(false)
const expenseSaving = ref(false)
const expense = reactive({ tanggal: todayISO(), keterangan: '', kategori: 'Listrik', nominal: null })
const expenseErrors = reactive({ keterangan: '', nominal: '' })

function openExpense() {
  Object.assign(expense, { tanggal: todayISO(), keterangan: '', kategori: 'Listrik', nominal: null })
  Object.assign(expenseErrors, { keterangan: '', nominal: '' })
  expenseOpen.value = true
}

async function saveExpense() {
  expenseErrors.keterangan = expense.keterangan.trim() ? '' : 'Keterangan wajib diisi.'
  expenseErrors.nominal = Number(expense.nominal) > 0 ? '' : 'Nominal harus lebih dari 0.'
  if (expenseErrors.keterangan || expenseErrors.nominal || !expense.tanggal || expenseSaving.value) return

  expenseSaving.value = true
  try {
    await keuanganApi.addExpense({
      tanggal: expense.tanggal,
      keterangan: expense.keterangan.trim(),
      kategori: expense.kategori,
      nominal: Math.round(Number(expense.nominal)),
    })
    expenseOpen.value = false
    ui.showToast('Pengeluaran berhasil dicatat.', 'success')
    loadReport()
  } catch (err) {
    ui.showError(err, 'Gagal Mencatat Pengeluaran')
  } finally {
    expenseSaving.value = false
  }
}

// ---------- Unduh rekap ----------
const downloading = ref(false)

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result).split(',')[1] ?? '')
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(blob)
  })
}

async function downloadRecap() {
  if (downloading.value || rangeInvalid.value) return
  downloading.value = true
  const fileName = `rekap-keuangan_${range.dari}_${range.sampai}.xlsx`
  try {
    const blob = await keuanganApi.downloadRecap({ ...range })
    if (Capacitor.isNativePlatform()) {
      const [{ Filesystem, Directory }, { Share }] = await Promise.all([
        import('@capacitor/filesystem'),
        import('@capacitor/share'),
      ])
      const data = await blobToBase64(blob)
      const { uri } = await Filesystem.writeFile({ path: fileName, data, directory: Directory.Documents, recursive: true })
      ui.showToast('Rekap tersimpan di folder Documents.', 'success')
      try {
        await Share.share({ title: 'Rekap Keuangan Kostopia', url: uri })
      } catch {
        // pengguna menutup dialog bagikan
      }
    } else {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      link.remove()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
      ui.showToast('Rekap keuangan diunduh.', 'success')
    }
  } catch (err) {
    ui.showError(err, 'Gagal Mengunduh Rekap')
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader title="Keuangan" subtitle="Verifikasi pembayaran & laporan kas kos.">
      <SegmentedTabs v-model="tab" :options="tabOptions" label="Bagian keuangan" />
    </AppHeader>

    <!-- ================= Verifikasi ================= -->
    <div v-if="tab === 'verifikasi'" class="app-page">
      <div v-if="tenantId" class="tenant-chip">
        <span>Tagihan {{ tenantName }}</span>
        <button type="button" aria-label="Hapus filter penghuni" @click="clearTenant">
          <AppIcon name="close" :size="14" />
        </button>
      </div>

      <div class="pill-scroll" role="tablist" aria-label="Filter status tagihan">
        <button
          v-for="pill in statusPills"
          :key="pill.value"
          type="button"
          role="tab"
          class="pill"
          :class="{ 'is-active': statusFilter === pill.value }"
          :aria-selected="statusFilter === pill.value"
          @click="statusFilter = pill.value"
        >
          {{ pill.label }}<span v-if="pill.count !== null" class="pill__count">{{ pill.count }}</span>
        </button>
      </div>

      <label>
        <span class="sr-only">Periode tagihan</span>
        <select v-model="periode" class="select">
          <option v-if="tenantId" value="">Semua bulan</option>
          <option v-for="m in monthOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </label>

      <StateBlock
        :loading="billsLoading"
        :error="billsError"
        :empty="!bills.length"
        empty-icon="receipt"
        :empty-title="statusFilter === 'Menunggu Verifikasi' ? 'Tidak ada yang perlu diverifikasi' : 'Tidak ada tagihan'"
        empty-text="Tagihan dengan filter ini tidak ditemukan."
        @retry="loadBills"
      >
        <div class="card-list">
          <RouterLink
            v-for="bill in bills"
            :key="bill.id"
            :to="{ name: 'pemilik-tagihan-detail', params: { id: bill.id } }"
            class="list-card bill-card"
          >
            <UserAvatar :name="bill.penghuni?.nama_lengkap" :size="42" />
            <div class="bill-card__body">
              <p class="bill-card__name">{{ bill.penghuni?.nama_lengkap ?? '—' }}</p>
              <p class="list-card__meta">{{ billMeta(bill) }}</p>
              <div class="bill-card__foot">
                <strong>{{ formatRupiah(bill.jumlah_tagihan) }}</strong>
                <StatusBadge :tone="statusTone(bill.status_tagihan)">{{ bill.status_tagihan }}</StatusBadge>
              </div>
            </div>
          </RouterLink>
        </div>
      </StateBlock>
    </div>

    <!-- ================= Laporan ================= -->
    <div v-else class="app-page">
      <div class="range">
        <label>
          <span class="field-label">Dari</span>
          <input v-model="range.dari" type="date" class="input" :max="range.sampai">
        </label>
        <label>
          <span class="field-label">Sampai</span>
          <input v-model="range.sampai" type="date" class="input" :min="range.dari">
        </label>
      </div>
      <p v-if="rangeInvalid" class="field-error">Tanggal awal tidak boleh setelah tanggal akhir.</p>

      <StateBlock :loading="report.loading" :error="report.error" :has-data="!!report.summary" @retry="loadReport">
        <template v-if="report.summary">
          <div class="report-stats">
            <div class="stat-card report-stat">
              <p class="section-label">Pemasukan</p>
              <p class="report-stat__value">{{ formatRupiah(report.summary.pemasukan) }}</p>
              <p class="stat-card__note">{{ report.summary.jumlah_lunas }} tagihan lunas</p>
            </div>
            <div class="stat-card report-stat">
              <p class="section-label">Pengeluaran</p>
              <p class="report-stat__value">{{ formatRupiah(report.summary.pengeluaran) }}</p>
            </div>
            <div class="stat-card report-stat">
              <p class="section-label">Tunggakan</p>
              <p class="report-stat__value is-crimson">{{ formatRupiah(report.summary.tunggakan) }}</p>
              <p class="stat-card__note">{{ report.summary.jumlah_penunggak }} penghuni</p>
            </div>
            <div class="report-stat report-stat--peach">
              <p class="section-label">Laba bersih</p>
              <p class="report-stat__value">{{ formatRupiah(report.summary.laba_bersih) }}</p>
            </div>
          </div>

          <div class="report-actions">
            <button type="button" class="button button--primary" @click="openExpense">
              <AppIcon name="plus" :size="16" /> Catat Pengeluaran
            </button>
            <button type="button" class="button button--outline" :disabled="downloading || rangeInvalid" @click="downloadRecap">
              <AppIcon name="download" :size="16" /> {{ downloading ? 'Mengunduh…' : 'Unduh Rekap (.xlsx)' }}
            </button>
          </div>

          <RouterLink :to="{ name: 'pemilik-kamar' }" class="list-card link-card">
            <span>
              <span class="list-card__title">Kamar &amp; Tarif</span>
              <span class="list-card__meta">Atur harga sewa tiap kamar</span>
            </span>
            <AppIcon name="chevron-right" :size="18" />
          </RouterLink>

          <section class="panel tx-panel">
            <h2 class="panel-title">Daftar transaksi</h2>
            <p v-if="!report.transactions.length" class="tx-empty">Belum ada transaksi pada rentang ini.</p>
            <ul v-else class="tx-list">
              <li v-for="(tx, index) in report.transactions" :key="index" class="tx">
                <div class="tx__body">
                  <p class="tx__title">{{ tx.keterangan }}</p>
                  <p class="tx__meta">
                    {{ formatDate(tx.tanggal) }}
                    <StatusBadge :tone="KATEGORI_TONE[tx.kategori] ?? 'neutral'">{{ tx.kategori }}</StatusBadge>
                  </p>
                </div>
                <span class="tx__amount" :class="tx.nominal < 0 ? 'is-out' : 'is-in'">
                  {{ tx.nominal < 0 ? '−' : '+' }}{{ formatRupiah(Math.abs(tx.nominal)) }}
                </span>
              </li>
            </ul>
          </section>
        </template>
      </StateBlock>
    </div>

    <BottomSheet v-model:open="expenseOpen" title="Catat pengeluaran" description="Masuk ke laporan keuangan & rekap.">
      <form class="form-stack" novalidate @submit.prevent="saveExpense">
        <label>
          <span class="field-label">Tanggal <span class="req">*</span></span>
          <input v-model="expense.tanggal" type="date" class="input" required>
        </label>
        <label>
          <span class="field-label">Keterangan <span class="req">*</span></span>
          <input v-model="expense.keterangan" type="text" class="input" :class="{ 'is-invalid': expenseErrors.keterangan }" maxlength="120" placeholder="Contoh: Token listrik bulan November">
          <span v-if="expenseErrors.keterangan" class="field-error">{{ expenseErrors.keterangan }}</span>
        </label>
        <label>
          <span class="field-label">Kategori</span>
          <select v-model="expense.kategori" class="select">
            <option v-for="k in KATEGORI_PENGELUARAN" :key="k" :value="k">{{ k }}</option>
          </select>
        </label>
        <label>
          <span class="field-label">Nominal (Rp) <span class="req">*</span></span>
          <input v-model.number="expense.nominal" type="number" inputmode="numeric" min="1" class="input" :class="{ 'is-invalid': expenseErrors.nominal }" placeholder="500000">
          <span v-if="expenseErrors.nominal" class="field-error">{{ expenseErrors.nominal }}</span>
        </label>
        <div class="form-actions">
          <button type="button" class="button button--outline" @click="expenseOpen = false">Batal</button>
          <button type="submit" class="button button--primary" :disabled="expenseSaving">{{ expenseSaving ? 'Menyimpan…' : 'Simpan' }}</button>
        </div>
      </form>
    </BottomSheet>
  </div>
</template>

<style scoped>
.pill-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  margin: 0 -16px;
  padding: 0 16px 2px;
  scrollbar-width: none;
}

.pill-scroll .pill {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.pill__count {
  min-width: 18px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--mist);
  color: var(--ink);
  font-size: 11px;
  text-align: center;
}

.pill.is-active .pill__count {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.tenant-chip {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px 6px 14px;
  border-radius: 999px;
  background: var(--mist);
  font-size: 13px;
  font-weight: 600;
}

.tenant-chip button {
  display: flex;
  padding: 4px;
  border: 0;
  border-radius: 999px;
  background: #fff;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bill-card {
  display: flex;
  gap: 12px;
}

.bill-card__body {
  flex: 1;
  min-width: 0;
}

.bill-card__name {
  font-size: 15px;
  font-weight: 600;
}

.bill-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 10px;
}

.bill-card__foot strong {
  font-family: var(--font-editorial);
  font-size: 18px;
  font-weight: 400;
}

.range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.range .field-label {
  font-size: 12px;
}

.range .input {
  padding: 10px 10px;
}

.report-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.report-stat {
  padding: 16px;
}

.report-stat .section-label {
  font-size: 11px;
}

.report-stat__value {
  margin-top: 8px;
  font-family: var(--font-editorial);
  font-size: 20px;
  line-height: 1.2;
  word-break: break-word;
}

.report-stat--peach {
  background: var(--peach);
  border: 1px solid var(--peach-border);
  border-radius: var(--radius-card);
  color: var(--sienna);
}

.report-stat--peach .section-label {
  color: var(--sienna);
}

.is-crimson {
  color: var(--crimson);
}

.report-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.report-actions .button {
  padding: 12px 8px;
  font-size: 13px;
  white-space: normal;
}

.link-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--mist);
  border-color: transparent;
}

.link-card .list-card__title,
.link-card .list-card__meta {
  display: block;
  margin-top: 0;
}

.tx-panel {
  padding: 20px;
}

.tx-empty {
  margin-top: 10px;
  font-size: 13px;
  color: var(--slate);
}

.tx-list {
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}

.tx {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.tx:last-child {
  border-bottom: 0;
}

.tx__body {
  flex: 1;
  min-width: 0;
}

.tx__title {
  font-size: 14px;
  font-weight: 500;
}

.tx__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--slate);
}

.tx__amount {
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.tx__amount.is-in {
  color: var(--status-success-text);
}

.tx__amount.is-out {
  color: var(--crimson);
}
</style>
