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
const { selectedListing, filterCategory, fetchListings, compareList } = useListings()
const {
  showFilters,
  showMap,
  showSaved,
  showProfile,
  showPostAd,
  showCompare,
  showRoommates,
  showNeighborhoods,
  showReport,
  reportingListingId,
  toastMessage,
  showToast,
} = useModals()

useHead({
  title: 'Joyliy — Toshkentda Aqlli Ijara Ekosistemasi',
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'%3E%3Crect width='24' height='24' rx='5.5' fill='%23BC684B'/%3E%3Cpath d='M4.5 10.5L12 4.25L19.5 10.5V18.5C19.5 19.3284 18.8284 20 18 20H6C5.17157 20 4.5 19.3284 4.5 18.5V10.5Z' stroke='%23FFFFFF' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ccircle cx='12' cy='13' r='1.6' fill='%23FFFFFF'/%3E%3C/svg%3E" },
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
    { rel: 'alternate icon', type: 'image/x-icon', href: '/favicon.ico' },
    { rel: 'shortcut icon', href: '/favicon.ico' },
    { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
    { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' },
    { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
  ],
})

// Fetch initial listings on load
onMounted(async () => {
  await fetchListings()
})

const onSelectListing = (item: ListingItem) => {
  selectedListing.value = item
}

const onFilterMaklersiz = () => {
  filterCategory.value = 'mk'
  const el = document.getElementById('katalog')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const scrollToResults = () => {
  const el = document.getElementById('katalog')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
</script>

<template>
  <div class="app-layout">
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

    <!-- AI Virtual Rental Advisor Floating Widget -->
    <AIAssistantWidget />

    <!-- Toast Notification -->
    <div v-if="toastMessage" class="toast">
      {{ toastMessage }}
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="bn" aria-label="Mobil navigatsiya">
      <button type="button" class="on" @click="scrollToResults">
        <svg class="i" viewBox="0 0 24 24">
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <span>Bosh sahifa</span>
      </button>

      <button type="button" @click="showMap = true">
        <svg class="i" viewBox="0 0 24 24">
          <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
          <line x1="8" y1="2" x2="8" y2="18" />
          <line x1="16" y1="6" x2="16" y2="22" />
        </svg>
        <span>Xarita</span>
      </button>

      <button type="button" @click="showRoommates = true">
        <svg class="i" viewBox="0 0 24 24">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
        <span>Hamxona</span>
      </button>

      <button type="button" @click="showCompare = true">
        <span style="font-size: 16px;">⚖️</span>
        <span>Taqqoslash {{ compareList.length ? `(${compareList.length})` : '' }}</span>
      </button>

      <button type="button" @click="showSaved = true">
        <svg class="i" viewBox="0 0 24 24">
          <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
        </svg>
        <span>Saqlangan {{ favCount > 0 ? `(${favCount})` : '' }}</span>
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
</style>
