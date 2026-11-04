<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useModals } from '~/composables/useModals'
import AppHeader from '~/components/AppHeader.vue'
import AppFooter from '~/components/AppFooter.vue'
import ListingDetailModal from '~/components/ListingDetailModal.vue'
import FilterModal from '~/components/FilterModal.vue'
import SavedModal from '~/components/SavedModal.vue'
import MapModal from '~/components/MapModal.vue'
import ProfileModal from '~/components/ProfileModal.vue'
import PostAdModal from '~/components/PostAdModal.vue'
import RoommatesModal from '~/components/RoommatesModal.vue'
import CompareModal from '~/components/CompareModal.vue'
import NeighborhoodModal from '~/components/NeighborhoodModal.vue'
import AIAssistantWidget from '~/components/AIAssistantWidget.vue'
import ReportModal from '~/components/ReportModal.vue'

const { t } = useI18n()
const { count: favCount } = useFavorites()
const { selectedListing, filterCategory, fetchListings, compareList, clearCompare, runAiMatch } = useListings()
const {
  showFilters,
  showMap,
  showSaved,
  showProfile,
  showPostAd,
  showCompare,
  showRoommates,
  showNeighborhoods,
  showAssistant,
  showReport,
  reportingListingId,
  toastMessage,
  showToast,
} = useModals()

useHead({
  titleTemplate: (titleChunk) => {
    return titleChunk && !titleChunk.includes('Joyliy') ? `${titleChunk} — Joyliy.uz` : titleChunk || 'Joyliy — Toshkentda maklersiz ijara'
  },
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg', key: 'app-icon-svg' },
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico', key: 'app-icon-ico' },
    { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png', key: 'app-apple-touch-icon' },
  ],
})

const route = useRoute()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))

// Fetch initial listings on load
onMounted(async () => {
  if (!route.path.startsWith('/admin')) {
    await fetchListings()
  }
})

const onSelectListing = (item: ListingItem) => {
  selectedListing.value = item
}

