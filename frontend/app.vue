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
          <span class="fc-label">Kvartira taqqoslashda</span>
        </div>
        <div class="fc-right">
          <button class="fc-btn-view" @click="showCompare = true">
            Taqqoslash
          </button>
          <button class="fc-btn-clear" @click="clearCompare" title="Tozalash" aria-label="Tozalash">
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
    <nav class="bn" aria-label="Mobil navigatsiya">
      <!-- 1. Bosh sahifa -->
      <button
        type="button"
        :class="{ on: !showRoommates && !showCompare && !showAssistant && !showSaved }"
        @click="scrollToResults"
        aria-label="Bosh sahifa"
        title="Bosh sahifa"
      >
        <svg class="i" viewBox="0 0 24 24">
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
      </button>

      <!-- 2. Hamxona (Roommates) -->
      <button
        type="button"
        :class="{ on: showRoommates }"
        @click="showRoommates = true"
        aria-label="Hamxona"
        title="Hamxona"
      >
        <svg class="i" viewBox="0 0 24 24">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      </button>

      <!-- 3. Taqqoslash (Compare) -->
      <button
        type="button"
        class="btn-with-badge"
        :class="{ on: showCompare }"
        @click="showCompare = true"
        aria-label="Taqqoslash"
        title="Taqqoslash"
      >
        <svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
          <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
          <path d="M7 21h10"/>
          <path d="M12 3v18"/>
          <path d="M3 7h18"/>
        </svg>
        <span v-if="compareList.length > 0" class="bn-badge">{{ compareList.length }}</span>
      </button>

      <!-- 4. Chatbot (AI Maslahatchi) -->
      <button
        type="button"
        class="btn-with-badge"
        :class="{ on: showAssistant }"
        @click="showAssistant = true"
        aria-label="AI Maslahatchi"
        title="AI Maslahatchi"
      >
        <svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
        </svg>
      </button>

      <!-- 5. Saqlanganlar (Saved) -->
      <button
        type="button"
        class="btn-with-badge"
        :class="{ on: showSaved }"
        @click="showSaved = true"
        aria-label="Saqlanganlar"
        title="Saqlanganlar"
      >
        <svg class="i" viewBox="0 0 24 24">
          <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
        </svg>
        <span v-if="favCount > 0" class="bn-badge">{{ favCount }}</span>
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
  background: #17191D;
  color: #ffffff;
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
  background: var(--blue-primary, #2878C8);
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
  background: var(--blue-primary, #2878C8);
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
