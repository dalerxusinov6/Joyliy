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
  availableDistricts,
  fetchListings,
} = useListings()

const { showFilters, showMap, showPostAd } = useModals()

// Pre-fetch during SSR and client navigation
await useAsyncData('listings_ssr', async () => {
  await fetchListings()
  return true
})

// Editorial categories
const categories = [
  { key: '', title: 'Barcha takliflar' },
  { key: 'mk', title: 'Maklersiz e’lonlar' },
  { key: '3days', title: 'Oxirgi 3 kun' },
  { key: '1', title: '1 xonali' },
  { key: '2', title: '2 xonali' },
  { key: '3', title: '3 xonali' },
  { key: 'room', title: 'Sheriklik uchun' },
]

// Audience options
const audienceOptions = [
  { key: 'all', title: 'Barchasi', type: 'all' },
  { key: 'family', title: 'Oila uchun', type: 'family' },
  { key: 'female', title: 'Qizlar uchun', type: 'female' },
  { key: 'male', title: 'Yigitlar uchun', type: 'male' },
]

const getAudienceCount = (key: string) => {
  if (key === 'all') return listings.value.length
  return listings.value.filter((x) => x.target_audience === key).length
}

const getDistrictCount = (name: string) => {
  return listings.value.filter((x) => x.district === name).length
}

