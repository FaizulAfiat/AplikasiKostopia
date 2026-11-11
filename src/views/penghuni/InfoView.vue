<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { aturanApi, pengumumanApi, penilaianApi } from '@/services/endpoints'
import { useResource } from '@/composables/useResource'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import SegmentedTabs from '@/components/app/SegmentedTabs.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()

const TABS = ['pengumuman', 'aturan', 'penilaian']
const normalize = (value) => (TABS.includes(value) ? value : 'pengumuman')

const tab = ref(normalize(route.query.tab))
watch(() => route.query.tab, (value) => (tab.value = normalize(value)))
watch(tab, (value) => {
  if (normalize(route.query.tab) !== value) router.replace({ query: value === 'pengumuman' ? {} : { tab: value } })
})

const tabOptions = [
  { value: 'pengumuman', label: 'Pengumuman' },
  { value: 'aturan', label: 'Aturan' },
  { value: 'penilaian', label: 'Penilaian' },
]

// Data dimuat saat tab pertama kali dibuka
const announcements = useResource(() => pengumumanApi.list(), { immediate: false, initial: [] })
const rules = useResource(() => aturanApi.list(), { immediate: false, initial: [] })
const reviews = useResource(() => penilaianApi.list(), { immediate: false, initial: [] })
const loaded = new Set()

watch(
  tab,
  (value) => {
    if (loaded.has(value)) return
    loaded.add(value)
    ;({ pengumuman: announcements, aturan: rules, penilaian: reviews })[value].reload()
  },
  { immediate: true },
)

// ---------- Pengumuman ----------
const expanded = ref(new Set())
const readIds = new Set()

const featured = computed(() => announcements.data.value?.[0] ?? null)
const others = computed(() => announcements.data.value?.slice(1) ?? [])

function markRead(item) {
  if (!item || item.sudah_dibaca || readIds.has(item.id)) return
  readIds.add(item.id)
  pengumumanApi.markRead(item.id).catch(() => readIds.delete(item.id))
}

watch(featured, (item) => markRead(item))

function toggle(item) {
  const next = new Set(expanded.value)
  if (next.has(item.id)) next.delete(item.id)
  else {
    next.add(item.id)
    markRead(item)
  }
  expanded.value = next
}

function isUnread(item) {
  return !item.sudah_dibaca && !readIds.has(item.id)
}

function authorLabel(item) {
  const name = item.pembuat?.nama_lengkap
  return name ? `Dari ${name} · Pemilik kos` : 'Dari pemilik kos'
}

// ---------- Aturan ----------
function sanksiTone(sanksi = '') {
  return /denda/i.test(sanksi) ? 'danger' : 'neutral'
}

// ---------- Penilaian ----------
const ASPEK = ['Umum', 'Kebersihan', 'Keamanan', 'Fasilitas', 'Pelayanan']
const STAR_LABELS = ['Belum memilih', 'Sangat buruk', 'Buruk', 'Cukup', 'Baik', 'Sangat baik']

const reviewForm = reactive({ skor_bintang: 0, aspek: 'Umum', ulasan_feedback: '' })
const starError = ref('')
const submitting = ref(false)

function setStars(value) {
  reviewForm.skor_bintang = value
  starError.value = ''
}

