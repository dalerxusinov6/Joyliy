<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'
import ListingDetail from '~/components/ListingDetail.vue'
import { useModals } from '~/composables/useModals'

const route = useRoute()
const router = useRouter()
const listingId = computed(() => Number(route.params.id))

const { t, tDistrict, formatPrice } = useI18n()
const { isFavorite, toggleFavorite } = useFavorites()
const { listings, fetchListings, mapRawItem } = useListings()
const { showToast } = useModals()

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

const mapped = computed(() => (listing.value ? (mapRawItem(listing.value as any, 0) as ListingItem) : null))
const goTo = (l: ListingItem) => navigateTo(`/elon/${l.id}`)
</script>

<template>
  <div class="elon-page">
    <ListingDetail v-if="mapped" :key="mapped.id" :listing="mapped" page @select="goTo" @toast="showToast" />
    <div v-else class="wrap nf">
      <p class="p-label">404</p>
      <h1>E’lon topilmadi</h1>
      <p class="p-muted">Bu e’lon mavjud emas yoki arxivlangan.</p>
      <NuxtLink to="/" class="pbtn dark">Bosh sahifaga qaytish</NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.nf { padding-top: 160px; padding-bottom: 120px; display: grid; gap: 14px; justify-items: start; }
.nf h1 { margin: 0; font: 300 clamp(2rem, 4vw, 3.4rem)/1.06 var(--font-sans); letter-spacing: -.04em; }
</style>