const selectCategory = (catKey: string) => {
  filterCategory.value = catKey
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

// Dominant featured listing vs grid listings
const dominantFeatured = computed(() => {
  if (!filteredListings.value.length) return null
  return filteredListings.value[0]
})

const remainingListings = computed(() => {
  if (!filteredListings.value.length) return []
  return filteredListings.value.slice(1)
})

const formatPrice = (val: number) => {
  return val.toLocaleString('ru-RU').replace(/\u00a0/g, ' ') + ' so‘m'
}
</script>

<template>
  <div class="editorial-home">
    <!-- Hero with Architectural Console -->
    <HeroSearch @openFilters="showFilters = true" />

    <!-- Curated Category Tabs Bar -->
    <div class="wrap">
      <div class="category-strip">
        <div class="category-scroll">
          <button
            v-for="cat in categories"
            :key="cat.key"
            type="button"
            class="cat-tab"
            :class="{ active: filterCategory === cat.key }"
            @click="selectCategory(cat.key)"
          >
            <span class="cat-name">{{ cat.title }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Catalog Section -->
    <div class="wrap">
      <section id="katalog" class="catalog-section">
        <!-- Catalog Header -->
        <div class="catalog-header">
          <div class="header-left">
            <h2 class="catalog-title">
              Saralangan xonadonlar
            </h2>
            <p class="catalog-count-note">
              {{ isLoading ? 'Yuklanmoqda...' : `${filteredListings.length} ta tekshirilgan e’lon mavjud` }}
            </p>
          </div>

          <!-- Catalog Actions -->
          <div class="header-right">
            <button class="btn map-view-btn" type="button" @click="showMap = true">
              <svg class="i" viewBox="0 0 24 24">
                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                <line x1="8" y1="2" x2="8" y2="18" />
                <line x1="16" y1="6" x2="16" y2="22" />
              </svg>
              <span>Xaritada ko‘rish</span>
            </button>

            <button v-if="hasActiveFilters" class="btn clear-filter-btn" type="button" @click="clearFilters">
              <span>Filtrlarni tozalash</span>
            </button>
          </div>
        </div>

        <!-- Audience Filter Strip -->
        <div class="audience-strip">
          <span class="audience-title">Ijarachilar toifasi:</span>
          <div class="audience-pills">
            <button
              v-for="aud in audienceOptions"
              :key="aud.key"
              type="button"
              class="aud-btn"
              :class="{ active: filterAudience === aud.key }"
              @click="filterAudience = aud.key"
            >
              <span class="aud-icon">
                <svg v-if="aud.type === 'all'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="svg-i">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <svg v-else-if="aud.type === 'family'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="svg-i">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                <svg v-else-if="aud.type === 'female'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="svg-i">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                <svg v-else-if="aud.type === 'male'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="svg-i">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </span>
              <span class="aud-name">{{ aud.title }}</span>
              <span class="aud-count" v-if="getAudienceCount(aud.key) > 0">
                {{ getAudienceCount(aud.key) }}
              </span>
            </button>
          </div>
        </div>

        <!-- Dominant Featured Showcase (1 visually dominant hero card) -->
        <div v-if="dominantFeatured" class="featured-showcase" @click="onSelectListing(dominantFeatured)">
          <div class="featured-media">
            <img
              v-if="dominantFeatured.image_urls && dominantFeatured.image_urls.length"
              :src="dominantFeatured.image_urls[0]"
              :alt="dominantFeatured.title"
              class="featured-img"
            />
            <div v-else class="featured-placeholder">
              <span>Tanlangan turar joy</span>
            </div>
            <div class="featured-badge-bar">
              <span class="featured-pill">Tanlangan e’lon</span>
              <span v-if="dominantFeatured.is_owner" class="featured-owner-pill">100% Maklersiz</span>
            </div>
          </div>

          <div class="featured-info">
            <div class="featured-top-meta">
              <span class="featured-location-tag">
                <svg class="i" viewBox="0 0 24 24" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle;">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                <span>{{ dominantFeatured.district }} · Metroga {{ dominantFeatured.metro_minutes || 5 }} daqiqa</span>
              </span>
            </div>

            <h3 class="featured-title">
              {{ dominantFeatured.title }}
            </h3>

            <div class="featured-specs-row">
              <div class="spec-block">
                <span class="spec-k">Maydon</span>
                <span class="spec-v">{{ dominantFeatured.area }} m²</span>
              </div>
              <div class="spec-block">
                <span class="spec-k">Xonalar</span>
                <span class="spec-v">{{ dominantFeatured.rooms }} xona</span>
              </div>
              <div class="spec-block">
                <span class="spec-k">Qavat</span>
                <span class="spec-v">{{ dominantFeatured.floor || '3/9' }}</span>
              </div>
            </div>

            <div class="featured-bottom-bar">
              <div class="featured-price">
                <span class="f-price">{{ formatPrice(dominantFeatured.price_uzs) }}</span>
                <span class="f-period">/ oy</span>
              </div>

              <button class="btn p inspect-btn" type="button">
                <span>Batafsil ko‘rish</span>
                <svg class="i" viewBox="0 0 24 24">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Remaining Listings Architectural Grid -->
        <div v-if="remainingListings.length" class="grid g4 catalog-grid">
          <ListingCard
            v-for="item in remainingListings"
            :key="item.id"
            :listing="item"
            @select="onSelectListing"
          />
        </div>

        <!-- Empty State -->
        <div v-else-if="!dominantFeatured" class="empty-monograph">
          <span class="numeral-accent">00</span>
          <h3>Hech qanday e’lon topilmadi</h3>
          <p>Tanlangan filtrlarga mos xonadonlar mavjud emas. Filtrlarni o‘zgartirib qayta urinib ko‘ring.</p>
          <button class="btn p" type="button" @click="clearFilters">Filtrlarni tozalash</button>
        </div>
      </section>

      <!-- Neighborhood Exploration Section (District Index) -->
      <section class="neighborhood-section">
        <div class="section-title-wrap">
          <h2 class="section-title">
            Toshkent tumanlari
          </h2>
          <p class="section-subtitle">
            O‘zingizga ma’qul hududdagi xonadonlarni o‘rganing.
          </p>
        </div>

        <div class="districts-index-grid">
          <button
            v-for="d in availableDistricts.slice(0, 8)"
            :key="d"
            type="button"
            class="district-index-card"
            :class="{ active: filterDistrict === d }"
            @click="filterDistrict = filterDistrict === d ? '' : d"
          >
            <div class="district-top">
              <span class="district-count">{{ getDistrictCount(d) }} ta e’lon</span>
            </div>
            <h4 class="district-heading">{{ d }}</h4>
            <div class="district-bottom">
              <span class="district-link-text">Katalogda ko‘rish →</span>
            </div>
          </button>
        </div>
      </section>

      <!-- Brand Story / Philosophy Section (Falsafa) -->
      <section id="falsafa" class="philosophy-section">
        <div class="philosophy-masthead">
          <h2 class="philosophy-heading">
            Uy ijarasi sokin, shaffof va vositachisiz bo‘lishi lozim.
          </h2>
        </div>

        <div class="philosophy-grid">
          <!-- Pillar 1 -->
          <div class="philosophy-col">
            <div class="col-icon-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="p-icon">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <h3 class="col-title">To‘g‘ridan-to‘g‘ri aloqa</h3>
            <p class="col-text">
              Hech qanday makler va keraksiz 50% vositachilik to‘lovisiz. Ijarachi va mulk egasi o‘rtasida shaffof, qulay muloqot o‘rnatiladi.
            </p>
          </div>

          <!-- Pillar 2 -->
          <div class="philosophy-col">
            <div class="col-icon-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="p-icon">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <h3 class="col-title">Saralangan tozalik</h3>
            <p class="col-text">
              Dublikatlar va soxta fotosuratlar doimiy filtrlanadi. Har bir e’londa asl manba, haqiqiy narx va maydon ochiq ko‘rsatiladi.
            </p>
          </div>

          <!-- Pillar 3 -->
          <div class="philosophy-col">
            <div class="col-icon-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="p-icon">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <h3 class="col-title">Maqsadli qulaylik</h3>
            <p class="col-text">
              Oila uchun alohida, talabalar, xonadoshlar va qizlar uchun moslashtirilgan aqlli tahlil yordamida o‘z uyingizni tezroq topasiz.
            </p>
          </div>
        </div>
      </section>

      <!-- Owner Conversion Section -->
      <section class="owner-conversion-section">
        <div class="conversion-panel">
          <div class="conversion-left">
            <h2 class="conversion-title">
              Kvartirangizni vositachisiz ijaraga bering.
            </h2>
            <p class="conversion-lead">
              E’loningizni Joyliy platformasida bepul chop eting. Munosib ijarachilar bilan to‘g‘ridan-to‘g‘ri bog‘lanib, vaqtingizni va vositachilik xarajatlarini tejang.
            </p>
          </div>
          <div class="conversion-right">
            <button class="btn p conversion-btn" type="button" @click="showPostAd = true">
              <span>E’lonni joylashtirish</span>
              <svg class="i" viewBox="0 0 24 24">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.editorial-home {
  padding-bottom: 40px;
}

/* Category Strip */
.category-strip {
  border-top: 1px solid var(--sand);
  border-bottom: 1px solid var(--sand);
  padding: 12px 0;
  margin-bottom: 40px;
}

.category-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  scrollbar-width: none;
}

.category-scroll::-webkit-scrollbar {
  display: none;
}

.cat-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  border: 1px solid var(--sand);
  background: var(--surf);
  color: var(--ink);
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  min-height: 42px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.cat-code {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--terracotta);
}

