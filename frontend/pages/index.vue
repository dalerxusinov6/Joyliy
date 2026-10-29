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
  filterAudience,
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

// Audience options (family, female, male, all)
const audienceOptions = [
  { key: 'all', title: 'Barchasi', icon: '🌐' },
  { key: 'family', title: 'Oila uchun', icon: '👨‍👩‍👧' },
  { key: 'female', title: 'Qizlar uchun', icon: '👩' },
  { key: 'male', title: 'Yigitlar uchun', icon: '👨' },
]

const getAudienceCount = (key: string) => {
  if (key === 'all') return listings.value.length
  return listings.value.filter((x) => x.target_audience === key).length
}

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
  filterAudience.value = 'all'
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
    filterAudience.value !== 'all' ||
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
      <section class="shelf-section">
        <div class="cats" id="cats">
          <button
            v-for="cat in categories"
            :key="cat.key"
            class="cat"
            :class="{ on: filterCategory === cat.key }"
            @click="toggleCategory(cat.key)"
          >
            <!-- Bed icon -->
            <svg v-if="cat.icon === 'bed'" class="i cat-icon" viewBox="0 0 24 24">
              <path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9" />
            </svg>

            <!-- Users icon -->
            <svg v-else-if="cat.icon === 'users'" class="i cat-icon" viewBox="0 0 24 24">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>

            <!-- Cap icon -->
            <svg v-else-if="cat.icon === 'cap'" class="i cat-icon" viewBox="0 0 24 24">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
              <path d="M6 12v5c3 3 9 3 12 0v-5" />
            </svg>

            <!-- Shield icon -->
            <svg v-else-if="cat.icon === 'shield'" class="i cat-icon" viewBox="0 0 24 24">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>

            <!-- Calendar icon -->
            <svg v-else-if="cat.icon === 'calendar'" class="i cat-icon" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>

            <span class="cat-label">{{ cat.title }}</span>
          </button>
        </div>
      </section>
    </div>

    <!-- Main Results Section -->
    <div class="wrap">
      <section id="natija">
        <div class="sh results-header">
          <div>
            <div class="results-tag">E’lonlar katalogi</div>
            <h2 id="rt" class="section-heading">{{ t('featured_rentals') }}</h2>
            <p class="sub" id="rc">
              {{ isLoading ? 'Yuklanmoqda...' : `${filteredListings.length} ta tasdiqlangan e’lon topildi` }}
            </p>
          </div>

          <div class="results-actions">
            <!-- Map trigger button -->
            <button class="btn map-btn" type="button" @click="showMap = true">
              <svg class="i" viewBox="0 0 24 24">
                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                <line x1="8" y1="2" x2="8" y2="18" />
                <line x1="16" y1="6" x2="16" y2="22" />
              </svg>
              <span>{{ t('view_on_map') }}</span>
            </button>

            <!-- Clear filters button -->
            <button v-if="hasActiveFilters" class="btn clear-btn" type="button" id="clr" @click="clearFilters">
              {{ t('clear') }}
            </button>
          </div>
        </div>

        <!-- Audience Filter Bar (Kimlar uchun: Oila / Qizlar / Yigitlar / Barchasi) -->
        <div class="aud-filter-wrap">
          <div class="aud-pills-row">
            <button
              v-for="aud in audienceOptions"
              :key="aud.key"
              type="button"
              class="aud-pill"
              :class="{ active: filterAudience === aud.key }"
              @click="filterAudience = aud.key"
            >
              <span class="aud-icon">{{ aud.icon }}</span>
              <span class="aud-text">{{ aud.title }}</span>
              <span class="aud-num" v-if="getAudienceCount(aud.key) > 0">
                {{ getAudienceCount(aud.key) }}
              </span>
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
          <svg class="i" style="width: 48px; height: 48px; margin-bottom: 12px; color: var(--tx-muted)" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <h3 style="margin: 0 0 8px; font-size: 18px">{{ t('no_results') }}</h3>
          <p class="mu" style="margin: 0 0 18px">{{ t('try_adjusting') }}</p>
          <button class="btn p" type="button" @click="clearFilters">{{ t('clear') }}</button>
        </div>
      </section>

      <!-- Section: Yangi qo‘shilganlar -->
      <section v-if="newListings.length" class="curated-section">
        <div class="sh">
          <div>
            <div class="results-tag">Eng so‘nggi takliflar</div>
            <h2 class="section-heading">Oxirgi 3 kundagi e’lonlar</h2>
            <p class="sub">Yaqinda joylangan va hozirda ijaraga tayyor bo‘lgan xonadonlar</p>
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
      <section v-if="metroListings.length" class="curated-section">
        <div class="sh">
          <div>
            <div class="results-tag">Transport qulayligi</div>
            <h2 class="section-heading">Metro bekatlariga yaqin uylar</h2>
            <p class="sub">Toshkent metropolitenigacha 7 daqiqagacha piyoda masofadagi uylar</p>
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
      <section v-if="roomListings.length" class="curated-section">
        <div class="sh">
          <div>
            <div class="results-tag">Tejamkor ijara</div>
            <h2 class="section-heading">Sheriklik va talabalar uchun</h2>
            <p class="sub">Xonadosh bilan birga yashash yoki qulay 1 xonali ixcham kvartiralar</p>
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

      <!-- Trust & Differentiation Section: Nega aynan Joyliy? -->
      <section id="nega" class="trust-section">
        <div class="trust-header">
          <span class="results-tag">Afzalliklarimiz</span>
          <h2 class="section-heading">Nega aynan Joyliy?</h2>
          <p class="sub">O‘zbekiston ijara bozorini shaffof, adolatli va zamonaviy qilishga intilamiz</p>
        </div>

        <div class="trust-grid">
          <div class="trust-card">
            <div class="trust-icon-box">
              <svg class="i trust-icon" viewBox="0 0 24 24">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <h3>To‘g‘ridan-to‘g‘ri uy egasi</h3>
            <p>Hech qanday makler yoki rieltorlik foizlarisiz. 1 oylik yoki 50% qo‘shimcha komissiyalarni unuting.</p>
          </div>

          <div class="trust-card">
            <div class="trust-icon-box">
              <svg class="i trust-icon" viewBox="0 0 24 24">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>
            <h3>Saralangan toza e’lonlar</h3>
            <p>Dublikatlar, eskirgan takliflar va soxta rasmlar filtrlanadi. Har bir e’londa asl manba shaffof ko‘rsatiladi.</p>
          </div>

          <div class="trust-card">
            <div class="trust-icon-box">
              <svg class="i trust-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
                <path d="m4.93 4.93 4.24 4.24M14.83 14.83l4.24 4.24M14.83 9.17l4.24-4.24M4.93 19.07l4.24-4.24" />
              </svg>
            </div>
            <h3>Aniq maqsadli filtrlash</h3>
            <p>Oila uchun alohida, talabalar, qizlar yoki yigitlar uchun mos xonadonlarni bir bosishda toping.</p>
          </div>

          <div class="trust-card">
            <div class="trust-icon-box">
              <svg class="i trust-icon" viewBox="0 0 24 24">
                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                <line x1="8" y1="2" x2="8" y2="18" />
                <line x1="16" y1="6" x2="16" y2="22" />
              </svg>
            </div>
            <h3>Interaktiv xarita va bot</h3>
            <p>Toshkent tumanlari bo‘yicha narxlarni xaritada solishtiring yoki Telegram bot orqali yangilarini kuzating.</p>
          </div>
        </div>
      </section>

      <!-- How it Works Section -->
      <section id="qanday" class="how-section">
        <div class="trust-header">
          <span class="results-tag">Oddiy jarayon</span>
          <h2 class="section-heading">{{ t('how_it_works') }}</h2>
          <p class="sub">{{ t('three_steps') }}</p>
        </div>

        <div class="steps">
          <div class="step">
            <div class="n">01</div>
            <h3>Uyni qidiring</h3>
            <p>O‘zingizga ma’qul tuman, metro masofasi, xonalar soni va byudjet bo‘yicha filtrlang.</p>
          </div>
          <div class="step">
            <div class="n">02</div>
            <h3>E’lonni ko‘rib chiqing</h3>
            <p>Haqiqiy fotosuratlar, qulayliklar va joylashuvni ko‘rib, sizga mos kelishini aniqlang.</p>
          </div>
          <div class="step">
            <div class="n">03</div>
            <h3>Uy egasi bilan bog‘laning</h3>
            <p>Telefon orqali qo‘ng‘iroq qiling yoki Telegram orqali yozib, vositachisiz shartlarni kelishing.</p>
          </div>
        </div>
      </section>

      <!-- Owner CTA Section -->
      <section id="owner">
        <div class="cta">
          <div class="cta-content">
            <span class="cta-pill">Uy egalari uchun</span>
            <h2>O‘z kvartirangizni vositachisiz ijaraga bering</h2>
            <p>
              Joyliy platformasida e’lon berish bepul va qulay. Ijarachilar siz bilan to‘g‘ridan-to‘g‘ri bog‘lanadi va har ikki tomon ham mablag‘ini tejaydi.
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

