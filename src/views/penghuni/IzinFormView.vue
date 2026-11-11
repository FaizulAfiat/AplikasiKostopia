<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { izinApi } from '@/services/endpoints'
import { todayISO } from '@/utils/format'
import AppHeader from '@/components/app/AppHeader.vue'

const router = useRouter()
const ui = useUiStore()

const JENIS = [
  { value: 'Pulang Kampung', hint: 'Beberapa hari di rumah' },
  { value: 'Menginap di Luar', hint: 'Tidak tidur di kos' },
  { value: 'Pulang Larut', hint: 'Lewat jam malam' },
  { value: 'Lainnya', hint: 'Keperluan lain' },
]

const form = reactive({
  jenis_izin: 'Pulang Kampung',
  tanggal_mulai: todayISO(),
  tanggal_selesai: todayISO(1),
  alasan: '',
})
const errors = reactive({ tanggal: '', alasan: '' })
const reasonInput = ref(null)
const submitting = ref(false)

const singleDay = computed(() => form.jenis_izin === 'Pulang Larut')

watch(singleDay, (single) => {
  if (!single && form.tanggal_selesai <= form.tanggal_mulai) {
    const d = new Date(`${form.tanggal_mulai}T00:00:00`)
    d.setDate(d.getDate() + 1)
    form.tanggal_selesai = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }
})

async function onSubmit() {
  const selesai = singleDay.value ? form.tanggal_mulai : form.tanggal_selesai
  errors.tanggal = !form.tanggal_mulai || !selesai
    ? 'Tanggal wajib diisi.'
    : selesai < form.tanggal_mulai
      ? 'Tanggal selesai tidak boleh sebelum tanggal mulai.'
      : ''
  errors.alasan = form.alasan.trim() ? '' : 'Alasan wajib diisi.'
  if (errors.tanggal) return
  if (errors.alasan) return reasonInput.value?.focus()
  if (submitting.value) return

  submitting.value = true
  try {
    await izinApi.create({
      jenis_izin: form.jenis_izin,
      tanggal_mulai: form.tanggal_mulai,
      tanggal_selesai: selesai,
      alasan: form.alasan.trim(),
    })
    ui.showToast('Pengajuan izin terkirim. Menunggu persetujuan pemilik.', 'success')
    router.replace({ name: 'penghuni-layanan', query: { tab: 'izin' } })
  } catch (error) {
    if (error.status === 422) errors.tanggal = error.message
    ui.showError(error, 'Izin Gagal Diajukan')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader
      :back="{ name: 'penghuni-layanan', query: { tab: 'izin' } }"
      title="Ajukan izin"
      subtitle="Beri tahu pemilik kos saat Anda tidak berada di kos."
    />

    <form class="app-page app-page--plain form-stack" novalidate @submit.prevent="onSubmit">
      <fieldset class="izin__fieldset">
        <legend class="field-label">Jenis izin</legend>
        <div class="izin__types" role="radiogroup">
          <button
            v-for="option in JENIS"
            :key="option.value"
            type="button"
            role="radio"
            class="pill izin__type"
            :class="{ 'is-active': form.jenis_izin === option.value }"
            :aria-checked="form.jenis_izin === option.value"
            @click="form.jenis_izin = option.value"
          >
            <span>{{ option.value }}</span>
            <small>{{ option.hint }}</small>
          </button>
        </div>
      </fieldset>

      <div class="izin__dates" :class="{ 'izin__dates--single': singleDay }">
        <div>
          <label for="izin-mulai" class="field-label">{{ singleDay ? 'Tanggal' : 'Tanggal mulai' }}</label>
          <input
            id="izin-mulai"
            v-model="form.tanggal_mulai"
            type="date"
            class="input"
            :class="{ 'is-invalid': errors.tanggal }"
            @input="errors.tanggal = ''"
          >
        </div>
        <div v-if="!singleDay">
          <label for="izin-selesai" class="field-label">Tanggal selesai</label>
          <input
            id="izin-selesai"
            v-model="form.tanggal_selesai"
            type="date"
            class="input"
            :class="{ 'is-invalid': errors.tanggal }"
            :min="form.tanggal_mulai"
            @input="errors.tanggal = ''"
          >
        </div>
      </div>
      <p v-if="errors.tanggal" class="field-error izin__date-error" role="alert">{{ errors.tanggal }}</p>

      <div>
        <label for="izin-alasan" class="field-label">Alasan <span class="req">*</span></label>
        <textarea
          id="izin-alasan"
          ref="reasonInput"
          v-model="form.alasan"
          class="textarea"
          :class="{ 'is-invalid': errors.alasan }"
          maxlength="500"
          placeholder="Contoh: Pulang ke Bandung untuk acara keluarga."
          :aria-invalid="errors.alasan ? 'true' : undefined"
          @input="errors.alasan = ''"
        />
        <p v-if="errors.alasan" class="field-error" role="alert">{{ errors.alasan }}</p>
      </div>

      <button type="submit" class="button button--primary button--block" :disabled="submitting">
        {{ submitting ? 'Mengirim…' : 'Ajukan Izin' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.izin__fieldset {
  margin: 0;
  padding: 0;
  border: 0;
}

.izin__fieldset legend {
  padding: 0;
}

.izin__types {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.izin__type {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 12px 14px;
  border-radius: 14px;
  text-align: left;
}

.izin__type small {
  font-size: 11px;
  font-weight: 400;
  opacity: 0.75;
}

.izin__dates {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.izin__dates--single {
  grid-template-columns: 1fr;
}

.izin__date-error {
  margin-top: -10px;
}
</style>
