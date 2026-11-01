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

// Curated categories matching Iconly pill tabs
const categories = [
  { key: '', title: 'Barchasi' },
  { key: 'mk', title: '🏠 Maklersiz' },
  { key: 'fair_cheap', title: '🟢 Bozordan arzon' },
  { key: '3days', title: '⚡️ Yangi e’lonlar' },
  { key: '1', title: '1 xonali' },
  { key: '2', title: '2 xonali' },
  { key: '3', title: '3 xonali' },
  { key: 'room', title: '👥 Sheriklik' },
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
  <div class="iconly-homepage">
    <!-- Hero with Atmospheric Dashboard Banner & Console -->
    <HeroSearch @openFilters="showFilters = true" />

    <!-- Curated Category Strip (Pill Tabs matching Image 2) -->
    <div class="wrap">
      <div class="category-pill-container">
        <div class="category-pill-scroll">
          <button
            v-for="cat in categories"
            :key="cat.key"
            type="button"
            class="category-pill-btn"
            :class="{ active: filterCategory === cat.key }"
            @click="selectCategory(cat.key)"
          >
            <span>{{ cat.title }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Catalog Section: Tanlangan takliflar -->
    <div class="wrap">
      <section id="katalog" class="catalog-section">
        <!-- Section Header -->
        <div class="section-heading-bar">
          <div class="heading-left">
            <h2 class="section-title">
              Tanlangan takliflar
            </h2>
            <p class="section-subtitle">
              Siz uchun saralangan eng yaxshi uy-joylar.
            </p>
          </div>

          <!-- Catalog Actions -->
          <div class="heading-actions">
            <button class="btn-map-action" type="button" @click="showMap = true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="action-icon">
                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                <line x1="8" y1="2" x2="8" y2="18" />
                <line x1="16" y1="6" x2="16" y2="22" />
              </svg>
              <span>Xarita</span>
            </button>

            <button v-if="hasActiveFilters" class="btn-clear-action" type="button" @click="clearFilters">
              <span>Tozalash ✕</span>
            </button>
          </div>
        </div>

        <!-- Audience Filter Pill Strip -->
        <div class="audience-pill-row">
          <span class="aud-lbl">Ijarachilar toifasi:</span>
          <div class="aud-scroll">
            <button
              v-for="aud in audienceOptions"
              :key="aud.key"
              type="button"
              class="aud-pill-btn"
              :class="{ active: filterAudience === aud.key }"
              @click="filterAudience = aud.key"
            >
              <span>{{ aud.title }}</span>
              <span class="aud-pill-count" v-if="getAudienceCount(aud.key) > 0">
                {{ getAudienceCount(aud.key) }}
              </span>
            </button>
          </div>
        </div>

        <!-- Dominant Featured Showcase Card (Matching Image 2 Mobile Hero / Desktop Spec Overlay) -->
        <div v-if="dominantFeatured" class="iconly-featured-card" @click="onSelectListing(dominantFeatured)">
          <div class="featured-media-frame">
            <img
              v-if="dominantFeatured.image_urls && dominantFeatured.image_urls.length"
              :src="dominantFeatured.image_urls[0]"
              :alt="dominantFeatured.title"
              class="featured-photo"
            />
            <div v-else class="featured-placeholder">
              <span>Joyliy Tanlangan Xonadon</span>
            </div>

            <!-- Top Left Tag -->
            <div class="featured-top-left-tag">
              <span class="hot-rent-pill">🔥 Qaynoq taklif</span>
              <span v-if="dominantFeatured.is_owner" class="owner-pill">Maklersiz</span>
            </div>

            <!-- Bottom Floating Frosted Glass Specs Overlay (Exactly matching Image 2!) -->
            <div class="featured-frosted-specs-overlay">
              <div class="frosted-spec-cell">
                <span class="f-lbl">Maydon</span>
                <span class="f-val">{{ dominantFeatured.area }} m²</span>
              </div>
              <div class="frosted-spec-div"></div>
              <div class="frosted-spec-cell">
                <span class="f-lbl">Xonalar</span>
                <span class="f-val">{{ dominantFeatured.rooms }} xona</span>
              </div>
              <div class="frosted-spec-div"></div>
              <div class="frosted-spec-cell">
                <span class="f-lbl">Qavat</span>
                <span class="f-val">{{ dominantFeatured.floor || '3/9' }}</span>
              </div>
            </div>
          </div>

          <div class="featured-content-plate">
            <div class="featured-price-row">
              <div>
                <span class="f-price-value">{{ formatPrice(dominantFeatured.price_uzs) }}</span>
                <span class="f-price-period">/ oy</span>
              </div>
              <div class="f-score-indicator" title="Sifat ko‘rsatkichi">
                <span>9.4</span>
              </div>
            </div>

            <h3 class="f-card-title">
              {{ dominantFeatured.title }}
            </h3>

            <div class="f-location-row">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="pin-mini">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <span>{{ dominantFeatured.district }} · Metroga {{ dominantFeatured.metro_minutes || 5 }} daqiqa</span>
            </div>

            <div class="f-action-bar">
              <button class="btn btn-dark inspect-cta" type="button">
                <span>Batafsil ko‘rish</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="arrow-mini">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Remaining Listings Grid (3-column responsive cards) -->
        <div v-if="remainingListings.length" class="grid catalog-listings-grid">
          <ListingCard
            v-for="item in remainingListings"
            :key="item.id"
            :listing="item"
            @select="onSelectListing"
          />
        </div>

        <!-- Empty State -->
        <div v-else-if="!dominantFeatured" class="empty-state-card">
          <div class="empty-icon-wrap">🔍</div>
          <h3>Hech qanday e’lon topilmadi</h3>
          <p>Tanlangan filtrlarga mos xonadonlar topilmadi. Filtrlarni tozalab qayta urinib ko‘ring.</p>
          <button class="btn btn-dark" type="button" @click="clearFilters">Filtrlarni tozalash</button>
        </div>
      </section>

      <!-- Popular Districts in Tashkent Section -->
      <section id="tumanlar" class="districts-section">
        <div class="section-heading-bar">
          <div class="heading-left">
            <h2 class="section-title">
              Toshkentning mashhur hududlari
            </h2>
            <p class="section-subtitle">
              Har bir tumanning o‘ziga xos infratuzilmasi va narx darajasi.
            </p>
          </div>
        </div>

        <div class="districts-grid">
          <button
            v-for="d in availableDistricts.slice(0, 6)"
            :key="d"
            type="button"
            class="district-pill-card"
            :class="{ active: filterDistrict === d }"
            @click="filterDistrict = filterDistrict === d ? '' : d"
          >
            <div class="district-info-left">
              <span class="district-name-bold">{{ d }}</span>
              <span class="district-count-tag">{{ getDistrictCount(d) }} ta xonadon</span>
            </div>
            <div class="district-arrow-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="d-arr">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </button>
        </div>
      </section>

      <!-- Why Joyliy.uz Trust Section -->
      <section class="why-joyliy-section">
        <div class="why-heading-wrap">
          <h2 class="section-title">Nega aynan Joyliy.uz?</h2>
          <p class="section-subtitle">O‘zbekiston uy-joy ijarasidagi yangi avlod intellektual standarti.</p>
        </div>

        <div class="why-cards-grid">
          <div class="why-card">
            <div class="why-icon-circle">
              <span class="icon-emoji">🤝</span>
            </div>
            <h4 class="why-card-title">0% Vositachilik to‘lovi</h4>
            <p class="why-card-desc">
              Hech qanday makler va ortiqcha 50% komissiyasiz. Mulk egasi bilan to‘g‘ridan-to‘g‘ri shaffof shartnoma tuzing.
            </p>
          </div>

          <div class="why-card">
            <div class="why-icon-circle">
              <span class="icon-emoji">🤖</span>
            </div>
            <h4 class="why-card-title">Groq Qwen AI Tahlili</h4>
            <p class="why-card-desc">
              Har bir e’lon sun’iy intellekt tomonidan tahlil qilinib, haqiqiy bozor narxi va xavf darajasi baholanadi.
            </p>
          </div>

          <div class="why-card">
            <div class="why-icon-circle">
              <span class="icon-emoji">🛡</span>
            </div>
            <h4 class="why-card-title">100% Tekshirilgan E’lonlar</h4>
            <p class="why-card-desc">
              Har kuni yangilanuvchi avtomatlashtirilgan filtrlar soxta e’lonlar va firibgarlik holatlarini bartaraf etadi.
            </p>
          </div>
        </div>
      </section>

      <!-- Call-to-action for Landlords -->
      <section class="landlord-cta-section">
        <div class="landlord-cta-card">
          <div class="cta-text-side">
            <span class="cta-pill-badge">Mulk egalari uchun</span>
            <h3 class="cta-title">Xonadoningizni tez va ishonchli ijaraga bering</h3>
            <p class="cta-desc">
              E’loningizni 2 daqiqada bepul joylashtiring va minglab talabgorlar bilan vositachisiz bog‘laning.
            </p>
            <button class="btn btn-dark cta-main-btn" @click="showPostAd = true">
              Bepul e’lon berish →
            </button>
          </div>
          <div class="cta-visual-side">
            <div class="cta-stat-pill">
              <span class="stat-number">10,000+</span>
              <span class="stat-desc">Oylik faol qidiruvchilar</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.iconly-homepage {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Category Pill Tabs (Matching Image 2) */
.category-pill-container {
  padding: 8px 0 16px;
}

.category-pill-scroll {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  padding: 4px 2px;
}

.category-pill-scroll::-webkit-scrollbar {
  display: none;
}

.category-pill-btn {
  font-family: var(--font-sans);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  padding: 8px 18px;
  border-radius: var(--radius-full);
  white-space: nowrap;
  transition: all 0.18s var(--ease);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
}

.category-pill-btn:hover {
  color: var(--text-primary);
  border-color: rgba(23, 25, 29, 0.15);
}

.category-pill-btn.active {
  background: #17191D;
  color: #FFFFFF;
  border-color: #17191D;
  box-shadow: 0 4px 12px rgba(23, 25, 29, 0.15);
}

:root[data-theme="dark"] .category-pill-btn.active {
  background: var(--blue-primary);
  border-color: var(--blue-primary);
}

/* Catalog Section */
.catalog-section {
  padding: 16px 0 36px;
}

.section-heading-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-title {
  font-family: var(--font-sans);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.section-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.heading-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-map-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 16px;
  border-radius: var(--radius-full);
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  transition: all 0.18s ease;
}

.btn-map-action:hover {
  border-color: var(--blue-primary);
  color: var(--blue-primary);
}

.action-icon {
  width: 15px;
  height: 15px;
}

.btn-clear-action {
  height: 38px;
  padding: 0 14px;
  border-radius: var(--radius-full);
  background: rgba(239, 68, 68, 0.1);
  color: #DC2626;
  font-size: 12.5px;
  font-weight: 700;
  border: none;
  transition: opacity 0.15s ease;
}

.btn-clear-action:hover {
  opacity: 0.85;
}

/* Audience Filter Row */
.audience-pill-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  overflow-x: auto;
  scrollbar-width: none;
}

.audience-pill-row::-webkit-scrollbar {
  display: none;
}

.aud-lbl {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}

.aud-scroll {
  display: flex;
  align-items: center;
  gap: 6px;
}

.aud-pill-btn {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  padding: 5px 12px;
  border-radius: var(--radius-full);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.aud-pill-btn:hover {
  color: var(--text-primary);
}

.aud-pill-btn.active {
  background: var(--blue-pale);
  color: var(--blue-deep);
  border-color: rgba(40, 120, 200, 0.3);
}

.aud-pill-count {
  font-size: 10.5px;
  font-weight: 700;
  background: rgba(23, 25, 29, 0.08);
  padding: 1px 6px;
  border-radius: var(--radius-full);
}

/* Dominant Featured Card (Iconly Hero Card with Floating Specs Overlay) */
.iconly-featured-card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-card);
  padding: 14px;
  margin-bottom: 28px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  cursor: pointer;
  box-shadow: 0 8px 30px rgba(40, 120, 200, 0.06);
  transition: all 0.25s var(--ease);
}

@media (min-width: 900px) {
  .iconly-featured-card {
    grid-template-columns: 1.2fr 1fr;
    padding: 18px;
    gap: 28px;
    align-items: center;
  }
}

.iconly-featured-card:hover {
  border-color: rgba(40, 120, 200, 0.35);
  box-shadow: 0 18px 44px rgba(40, 120, 200, 0.12);
  transform: translateY(-2px);
}

.featured-media-frame {
  position: relative;
  aspect-ratio: 16/10;
  border-radius: var(--radius-inner);
  overflow: hidden;
  background: var(--surface-subtle);
}

.featured-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.featured-top-left-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 6px;
  z-index: 3;
}

