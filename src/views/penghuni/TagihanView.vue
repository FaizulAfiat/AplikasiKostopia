<script setup>
import { computed } from 'vue'
import { tagihanApi } from '@/services/endpoints'
import { useResource } from '@/composables/useResource'
import { formatDate, formatRupiah, formatShortDate, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

const { data, loading, error, reload } = useResource(() => tagihanApi.list(), { initial: [] })

const UNPAID = ['Belum Bayar', 'Ditolak']

// Tagihan yang perlu dibayar (paling lama dulu) di atas, lalu sisanya terbaru dulu.
const sorted = computed(() => {
  const list = data.value ?? []
  const due = list.filter((t) => UNPAID.includes(t.status_tagihan)).sort((a, b) => a.periode.localeCompare(b.periode))
  const rest = list.filter((t) => !UNPAID.includes(t.status_tagihan))
  return [...due, ...rest]
})

const highlightId = computed(() => {
  const first = sorted.value[0]
  return first && UNPAID.includes(first.status_tagihan) ? first.id : null
})

function subtitle(bill) {
  switch (bill.status_tagihan) {
    case 'Lunas':
      return bill.diverifikasi_at ? `Disetujui ${formatDate(bill.diverifikasi_at)}` : 'Lunas'
    case 'Ditolak':
      return `Ditolak: ${bill.alasan_tolak || 'bukti tidak valid'}`
    case 'Menunggu Verifikasi':
      return bill.tanggal_unggah ? `Bukti diunggah ${formatDate(bill.tanggal_unggah)}` : 'Bukti sedang diperiksa'
    default:
      return `Jatuh tempo ${formatShortDate(bill.jatuh_tempo)} · tenggang s/d ${formatShortDate(bill.batas_tenggang)}`
  }
}
</script>

<template>
  <div>
    <AppHeader
      hero
      title="Tagihan"
      subtitle="Tagihan dibuat otomatis setiap tanggal 1. Bayar lewat transfer, lalu unggah fotonya di sini."
    />

    <div class="app-page">
      <StateBlock
        :loading="loading"
        :error="error"
        :has-data="sorted.length > 0"
        :empty="!sorted.length"
        empty-icon="receipt"
        empty-title="Belum ada tagihan"
        empty-text="Tagihan akan muncul otomatis setelah Anda menempati kamar."
        @retry="reload"
      >
        <ul class="bills">
          <li v-for="bill in sorted" :key="bill.id">
            <RouterLink
              :to="{ name: 'penghuni-tagihan-detail', params: { id: bill.id } }"
              class="list-card bill"
              :class="{ 'bill--current': bill.id === highlightId }"
            >
              <p v-if="bill.id === highlightId" class="bill__flag">Perlu dibayar</p>
              <div class="list-card__head">
                <span class="bill__period">{{ bill.periode_label }}</span>
                <StatusBadge :tone="statusTone(bill.status_tagihan)">{{ bill.status_tagihan }}</StatusBadge>
              </div>
              <div class="bill__row">
                <p class="bill__amount">{{ formatRupiah(bill.jumlah_tagihan) }}</p>
                <AppIcon name="chevron-right" :size="18" class="bill__chevron" />
              </div>
              <p class="list-card__meta" :class="{ 'is-danger': bill.status_tagihan === 'Ditolak' }">{{ subtitle(bill) }}</p>
            </RouterLink>
          </li>
        </ul>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.bills {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.bill--current {
  border-color: var(--crimson);
  box-shadow: 0 10px 24px -14px rgba(112, 0, 32, 0.5);
}

.bill__flag {
  margin-bottom: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--crimson);
}

.bill__period {
  font-size: 14px;
  font-weight: 600;
}

.bill__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}

.bill__amount {
  font-family: var(--font-editorial);
  font-size: 26px;
  line-height: 1.15;
}

.bill__chevron {
  color: var(--slate);
}

.list-card__meta.is-danger {
  color: var(--status-danger-text);
}
</style>
