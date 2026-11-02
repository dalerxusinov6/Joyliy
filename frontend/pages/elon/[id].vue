<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'
import ListingCard from '~/components/ListingCard.vue'

const route = useRoute()
const router = useRouter()
const listingId = computed(() => Number(route.params.id))

const { t, tDistrict, formatPrice } = useI18n()
const { isFavorite, toggleFavorite } = useFavorites()
const { isInCompare, toggleCompare, listings, fetchListings } = useListings()

const activePhotoIndex = ref(0)

// Fetch current listing
const { data: listing, error } = await useAsyncData(
  `listing_detail_${listingId.value}`,
  async () => {
    try {
      const res = await $fetch<ListingItem>(`/api/listings/${listingId.value}`)
      return res
    } catch (err) {
      return null
    }
  }
)

// Ensure catalog is populated for related items
if (!listings.value || listings.value.length === 0) {
  await fetchListings()
}

// District slug helper
const districtSlugMap: Record<string, string> = {
  'chilonzor': 'chilonzor',
  'yunusobod': 'yunusobod',
  'mirzo ulug‘bek': 'mirzo-ulugbek',
  'mirzo ulug\'bek': 'mirzo-ulugbek',
  'mirzo ulugbek': 'mirzo-ulugbek',
  'мирзо-улугбек': 'mirzo-ulugbek',
  'yakkasaroy': 'yakkasaroy',
  'mirobod': 'mirobod',
  'shayxontohur': 'shayxontohur',
  'olmazor': 'olmazor',
  'uchtepa': 'uchtepa',
  'sergeli': 'sergeli',
  'yashnobod': 'yashnobod',
  'bektemir': 'bektemir',
  'yangi hayot': 'yangihayot',
  'yangihayot': 'yangihayot',
}

const districtSlug = computed(() => {
  if (!listing.value?.district) return 'toshkent'
  const key = listing.value.district.toLowerCase().trim()
  return districtSlugMap[key] || 'toshkent'
})

// Related listings in the same district
const relatedListings = computed(() => {
  if (!listing.value || !listings.value) return []
  return listings.value
    .filter((x) => x.id !== listing.value!.id && x.district === listing.value!.district)
    .slice(0, 4)
})

// Dynamic SEO Metadata
const pageTitle = computed(() => {
  if (!listing.value) return "E'lon topilmadi — Joyliy.uz"
  const roomsStr = listing.value.rooms ? `${listing.value.rooms} xonali kvartira` : 'Kvartira'
  const distStr = listing.value.district ? tDistrict(listing.value.district) : 'Toshkent'
  const dealStr = listing.value.deal_type === 'sale' ? 'sotiladi' : 'ijaraga beriladi'
  return `${distStr}da ${roomsStr} ${dealStr} — Joyliy.uz`
})

const pageDescription = computed(() => {
  if (!listing.value) return "Ushbu e'lon mavjud emas yoki arxivlangan."
  const roomsStr = listing.value.rooms ? `${listing.value.rooms} xonali` : ''
  const distStr = listing.value.district ? tDistrict(listing.value.district) : 'Toshkent'
  const priceStr = formatPrice(listing.value.price_uzs)
  const areaStr = listing.value.area ? `${listing.value.area} m²` : ''
  return `Toshkent shahri ${distStr} tumanida ${roomsStr} xonadon. Narxi: ${priceStr}. Maydoni: ${areaStr}. Fotosuratlar, xaritalar va aloqa ma'lumotlarini Joyliy.uz da ko'ring.`
})

const canonicalUrl = computed(() => `https://joyliy.uz/elon/${listingId.value}`)
const ogImageUrl = computed(() => {
  return listing.value?.image_urls?.[0] || 'https://joyliy.uz/apple-touch-icon.png'
})

useSeoMeta({
  title: pageTitle,
  description: pageDescription,
  canonical: canonicalUrl,
  ogTitle: pageTitle,
  ogDescription: pageDescription,
  ogImage: ogImageUrl,
  ogUrl: canonicalUrl,
  ogType: 'article',
  twitterCard: 'summary_large_image',
  twitterTitle: pageTitle,
  twitterDescription: pageDescription,
  twitterImage: ogImageUrl,
  robots: listing.value ? 'index, follow' : 'noindex, follow',
})