.cat-tab:hover {
  border-color: var(--ink);
}

.cat-tab.active {
  background: var(--ink);
  color: var(--ivory);
  border-color: var(--ink);
}

.cat-tab.active .cat-code {
  color: var(--terracotta);
}

/* Catalog Section */
.catalog-section {
  padding: 20px 0 60px;
}

.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  gap: 20px;
  flex-wrap: wrap;
}

.catalog-title {
  font-size: clamp(28px, 4vw, 44px);
  margin: 6px 0 4px;
}

.catalog-count-note {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--muted);
  margin: 0;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.map-view-btn {
  background: var(--surf);
  border-color: var(--sand);
}

.map-view-btn:hover {
  border-color: var(--ink);
}

.clear-filter-btn {
  color: var(--terracotta);
  border-color: var(--terracotta);
  background: var(--terracotta-subtle);
}

/* Audience Strip */
.audience-strip {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 32px;
  padding: 14px 18px;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: 14px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.audience-strip::-webkit-scrollbar {
  display: none;
}

.audience-title {
  font-family: var(--font-mono);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  font-weight: 700;
  white-space: nowrap;
}

.audience-pills {
  display: flex;
  gap: 10px;
}

.aud-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 10px;
  border: 1px solid var(--sand);
  background: var(--ivory);
  color: var(--ink);
  font-size: 13.5px;
  font-weight: 600;
  min-height: 42px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
}

.aud-btn .svg-i {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.aud-btn:hover {
  border-color: var(--ink);
}

.aud-btn.active {
  background: var(--terracotta);
  border-color: var(--terracotta);
  color: #FFFFFF;
}

.aud-count {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.08);
}

.aud-btn.active .aud-count {
  background: rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
}

/* Featured Showcase (Visually Dominant Hero Item) */
.featured-showcase {
  display: grid;
  grid-template-columns: 1fr;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  overflow: hidden;
  margin-bottom: 36px;
  box-shadow: var(--sh-card);
  cursor: pointer;
  transition: all 0.25s var(--ease);
}

.featured-showcase:hover {
  border-color: var(--ink);
  box-shadow: var(--sh-hover);
  transform: translateY(-2px);
}

.featured-media {
  position: relative;
  aspect-ratio: 16/10;
  background: var(--sand-light);
  overflow: hidden;
}

.featured-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s var(--ease);
}

.featured-showcase:hover .featured-img {
  transform: scale(1.02);
}

.featured-badge-bar {
  position: absolute;
  top: 16px;
  left: 16px;
  display: flex;
  gap: 8px;
}

.featured-pill {
  background: var(--ink);
  color: var(--ivory);
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  font-weight: 700;
}

.featured-owner-pill {
  background: var(--terracotta);
  color: #FFFFFF;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  font-weight: 700;
}

