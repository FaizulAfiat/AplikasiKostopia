const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export const MIN_PASSWORD_LENGTH = 8

export function isValidEmail(value) {
  return EMAIL_PATTERN.test(value.trim())
}

/** Nomor HP Indonesia tanpa +62 / 0 di depan, 9–13 digit. */
export function normalizePhone(value) {
  return value.replace(/\D/g, '').replace(/^(62|0)/, '')
}

export function isValidPhone(value) {
  const digits = normalizePhone(value)
  return digits.length >= 9 && digits.length <= 13
}
