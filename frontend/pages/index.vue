<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useModals } from '~/composables/useModals'
import HeroSearch from '~/components/HeroSearch.vue'
import ListingCard from '~/components/ListingCard.vue'

const { t } = useI18n()
const {
  listings,
  filteredListings,
  isLoading,
  selectedListing,
  filterDistrict,
  filterRooms,
  filterMaxPrice,
  filterCategory,
  filterAmenities,
  filterSort,
  fetchListings,
} = useListings()

const { showFilters, showMap, showPostAd } = useModals()

// Pre-fetch during SSR and client navigation
await useAsyncData('listings_ssr', async () => {
  await fetchListings()
  return true
})

// Category definitions
const categories = [
  { key: '3days', title: 'Oxirgi 3 kun', icon: 'calendar' },
  { key: 'mk', title: 'Maklersiz kvartiralar', icon: 'shield' },
  { key: '1', title: '1 xonali', icon: 'bed' },
  { key: '2', title: '2 xonali', icon: 'bed' },
  { key: '3', title: '3 xonali', icon: 'bed' },
  { key: 'room', title: 'Sheriklik uchun', icon: 'users' },
  { key: 'stu', title: 'Talabalar uchun', icon: 'cap' },
]

const toggleCategory = (catKey: string) => {
  if (filterCategory.value === catKey) {
    filterCategory.value = ''
  } else {
    filterCategory.value = catKey
  }
}

const onSelectListing = (item: ListingItem) => {
  selectedListing.value = item
}

const clearFilters = () => {
  filterDistrict.value = ''
  filterRooms.value = ''
  filterMaxPrice.value = ''
  filterCategory.value = ''
  filterAmenities.value.owner_only = false
  filterAmenities.value.mebel = false
  filterAmenities.value.kond = false
  filterAmenities.value.kir = false
  filterAmenities.value.net = false
  filterSort.value = 'new'
}

const hasActiveFilters = computed(() => {
  return (
    !!filterDistrict.value ||
    !!filterRooms.value ||
    !!filterMaxPrice.value ||
    !!filterCategory.value ||
    filterAmenities.value.owner_only ||
    filterAmenities.value.mebel ||
    filterAmenities.value.kond ||
    filterAmenities.value.kir ||
    filterAmenities.value.net ||
    filterSort.value !== 'new'
  )
})

// Curated collections
const newListings = computed(() => {
  return [...listings.value]
    .filter((x) => (x.days_ago || 0) <= 3)
    .sort((a, b) => (a.days_ago || 0) - (b.days_ago || 0))
    .slice(0, 8)
})

const metroListings = computed(() => {
  return listings.value.filter((x) => (x.metro_minutes || 5) <= 7).slice(0, 4)
})

const roomListings = computed(() => {
  return listings.value.filter((x) => x.is_shared_room || x.rooms <= 1).slice(0, 4)
})
</script>