.featured-info {
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.featured-top-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.featured-index-num {
  font-family: var(--font-serif);
  font-style: italic;
  font-size: 20px;
  color: var(--terracotta);
}

.featured-title {
  font-family: var(--font-serif);
  font-size: clamp(20px, 2.5vw, 28px);
  line-height: 1.25;
  color: var(--ink);
  margin: 0 0 20px;
  font-weight: 500;
}

.featured-specs-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px 0;
  border-top: 1px solid var(--sand-light);
  border-bottom: 1px solid var(--sand-light);
  margin-bottom: 24px;
}

.spec-block {
  display: flex;
  flex-direction: column;
}

.spec-k {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}

.spec-v {
  font-size: 16px;
  font-weight: 700;
  color: var(--ink);
  margin-top: 2px;
}

.featured-bottom-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.featured-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.f-price {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--ink);
  font-feature-settings: "tnum";
}

.f-period {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--muted);
}

.inspect-btn {
  padding: 0 22px;
}

/* Empty Monograph */
.empty-monograph {
  text-align: center;
  padding: 64px 20px;
  border: 1px dashed var(--sand);
  border-radius: var(--radius-xs);
  background: var(--surf);
}

.empty-monograph h3 {
  font-family: var(--font-serif);
  font-size: 22px;
  margin: 12px 0 8px;
}

.empty-monograph p {
  color: var(--muted);
  max-width: 440px;
  margin: 0 auto 24px;
  font-size: 14.5px;
}

/* Neighborhoods Section */
.neighborhood-section {
  padding: 60px 0;
  border-top: 1px solid var(--sand);
}

.section-title-wrap {
  margin-bottom: 32px;
}

.section-title {
  font-size: clamp(28px, 4vw, 44px);
  margin: 6px 0 8px;
}

.section-subtitle {
  color: var(--muted);
  margin: 0;
  font-size: 15px;
}

.districts-index-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, 1fr);
}

.district-index-card {
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  padding: 20px;
  text-align: left;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 120px;
}

.district-index-card:hover {
  border-color: var(--ink);
  background: var(--sand-light);
}

.district-index-card.active {
  border-color: var(--terracotta);
  background: var(--terracotta-subtle);
}

.district-top {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
}

.district-code {
  color: var(--muted);
}

.district-count {
  color: var(--terracotta);
  font-weight: 700;
}

.district-heading {
  margin: 12px 0;
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
}

.district-bottom {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted);
}

/* Philosophy Section */
.philosophy-section {
  padding: 72px 0;
  border-top: 1px solid var(--sand);
}

.philosophy-masthead {
  max-width: 760px;
  margin-bottom: 48px;
}

.philosophy-heading {
  font-size: clamp(30px, 4.5vw, 48px);
  line-height: 1.15;
  margin-top: 10px;
}

.philosophy-grid {
  display: grid;
  gap: 36px;
  grid-template-columns: 1fr;
}

.philosophy-col {
  display: flex;
  flex-direction: column;
  padding-top: 24px;
  border-top: 1px solid var(--sand);
}

.col-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--terracotta-subtle);
  color: var(--terracotta);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.p-icon {
  width: 22px;
  height: 22px;
}

.svg-i {
  width: 14px;
  height: 14px;
  display: inline-block;
  vertical-align: middle;
}

.col-title {
  font-family: var(--font-serif);
  font-size: 21px;
  font-weight: 600;
  color: var(--ink);
  margin: 14px 0 10px;
}

.col-text {
  color: var(--muted);
  font-size: 14.5px;
  line-height: 1.65;
  margin: 0;
}

/* Owner Conversion Section */
.owner-conversion-section {
  padding: 40px 0 60px;
}

.conversion-panel {
  background: var(--ink);
  color: var(--ivory);
  border-radius: var(--radius-xs);
  padding: 48px 40px;
  display: grid;
  gap: 32px;
  align-items: center;
}

.conversion-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.15em;
  color: var(--terracotta);
}

.conversion-title {
  color: var(--ivory);
  font-size: clamp(28px, 4vw, 44px);
  margin: 12px 0 16px;
}

.conversion-lead {
  color: #B5BAB5;
  font-size: 15.5px;
  line-height: 1.65;
  margin: 0;
  max-width: 640px;
}

.conversion-btn {
  background: var(--terracotta) !important;
  color: #FFFFFF !important;
  border-color: var(--terracotta) !important;
  padding: 16px 32px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  width: fit-content;
}

@media (min-width: 768px) {
  .districts-index-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  .philosophy-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .featured-showcase {
    grid-template-columns: 1.15fr 0.85fr;
  }
  .conversion-panel {
    grid-template-columns: 1fr auto;
  }
}
</style>