// Schema.org Structured Data
useHead(() => {
  if (!listing.value) return {}

  const schemaGraph = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'BreadcrumbList',
        itemListElement: [
          {
            '@type': 'ListItem',
            position: 1,
            name: 'Bosh sahifa',
            item: 'https://joyliy.uz/',
          },
          {
            '@type': 'ListItem',
            position: 2,
            name: 'Toshkent',
            item: 'https://joyliy.uz/toshkent',
          },
          {
            '@type': 'ListItem',
            position: 3,
            name: listing.value.district || 'Tuman',
            item: `https://joyliy.uz/toshkent/${districtSlug.value}`,
          },
          {
            '@type': 'ListItem',
            position: 4,
            name: listing.value.title,
            item: canonicalUrl.value,
          },
        ],
      },
      {
        '@type': ['Apartment', 'RealEstateListing'],
        '@id': canonicalUrl.value,
        name: listing.value.title,
        description: listing.value.description || pageDescription.value,
        url: canonicalUrl.value,
        image: listing.value.image_urls || [],
        numberOfRooms: listing.value.rooms,
        floorSize: listing.value.area
          ? {
              '@type': 'QuantitativeValue',
              value: listing.value.area,
              unitCode: 'MTK',
            }
          : undefined,
        address: {
          '@type': 'PostalAddress',
          addressLocality: 'Toshkent',
          addressRegion: listing.value.district || 'Toshkent',
          addressCountry: 'UZ',
        },
        geo: listing.value.coordinates_lat
          ? {
              '@type': 'GeoCoordinates',
              latitude: listing.value.coordinates_lat,
              longitude: listing.value.coordinates_lon,
            }
          : undefined,
        offers: {
          '@type': 'Offer',
          price: listing.value.price_uzs,
          priceCurrency: 'UZS',
          availability: 'https://schema.org/InStock',
          validFrom: listing.value.first_seen_at || undefined,
        },
      },
    ],
  }

  return {
    link: [
      { rel: 'canonical', href: canonicalUrl.value },
      { rel: 'alternate', hreflang: 'uz', href: canonicalUrl.value },
      { rel: 'alternate', hreflang: 'ru', href: `${canonicalUrl.value}?lang=ru` },
      { rel: 'alternate', hreflang: 'x-default', href: canonicalUrl.value },
    ],
    script: [
      {
        type: 'application/ld+json',
        children: JSON.stringify(schemaGraph),
      },
    ],
  }
})
</script>

