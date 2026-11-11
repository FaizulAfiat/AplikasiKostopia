<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useLogout } from '@/composables/useLogout'
import { useResource } from '@/composables/useResource'
import { authApi, kendaraanApi } from '@/services/endpoints'
import AppHeader from '@/components/app/AppHeader.vue'
import BottomSheet from '@/components/app/BottomSheet.vue'
import StateBlock from '@/components/app/StateBlock.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import AppIcon from '@/components/AppIcon.vue'

const auth = useAuthStore()
const ui = useUiStore()
const logout = useLogout()

const isTenant = computed(() => !auth.isOwner)
const backRoute = computed(() => ({ name: auth.isOwner ? 'pemilik-lainnya' : 'penghuni-beranda' }))
const roleLabel = computed(() => {
  if (auth.isOwner) return 'Pemilik kos'
  return auth.user?.kamar ? `Penghuni · Kamar ${auth.user.kamar}` : 'Penghuni'
})

// ---------- Data diri ----------
const profile = reactive({
  nama_lengkap: '',
  nomor_telepon: '',
  asal_kampus: '',
  kontak_darurat_nama: '',
  kontak_darurat_telepon: '',
})
const profileErrors = reactive({ nama_lengkap: '', nomor_telepon: '' })
const savingProfile = ref(false)

function fillProfile(user) {
  if (!user) return
  Object.keys(profile).forEach((key) => (profile[key] = user[key] ?? ''))
}

watch(() => auth.user, fillProfile, { immediate: true })

onMounted(() => {
  // Segarkan data akun di latar belakang; abaikan jika gagal
  auth.refresh().catch(() => {})
})

const PHONE_RE = /^\+?[0-9\s-]{8,16}$/

async function saveProfile() {
  profileErrors.nama_lengkap = profile.nama_lengkap.trim() ? '' : 'Nama lengkap wajib diisi.'
  profileErrors.nomor_telepon = !profile.nomor_telepon.trim() || PHONE_RE.test(profile.nomor_telepon.trim())
    ? ''
    : 'Nomor telepon tidak valid.'
  if (profileErrors.nama_lengkap || profileErrors.nomor_telepon || savingProfile.value) return

  const payload = {
    nama_lengkap: profile.nama_lengkap.trim(),
    nomor_telepon: profile.nomor_telepon.trim(),
  }
  if (isTenant.value) {
    payload.asal_kampus = profile.asal_kampus.trim() || null
    payload.kontak_darurat_nama = profile.kontak_darurat_nama.trim() || null
    payload.kontak_darurat_telepon = profile.kontak_darurat_telepon.trim() || null
  }

  savingProfile.value = true
  try {
    await auth.updateProfile(payload)
    ui.showToast('Data diri disimpan', 'success')
  } catch (error) {
    ui.showError(error, 'Gagal Menyimpan')
  } finally {
    savingProfile.value = false
  }
}

// ---------- Kendaraan (Penghuni) ----------
const vehicles = useResource(() => kendaraanApi.list(), { immediate: false, initial: [] })
onMounted(() => {
  if (isTenant.value) vehicles.reload()
})

const vehicleSheet = ref(false)
const vehicleForm = reactive({ jenis_kendaraan: 'Motor', nomor_polisi: '', merk_warna: '' })
const vehicleError = ref('')
const savingVehicle = ref(false)
const deletingId = ref(null)

function openVehicleSheet() {
  Object.assign(vehicleForm, { jenis_kendaraan: 'Motor', nomor_polisi: '', merk_warna: '' })
  vehicleError.value = ''
  vehicleSheet.value = true
}

async function saveVehicle() {
  const plat = vehicleForm.nomor_polisi.trim().toUpperCase().replace(/\s+/g, ' ')
  vehicleError.value = plat ? '' : 'Nomor polisi wajib diisi.'
  if (vehicleError.value || savingVehicle.value) return

  savingVehicle.value = true
  try {
    const created = await kendaraanApi.create({
      jenis_kendaraan: vehicleForm.jenis_kendaraan,
      nomor_polisi: plat,
      merk_warna: vehicleForm.merk_warna.trim() || null,
    })
    vehicles.data.value = [...(vehicles.data.value ?? []), created]
    vehicleSheet.value = false
    ui.showToast('Kendaraan ditambahkan', 'success')
  } catch (error) {
    if (error.status === 400 || error.status === 422) vehicleError.value = error.message
    else ui.showError(error, 'Gagal Menambah Kendaraan')
  } finally {
    savingVehicle.value = false
  }
}