<style scoped>
.shelf-section {
  padding: 16px 0 8px;
}

.cat-icon {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.cat-label {
  letter-spacing: -0.01em;
}

.results-header {
  align-items: flex-end;
}

.results-tag {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ac);
  margin-bottom: 4px;
}

.section-heading {
  font-size: 26px;
  letter-spacing: -0.03em;
  margin: 0 0 6px;
}

.results-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.map-btn {
  background: var(--surf);
  border-color: var(--bd);
  font-weight: 600;
}

.map-btn:hover {
  border-color: var(--ac);
  color: var(--ac);
}

.clear-btn {
  color: #E11D48;
  border-color: #FECDD3;
  background: #FFF1F2;
}

.clear-btn:hover {
  background: #FFE4E6;
  border-color: #FDA4AF;
}

.aud-filter-wrap {
  margin: 14px 0 24px;
  overflow-x: auto;
  padding-bottom: 6px;
  scrollbar-width: none;
}

.aud-filter-wrap::-webkit-scrollbar {
  display: none;
}

.aud-pills-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
}

.aud-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--card);
  border: 1px solid var(--bd);
  border-radius: var(--radius-full);
  padding: 8px 18px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--tx);
  cursor: pointer;
  transition: all 0.2s var(--ease-smooth);
  white-space: nowrap;
  user-select: none;
}