<template>
  <div class="home-page">
    <!-- Hero with Search -->
    <HeroSearch @openFilters="showFilters = true" />

    <!-- Categories Shelf -->
    <div class="wrap">
      <section style="padding-top: 8px">
        <div class="cats" id="cats">
          <button
            v-for="cat in categories"
            :key="cat.key"
            class="cat"
            :class="{ on: filterCategory === cat.key }"
            @click="toggleCategory(cat.key)"
          >
            <!-- Bed icon -->
            <svg v-if="cat.icon === 'bed'" class="i" viewBox="0 0 24 24">
              <path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9" />
            </svg>

            <!-- Users icon -->
            <svg v-else-if="cat.icon === 'users'" class="i" viewBox="0 0 24 24">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>

            <!-- Cap icon -->
            <svg v-else-if="cat.icon === 'cap'" class="i" viewBox="0 0 24 24">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
              <path d="M6 12v5c3 3 9 3 12 0v-5" />
            </svg>

            <!-- Shield icon -->
            <svg v-else-if="cat.icon === 'shield'" class="i" viewBox="0 0 24 24">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>

            <!-- Calendar icon -->
            <svg v-else-if="cat.icon === 'calendar'" class="i" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>

            <span>{{ cat.title }}</span>
          </button>
        </div>
      </section>
    </div>

    <!-- Main Results Section -->
    <div class="wrap">
      <section id="natija">
        <div class="sh">
          <div>
            <h2 id="rt">{{ t('featured_rentals') }}</h2>
            <p class="sub" id="rc">
              {{ isLoading ? 'Yuklanmoqda...' : `${filteredListings.length} ta e’lon topildi` }}
            </p>
          </div>

          <div style="display: flex; gap: 8px; align-items: center">
            <button class="btn" type="button" @click="showMap = true">
              <svg class="i" viewBox="0 0 24 24">
                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                <line x1="8" y1="2" x2="8" y2="18" />
                <line x1="16" y1="6" x2="16" y2="22" />
              </svg>
              <span>{{ t('view_on_map') }}</span>
            </button>

            <button v-if="hasActiveFilters" class="btn" type="button" id="clr" @click="clearFilters">
              {{ t('clear') }}
            </button>
          </div>
        </div>

        <!-- Listings Grid -->
        <div v-if="filteredListings.length" class="grid g4" id="gMain">
          <ListingCard
            v-for="item in filteredListings"
            :key="item.id"
            :listing="item"
            @select="onSelectListing"
          />
        </div>

        <!-- Empty State -->
        <div v-else class="empty">
          <svg class="i" style="width: 48px; height: 48px; margin-bottom: 8px; color: var(--mu)" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <h3 style="margin: 0 0 8px">{{ t('no_results') }}</h3>
          <p class="mu" style="margin: 0 0 16px">{{ t('try_adjusting') }}</p>
          <button class="btn p" type="button" @click="clearFilters">{{ t('clear') }}</button>
        </div>
      </section>

      <!-- Section: Yangi qo‘shilganlar -->
      <section v-if="newListings.length">
        <div class="sh">
          <div>
            <h2>Oxirgi 3 kundagi e’lonlar</h2>
            <p class="sub">So‘nggi 3 kunda (26, 27, 28-oktyabr) joylangan kvartiralar</p>
          </div>
        </div>
        <div class="grid g4" id="gNew">
          <ListingCard
            v-for="item in newListings"
            :key="'new-' + item.id"
            :listing="item"
            @select="onSelectListing"
          />
        </div>
      </section>

      <!-- Section: Metro yaqinida -->
      <section v-if="metroListings.length">
        <div class="sh">
          <div>
            <h2>Metro yaqinida</h2>
            <p class="sub">Metrogacha 7 daqiqagacha piyoda</p>
          </div>
        </div>
        <div class="grid g4" id="gMetro">
          <ListingCard
            v-for="item in metroListings"
            :key="'metro-' + item.id"
            :listing="item"
            @select="onSelectListing"
          />
        </div>
      </section>

      <!-- Section: Sheriklik uchun -->
      <section v-if="roomListings.length">
        <div class="sh">
          <div>
            <h2>Sheriklik uchun</h2>
            <p class="sub">Xonadosh qidirayotganlar uchun</p>
          </div>
        </div>
        <div class="grid g4" id="gRoom">
          <ListingCard
            v-for="item in roomListings"
            :key="'room-' + item.id"
            :listing="item"
            @select="onSelectListing"
          />
        </div>
      </section>

      <!-- How it Works Section -->
      <section id="qanday">
        <h2>{{ t('how_it_works') }}</h2>
        <p class="sub">{{ t('three_steps') }}</p>
        <div class="steps">
          <div class="step">
            <div class="n">1</div>
            <h3>Qidiring</h3>
            <p>Hudud, metro, xonalar soni va narx bo‘yicha filtrlang.</p>
          </div>
          <div class="step">
            <div class="n">2</div>
            <h3>Bog‘laning</h3>
            <p>Egasiga to‘g‘ridan-to‘g‘ri qo‘ng‘iroq qiling yoki Telegram orqali yozing.</p>
          </div>
          <div class="step">
            <div class="n">3</div>
            <h3>Ko‘rib, kelishing</h3>
            <p>Kvartirani o‘z ko‘zingiz bilan ko‘rib, shartlarni egasi bilan kelishing. Shubhali e’lonlar haqida xabar bering.</p>
          </div>
        </div>
      </section>

      <!-- Owner CTA Section -->
      <section id="owner">
        <div class="cta">
          <div>
            <h2>Kvartirangiz bormi?</h2>
            <p>
              E’loningizni joylang va ijarachilar bilan vositachisiz bog‘laning. “Maklersiz” belgisi faqat egalik tasdiqlangan e’lonlarga beriladi.
            </p>
          </div>
          <button class="btn" type="button" id="pub2" @click="showPostAd = true">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M12 5v14M5 12h14" />
            </svg>
            <span>E’lon berish</span>
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