<template>
  <div class="property-page-container">
    <!-- Breadcrumbs Navigation -->
    <nav class="breadcrumb-container" aria-label="Breadcrumb">
      <ol class="breadcrumb-list">
        <li class="breadcrumb-item">
          <NuxtLink to="/" class="breadcrumb-link">{{ t('nav_home') || 'Bosh sahifa' }}</NuxtLink>
        </li>
        <li class="breadcrumb-sep">/</li>
        <li class="breadcrumb-item">
          <NuxtLink to="/toshkent" class="breadcrumb-link">Toshkent</NuxtLink>
        </li>
        <li v-if="listing?.district" class="breadcrumb-sep">/</li>
        <li v-if="listing?.district" class="breadcrumb-item">
          <NuxtLink :to="'/toshkent/' + districtSlug" class="breadcrumb-link">
            {{ tDistrict(listing.district) }}
          </NuxtLink>
        </li>
        <li class="breadcrumb-sep">/</li>
        <li class="breadcrumb-item current" aria-current="page">
          <span>{{ listing ? listing.title : "E'lon" }}</span>
        </li>
      </ol>
    </nav>

    <!-- Listing Not Found State -->
    <div v-if="!listing" class="not-found-card">
      <div class="not-found-icon">🔍</div>
      <h1 class="not-found-title">E‘lon topilmadi yoki arxivlangan</h1>
      <p class="not-found-desc">
        Ushbu e‘lon egasi tomonidan o‘chirilgan yoki ijaraga berilgan bo‘lishi mumkin. Quyidagi yangi variantlarni ko‘rib chiqing.
      </p>
      <NuxtLink to="/" class="return-home-btn">
        Asosiy sahifaga qaytish
      </NuxtLink>
    </div>

    <!-- Main Listing View -->
    <article v-else class="listing-full-view">
      <!-- Title & Header Bar -->
      <header class="listing-header-section">
        <div class="header-main-meta">
          <div class="badges-row">
            <span v-if="listing.deal_type === 'sale'" class="badge badge-sale">
              {{ t('badge_for_sale') || 'Sotiladi' }}
            </span>
            <span v-else class="badge badge-rent">
              {{ t('badge_for_rent') || 'Ijara' }}
            </span>

            <span v-if="listing.is_owner" class="badge badge-owner">
              {{ listing.deal_type === 'sale' ? t('from_owner') : t('no_agent') }}
            </span>

            <span v-if="listing.fair_price_category === 'BELOW_MARKET'" class="badge badge-below-market">
              {{ listing.deal_type === 'sale' ? t('badge_cheap_price') : t('badge_below_market') }}
            </span>
          </div>

          <h1 class="listing-main-title">{{ listing.title }}</h1>

          <div class="listing-address-row">
            <svg class="loc-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            <span>Toshkent, {{ tDistrict(listing.district) }}</span>
            <span v-if="listing.metro_station" class="metro-info">
              • 🚇 {{ listing.metro_station }} ({{ listing.metro_distance_m ? listing.metro_distance_m + ' m' : 'yaqinida' }})
            </span>
          </div>
        </div>

        <div class="header-action-buttons">
          <button
            type="button"
            class="action-pill-btn"
            :class="{ active: isFavorite(listing.id) }"
            @click="toggleFavorite(listing.id)"
          >
            <svg viewBox="0 0 24 24" class="btn-svg" :fill="isFavorite(listing.id) ? '#FF4B4B' : 'none'" stroke="currentColor" stroke-width="2">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            <span>{{ isFavorite(listing.id) ? 'Saqlangan' : 'Saqlash' }}</span>
          </button>

          <button
            type="button"
            class="action-pill-btn"
            :class="{ active: isInCompare(listing.id) }"
            @click="toggleCompare(listing)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-svg">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="M7 21h10"/>
              <path d="M12 3v18"/>
              <path d="M3 7h18"/>
            </svg>
            <span>Taqqosla</span>
          </button>
        </div>
      </header>

      <!-- Grid: Media + Details Sidebar -->
      <div class="listing-layout-grid">
        <!-- Main Media Gallery & Description Column -->
        <div class="gallery-description-col">
          <!-- Main Hero Gallery -->
          <div class="hero-gallery-card">
            <div v-if="listing.image_urls && listing.image_urls.length" class="hero-photo-container">
              <img
                :src="listing.image_urls[activePhotoIndex] || listing.image_urls[0]"
                :alt="listing.title + ' — Toshkent Joyliy.uz'"
                class="main-active-photo"
                width="800"
                height="500"
              />
              <div class="photo-counter-badge">
                {{ activePhotoIndex + 1 }} / {{ listing.image_urls.length }}
              </div>
            </div>
            <div v-else class="hero-placeholder">
              <span>Fotosurat yuklanmagan</span>
            </div>

            <!-- Thumbnail Carousel -->
            <div v-if="listing.image_urls && listing.image_urls.length > 1" class="gallery-thumbs-row">
              <button
                v-for="(img, idx) in listing.image_urls"
                :key="idx"
                type="button"
                class="thumb-button"
                :class="{ active: activePhotoIndex === idx }"
                @click="activePhotoIndex = idx"
              >
                <img :src="img" :alt="listing.title + ' foto ' + (idx + 1)" width="70" height="50" loading="lazy" />
              </button>
            </div>
          </div>

          <!-- Specs Highlights -->
          <div class="specs-grid-section">
            <h2 class="section-subheading">Asosiy ko‘rsatkichlar</h2>
            <div class="specs-matrix">
              <div class="spec-cell">
                <span class="spec-label">Xonalar</span>
                <span class="spec-val">{{ listing.rooms ? listing.rooms + ' xona' : '—' }}</span>
              </div>
              <div class="spec-cell">
                <span class="spec-label">Maydoni</span>
                <span class="spec-val">{{ listing.area ? listing.area + ' m²' : '—' }}</span>
              </div>
              <div class="spec-cell">
                <span class="spec-label">Qavat</span>
                <span class="spec-val">{{ listing.floor || '—' }}</span>
              </div>
              <div class="spec-cell">
                <span class="spec-label">Mulk turi</span>
                <span class="spec-val">{{ listing.property_type || 'Kvartira' }}</span>
              </div>
              <div class="spec-cell">
                <span class="spec-label">Ta’mir</span>
                <span class="spec-val">{{ listing.renovation_type || 'Yaxshi' }}</span>
              </div>
              <div class="spec-cell">
                <span class="spec-label">Mebel</span>
                <span class="spec-val">{{ listing.is_furnished ? 'Bor' : 'Yo‘q' }}</span>
              </div>
            </div>
          </div>

          <!-- Description Section -->
          <div class="description-section">
            <h2 class="section-subheading">Tavsif</h2>
            <div class="description-text-wrap">
              <p class="description-content">
                {{ listing.description || "Ushbu e'lon uchun batafsil matn taqdim etilmagan." }}
              </p>
            </div>
          </div>
        </div>

        <!-- Sticky Pricing & Contact Sidebar -->
        <aside class="pricing-contact-sidebar">
          <div class="price-action-card">
            <div class="price-amount-box">
              <span class="price-val">{{ formatPrice(listing.price_uzs) }}</span>
              <span v-if="listing.deal_type !== 'sale'" class="period-text">{{ t('per_month') || '/oyiga' }}</span>
              <span v-else class="period-text">{{ t('sale_price_lbl') || 'sotuv narxi' }}</span>
            </div>

            <!-- Valuation Score Badge -->
            <div v-if="listing.fair_price_category" class="ai-valuation-pill">
              <span class="sparkle-icon">✨</span>
              <span>
                {{ listing.fair_price_category === 'BELOW_MARKET' ? "Bozor narxidan arzonroq variant" : "Bozor o'rtacha narxiga mos" }}
              </span>
            </div>

            <!-- Contacts -->
            <div class="contact-actions">
              <a
                v-if="listing.contact_phone"
                :href="'tel:' + listing.contact_phone"
                class="contact-primary-btn"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="call-svg">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
                <span>Qo‘ng‘iroq qilish</span>
              </a>

              <a
                v-if="listing.contact_telegram"
                :href="'https://t.me/' + listing.contact_telegram.replace('@', '')"
                target="_blank"
                rel="noopener noreferrer"
                class="contact-telegram-btn"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" class="tg-svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.52 2.77-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
                </svg>
                <span>Telegram orqali yozish</span>
              </a>

              <a
                v-if="listing.canonical_url"
                :href="listing.canonical_url"
                target="_blank"
                rel="nofollow noopener noreferrer"
                class="source-original-link"
              >
                <span>Asl manbada ko‘rish (OLX)</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="arrow-svg">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </a>
            </div>
          </div>
        </aside>
      </div>

      <!-- Related Listings for Internal SEO Link Graph -->
      <section v-if="relatedListings.length" class="related-listings-section">
        <h2 class="related-heading">{{ tDistrict(listing.district) }} tumanidagi o‘xshash e‘lonlar</h2>
        <div class="related-grid">
          <ListingCard
            v-for="item in relatedListings"
            :key="item.id"
            :listing="item"
          />
        </div>
      </section>
    </article>
  </div>
