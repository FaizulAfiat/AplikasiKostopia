<script setup>
import { computed, ref } from 'vue'
import { uploadFile, MAX_UPLOAD_MB } from '@/services/endpoints'
import { fileUrl } from '@/services/config'
import AppIcon from '@/components/AppIcon.vue'

/**
 * Pilih & langsung unggah foto ke backend (POST /files).
 *  - Satu foto:   <PhotoPicker v-model="form.foto_url" />            (string | null)
 *  - Banyak foto: <PhotoPicker v-model="form.lampiran" :max="3" multiple />  (string[])
 * Nilai yang disimpan adalah path dari server, mis. "/uploads/abc.jpg".
 */
const model = defineModel({ type: [String, Array, null], default: null })

const props = defineProps({
  multiple: { type: Boolean, default: false },
  max: { type: Number, default: 1 },
  accept: { type: String, default: 'image/*' },
  label: { type: String, default: 'Tambah foto' },
})

const uploading = ref(false)
const error = ref('')
const input = ref(null)

const items = computed(() => {
  if (props.multiple) return Array.isArray(model.value) ? model.value : []
  return model.value ? [model.value] : []
})
const canAdd = computed(() => items.value.length < (props.multiple ? props.max : 1))

function isPdf(path) {
  return /\.pdf($|\?)/i.test(path)
}

async function onSelected(event) {
  const files = Array.from(event.target.files ?? [])
  event.target.value = ''
  if (!files.length) return

  error.value = ''
  const room = props.multiple ? props.max - items.value.length : 1
  const picked = files.slice(0, room)
  if (files.length > room) error.value = `Maksimal ${props.max} file.`

  uploading.value = true
  try {
    const uploaded = []
    for (const file of picked) uploaded.push(await uploadFile(file))
    model.value = props.multiple ? [...items.value, ...uploaded] : uploaded[0]
  } catch (err) {
    error.value = err.message || 'Gagal mengunggah file.'
  } finally {
    uploading.value = false
  }
}

function remove(index) {
  if (props.multiple) model.value = items.value.filter((_, i) => i !== index)
  else model.value = null
}
</script>

<template>
  <div class="picker">
    <div class="picker__row">
      <div v-for="(path, index) in items" :key="path" class="picker__thumb">
        <a v-if="isPdf(path)" :href="fileUrl(path)" target="_blank" rel="noopener" class="picker__pdf">PDF</a>
        <img v-else :src="fileUrl(path)" alt="Pratinjau file terunggah">
        <button type="button" class="picker__remove" aria-label="Hapus file" @click="remove(index)">✕</button>
      </div>

      <button v-if="canAdd" type="button" class="picker__add" :disabled="uploading" @click="input.click()">
        <span v-if="uploading" class="picker__spinner" aria-hidden="true" />
        <AppIcon v-else name="plus" :size="20" />
        <span>{{ uploading ? 'Mengunggah…' : label }}</span>
      </button>
    </div>

    <input
      ref="input"
      type="file"
      class="sr-only"
      tabindex="-1"
      aria-hidden="true"
      :accept="accept"
      :multiple="multiple"
      @change="onSelected"
    >
    <p class="picker__hint">JPG, PNG{{ accept.includes('pdf') ? ', atau PDF' : '' }} · maksimal {{ MAX_UPLOAD_MB }} MB</p>
    <p v-if="error" class="field-error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.picker__row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.picker__thumb {
  position: relative;
  width: 88px;
  height: 88px;
}

.picker__thumb img,
.picker__pdf {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid var(--border);
  border-radius: 14px;
}

.picker__pdf {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--mist);
  font-weight: 700;
  color: var(--crimson);
}

.picker__remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  border-radius: 999px;
  background: var(--ink);
  color: #fff;
  font-size: 11px;
}

.picker__add {
  width: 88px;
  height: 88px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: var(--fog);
  border: 1px dashed #cdbfbc;
  border-radius: 14px;
  font-size: 11px;
  color: var(--slate);
}

.picker__add:disabled {
  cursor: progress;
}

.picker__spinner {
  width: 20px;
  height: 20px;
  border: 3px solid var(--mist);
  border-top-color: var(--crimson);
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

.picker__hint {
  margin-top: 6px;
  font-size: 11px;
  color: var(--slate);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
