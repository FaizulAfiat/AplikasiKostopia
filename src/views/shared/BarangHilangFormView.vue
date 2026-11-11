<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { barangHilangApi } from '@/services/endpoints'
import AppHeader from '@/components/app/AppHeader.vue'
import PhotoPicker from '@/components/app/PhotoPicker.vue'

/**
 * UC-15 langkah 3–6: pilih jenis (hilang/temuan), isi nama, deskripsi, lokasi, foto → Kirim.
 * Skenario alternatif 6a: nama barang kosong → sistem meminta nama barang diisi.
 */
const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

const boardRoute = computed(() => (auth.isOwner ? { name: 'pemilik-layanan', query: { tab: 'barang' } } : { name: 'penghuni-barang-hilang' }))

const typeOptions = computed(() => [
  { value: 'Hilang', label: auth.isOwner ? 'Kehilangan' : 'Saya kehilangan' },
  { value: 'Temuan', label: auth.isOwner ? 'Menemukan' : 'Saya menemukan' },
])

const form = reactive({
  jenis: auth.isOwner ? 'Temuan' : 'Hilang',
  judul_barang: '',
  deskripsi: '',
  lokasi: '',
  foto_url: null,
})
const nameError = ref('')
const nameInput = ref(null)
const submitting = ref(false)

const isLost = computed(() => form.jenis === 'Hilang')

async function onSubmit() {
  nameError.value = form.judul_barang.trim() ? '' : 'Nama barang wajib diisi.'
  if (nameError.value) {
    nameInput.value?.focus()
    return
  }
  if (submitting.value) return

  submitting.value = true
  try {
    await barangHilangApi.create({
      jenis: form.jenis,
      judul_barang: form.judul_barang.trim(),
      deskripsi: form.deskripsi.trim() || null,
      lokasi: form.lokasi.trim() || null,
      foto_url: form.foto_url,
    })
    ui.showToast('Laporan terkirim dan tampil di papan informasi.', 'success')
    router.replace(boardRoute.value)
  } catch (error) {
    if (error.status === 422) nameError.value = error.message
    ui.showError(error, 'Laporan Gagal Dikirim')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader :back="boardRoute" title="Buat laporan" subtitle="Tampil di papan informasi untuk semua penghuni & pemilik." />

    <form class="app-page app-page--plain form-stack" novalidate @submit.prevent="onSubmit">
      <fieldset class="lf-form__fieldset">
        <legend class="field-label">Jenis laporan</legend>
        <div class="lf-form__types" role="radiogroup">
          <button
            v-for="option in typeOptions"
            :key="option.value"
            type="button"
            role="radio"
            class="pill"
            :class="{ 'is-active': form.jenis === option.value }"
            :aria-checked="form.jenis === option.value"
            @click="form.jenis = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </fieldset>

      <div>
        <label for="lf-name" class="field-label">Nama barang <span class="req">*</span></label>
        <input
          id="lf-name"
          ref="nameInput"
          v-model="form.judul_barang"
          type="text"
          class="input"
          :class="{ 'is-invalid': nameError }"
          maxlength="80"
          :placeholder="isLost ? 'Contoh: Dompet kulit cokelat' : 'Contoh: Helm hitam KYT'"
          :aria-invalid="nameError ? 'true' : undefined"
          aria-describedby="lf-name-error"
          @input="nameError = ''"
        >
        <p v-if="nameError" id="lf-name-error" class="field-error" role="alert">{{ nameError }}</p>
      </div>

      <div>
        <label for="lf-desc" class="field-label">Deskripsi</label>
        <textarea id="lf-desc" v-model="form.deskripsi" class="textarea" maxlength="500" placeholder="Ciri-ciri barang: warna, merek, isi..." />
      </div>

      <div>
        <label for="lf-location" class="field-label">{{ isLost ? 'Lokasi terakhir terlihat' : 'Lokasi ditemukan' }}</label>
        <input
          id="lf-location"
          v-model="form.lokasi"
          type="text"
          class="input"
          maxlength="120"
          :placeholder="isLost ? 'Contoh: Dapur bersama lantai 1' : 'Contoh: Pos jaga depan'"
        >
      </div>

      <div>
        <p class="field-label">Foto <span class="field-label__hint">— membantu orang lain mengenali barang</span></p>
        <PhotoPicker v-model="form.foto_url" />
      </div>

      <button type="submit" class="button button--primary button--block" :disabled="submitting">
        {{ submitting ? 'Mengirim…' : 'Kirim Laporan' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.lf-form__fieldset {
  margin: 0;
  padding: 0;
  border: 0;
}

.lf-form__fieldset legend {
  padding: 0;
}

.lf-form__types {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.lf-form__types .pill {
  border-radius: 12px;
  padding: 11px 12px;
}
</style>