async function removeVehicle(vehicle) {
  const ok = await ui.confirm(
    `Hapus ${vehicle.nomor_polisi}?`,
    'Kendaraan ini tidak lagi terdaftar di parkir kos.',
    { confirmLabel: 'Hapus', tone: 'danger' },
  )
  if (!ok) return
  deletingId.value = vehicle.id
  try {
    await kendaraanApi.remove(vehicle.id)
    vehicles.data.value = vehicles.data.value.filter((v) => v.id !== vehicle.id)
    ui.showToast('Kendaraan dihapus', 'success')
  } catch (error) {
    ui.showError(error, 'Gagal Menghapus')
  } finally {
    deletingId.value = null
  }
}

// ---------- Ganti kata sandi ----------
const passwordSheet = ref(false)
const passwordForm = reactive({ lama: '', baru: '', konfirmasi: '' })
const passwordErrors = reactive({ lama: '', baru: '', konfirmasi: '' })
const savingPassword = ref(false)

function openPasswordSheet() {
  Object.assign(passwordForm, { lama: '', baru: '', konfirmasi: '' })
  Object.assign(passwordErrors, { lama: '', baru: '', konfirmasi: '' })
  passwordSheet.value = true
}

async function savePassword() {
  passwordErrors.lama = passwordForm.lama ? '' : 'Kata sandi lama wajib diisi.'
  passwordErrors.baru = passwordForm.baru.length >= 8 ? '' : 'Kata sandi baru minimal 8 karakter.'
  passwordErrors.konfirmasi = passwordForm.konfirmasi === passwordForm.baru ? '' : 'Konfirmasi kata sandi tidak sama.'
  if (passwordErrors.lama || passwordErrors.baru || passwordErrors.konfirmasi || savingPassword.value) return

  savingPassword.value = true
  try {
    await authApi.changePassword(passwordForm.lama, passwordForm.baru)
    passwordSheet.value = false
    ui.showToast('Kata sandi berhasil diubah', 'success')
  } catch (error) {
    if (error.status === 400) passwordErrors.lama = error.message
    else if (error.status === 422) passwordErrors.baru = error.message
    else ui.showError(error, 'Gagal Mengubah Kata Sandi')
  } finally {
    savingPassword.value = false
  }
}

// ---------- Keluar ----------
async function confirmLogout() {
  const ok = await ui.confirm('Keluar dari akun?', 'Anda perlu masuk lagi untuk menggunakan Kostopia.', {
    confirmLabel: 'Keluar',
    tone: 'danger',
  })
  if (ok) logout()
}
</script>