const onFilterMaklersiz = () => {
  filterCategory.value = 'mk'
  const el = document.getElementById('katalog')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const bnActive = ref<'home' | 'search'>('home')
const bnHome = async () => {
  bnActive.value = 'home'
  if (route.path !== '/') await navigateTo('/')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
const bnSearch = async () => {
  bnActive.value = 'search'
  if (route.path !== '/') await navigateTo('/')
  window.scrollTo({ top: 0, behavior: 'smooth' })
  setTimeout(() => (document.getElementById('p-ai-in') as HTMLInputElement | null)?.focus({ preventScroll: true }), 450)
}

const onAssistantShowAll = async (q: string) => {
  showAssistant.value = false
  await runAiMatch(q)
  document.getElementById('katalog')?.scrollIntoView({ behavior: 'smooth' })
}

const scrollToResults = () => {
  const el = document.getElementById('katalog')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
// Body scroll and navigation lock when any modal is open
const isAnyModalOpen = computed(() => {
  return !!(
    selectedListing.value ||
    showFilters.value ||
    showMap.value ||
    showSaved.value ||
    showProfile.value ||
    showPostAd.value ||
    showCompare.value ||
    showRoommates.value ||
    showNeighborhoods.value ||
    showReport.value ||
    showAssistant.value
  )
})

watch(isAnyModalOpen, (open) => {
  if (import.meta.client) {
    if (open) {
      document.body.classList.add('modal-open')
    } else {
      document.body.classList.remove('modal-open')
    }
  }
}, { immediate: true })

onUnmounted(() => {
  if (import.meta.client) {
    document.body.classList.remove('modal-open')
  }
})
</script>

<template>
  <div v-if="isAdminRoute" class="admin-app-wrapper">
    <NuxtPage />
  </div>
  <div v-else class="app-layout">
    <AppHeader
      @openFavorites="showSaved = true"
      @openProfile="showProfile = true"
      @openNew="showPostAd = true"
      @filterMaklersiz="onFilterMaklersiz"
      @openMap="showMap = true"
      @openRoommates="showRoommates = true"
      @openCompare="showCompare = true"
      @openNeighborhoods="showNeighborhoods = true"
    />

    <main>
      <NuxtPage />
    </main>

    <AppFooter />

    <!-- Modals -->
    <ListingDetailModal
      :listing="selectedListing"
      @close="selectedListing = null"
      @toast="showToast"
    />

    <FilterModal
      :show="showFilters"
      @close="showFilters = false"
    />

    <SavedModal
      :show="showSaved"
      @close="showSaved = false"
      @select="onSelectListing"
    />

    <MapModal
      :show="showMap"
      @close="showMap = false"
      @select="onSelectListing"
    />

    <ProfileModal
      :show="showProfile"
      @close="showProfile = false"
      @toast="showToast"
    />

    <PostAdModal
      :show="showPostAd"
      @close="showPostAd = false"
      @toast="showToast"
    />

    <!-- Ecosystem Modals -->
    <RoommatesModal
      :show="showRoommates"
      @close="showRoommates = false"
      @toast="showToast"
    />

    <CompareModal
      :show="showCompare"
      @close="showCompare = false"
      @selectListing="onSelectListing"
    />

    <NeighborhoodModal
      :show="showNeighborhoods"
      @close="showNeighborhoods = false"
    />

    <ReportModal
      :show="showReport"
      :listingId="reportingListingId"
      @close="showReport = false"
      @toast="showToast"
    />

    <!-- AI Virtual Rental Advisor Floating Widget / Mobile Bottom Sheet -->
    <AIAssistantWidget
      :show="showAssistant"
      @close="showAssistant = false"
      @showAll="onAssistantShowAll"
    />

    <!-- Floating comparison tray -->
    <Transition name="tray">
      <div v-if="compareList.length > 0 && !showCompare" class="tray">
        <span class="tray-t">{{ compareList.length }} ta xonadon taqqoslashda</span>
        <button type="button" class="tray-go" :disabled="compareList.length < 2" @click="showCompare = true">{{ t('compare') }}</button>
        <button type="button" class="tray-x" :title="t('clear')" :aria-label="t('clear')" @click="clearCompare">×</button>
      </div>
    </Transition>

    <!-- Toast Notification -->
    <div v-if="toastMessage" class="toast">
      {{ toastMessage }}
    </div>

    <!-- Mobile Bottom Navigation (Floating Pill Capsule - Iconly Mobile Reference: ONLY ICONS) -->
    <nav class="bn" :aria-label="t('mobile_nav')">
      <button type="button" :class="{ on: bnActive === 'home' }" :aria-label="t('home')" :title="t('home')" @click="bnHome">
        <svg class="i" viewBox="0 0 24 24"><path d="M3 11l9-7 9 7" /><path d="M5 10v10h14V10" /></svg>
      </button>
      <button type="button" :class="{ on: bnActive === 'search' }" aria-label="Qidiruv" title="Qidiruv" @click="bnSearch">
        <svg class="i" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" /></svg>
      </button>
      <button type="button" class="btn-with-badge" :class="{ on: showCompare }" :aria-label="t('compare')" :title="t('compare')" @click="showCompare = true">
        <svg class="i" viewBox="0 0 24 24"><path d="M7 4v16M17 4v16M3 8h8M13 16h8" /></svg>
        <span v-if="compareList.length > 0" class="bn-badge">{{ compareList.length }}</span>
      </button>
      <button type="button" class="btn-with-badge" :class="{ on: showSaved }" :aria-label="t('saved')" :title="t('saved')" @click="showSaved = true">
        <svg class="i" viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" /></svg>
        <span v-if="favCount > 0" class="bn-badge">{{ favCount }}</span>
      </button>
      <button type="button" :class="{ on: showProfile }" :aria-label="t('profile')" :title="t('profile')" @click="showProfile = true">
        <svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" /></svg>
      </button>
    </nav>
  </div>
</template>

<style scoped>
.app-layout { min-height: 100vh; display: flex; flex-direction: column; }
main { flex: 1; }
.tray { position: fixed; left: 50%; bottom: calc(20px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%); z-index: 1050; display: flex; align-items: center; gap: 12px; padding: 8px 8px 8px 18px; border-radius: 999px; background: var(--accent-black); color: var(--on-ink); font: 600 13px var(--font-sans); box-shadow: var(--sh-floating); max-width: calc(100% - 220px); white-space: nowrap; }
.tray-go { border: 0; border-radius: 999px; padding: 9px 16px; background: var(--on-ink); color: var(--accent-black); font: 700 13px var(--font-sans); cursor: pointer; }
.tray-go:disabled { opacity: .5; cursor: not-allowed; }
.tray-x { border: 0; background: none; color: inherit; cursor: pointer; opacity: .7; font-size: 18px; width: 26px; height: 26px; }
.tray-enter-active, .tray-leave-active { transition: all .25s ease; }
.tray-enter-from, .tray-leave-to { opacity: 0; transform: translate(-50%, 20px); }
@media (max-width: 1023px) { .tray { display: none; } }
</style>
