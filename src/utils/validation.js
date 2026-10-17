// Shared form validation helpers for auth pages.

// Practical email pattern: local@domain.tld (no spaces, a dot in the domain,
// TLD of at least 2 letters, no leading/trailing/double dots).
const EMAIL_REGEX =
  /^[A-Za-z0-9._%+-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,}$/

/**
 * Returns an error message (Indonesian) or '' when the email is valid.
 */
export function validateEmail(value) {
  const email = (value || '').trim()
  if (!email) return 'Email wajib diisi.'
  if (email.length > 254) return 'Email terlalu panjang.'
  if (!EMAIL_REGEX.test(email) || email.includes('..')) {
    return 'Format email tidak valid. Contoh: nama@gmail.com'
  }
  return ''
}

export function validatePassword(value, { minLength = 0 } = {}) {
  if (!value) return 'Kata sandi wajib diisi.'
  if (minLength && value.length < minLength) return `Kata sandi minimal ${minLength} karakter.`
  return ''
}

export function validatePhone(value) {
  const phone = (value || '').trim()
  if (!phone) return 'Nomor telepon wajib diisi.'
  if (!/^0\d{8,13}$/.test(phone)) return 'Nomor telepon tidak valid. Contoh: 081234567890'
  return ''
}

export function validateRequired(value, label) {
  return (value || '').trim() ? '' : `${label} wajib diisi.`
}
