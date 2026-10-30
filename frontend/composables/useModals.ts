import { ref } from 'vue'

export function useModals() {
  const showFilters = useState<boolean>('modal_filters', () => false)
  const showMap = useState<boolean>('modal_map', () => false)
  const showSaved = useState<boolean>('modal_saved', () => false)
  const showProfile = useState<boolean>('modal_profile', () => false)
  const showPostAd = useState<boolean>('modal_post_ad', () => false)

  // Ecosystem modals
  const showCompare = useState<boolean>('modal_compare', () => false)
  const showRoommates = useState<boolean>('modal_roommates', () => false)
  const showNeighborhoods = useState<boolean>('modal_neighborhoods', () => false)
  const showAssistant = useState<boolean>('modal_assistant', () => false)
  const showReport = useState<boolean>('modal_report', () => false)
  const reportingListingId = useState<number | null>('reporting_listing_id', () => null)

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

  const openReportModal = (listingId: number) => {
    reportingListingId.value = listingId
    showReport.value = true
  }

  return {
    showFilters,
    showMap,
    showSaved,
    showProfile,
    showPostAd,

    // Ecosystem
    showCompare,
    showRoommates,
    showNeighborhoods,
    showAssistant,
    showReport,
    reportingListingId,
    openReportModal,

    toastMessage,
    showToast,
  }
}
