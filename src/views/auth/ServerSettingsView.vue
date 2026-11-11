<script setup>
import { ref } from 'vue'
import { defaultServerUrl, getServerUrl, setServerUrl } from '@/services/config'
import { useUiStore } from '@/stores/ui'
import AppHeader from '@/components/app/AppHeader.vue'

const ui = useUiStore()

const url = ref(getServerUrl())
const testing = ref(false)
const result = ref(null)

async function testConnection() {
  testing.value = true
  result.value = null
  try {
    const response = await fetch(`${url.value.trim().replace(/\/+$/, '')}/api/v1/health`)
    result.value = response.ok
      ? { ok: true, text: 'Terhubung ke server Kostopia.' }
      : { ok: false, text: `Server menjawab dengan status ${response.status}.` }
  } catch {
    result.value = { ok: false, text: 'Tidak dapat terhubung. Periksa alamat, Wi-Fi, dan pastikan server menyala.' }
  } finally {
    testing.value = false
  }
}

function save() {
  setServerUrl(url.value)
  url.value = getServerUrl()
  ui.showToast('Alamat server disimpan', 'success')
}

function reset() {
  setServerUrl('')
  url.value = defaultServerUrl()
  result.value = null
}
</script>

<template>
  <div class="auth-stage-page">
    <AppHeader back title="Pengaturan Server" subtitle="Alamat backend Kostopia (FastAPI)" />

    <div class="app-page app-page--plain">
      <div class="panel form-stack">
        <div>
          <label for="server-url" class="field-label">Alamat server</label>
          <input id="server-url" v-model="url" type="url" class="input" inputmode="url" placeholder="http://192.168.1.10:8000">
          <p class="hint">
            Emulator Android: <code>http://10.0.2.2:8000</code><br>
            HP sungguhan: <code>http://&lt;IP laptop&gt;:8000</code> (HP & laptop di Wi-Fi yang sama)
          </p>
        </div>

        <p v-if="result" class="result" :class="result.ok ? 'is-ok' : 'is-fail'" role="status">{{ result.text }}</p>

        <div class="form-actions">
          <button type="button" class="button button--outline" :disabled="testing" @click="testConnection">
            {{ testing ? 'Menguji…' : 'Uji koneksi' }}
          </button>
          <button type="button" class="button button--dark" @click="save">Simpan</button>
        </div>
        <button type="button" class="link reset" @click="reset">Kembalikan ke bawaan</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hint {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--slate);
}

code {
  padding: 1px 6px;
  border-radius: 6px;
  background: var(--mist);
  font-size: 12px;
}

.result {
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
}

.result.is-ok {
  background: var(--status-success-bg);
  color: var(--status-success-text);
}

.result.is-fail {
  background: var(--status-danger-bg);
  color: var(--status-danger-text);
}

.reset {
  align-self: center;
  font-weight: 500;
  color: var(--slate);
}
</style>
