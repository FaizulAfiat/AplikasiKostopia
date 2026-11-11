<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { authApi } from '@/services/endpoints'
import {
  MIN_PASSWORD_LENGTH,
  isValidEmail,
  isValidPhone,
  normalizePhone,
} from '@/utils/validators'
import AppIcon from '@/components/AppIcon.vue'
import AppInput from '@/components/AppInput.vue'
import BrandLogo from '@/components/BrandLogo.vue'
import PageHeader from '@/components/PageHeader.vue'

const router = useRouter()
const ui = useUiStore()

const form = reactive({
  name: '',
  email: '',
  phone: '',
  password: '',
  confirm: '',
  agree: false,
  peran: 'Penghuni',
})

const ROLE_OPTIONS = [
  { value: 'Penghuni', label: 'Saya penghuni kos' },
  { value: 'Pemilik', label: 'Saya pemilik kos' },
]
const errors = reactive({ name: '', email: '', phone: '', password: '', confirm: '', agree: '' })
const submitting = ref(false)

function validate() {
  Object.keys(errors).forEach((key) => (errors[key] = ''))

  if (!form.name.trim()) errors.name = 'Nama lengkap wajib diisi.'
  if (!isValidEmail(form.email)) errors.email = 'Email tidak boleh kosong dan harus berformat valid.'
  if (!isValidPhone(form.phone)) errors.phone = 'Nomor HP harus 9–13 digit.'
  if (form.password.length < MIN_PASSWORD_LENGTH) {
    errors.password = `Kata sandi minimal ${MIN_PASSWORD_LENGTH} karakter.`
  }
  if (form.confirm !== form.password || !form.confirm) {
    errors.confirm = 'Konfirmasi kata sandi harus sama persis.'
  }
  if (!form.agree) errors.agree = 'Anda perlu menyetujui Tata Tertib Kos dan Kebijakan Privasi.'

  return Object.values(errors).every((message) => !message)
}

async function onSubmit() {
  if (submitting.value || !validate()) return

  submitting.value = true
  ui.showLoading('Mendaftarkan Akun', 'Menyimpan data diri Anda ke sistem Kostopia...')
  try {
    await authApi.register({
      nama_lengkap: form.name.trim(),
      email: form.email.trim().toLowerCase(),
      nomor_telepon: `0${normalizePhone(form.phone)}`,
      password: form.password,
      peran: form.peran,
    })
    ui.showToast('Akun berhasil didaftarkan! Silakan masuk.', 'success')
    router.push({ name: 'login' })
  } catch (error) {
    ui.showAlert('Pendaftaran Gagal', error.message, error.isNetwork ? 'network' : 'error')
  } finally {
    ui.hideLoading()
    submitting.value = false
  }
}
</script>

<template>
  <main class="screen">
    <div>
      <PageHeader :back-to="{ name: 'login' }">
        <BrandLogo :size="24" :radius="6" />
        <span class="overline">Registrasi Akun</span>
      </PageHeader>

      <div class="register__intro">
        <h1 class="title-editorial register__title">Buat Akun Kostopia</h1>
        <p class="subtitle">Daftarkan data diri Anda untuk terhubung ke sistem kos.</p>
      </div>

      <form class="form register__form" novalidate @submit.prevent="onSubmit">
        <div class="register__roles" role="radiogroup" aria-label="Daftar sebagai">
          <button
            v-for="option in ROLE_OPTIONS"
            :key="option.value"
            type="button"
            role="radio"
            class="register__role"
            :class="{ 'is-active': form.peran === option.value }"
            :aria-checked="form.peran === option.value"
            @click="form.peran = option.value"
          >
            {{ option.label }}
          </button>
        </div>

        <AppInput
          v-model="form.name"
          label="Nama Lengkap Sesuai KTP"
          required
          autocomplete="name"
          placeholder="Contoh: Fajar Pratama"
          :error="errors.name"
        />

        <AppInput
          v-model="form.email"
          label="Alamat Email Aktif"
          type="email"
          required
          autocomplete="email"
          placeholder="nama@email.com"
          :error="errors.email"
        />

        <AppInput
          v-model="form.phone"
          label="Nomor WhatsApp / HP"
          type="tel"
          prefix="+62"
          required
          autocomplete="tel-national"
          inputmode="numeric"
          placeholder="812-3456-7890"
          :error="errors.phone"
        />

        <AppInput
          v-model="form.password"
          label="Kata Sandi"
          type="password"
          required
          autocomplete="new-password"
          :placeholder="`Minimal ${MIN_PASSWORD_LENGTH} karakter kombinasi`"
          :error="errors.password"
        />

        <AppInput
          v-model="form.confirm"
          label="Konfirmasi Kata Sandi"
          type="password"
          required
          autocomplete="new-password"
          placeholder="Ulangi kata sandi Anda"
          :error="errors.confirm"
        />

        <div>
          <label class="checkbox register__agree">
            <input v-model="form.agree" type="checkbox" :aria-invalid="errors.agree ? 'true' : undefined">
            <span>
              Saya menyetujui <strong class="register__highlight">Tata Tertib Kos</strong> serta Kebijakan
              Privasi data Kostopia.
            </span>
          </label>
          <p v-if="errors.agree" class="register__agree-error">{{ errors.agree }}</p>
        </div>

        <button type="submit" class="btn btn-primary register__submit" :disabled="submitting">
          <span>Daftar Sekarang</span>
          <AppIcon name="arrow-right" />
        </button>
      </form>
    </div>

    <footer class="register__footer">
      Sudah memiliki akun?
      <RouterLink :to="{ name: 'login' }" class="link">Masuk di Sini</RouterLink>
    </footer>
  </main>
</template>

<style scoped>
.register__intro {
  margin-bottom: 20px;
}

.register__title {
  font-size: 24px;
}

.register__form {
  gap: 14px;
}

.register__roles {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  padding: 4px;
  background: var(--mist);
  border-radius: var(--radius-field);
}

.register__role {
  padding: 10px 8px;
  border: 0;
  border-radius: 11px;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: var(--slate);
}

.register__role.is-active {
  background: #fff;
  color: var(--crimson);
  box-shadow: var(--shadow-subtle);
}

.register__agree {
  font-size: 11px;
}

.register__highlight {
  font-weight: 500;
  color: var(--crimson);
}

.register__agree-error {
  margin-top: 4px;
  padding-left: 24px;
  font-size: 11px;
  font-weight: 500;
  color: var(--crimson);
}

.register__submit {
  margin-top: 8px;
}

.register__footer {
  font-size: 12px;
  color: var(--slate);
  text-align: center;
}

.register__footer .link {
  margin-left: 4px;
}
</style>
