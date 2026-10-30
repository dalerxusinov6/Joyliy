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
  showReport,
  reportingListingId,
  toastMessage,
  showToast,
} = useModals()

useHead({
  title: 'Joyliy — Toshkentda Aqlli Ijara Ekosistemasi',
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg', key: 'app-icon-svg' },
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico', key: 'app-icon-ico' },
    { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png', key: 'app-apple-touch-icon' },
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

    <!-- Floating Comparison Bar -->
    <Transition name="slide-fade">
      <div v-if="compareList.length > 0 && !showCompare" class="floating-compare-bar">
        <div class="fc-left">
          <span class="fc-pill">⚖️ {{ compareList.length }}</span>
          <span class="fc-label">Kvartira taqqoslashda</span>
        </div>
        <div class="fc-right">
          <button class="fc-btn-view" @click="showCompare = true">
            Taqqoslash
          </button>
          <button class="fc-btn-clear" @click="clearCompare" title="Tozalash">
            ✕
          </button>
        </div>
      </div>
    </Transition>

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

.floating-compare-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1050;
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--ink, #181C18);
  color: #ffffff;
  padding: 8px 10px 8px 16px;
  border-radius: var(--radius-full, 9999px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(255, 255, 255, 0.12);
  white-space: nowrap;
}

@media (max-width: 640px) {
  .floating-compare-bar {
    bottom: calc(72px + env(safe-area-inset-bottom, 0px));
    left: 16px;
    right: 16px;
    transform: none;
    justify-content: space-between;
  }
}

.fc-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.fc-pill {
  background: var(--terracotta, #C85A32);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  font-family: var(--font-mono);
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
  background: var(--terracotta, #C85A32);
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
