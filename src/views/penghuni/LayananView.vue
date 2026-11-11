<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { aspirasiApi, izinApi } from '@/services/endpoints'
import { fileUrl } from '@/services/config'
import { useResource } from '@/composables/useResource'
import { formatDate, formatShortDate, statusTone } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import SegmentedTabs from '@/components/app/SegmentedTabs.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

const route = useRoute()
const router = useRouter()

const tab = ref(route.query.tab === 'izin' ? 'izin' : 'aspirasi')
watch(() => route.query.tab, (value) => (tab.value = value === 'izin' ? 'izin' : 'aspirasi'))
watch(tab, (value) => {
  if ((route.query.tab ?? 'aspirasi') !== value) router.replace({ query: value === 'izin' ? { tab: 'izin' } : {} })
})

const aspirasi = useResource(() => aspirasiApi.list(), { initial: [] })
const izin = useResource(() => izinApi.list(), { initial: [] })

const tabs = computed(() => [
  { value: 'aspirasi', label: 'Aspirasi', count: aspirasi.data.value?.length || undefined },
  { value: 'izin', label: 'Izin', count: izin.data.value?.length || undefined },
])

function dateRange(item) {
  if (item.tanggal_mulai === item.tanggal_selesai) return formatDate(item.tanggal_mulai)
  return `${formatShortDate(item.tanggal_mulai)} – ${formatDate(item.tanggal_selesai)}`
}
</script>

<template>
  <div>
    <AppHeader hero title="Aspirasi & Izin" subtitle="Sampaikan keluhan atau saran, dan ajukan izin ke pemilik kos.">
      <SegmentedTabs v-model="tab" :options="tabs" dark label="Jenis layanan" />
    </AppHeader>

    <div class="app-page">
      <!-- Aspirasi -->
      <template v-if="tab === 'aspirasi'">
        <h2 class="section-label">Riwayat aspirasi</h2>
        <StateBlock
          :loading="aspirasi.loading.value"
          :error="aspirasi.error.value"
          :has-data="aspirasi.data.value.length > 0"
          :empty="!aspirasi.data.value.length"
          empty-icon="chat"
          empty-title="Belum ada aspirasi"
          empty-text="Laporkan kerusakan, keluhan, atau saran — pemilik akan menanggapinya di sini."
          @retry="aspirasi.reload"
        >
          <ul class="svc-list">
            <li v-for="item in aspirasi.data.value" :key="item.id" class="list-card">
              <div class="list-card__head">
                <span class="svc-meta">{{ item.kategori }} · {{ formatDate(item.created_at) }}</span>
                <StatusBadge :tone="statusTone(item.status_penanganan)">{{ item.status_penanganan }}</StatusBadge>
              </div>
              <h3 class="list-card__title">{{ item.judul }}</h3>
              <p class="svc-body">{{ item.deskripsi_kendala }}</p>
              <div v-if="item.lampiran_foto_urls?.length" class="svc-photos">
                <a v-for="path in item.lampiran_foto_urls" :key="path" :href="fileUrl(path)" target="_blank" rel="noopener">
                  <img :src="fileUrl(path)" alt="Lampiran aspirasi" loading="lazy">
                </a>
              </div>
              <p v-if="item.tanggapan_pemilik" class="svc-reply">
                <strong>Tanggapan pemilik:</strong> {{ item.tanggapan_pemilik }}
              </p>
            </li>
          </ul>
        </StateBlock>

        <RouterLink :to="{ name: 'penghuni-aspirasi-baru' }" class="fab">
          <AppIcon name="plus" :size="18" :stroke-width="2.4" /> Buat aspirasi
        </RouterLink>
      </template>

      <!-- Izin -->
      <template v-else>
        <h2 class="section-label">Riwayat izin</h2>
        <StateBlock
          :loading="izin.loading.value"
          :error="izin.error.value"
          :has-data="izin.data.value.length > 0"
          :empty="!izin.data.value.length"
          empty-icon="calendar"
          empty-title="Belum ada pengajuan izin"
          empty-text="Ajukan izin pulang kampung, menginap di luar, atau pulang larut."
          @retry="izin.reload"
        >
          <ul class="svc-list">
            <li v-for="item in izin.data.value" :key="item.id" class="list-card">
              <div class="list-card__head">
                <span class="svc-meta">{{ item.jenis_izin }}</span>
                <StatusBadge :tone="statusTone(item.status_izin)">{{ item.status_izin }}</StatusBadge>
              </div>
              <h3 class="list-card__title">{{ dateRange(item) }}</h3>
              <p class="list-card__meta">{{ item.durasi }} · diajukan {{ formatDate(item.created_at) }}</p>
              <p class="svc-body">{{ item.alasan }}</p>
              <p v-if="item.catatan_pemilik" class="svc-reply">
                <strong>Catatan pemilik:</strong> {{ item.catatan_pemilik }}
              </p>
            </li>
          </ul>
        </StateBlock>

        <RouterLink :to="{ name: 'penghuni-izin-baru' }" class="fab">
          <AppIcon name="plus" :size="18" :stroke-width="2.4" /> Ajukan izin
        </RouterLink>
      </template>
    </div>
  </div>
</template>

<style scoped>
.svc-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.svc-meta {
  font-size: 12px;
  font-weight: 600;
  color: var(--slate);
}

.svc-body {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-line;
}

.svc-photos {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.svc-photos img {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border: 1px solid var(--border);
  border-radius: 12px;
}

.svc-reply {
  margin-top: 12px;
  padding: 12px 14px;
  background: var(--mist);
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
}
</style>