.hot-rent-pill {
  background: #17191D;
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.owner-pill {
  background: #10B981;
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

/* Frosted Specs Overlay across Bottom of Image (Signature Image 2 Style!) */
.featured-frosted-specs-overlay {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: var(--radius-md);
  padding: 10px 18px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

:root[data-theme="dark"] .featured-frosted-specs-overlay {
  background: rgba(22, 27, 34, 0.88);
}

.frosted-spec-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.f-lbl {
  font-size: 11px;
  color: var(--text-secondary);
}

.f-val {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.frosted-spec-div {
  width: 1px;
  height: 22px;
  background: var(--border-subtle);
}

.featured-content-plate {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 6px 4px;
}

.featured-price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.f-price-value {
  font-family: var(--font-sans);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
}

.f-price-period {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-left: 3px;
}

.f-score-indicator {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 3px solid #10B981;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13.5px;
  font-weight: 800;
  color: var(--text-primary);
}

.f-card-title {
  font-family: var(--font-sans);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.35;
  margin: 0;
}

.f-location-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.pin-mini {
  width: 15px;
  height: 15px;
  color: var(--blue-primary);
}

.f-action-bar {
  margin-top: 8px;
}

.inspect-cta {
  height: 42px;
  padding: 0 20px;
  border-radius: var(--radius-full);
}

.arrow-mini {
  width: 14px;
  height: 14px;
}

/* Empty State Card */
.empty-state-card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-card);
  padding: 48px 24px;
  text-align: center;
  max-width: 480px;
  margin: 40px auto;
}

.empty-icon-wrap {
  font-size: 36px;
  margin-bottom: 12px;
}

/* Popular Districts Section */
.districts-section {
  padding: 36px 0;
}

.districts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

@media (min-width: 768px) {
  .districts-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
}

.district-pill-card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s var(--ease);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.district-pill-card:hover {
  border-color: var(--blue-primary);
  box-shadow: 0 8px 24px rgba(40, 120, 200, 0.1);
  transform: translateY(-2px);
}

.district-pill-card.active {
  background: var(--blue-pale);
  border-color: var(--blue-primary);
}

.district-info-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
}

.district-name-bold {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.district-count-tag {
  font-size: 12px;
  color: var(--text-secondary);
}

.district-arrow-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--surface-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.district-pill-card:hover .district-arrow-circle {
  background: var(--blue-primary);
  color: #FFFFFF;
}

.d-arr {
  width: 14px;
  height: 14px;
}

/* Why Joyliy Section */
.why-joyliy-section {
  padding: 40px 0;
}

.why-heading-wrap {
  text-align: center;
  margin-bottom: 32px;
}

.why-cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 768px) {
  .why-cards-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
  }
}

