<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { aspirasiApi } from '@/services/endpoints'
import AppHeader from '@/components/app/AppHeader.vue'
import PhotoPicker from '@/components/app/PhotoPicker.vue'

const router = useRouter()
const ui = useUiStore()

const KATEGORI = ['Kerusakan', 'Fasilitas', 'Kebersihan', 'Keamanan', 'Saran']

const form = reactive({ kategori: 'Kerusakan', judul: '', deskripsi_kendala: '', lampiran_foto_urls: [] })
const errors = reactive({ judul: '', deskripsi_kendala: '' })
const titleInput = ref(null)
const descInput = ref(null)
const submitting = ref(false)

async function onSubmit() {
  errors.judul = form.judul.trim() ? '' : 'Judul wajib diisi.'
  errors.deskripsi_kendala = form.deskripsi_kendala.trim() ? '' : 'Deskripsi kendala wajib diisi.'
  if (errors.judul) return titleInput.value?.focus()
  if (errors.deskripsi_kendala) return descInput.value?.focus()
  if (submitting.value) return

  submitting.value = true
  try {
    await aspirasiApi.create({
      kategori: form.kategori,
      judul: form.judul.trim(),
      deskripsi_kendala: form.deskripsi_kendala.trim(),
      lampiran_foto_urls: form.lampiran_foto_urls,
    })
    ui.showToast('Laporan terkirim ke pemilik kos.', 'success')
    router.replace({ name: 'penghuni-layanan' })
  } catch (error) {
    ui.showError(error, 'Laporan Gagal Dikirim')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <AppHeader
      :back="{ name: 'penghuni-layanan' }"
      title="Buat laporan"
      subtitle="Keluhan, kerusakan fasilitas, atau saran untuk pemilik kos."
    />

    <form class="app-page app-page--plain form-stack" novalidate @submit.prevent="onSubmit">
      <div>
        <label for="asp-kategori" class="field-label">Kategori</label>
        <select id="asp-kategori" v-model="form.kategori" class="select">
          <option v-for="item in KATEGORI" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>

      <div>
        <label for="asp-judul" class="field-label">Judul <span class="req">*</span></label>
        <input
          id="asp-judul"
          ref="titleInput"
          v-model="form.judul"
          type="text"
          class="input"
          :class="{ 'is-invalid': errors.judul }"
          maxlength="100"
          placeholder="Contoh: Keran kamar mandi bocor"
          :aria-invalid="errors.judul ? 'true' : undefined"
          @input="errors.judul = ''"
        >
        <p v-if="errors.judul" class="field-error" role="alert">{{ errors.judul }}</p>
      </div>

      <div>
        <label for="asp-desc" class="field-label">Deskripsi kendala <span class="req">*</span></label>
        <textarea
          id="asp-desc"
          ref="descInput"
          v-model="form.deskripsi_kendala"
          class="textarea"
          :class="{ 'is-invalid': errors.deskripsi_kendala }"
          rows="5"
          maxlength="1000"
          placeholder="Jelaskan apa yang terjadi dan di mana lokasinya..."
          :aria-invalid="errors.deskripsi_kendala ? 'true' : undefined"
          @input="errors.deskripsi_kendala = ''"
        />
        <p v-if="errors.deskripsi_kendala" class="field-error" role="alert">{{ errors.deskripsi_kendala }}</p>
      </div>

      <div>
        <p class="field-label">Foto lampiran <span class="field-label__hint">— opsional, maks 3</span></p>
        <PhotoPicker v-model="form.lampiran_foto_urls" multiple :max="3" />
      </div>

      <button type="submit" class="button button--primary button--block" :disabled="submitting">
        {{ submitting ? 'Mengirim…' : 'Kirim Laporan' }}
      </button>
    </form>
  </div>
</template>
