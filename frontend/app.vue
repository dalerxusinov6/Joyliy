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

const { t } = useI18n()
const { count: favCount } = useFavorites()
const { selectedListing, filterCategory, fetchListings } = useListings()
const { showFilters, showMap, showSaved, showProfile, showPostAd, toastMessage, showToast } = useModals()

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

      <button type="button" @click="showSaved = true">
        <svg class="i" viewBox="0 0 24 24">
          <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
        </svg>
        <span>Saqlanganlar {{ favCount > 0 ? `(${favCount})` : '' }}</span>
      </button>

      <button type="button" @click="showProfile = true">
        <svg class="i" viewBox="0 0 24 24">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 21a8 8 0 0 1 16 0" />
        </svg>
        <span>Profil</span>
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
