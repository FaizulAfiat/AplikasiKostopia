<script setup>
import { computed, onMounted, ref, shallowRef } from 'vue'
import { penilaianApi } from '@/services/endpoints'
import { formatDate, formatDecimal } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'
import SegmentedTabs from '@/components/app/SegmentedTabs.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const summary = shallowRef(null)
const reviews = ref([])
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    const [s, list] = await Promise.all([penilaianApi.summary(), penilaianApi.list()])
    summary.value = s
    reviews.value = list
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

onMounted(load)

const distribution = computed(() => {
  const dist = summary.value?.distribusi ?? {}
  const total = Math.max(1, summary.value?.jumlah ?? 0)
  return [5, 4, 3, 2, 1].map((star) => {
    const count = dist[String(star)] ?? 0
    return { star, count, pct: Math.round((count / total) * 100) }
  })
})

const ASPEK = ['Semua', 'Kebersihan', 'Keamanan', 'Fasilitas', 'Pelayanan', 'Umum']
const aspek = ref('Semua')
const aspekOptions = computed(() =>
  ASPEK.map((value) => ({ value, label: value })).filter(
    (o) => o.value === 'Semua' || reviews.value.some((r) => r.aspek === o.value),
  ),
)
const filtered = computed(() => (aspek.value === 'Semua' ? reviews.value : reviews.value.filter((r) => r.aspek === aspek.value)))

const starFill = (score, index) => Math.max(0, Math.min(1, score - index)) * 100
</script>

<template>
  <div>
    <AppHeader :back="{ name: 'pemilik-lainnya' }" title="Penilaian" subtitle="Rating & ulasan dari penghuni." />

    <div class="app-page app-page--plain">
      <StateBlock :loading="loading" :error="error" :has-data="!!summary" @retry="load">
        <template v-if="summary">
          <section class="panel score">
            <div class="score__main">
              <p class="score__value">{{ formatDecimal(summary.rata_rata || 0) }}<span> / 5</span></p>
              <div class="stars stars--lg" :aria-label="`Rata-rata ${formatDecimal(summary.rata_rata || 0)} dari 5 bintang`">
                <span v-for="i in 5" :key="i" class="star">
                  <span class="star__fill" :style="{ width: `${starFill(summary.rata_rata || 0, i - 1)}%` }">★</span>★
                </span>
              </div>
              <p class="score__count">{{ summary.jumlah }} ulasan</p>
            </div>
            <ul class="dist">
              <li v-for="row in distribution" :key="row.star" class="dist__row">
                <span class="dist__label">{{ row.star }}★</span>
                <span class="dist__track"><span class="dist__bar" :style="{ width: `${row.pct}%` }" /></span>
                <span class="dist__count">{{ row.count }}</span>
              </li>
            </ul>
          </section>

          <section v-if="summary.per_aspek?.length" class="panel aspects">
            <h2 class="panel-title">Per aspek</h2>
            <ul class="aspect-list">
              <li v-for="a in summary.per_aspek" :key="a.aspek" class="aspect">
                <span class="aspect__name">{{ a.aspek }}</span>
                <span class="aspect__track"><span class="aspect__bar" :style="{ width: `${(a.rata_rata / 5) * 100}%` }" /></span>
                <span class="aspect__score">{{ formatDecimal(a.rata_rata) }}</span>
                <span class="aspect__n">({{ a.jumlah }})</span>
              </li>
            </ul>
          </section>

          <h2 class="section-label">Ulasan penghuni</h2>
          <SegmentedTabs v-if="aspekOptions.length > 2" v-model="aspek" :options="aspekOptions" label="Filter aspek" />

          <p v-if="!filtered.length" class="empty-state">Belum ada ulasan{{ aspek !== 'Semua' ? ` untuk aspek ${aspek}` : '' }}.</p>
          <div v-else class="reviews">
            <article v-for="r in filtered" :key="r.id" class="list-card review">
              <div class="list-card__head">
                <div class="stars" :aria-label="`${r.skor_bintang} bintang`">
                  <span v-for="i in 5" :key="i" class="star" :class="{ 'is-on': i <= r.skor_bintang }">★</span>
                </div>
                <span class="chip">{{ r.aspek }}</span>
              </div>
              <p v-if="r.ulasan_feedback" class="review__text">“{{ r.ulasan_feedback }}”</p>
              <p v-else class="review__text review__text--muted">Tanpa ulasan tertulis.</p>
              <div class="review__foot">
                <UserAvatar :name="r.pengguna?.nama_lengkap" :size="26" />
                <span class="list-card__meta">
                  {{ r.pengguna?.nama_lengkap ?? 'Penghuni' }}<template v-if="r.pengguna?.kamar"> · {{ r.pengguna.kamar }}</template> · {{ formatDate(r.created_at) }}
                </span>
              </div>
            </article>
          </div>
        </template>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.score {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.score__value {
  font-family: var(--font-editorial);
  font-size: 46px;
  line-height: 1;
}

.score__value span {
  font-size: 18px;
  color: var(--slate);
}

.score__count {
  margin-top: 4px;
  font-size: 12px;
  color: var(--slate);
}

.stars {
  display: inline-flex;
  gap: 2px;
  font-size: 15px;
  line-height: 1;
}

.stars--lg {
  margin-top: 8px;
  font-size: 18px;
}

.star {
  position: relative;
  color: #e3d9d6;
}

.star.is-on {
  color: #c98a00;
}

.star__fill {
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  color: #c98a00;
  white-space: nowrap;
}

.dist {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.dist__row,
.aspect {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.dist__label {
  width: 24px;
  color: var(--slate);
}

.dist__track,
.aspect__track {
  flex: 1;
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--mist);
}

.dist__bar,
.aspect__bar {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: var(--maroon);
}

.dist__count {
  width: 22px;
  text-align: right;
  color: var(--slate);
}

.aspects {
  padding: 20px;
}

.aspects .panel-title {
  font-size: 20px;
}

.aspect-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
}

.aspect {
  font-size: 13px;
}

.aspect__name {
  width: 86px;
  font-weight: 500;
}

.aspect__bar {
  background: var(--crimson);
}

.aspect__score {
  width: 28px;
  font-weight: 700;
  text-align: right;
}

.aspect__n {
  width: 32px;
  font-size: 11px;
  color: var(--slate);
}

.reviews {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chip {
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--mist);
  font-size: 11px;
  font-weight: 600;
  color: var(--slate);
}

.review__text {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.55;
}

.review__text--muted {
  color: var(--slate);
  font-style: italic;
}

.review__foot {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.review__foot .list-card__meta {
  margin-top: 0;
}
</style>