.aud-pill:hover {
  border-color: var(--bd-hover);
  background: var(--surf-muted);
  transform: translateY(-1px);
}

.aud-pill.active {
  background: var(--ac);
  color: #FFFFFF;
  border-color: var(--ac);
  box-shadow: 0 4px 14px rgba(23, 77, 58, 0.25);
}

.aud-icon {
  font-size: 15px;
  line-height: 1;
}

.aud-num {
  font-size: 11px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 12px;
  background: var(--surf-muted);
  color: var(--tx-muted);
}

.aud-pill.active .aud-num {
  background: rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
}

.curated-section {
  padding-top: 48px;
}

.trust-section,
.how-section {
  padding: 56px 0 32px;
}

.trust-header {
  text-align: center;
  max-width: 620px;
  margin: 0 auto 36px;
}

.trust-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr;
}

.trust-card {
  background: var(--card);
  border: 1px solid var(--bd);
  border-radius: var(--radius-lg);
  padding: 28px 24px;
  transition: transform 0.2s var(--ease-smooth), border-color 0.2s ease, box-shadow 0.2s ease;
}

.trust-card:hover {
  transform: translateY(-3px);
  border-color: var(--bd-hover);
  box-shadow: var(--sh);
}

.trust-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--mint-subtle);
  color: var(--ac);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}

.trust-icon {
  width: 22px;
  height: 22px;
  stroke-width: 2;
}

.trust-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 700;
  color: var(--tx);
  letter-spacing: -0.015em;
}

.trust-card p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--tx-muted);
}

.cta-pill {
  display: inline-block;
  background: rgba(185, 242, 208, 0.2);
  color: var(--mint);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  margin-bottom: 12px;
}

@media (min-width: 768px) {
  .trust-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .trust-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
