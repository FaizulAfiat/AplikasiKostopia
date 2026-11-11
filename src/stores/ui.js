import { ref } from 'vue'
import { defineStore } from 'pinia'

// State global untuk toast, indikator loading, dan dialog peringatan.
export const useUiStore = defineStore('ui', () => {
  const toast = ref({ visible: false, message: '', type: 'info' })
  const loading = ref({ visible: false, title: '', description: '' })
  const alert = ref({ visible: false, title: '', description: '', variant: 'error' })

  let toastTimer = null

  function showToast(message, type = 'info') {
    toast.value = { visible: true, message, type }
    clearTimeout(toastTimer)
    toastTimer = setTimeout(hideToast, 3500)
  }

  function hideToast() {
    clearTimeout(toastTimer)
    toast.value.visible = false
  }

  function showLoading(title = 'Memproses', description = '') {
    loading.value = { visible: true, title, description }
  }

  function hideLoading() {
    loading.value.visible = false
  }

  /** @param {'error' | 'network'} variant */
  function showAlert(title, description, variant = 'error') {
    alert.value = { visible: true, title, description, variant }
  }

  function closeAlert() {
    alert.value.visible = false
  }

  // ---------- Dialog konfirmasi (Promise<boolean>) ----------
  const confirmState = ref({ visible: false, title: '', description: '', confirmLabel: 'Ya', tone: 'primary' })
  let confirmResolver = null

  /**
   * const ok = await ui.confirm('Hapus pengumuman?', 'Tindakan ini tidak dapat dibatalkan.', { confirmLabel: 'Hapus', tone: 'danger' })
   */
  function confirm(title, description = '', { confirmLabel = 'Ya, lanjutkan', tone = 'primary' } = {}) {
    confirmResolver?.(false)
    confirmState.value = { visible: true, title, description, confirmLabel, tone }
    return new Promise((resolve) => {
      confirmResolver = resolve
    })
  }

  function resolveConfirm(result) {
    confirmState.value.visible = false
    confirmResolver?.(result)
    confirmResolver = null
  }

  /** Tampilkan error dari API (ApiError) dengan judul yang sesuai. */
  function showError(error, title = 'Terjadi Kendala') {
    if (error?.isNetwork) showAlert('Koneksi Terputus', error.message, 'network')
    else showAlert(title, error?.message || 'Terjadi kesalahan. Coba lagi.')
  }

  return {
    confirmState,
    confirm,
    resolveConfirm,
    showError,
    toast,
    loading,
    alert,
    showToast,
    hideToast,
    showLoading,
    hideLoading,
    showAlert,
    closeAlert,
  }
})