async function submitReview() {
  if (!reviewForm.skor_bintang) {
    starError.value = 'Pilih jumlah bintang terlebih dahulu.'
    return
  }
  if (submitting.value) return
  submitting.value = true
  try {
    const created = await penilaianApi.create({
      skor_bintang: reviewForm.skor_bintang,
      aspek: reviewForm.aspek,
      ulasan_feedback: reviewForm.ulasan_feedback.trim() || null,
    })
    reviews.data.value = [created, ...(reviews.data.value ?? [])]
    Object.assign(reviewForm, { skor_bintang: 0, aspek: 'Umum', ulasan_feedback: '' })
    ui.showToast('Terima kasih! Penilaian Anda terkirim.', 'success')
  } catch (error) {
    ui.showError(error, 'Penilaian Gagal Dikirim')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader hero title="Info Kos" subtitle="Pengumuman dari pemilik, tata tertib yang berlaku, dan penilaian Anda.">
      <SegmentedTabs v-model="tab" :options="tabOptions" dark label="Bagian info kos" />
    </AppHeader>

    <div class="app-page">
      <!-- ================= Pengumuman ================= -->
      <StateBlock
        v-if="tab === 'pengumuman'"
        :loading="announcements.loading.value"
        :error="announcements.error.value"
        :has-data="announcements.data.value.length > 0"
        :empty="!announcements.data.value.length"
        empty-icon="bell"
        empty-title="Belum ada pengumuman"
        empty-text="Pengumuman dari pemilik kos akan tampil di sini."
        @retry="announcements.reload"
      >
        <div class="info-stack">
          <article v-if="featured" class="announce-feature">
            <div class="announce-feature__head">
              <p class="announce-feature__from">{{ authorLabel(featured) }}</p>
              <StatusBadge v-if="featured.disematkan" tone="warning">Disematkan</StatusBadge>
            </div>
            <time class="announce-feature__date" :datetime="featured.created_at">{{ formatDate(featured.created_at) }}</time>
            <h2 class="announce-feature__title">{{ featured.judul }}</h2>
            <p class="announce-feature__body">{{ featured.isi_pengumuman }}</p>
          </article>

          <template v-if="others.length">
            <h2 class="section-label">Pengumuman lainnya</h2>
            <ul class="info-list">
              <li v-for="item in others" :key="item.id">
                <button
                  type="button"
                  class="list-card announce"
                  :aria-expanded="expanded.has(item.id)"
                  @click="toggle(item)"
                >
                  <div class="list-card__head">
                    <span class="announce__date">
                      <span v-if="isUnread(item)" class="announce__dot" aria-label="Belum dibaca" />
                      {{ formatDate(item.created_at) }}
                    </span>
                    <StatusBadge v-if="item.disematkan" tone="warning">Disematkan</StatusBadge>
                  </div>
                  <h3 class="announce__title">{{ item.judul }}</h3>
                  <p class="announce__body" :class="{ 'is-clamped': !expanded.has(item.id) }">{{ item.isi_pengumuman }}</p>
                  <span class="announce__toggle">
                    {{ expanded.has(item.id) ? 'Tutup' : 'Baca selengkapnya' }}
                    <AppIcon name="chevron-down" :size="14" :class="{ 'is-flipped': expanded.has(item.id) }" />
                  </span>
                </button>
              </li>
            </ul>
          </template>
        </div>
      </StateBlock>

      <!-- ================= Aturan ================= -->
      <StateBlock
        v-else-if="tab === 'aturan'"
        :loading="rules.loading.value"
        :error="rules.error.value"
        :has-data="rules.data.value.length > 0"
        :empty="!rules.data.value.length"
        empty-icon="book"
        empty-title="Belum ada aturan"
        empty-text="Tata tertib kos yang berlaku akan tampil di sini."
        @retry="rules.reload"
      >
        <section class="panel">
          <h2 class="section-label">Aturan kos · {{ rules.data.value.length }} aturan aktif</h2>
          <ol class="rules">
            <li v-for="(rule, index) in rules.data.value" :key="rule.id" class="rule">
              <span class="rule__no">{{ String(index + 1).padStart(2, '0') }}</span>
              <div class="rule__body">
                <h3 class="rule__title">{{ rule.judul }}</h3>
                <p v-if="rule.deskripsi" class="rule__desc">{{ rule.deskripsi }}</p>
                <StatusBadge v-if="rule.sanksi" :tone="sanksiTone(rule.sanksi)" class="rule__sanksi">Sanksi: {{ rule.sanksi }}</StatusBadge>
              </div>
            </li>
          </ol>
        </section>
      </StateBlock>

      <!-- ================= Penilaian ================= -->
      <template v-else>
        <form class="panel form-stack" novalidate @submit.prevent="submitReview">
          <div>
            <h2 class="panel-title">Beri penilaian</h2>
            <p class="panel-desc">Bagaimana pengalaman Anda tinggal di kos ini?</p>
          </div>

          <div>
            <div class="stars" role="radiogroup" aria-label="Jumlah bintang">
              <button
                v-for="n in 5"
                :key="n"
                type="button"
                role="radio"
                class="stars__item"
                :class="{ 'is-on': n <= reviewForm.skor_bintang }"
                :aria-checked="reviewForm.skor_bintang === n"
                :aria-label="`${n} bintang — ${STAR_LABELS[n]}`"
                @click="setStars(n)"
              >
                <svg viewBox="0 0 24 24" width="36" height="36" aria-hidden="true">
                  <path
                    d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                    stroke-width="1.5"
                    stroke-linejoin="round"
                  />
                </svg>
              </button>
            </div>
            <p class="stars__label" :class="{ 'is-set': reviewForm.skor_bintang }">{{ STAR_LABELS[reviewForm.skor_bintang] }}</p>
            <p v-if="starError" class="field-error" role="alert">{{ starError }}</p>
          </div>

          <div>
            <label for="rv-aspek" class="field-label">Aspek yang dinilai</label>
            <select id="rv-aspek" v-model="reviewForm.aspek" class="select">
              <option v-for="item in ASPEK" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>

          <div>
            <label for="rv-ulasan" class="field-label">Ulasan <span class="field-label__hint">— opsional</span></label>
            <textarea
              id="rv-ulasan"
              v-model="reviewForm.ulasan_feedback"
              class="textarea"
              maxlength="500"
              placeholder="Ceritakan apa yang sudah baik dan apa yang perlu diperbaiki..."
            />
          </div>

          <button type="submit" class="button button--primary button--block" :disabled="submitting">
            {{ submitting ? 'Mengirim…' : 'Kirim Penilaian' }}
          </button>
        </form>

        <h2 class="section-label">Penilaian saya</h2>
        <StateBlock
          :loading="reviews.loading.value"
          :error="reviews.error.value"
          :has-data="reviews.data.value.length > 0"
          :empty="!reviews.data.value.length"
          empty-icon="star"
          empty-title="Belum ada penilaian"
          empty-text="Penilaian yang Anda kirim akan tampil di sini."
          @retry="reviews.reload"
        >
          <ul class="info-list">
            <li v-for="item in reviews.data.value" :key="item.id" class="list-card">
              <div class="list-card__head">
                <span class="review__stars" :aria-label="`${item.skor_bintang} dari 5 bintang`">
                  {{ '★'.repeat(item.skor_bintang) }}<span class="review__stars-off">{{ '★'.repeat(5 - item.skor_bintang) }}</span>
                </span>
                <span class="review__date">{{ formatDate(item.created_at) }}</span>
              </div>
              <p class="list-card__title">{{ item.aspek }}</p>
              <p v-if="item.ulasan_feedback" class="review__text">{{ item.ulasan_feedback }}</p>
            </li>
          </ul>
        </StateBlock>
      </template>
    </div>
  </div>
</template>

<style scoped>
.info-stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

/* Pengumuman utama (satu-satunya kartu peach) */
.announce-feature {
  padding: 22px;
  background: var(--peach);
  border: 1px solid var(--peach-border);
  border-radius: var(--radius-card);
  color: var(--sienna);
}

.announce-feature__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.announce-feature__from {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.announce-feature__date {
  display: block;
  margin-top: 6px;
  font-size: 12px;
}

.announce-feature__title {
  margin-top: 8px;
  font-family: var(--font-editorial);
  font-size: 24px;
  font-weight: 400;
  line-height: 1.25;
  color: var(--ink);
}

.announce-feature__body {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-line;
}

.announce__date {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--slate);
}

.announce__dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--crimson);
}

