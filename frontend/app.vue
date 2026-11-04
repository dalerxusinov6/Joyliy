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
const { selectedListing, filterCategory, fetchListings, compareList, clearCompare } = useListings()
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
    />

    <!-- Floating Comparison Bar -->
    <Transition name="slide-fade">
      <div v-if="compareList.length > 0 && !showCompare" class="floating-compare-bar">
        <div class="fc-left">
          <span class="fc-pill">
            <svg class="fc-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="M7 21h10"/>
              <path d="M12 3v18"/>
              <path d="M3 7h18"/>
            </svg>
            <span>{{ compareList.length }}</span>
          </span>
          <span class="fc-label">{{ t('compare_floating_label') }}</span>
        </div>
        <div class="fc-right">
          <button class="fc-btn-view" @click="showCompare = true">
            {{ t('compare') }}
          </button>
          <button class="fc-btn-clear" @click="clearCompare" :title="t('clear')" :aria-label="t('clear')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="fc-close-svg">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>

    <!-- Toast Notification -->
    <div v-if="toastMessage" class="toast">
      {{ toastMessage }}
    </div>

    <!-- Mobile Bottom Navigation (Floating Pill Capsule - Iconly Mobile Reference: ONLY ICONS) -->
    <nav class="bn" :aria-label="t('mobile_nav')">
      <button type="button" :class="{ on: bnActive === 'home' }" :aria-label="t('home')" @click="bnHome">
        <svg class="i" viewBox="0 0 24 24"><path d="M3 11l9-7 9 7" /><path d="M5 10v10h14V10" /></svg>
        <span class="bn-l">{{ t('home') }}</span>
      </button>
      <button type="button" :class="{ on: bnActive === 'search' }" aria-label="Qidiruv" @click="bnSearch">
        <svg class="i" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" /></svg>
        <span class="bn-l">Qidiruv</span>
      </button>
      <button type="button" class="btn-with-badge" :class="{ on: showSaved }" :aria-label="t('saved')" @click="showSaved = true">
        <svg class="i" viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" /></svg>
        <span class="bn-l">{{ t('saved') }}</span>
        <span v-if="favCount > 0" class="bn-badge">{{ favCount }}</span>
      </button>
      <button type="button" :class="{ on: showProfile }" :aria-label="t('profile')" @click="showProfile = true">
        <svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" /></svg>
        <span class="bn-l">{{ t('profile') }}</span>
      </button>
    </nav>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
main {
  flex: 1;
}

.floating-compare-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1050;
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--accent-black);
  color: var(--on-ink);
  padding: 8px 10px 8px 16px;
  border-radius: var(--radius-full, 9999px);
  box-shadow: 0 12px 32px rgba(23, 25, 29, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.15);
  white-space: nowrap;
}

@media (max-width: 767px) {
  /* On mobile, comparison is integrated into bottom nav capsule with counter badge */
  .floating-compare-bar {
    display: none !important;
  }
}

.fc-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.fc-pill {
  background: var(--blue-primary, #514437);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  font-family: var(--font-mono);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.fc-svg {
  width: 13px;
  height: 13px;
}

.fc-close-svg {
  width: 12px;
  height: 12px;
}

.fc-label {
  font-size: 13px;
  font-weight: 600;
}

.fc-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.fc-btn-view {
  background: var(--blue-primary, #514437);
  color: #ffffff;
  border: none;
  font-size: 12.5px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: opacity 0.18s;
}

.fc-btn-view:hover {
  opacity: 0.92;
}

.fc-btn-clear {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: none;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.25s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translate(-50%, 20px);
  opacity: 0;
}

@media (max-width: 640px) {
  .slide-fade-enter-from,
  .slide-fade-leave-to {
    transform: translateY(20px);
  }
}
</style>