.why-card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-card);
  padding: 28px 24px;
  box-shadow: 0 4px 18px rgba(23, 25, 29, 0.03);
  transition: all 0.2s var(--ease);
}

.why-card:hover {
  border-color: rgba(40, 120, 200, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(40, 120, 200, 0.08);
}

.why-icon-circle {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--blue-pale);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}

.icon-emoji {
  font-size: 22px;
}

.why-card-title {
  font-family: var(--font-sans);
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.why-card-desc {
  font-size: 13.5px;
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0;
}

/* Landlord CTA Banner */
.landlord-cta-section {
  padding: 32px 0 48px;
}

.landlord-cta-card {
  background: var(--hero-gradient);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: var(--radius-hero);
  padding: 36px 28px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  align-items: center;
  box-shadow: 0 12px 36px rgba(40, 120, 200, 0.08);
}

:root[data-theme="dark"] .landlord-cta-card {
  background: linear-gradient(135deg, #161B22 0%, #1A2332 100%);
  border-color: rgba(255, 255, 255, 0.08);
}

@media (min-width: 768px) {
  .landlord-cta-card {
    grid-template-columns: 1.4fr 0.6fr;
    padding: 44px 40px;
  }
}

.cta-pill-badge {
  display: inline-block;
  background: rgba(40, 120, 200, 0.15);
  color: var(--blue-deep);
  font-size: 11.5px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  margin-bottom: 12px;
}

.cta-title {
  font-family: var(--font-sans);
  font-size: clamp(22px, 2.5vw, 32px);
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 10px;
  letter-spacing: -0.02em;
}

.cta-desc {
  font-size: 14.5px;
  color: var(--text-secondary);
  margin: 0 0 20px;
  max-width: 520px;
  line-height: 1.5;
}

.cta-main-btn {
  height: 44px;
  padding: 0 24px;
}

.cta-visual-side {
  display: flex;
  justify-content: center;
}

.cta-stat-pill {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-card);
  padding: 20px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8px 24px rgba(40, 120, 200, 0.1);
}

:root[data-theme="dark"] .cta-stat-pill {
  background: rgba(22, 27, 34, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.stat-number {
  font-size: 28px;
  font-weight: 800;
  color: var(--blue-primary);
  letter-spacing: -0.02em;
}

.stat-desc {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 600;
}
</style>