.announce__title {
  margin-top: 8px;
  font-family: var(--font-editorial);
  font-size: 19px;
  font-weight: 400;
  line-height: 1.3;
}

.announce__body {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.55;
  white-space: pre-line;
}

.announce__body.is-clamped {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.announce__toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--crimson);
}

.announce__toggle .is-flipped {
  transform: rotate(180deg);
}

/* Aturan */
.rules {
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}

.rule {
  display: flex;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}

.rule:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.rule__no {
  flex-shrink: 0;
  width: 32px;
  font-family: var(--font-editorial);
  font-size: 24px;
  line-height: 1.1;
  color: var(--crimson);
}

.rule__title {
  font-size: 15px;
  font-weight: 600;
}

.rule__desc {
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--slate);
}

.rule__sanksi {
  margin-top: 8px;
}

/* Penilaian */
.stars {
  display: flex;
  gap: 6px;
}

.stars__item {
  padding: 4px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #d8cfcd;
  fill: transparent;
  stroke: currentColor;
  transition: transform 0.1s ease;
}

.stars__item:active {
  transform: scale(0.9);
}

.stars__item.is-on {
  color: #c98a00;
  fill: #f2b53a;
}

.stars__label {
  margin-top: 4px;
  font-size: 13px;
  color: var(--slate);
}

.stars__label.is-set {
  font-weight: 600;
  color: var(--ink);
}

.review__stars {
  font-size: 16px;
  letter-spacing: 1px;
  color: #f2b53a;
}

.review__stars-off {
  color: #e2dad8;
}

.review__date {
  font-size: 12px;
  color: var(--slate);
}

.review__text {
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.5;
}
</style>
