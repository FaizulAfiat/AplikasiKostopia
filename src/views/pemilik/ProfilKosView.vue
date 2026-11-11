<script setup>
import { onMounted, reactive, ref } from 'vue'
import { profilKosApi } from '@/services/endpoints'
import { useUiStore } from '@/stores/ui'
import AppHeader from '@/components/app/AppHeader.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import AppIcon from '@/components/AppIcon.vue'

const ui = useUiStore()

const DEFAULTS = {
  nama_kos: '',
  alamat_lengkap: '',
  deskripsi: '',
  nomor_telepon_pengelola: '',
  bank_nama: '',
  bank_nomor_rekening: '',
  bank_atas_nama: '',
  tanggal_jatuh_tempo: 10,
  masa_tenggang_hari: 5,
  tarif_parkir_motor: 0,
  tarif_parkir_mobil: 75000,
  kapasitas_parkir_motor: 20,
  kapasitas_parkir_mobil: 4,
  kode_undangan: '',
}
const TEXT_FIELDS = ['nama_kos', 'alamat_lengkap', 'deskripsi', 'nomor_telepon_pengelola', 'bank_nama', 'bank_nomor_rekening', 'bank_atas_nama', 'kode_undangan']
const INT_FIELDS = ['tanggal_jatuh_tempo', 'masa_tenggang_hari', 'tarif_parkir_motor', 'tarif_parkir_mobil', 'kapasitas_parkir_motor', 'kapasitas_parkir_mobil']

const form = reactive({ ...DEFAULTS })
const errors = reactive({})
const exists = ref(true)
const loading = ref(false)
const error = ref(null)
const loaded = ref(false)
const saving = ref(false)

function fill(profil) {
  Object.keys(DEFAULTS).forEach((key) => {
    form[key] = profil?.[key] ?? DEFAULTS[key]
  })
}

async function load() {
  loading.value = true
  error.value = null
  try {
    fill(await profilKosApi.get())
    exists.value = true
    loaded.value = true
  } catch (err) {
    if (err.status === 404) {
      fill(null)
      exists.value = false
      loaded.value = true
    } else {
      error.value = err
    }
  } finally {
    loading.value = false
  }
}

onMounted(load)

function validate() {
  Object.keys(errors).forEach((k) => delete errors[k])
  if (!String(form.nama_kos).trim()) errors.nama_kos = 'Nama kos wajib diisi.'
  if (!String(form.alamat_lengkap).trim()) errors.alamat_lengkap = 'Alamat wajib diisi.'
  const due = Number(form.tanggal_jatuh_tempo)
  if (!Number.isInteger(due) || due < 1 || due > 28) errors.tanggal_jatuh_tempo = 'Isi tanggal 1–28.'
  INT_FIELDS.filter((k) => k !== 'tanggal_jatuh_tempo').forEach((key) => {
    const v = Number(form[key])
    if (form[key] === '' || form[key] === null || !Number.isFinite(v) || v < 0) errors[key] = 'Harus angka ≥ 0.'
  })
  return !Object.keys(errors).length
}

async function save() {
  if (!validate()) {
    ui.showToast('Periksa kembali isian yang ditandai.', 'error')
    return
  }
  if (saving.value) return
  saving.value = true
  const body = {}
  TEXT_FIELDS.forEach((key) => {
    const v = String(form[key] ?? '').trim()
    body[key] = v || null
  })
  if (body.kode_undangan) body.kode_undangan = body.kode_undangan.toUpperCase()
  INT_FIELDS.forEach((key) => (body[key] = Math.round(Number(form[key]))))
  try {
    const result = exists.value ? await profilKosApi.update(body) : await profilKosApi.create(body)
    fill(result ?? body)
    exists.value = true
    ui.showToast('Profil kos disimpan.', 'success')
  } catch (err) {
    ui.showError(err, 'Gagal Menyimpan Profil Kos')
  } finally {
    saving.value = false
  }
}

function generateCode() {
  form.kode_undangan = `KST-${Math.floor(1000 + Math.random() * 9000)}`
}
</script>