<template>
  <div>
    <AppHeader :back="backRoute" title="Akun saya" />

    <div class="app-page app-page--plain">
      <!-- Identitas -->
      <section class="akun__id">
        <UserAvatar :name="auth.user?.nama_lengkap" :size="64" tone="crimson" />
        <div class="akun__id-text">
          <h2 class="akun__name">{{ auth.user?.nama_lengkap || '—' }}</h2>
          <p class="akun__role">{{ roleLabel }}</p>
          <p class="akun__email">{{ auth.user?.email }}</p>
        </div>
      </section>

      <!-- Data diri -->
      <form class="panel form-stack" novalidate @submit.prevent="saveProfile">
        <h2 class="panel-title akun__panel-title">Data diri</h2>

        <div>
          <label for="ak-nama" class="field-label">Nama lengkap <span class="req">*</span></label>
          <input
            id="ak-nama"
            v-model="profile.nama_lengkap"
            type="text"
            class="input"
            :class="{ 'is-invalid': profileErrors.nama_lengkap }"
            autocomplete="name"
            maxlength="100"
            @input="profileErrors.nama_lengkap = ''"
          >
          <p v-if="profileErrors.nama_lengkap" class="field-error" role="alert">{{ profileErrors.nama_lengkap }}</p>
        </div>

        <div>
          <label for="ak-telp" class="field-label">Nomor telepon</label>
          <input
            id="ak-telp"
            v-model="profile.nomor_telepon"
            type="tel"
            inputmode="tel"
            class="input"
            :class="{ 'is-invalid': profileErrors.nomor_telepon }"
            autocomplete="tel"
            placeholder="08xxxxxxxxxx"
            @input="profileErrors.nomor_telepon = ''"
          >
          <p v-if="profileErrors.nomor_telepon" class="field-error" role="alert">{{ profileErrors.nomor_telepon }}</p>
        </div>

        <template v-if="isTenant">
          <div>
            <label for="ak-kampus" class="field-label">Asal kampus / instansi</label>
            <input
              id="ak-kampus"
              v-model="profile.asal_kampus"
              type="text"
              class="input"
              maxlength="120"
              placeholder="Contoh: Telkom University · Informatika"
            >
          </div>

          <p class="section-label akun__subhead">Kontak darurat</p>
          <div>
            <label for="ak-darurat-nama" class="field-label">Nama</label>
            <input
              id="ak-darurat-nama"
              v-model="profile.kontak_darurat_nama"
              type="text"
              class="input"
              maxlength="100"
              placeholder="Contoh: Ibu Siti (orang tua)"
            >
          </div>
          <div>
            <label for="ak-darurat-telp" class="field-label">Nomor telepon</label>
            <input
              id="ak-darurat-telp"
              v-model="profile.kontak_darurat_telepon"
              type="tel"
              inputmode="tel"
              class="input"
              placeholder="08xxxxxxxxxx"
            >
          </div>
        </template>

        <button type="submit" class="button button--primary button--block" :disabled="savingProfile">
          {{ savingProfile ? 'Menyimpan…' : 'Simpan Perubahan' }}
        </button>
      </form>

      <!-- Kendaraan -->
      <section v-if="isTenant" class="panel" aria-labelledby="veh-title">
        <div class="akun__panel-head">
          <h2 id="veh-title" class="panel-title akun__panel-title">Kendaraan saya</h2>
          <button type="button" class="button button--outline button--sm" @click="openVehicleSheet">
            <AppIcon name="plus" :size="14" /> Tambah
          </button>
        </div>
        <p class="panel-desc">Daftarkan kendaraan agar mendapat slot parkir. Motor pertama gratis.</p>

        <StateBlock
          :loading="vehicles.loading.value"
          :error="vehicles.error.value"
          :has-data="vehicles.data.value.length > 0"
          :empty="!vehicles.data.value.length"
          empty-icon="vehicle"
          empty-title="Belum ada kendaraan"
          @retry="vehicles.reload"
        >
          <ul class="vehicles">
            <li v-for="v in vehicles.data.value" :key="v.id" class="vehicle">
              <span class="vehicle__icon"><AppIcon name="vehicle" :size="20" /></span>
              <div class="vehicle__body">
                <p class="vehicle__plate">{{ v.nomor_polisi }}</p>
                <p class="vehicle__meta">
                  {{ [v.jenis_kendaraan, v.merk_warna].filter(Boolean).join(' · ') }}
                </p>
                <p class="vehicle__slot">{{ v.slot_parkir ? `Slot parkir ${v.slot_parkir}` : 'Slot parkir belum ditentukan' }}</p>
              </div>
              <button
                type="button"
                class="vehicle__delete"
                :disabled="deletingId === v.id"
                :aria-label="`Hapus ${v.nomor_polisi}`"
                @click="removeVehicle(v)"
              >
                <AppIcon name="trash" :size="18" />
              </button>
            </li>
          </ul>
        </StateBlock>
      </section>

      <!-- Keamanan & pengaturan -->
      <nav class="akun__links" aria-label="Pengaturan akun">
        <button type="button" class="akun__link" @click="openPasswordSheet">
          <AppIcon name="key" :size="18" />
          <span>Ganti kata sandi</span>
          <AppIcon name="chevron-right" :size="16" class="akun__link-chevron" />
        </button>
        <RouterLink :to="{ name: 'server-settings' }" class="akun__link">
          <AppIcon name="settings" :size="18" />
          <span>Pengaturan Server</span>
          <AppIcon name="chevron-right" :size="16" class="akun__link-chevron" />
        </RouterLink>
      </nav>

      <button type="button" class="button button--danger-outline button--block akun__logout" @click="confirmLogout">
        <AppIcon name="logout" :size="16" /> Keluar
      </button>
    </div>

    <!-- Sheet: tambah kendaraan -->
    <BottomSheet v-model:open="vehicleSheet" title="Tambah kendaraan" description="Data dipakai pemilik untuk mengatur parkir.">
      <form class="form-stack" novalidate @submit.prevent="saveVehicle">
        <fieldset class="akun__fieldset">
          <legend class="field-label">Jenis kendaraan</legend>
          <div class="akun__types" role="radiogroup">
            <button
              v-for="jenis in ['Motor', 'Mobil']"
              :key="jenis"
              type="button"
              role="radio"
              class="pill"
              :class="{ 'is-active': vehicleForm.jenis_kendaraan === jenis }"
              :aria-checked="vehicleForm.jenis_kendaraan === jenis"
              @click="vehicleForm.jenis_kendaraan = jenis"
            >
              {{ jenis }}
            </button>
          </div>
        </fieldset>
        <div>
          <label for="veh-plat" class="field-label">Nomor polisi <span class="req">*</span></label>
          <input
            id="veh-plat"
            v-model="vehicleForm.nomor_polisi"
            type="text"
            class="input akun__plate-input"
            :class="{ 'is-invalid': vehicleError }"
            maxlength="12"
            autocapitalize="characters"
            placeholder="D 4521 ABC"
            @input="vehicleForm.nomor_polisi = vehicleForm.nomor_polisi.toUpperCase(); vehicleError = ''"
          >
          <p v-if="vehicleError" class="field-error" role="alert">{{ vehicleError }}</p>
        </div>
        <div>
          <label for="veh-merk" class="field-label">Merk & warna</label>
          <input id="veh-merk" v-model="vehicleForm.merk_warna" type="text" class="input" maxlength="60" placeholder="Contoh: Honda Beat · Hitam">
        </div>
        <button type="submit" class="button button--primary button--block" :disabled="savingVehicle">
          {{ savingVehicle ? 'Menyimpan…' : 'Simpan Kendaraan' }}
        </button>
      </form>
    </BottomSheet>

    <!-- Sheet: ganti kata sandi -->
    <BottomSheet v-model:open="passwordSheet" title="Ganti kata sandi" description="Minimal 8 karakter.">
      <form class="form-stack" novalidate @submit.prevent="savePassword">
        <div>
          <label for="pw-lama" class="field-label">Kata sandi lama</label>
          <input
            id="pw-lama"
            v-model="passwordForm.lama"
            type="password"
            class="input"
            :class="{ 'is-invalid': passwordErrors.lama }"
            autocomplete="current-password"
            @input="passwordErrors.lama = ''"
          >
          <p v-if="passwordErrors.lama" class="field-error" role="alert">{{ passwordErrors.lama }}</p>
        </div>
        <div>
          <label for="pw-baru" class="field-label">Kata sandi baru</label>
          <input
            id="pw-baru"
            v-model="passwordForm.baru"
            type="password"
            class="input"
            :class="{ 'is-invalid': passwordErrors.baru }"
            autocomplete="new-password"
            @input="passwordErrors.baru = ''"
          >
          <p v-if="passwordErrors.baru" class="field-error" role="alert">{{ passwordErrors.baru }}</p>
        </div>
        <div>
          <label for="pw-konfirmasi" class="field-label">Konfirmasi kata sandi baru</label>
          <input
            id="pw-konfirmasi"
            v-model="passwordForm.konfirmasi"
            type="password"
            class="input"
            :class="{ 'is-invalid': passwordErrors.konfirmasi }"
            autocomplete="new-password"
            @input="passwordErrors.konfirmasi = ''"
          >
          <p v-if="passwordErrors.konfirmasi" class="field-error" role="alert">{{ passwordErrors.konfirmasi }}</p>
        </div>
        <button type="submit" class="button button--primary button--block" :disabled="savingPassword">
          {{ savingPassword ? 'Menyimpan…' : 'Ubah Kata Sandi' }}
        </button>
      </form>
    </BottomSheet>
  </div>