</template>

<style scoped>
.property-page-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 24px 20px 80px;
}

.breadcrumb-container {
  margin-bottom: 24px;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 13px;
  color: var(--muted, #6B7280);
}

.breadcrumb-link {
  color: var(--muted, #6B7280);
  text-decoration: none;
  transition: color 0.15s ease;
}

.breadcrumb-link:hover {
  color: var(--blue-primary, #2878C8);
}

.breadcrumb-sep {
  color: #D1D5DB;
}

.breadcrumb-item.current {
  color: var(--ink, #1F2937);
  font-weight: 500;
  max-width: 400px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.not-found-card {
  text-align: center;
  padding: 80px 20px;
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  margin-top: 40px;
}

.not-found-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.not-found-title {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
}

.not-found-desc {
  color: #6B7280;
  max-width: 480px;
  margin: 0 auto 24px;
  line-height: 1.5;
}

.return-home-btn {
  display: inline-flex;
  align-items: center;
  padding: 12px 24px;
  background: var(--blue-primary, #2878C8);
  color: #FFFFFF;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}

.listing-header-section {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.badges-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.badge-sale {
  background: #EBF5FF;
  color: #1E40AF;
}

.badge-rent {
  background: #F3F4F6;
  color: #374151;
}

.badge-owner {
  background: #ECFDF5;
  color: #065F46;
}

.badge-below-market {
  background: #FEF3C7;
  color: #92400E;
}

.listing-main-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  line-height: 1.3;
  margin: 0 0 10px;
}

.listing-address-row {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #4B5563;
  font-size: 14px;
}

.loc-icon {
  width: 16px;
  height: 16px;
  color: #9CA3AF;
}

.metro-info {
  color: #2563EB;
}

.header-action-buttons {
  display: flex;
  gap: 10px;
}

.action-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  color: #374151;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-pill-btn:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
}

.action-pill-btn.active {
  border-color: #2878C8;
  color: #2878C8;
}

.btn-svg {
  width: 16px;
  height: 16px;
}

.listing-layout-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 32px;
  align-items: start;
}

@media (max-width: 960px) {
  .listing-layout-grid {
    grid-template-columns: 1fr;
  }
}

.hero-gallery-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 16px;
  margin-bottom: 24px;
}

.hero-photo-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16/10;
  border-radius: 12px;
  overflow: hidden;
  background: #F3F4F6;
}

.main-active-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-counter-badge {
  position: absolute;
  right: 14px;
  bottom: 14px;
  background: rgba(17, 24, 39, 0.8);
  color: #FFFFFF;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  font-family: monospace;
}

.hero-placeholder {
  aspect-ratio: 16/10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F3F4F6;
  border-radius: 12px;
  color: #9CA3AF;
  font-size: 14px;
}

.gallery-thumbs-row {
  display: flex;
  gap: 10px;
  margin-top: 14px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.thumb-button {
  width: 80px;
  height: 56px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  padding: 0;
  cursor: pointer;
  flex: none;
}

.thumb-button.active {
  border-color: #2878C8;
}

.thumb-button img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.specs-grid-section,
.description-section {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  margin-bottom: 24px;
}

.section-subheading {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 16px;
}

.specs-matrix {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 600px) {
  .specs-matrix {
    grid-template-columns: repeat(2, 1fr);
  }
}

.spec-cell {
  background: #F9FAFB;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #F3F4F6;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.spec-label {
  font-size: 11px;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.spec-val {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.description-content {
  font-size: 15px;
  line-height: 1.7;
  color: #374151;
  white-space: pre-line;
  margin: 0;
}

.pricing-contact-sidebar {
  position: sticky;
  top: 90px;
}

.price-action-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.price-amount-box {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 12px;
}

.price-val {
  font-size: 30px;
  font-weight: 800;
  color: #111827;
}

.period-text {
  font-size: 14px;
  color: #6B7280;
}

.ai-valuation-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #F0FDF4;
  border: 1px solid #DCFCE7;
  color: #166534;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 20px;
}

.contact-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-primary-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  background: var(--blue-primary, #2878C8);
  color: #FFFFFF;
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.contact-primary-btn:hover {
  opacity: 0.95;
}

.call-svg, .tg-svg {
  width: 20px;
  height: 20px;
}

.contact-telegram-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  background: #229ED9;
  color: #FFFFFF;
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.contact-telegram-btn:hover {
  opacity: 0.95;
}

.source-original-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: #6B7280;
  text-decoration: none;
  margin-top: 6px;
}

.source-original-link:hover {
  color: #111827;
}

.arrow-svg {
  width: 14px;
  height: 14px;
}

.related-listings-section {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid #E5E7EB;
}

.related-heading {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 20px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
</style>

