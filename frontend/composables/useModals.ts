import { ref } from 'vue'

export function useModals() {
  const showFilters = useState<boolean>('modal_filters', () => false)
  const showMap = useState<boolean>('modal_map', () => false)
  const showSaved = useState<boolean>('modal_saved', () => false)
  const showProfile = useState<boolean>('modal_profile', () => false)
  const showPostAd = useState<boolean>('modal_post_ad', () => false)
  const toastMessage = useState<string | null>('toast_message', () => null)

  let toastTimer: any = null

  const showToast = (msg: string, duration = 3000) => {
    toastMessage.value = msg
    if (toastTimer) clearTimeout(toastTimer)
    if (import.meta.client) {
      toastTimer = setTimeout(() => {
        toastMessage.value = null
      }, duration)
    }
  }

  return {
    showFilters,
    showMap,
    showSaved,
    showProfile,
    showPostAd,
    toastMessage,
    showToast,
  }
}