</template>

<style scoped>
.akun__id {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 4px 4px 8px;
}

.akun__id-text {
  min-width: 0;
}

.akun__name {
  font-family: var(--font-editorial);
  font-size: 24px;
  font-weight: 400;
  line-height: 1.2;
}

.akun__role {
  margin-top: 2px;
  font-size: 13px;
  font-weight: 600;
  color: var(--crimson);
}

.akun__email {
  margin-top: 2px;
  overflow: hidden;
  font-size: 13px;
  color: var(--slate);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.akun__panel-title {
  font-size: 22px;
}

.akun__panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.akun__subhead {
  margin-top: 6px;
}

.vehicles {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.vehicle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--mist);
  border-radius: 18px;
}

.vehicle__icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #fff;
  color: var(--crimson);
}

.vehicle__body {
  flex: 1;
  min-width: 0;
}

.vehicle__plate {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.vehicle__meta,
.vehicle__slot {
  font-size: 12px;
  color: var(--slate);
}

.vehicle__delete {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--crimson);
}

.vehicle__delete:disabled {
  opacity: 0.4;
}

.akun__links {
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
}

.akun__link {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border: 0;
  border-bottom: 1px solid var(--border);
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  text-align: left;
}

.akun__link:last-child {
  border-bottom: 0;
}

.akun__link:active {
  background: var(--fog);
}

.akun__link span {
  flex: 1;
}

.akun__link-chevron {
  color: var(--slate);
}

.akun__logout {
  padding: 13px 18px;
}

.akun__fieldset {
  margin: 0;
  padding: 0;
  border: 0;
}

.akun__fieldset legend {
  padding: 0;
}

.akun__types {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.akun__types .pill {
  padding: 11px 12px;
  border-radius: 12px;
}

.akun__plate-input {
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
</style>
