import { onMounted, ref, shallowRef } from 'vue'

/**
 * Muat data dari API dengan status loading/error standar.
 *
 *   const { data, loading, error, reload } = useResource(() => tagihanApi.list())
 *
 * @template T
 * @param {() => Promise<T>} fetcher
 * @param {{ immediate?: boolean, initial?: T }} [options]
 */
export function useResource(fetcher, { immediate = true, initial = null } = {}) {
  const data = shallowRef(initial)
  const loading = ref(false)
  const error = ref(null)
  let requestId = 0

  async function reload() {
    const id = ++requestId
    loading.value = true
    error.value = null
    try {
      const result = await fetcher()
      if (id === requestId) data.value = result
      return result
    } catch (err) {
      if (id === requestId) error.value = err
      return null
    } finally {
      if (id === requestId) loading.value = false
    }
  }

  if (immediate) onMounted(reload)

  return { data, loading, error, reload }
}