<template>
  <div>
    <AppHeader :back="{ name: 'pemilik-lainnya' }" title="Profil Kos" :subtitle="exists ? 'Informasi yang dilihat penghuni.' : 'Profil belum diatur — lengkapi untuk mulai.'" />

    <form class="app-page app-page--plain" novalidate @submit.prevent="save">
      <StateBlock :loading="loading" :error="error" :has-data="loaded" @retry="load">
        <div v-if="!exists" class="notice">
          <AppIcon name="info" :size="18" />
          <span>Profil kos belum dibuat. Isi data di bawah lalu simpan.</span>
        </div>

        <section class="panel form-stack">
          <h2 class="panel-title">Informasi kos</h2>
          <label>
            <span class="field-label">Nama kos <span class="req">*</span></span>
            <input v-model="form.nama_kos" type="text" class="input" :class="{ 'is-invalid': errors.nama_kos }" maxlength="100" placeholder="Kos Griya Sukabirus">
            <span v-if="errors.nama_kos" class="field-error">{{ errors.nama_kos }}</span>
          </label>
          <label>
            <span class="field-label">Alamat lengkap <span class="req">*</span></span>
            <textarea v-model="form.alamat_lengkap" class="textarea textarea--sm" :class="{ 'is-invalid': errors.alamat_lengkap }" maxlength="300" placeholder="Jl. Sukabirus No. 12, Dayeuhkolot, Bandung" />
            <span v-if="errors.alamat_lengkap" class="field-error">{{ errors.alamat_lengkap }}</span>
          </label>
          <label>
            <span class="field-label">Deskripsi</span>
            <textarea v-model="form.deskripsi" class="textarea" maxlength="1000" placeholder="Fasilitas, lingkungan, dan informasi umum kos..." />
          </label>
          <label>
            <span class="field-label">Telepon pengelola</span>
            <input v-model="form.nomor_telepon_pengelola" type="tel" inputmode="tel" class="input" maxlength="20" placeholder="08xxxxxxxxxx">
          </label>
        </section>

        <section class="panel form-stack">
          <h2 class="panel-title">Rekening pembayaran</h2>
          <label>
            <span class="field-label">Nama bank</span>
            <input v-model="form.bank_nama" type="text" class="input" maxlength="40" placeholder="BCA">
          </label>
          <label>
            <span class="field-label">Nomor rekening</span>
            <input v-model="form.bank_nomor_rekening" type="text" inputmode="numeric" class="input" maxlength="30" placeholder="1234567890">
          </label>
          <label>
            <span class="field-label">Atas nama</span>
            <input v-model="form.bank_atas_nama" type="text" class="input" maxlength="80" placeholder="Budi Utomo">
          </label>
        </section>

        <section class="panel form-stack">
          <h2 class="panel-title">Tagihan</h2>
          <div class="row">
            <label>
              <span class="field-label">Jatuh tempo (tgl)</span>
              <input v-model.number="form.tanggal_jatuh_tempo" type="number" min="1" max="28" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.tanggal_jatuh_tempo }">
              <span v-if="errors.tanggal_jatuh_tempo" class="field-error">{{ errors.tanggal_jatuh_tempo }}</span>
            </label>
            <label>
              <span class="field-label">Masa tenggang (hari)</span>
              <input v-model.number="form.masa_tenggang_hari" type="number" min="0" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.masa_tenggang_hari }">
              <span v-if="errors.masa_tenggang_hari" class="field-error">{{ errors.masa_tenggang_hari }}</span>
            </label>
          </div>
        </section>

        <section class="panel form-stack">
          <div>
            <h2 class="panel-title">Parkir</h2>
            <p class="panel-desc">Motor pertama tiap penghuni gratis; tarif motor berlaku untuk motor berikutnya.</p>
          </div>
          <div class="row">
            <label>
              <span class="field-label">Tarif motor (Rp)</span>
              <input v-model.number="form.tarif_parkir_motor" type="number" min="0" step="1000" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.tarif_parkir_motor }">
              <span v-if="errors.tarif_parkir_motor" class="field-error">{{ errors.tarif_parkir_motor }}</span>
            </label>
            <label>
              <span class="field-label">Tarif mobil (Rp)</span>
              <input v-model.number="form.tarif_parkir_mobil" type="number" min="0" step="1000" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.tarif_parkir_mobil }">
              <span v-if="errors.tarif_parkir_mobil" class="field-error">{{ errors.tarif_parkir_mobil }}</span>
            </label>
            <label>
              <span class="field-label">Kapasitas motor</span>
              <input v-model.number="form.kapasitas_parkir_motor" type="number" min="0" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.kapasitas_parkir_motor }">
              <span v-if="errors.kapasitas_parkir_motor" class="field-error">{{ errors.kapasitas_parkir_motor }}</span>
            </label>
            <label>
              <span class="field-label">Kapasitas mobil</span>
              <input v-model.number="form.kapasitas_parkir_mobil" type="number" min="0" inputmode="numeric" class="input" :class="{ 'is-invalid': errors.kapasitas_parkir_mobil }">
              <span v-if="errors.kapasitas_parkir_mobil" class="field-error">{{ errors.kapasitas_parkir_mobil }}</span>
            </label>
          </div>
        </section>

        <section class="panel form-stack">
          <div>
            <h2 class="panel-title">Kode undangan</h2>
            <p class="panel-desc">Dibagikan ke calon penghuni saat mendaftar di aplikasi.</p>
          </div>
          <div class="code-row">
            <input v-model="form.kode_undangan" type="text" class="input" maxlength="20" placeholder="KST-8241" aria-label="Kode undangan">
            <button type="button" class="button button--outline" @click="generateCode"><AppIcon name="refresh" :size="16" /> Buat</button>
          </div>
        </section>

        <button type="submit" class="button button--primary button--block submit" :disabled="saving">
          {{ saving ? 'Menyimpan…' : exists ? 'Simpan Perubahan' : 'Buat Profil Kos' }}
        </button>
      </StateBlock>
    </form>
  </div>
</template>

<style scoped>
.panel {
  padding: 20px;
  margin-bottom: 14px;
}

.panel .panel-title {
  font-size: 20px;
}

.textarea--sm {
  min-height: 72px;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.row .field-label {
  font-size: 13px;
}

.code-row {
  display: flex;
  gap: 8px;
}

.code-row .input {
  flex: 1;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.notice {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding: 12px 16px;
  border-radius: 16px;
  background: var(--status-warning-bg);
  color: var(--status-warning-text);
  font-size: 13px;
}

.submit {
  padding: 14px;
}
</style>
