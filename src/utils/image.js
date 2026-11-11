function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('Gambar tidak dapat dibaca. Coba pilih foto lain.'))
    }
    img.src = url
  })
}

function drawScaled(img, maxSize) {
  const scale = Math.min(1, maxSize / Math.max(img.width, img.height))
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(img.width * scale)
  canvas.height = Math.round(img.height * scale)
  canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
  return canvas
}

/** Perkecil foto (sisi terpanjang maks `maxSize` px) → Blob JPEG siap diunggah. */
export async function compressImageToBlob(file, maxSize = 1280, quality = 0.82) {
  const canvas = drawScaled(await loadImage(file), maxSize)
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error('Gagal memproses gambar.'))),
      'image/jpeg',
      quality,
    )
  })
}

/** Perkecil foto → data URL (untuk pratinjau lokal). */
export async function compressImage(file, maxSize = 960, quality = 0.8) {
  return drawScaled(await loadImage(file), maxSize).toDataURL('image/jpeg', quality)
}
