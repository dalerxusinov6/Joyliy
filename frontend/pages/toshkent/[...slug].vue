<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'
import ListingCard from '~/components/ListingCard.vue'

const route = useRoute()
const { t, tDistrict } = useI18n()
const { listings, fetchListings } = useListings()

// Pre-fetch listings if not loaded
if (!listings.value || listings.value.length === 0) {
  await fetchListings()
}

// Slugs mapping & district intelligence
const DISTRICT_MAP: Record<string, { uz: string; ru: string; db: string[] }> = {
  'chilonzor': { uz: 'Chilonzor', ru: 'Чиланзар', db: ['Chilonzor', 'Чиланзар'] },
  'yunusobod': { uz: 'Yunusobod', ru: 'Юнусабад', db: ['Yunusobod', 'Юнусабад'] },
  'mirzo-ulugbek': { uz: 'Mirzo Ulug‘bek', ru: 'Мирзо-Улугбек', db: ['Mirzo Ulug‘bek', 'Mirzo Ulug\'bek', 'Mirzo Ulugbek', 'Мирзо-Улугбек'] },
  'yakkasaroy': { uz: 'Yakkasaroy', ru: 'Яккасарай', db: ['Yakkasaroy', 'Яккасарай'] },
  'mirobod': { uz: 'Mirobod', ru: 'Мирабад', db: ['Mirobod', 'Мирабад'] },
  'shayxontohur': { uz: 'Shayxontohur', ru: 'Шайхантахур', db: ['Shayxontohur', 'Шайхантахур'] },
  'olmazor': { uz: 'Olmazor', ru: 'Алмазар', db: ['Olmazor', 'Алмазар'] },
  'uchtepa': { uz: 'Uchtepa', ru: 'Учтепа', db: ['Uchtepa', 'Учтепа'] },
  'sergeli': { uz: 'Sergeli', ru: 'Сергели', db: ['Sergeli', 'Сергели'] },
  'yashnobod': { uz: 'Yashnobod', ru: 'Яшнабад', db: ['Yashnobod', 'Яшнабад'] },
  'bektemir': { uz: 'Bektemir', ru: 'Бектемир', db: ['Bektemir', 'Бектемир'] },
  'yangihayot': { uz: 'Yangi Hayot', ru: 'Янгихаёт', db: ['Yangi Hayot', 'Yangihayot', 'Янгихаёт'] },
}

const DISTRICT_LIST = [
  { slug: 'chilonzor', name: 'Chilonzor' },
  { slug: 'yunusobod', name: 'Yunusobod' },
  { slug: 'mirzo-ulugbek', name: 'Mirzo Ulug‘bek' },
  { slug: 'yakkasaroy', name: 'Yakkasaroy' },
  { slug: 'mirobod', name: 'Mirobod' },
  { slug: 'shayxontohur', name: 'Shayxontohur' },
  { slug: 'olmazor', name: 'Olmazor' },
  { slug: 'uchtepa', name: 'Uchtepa' },
  { slug: 'sergeli', name: 'Sergeli' },
  { slug: 'yashnobod', name: 'Yashnobod' },
  { slug: 'bektemir', name: 'Bektemir' },
  { slug: 'yangihayot', name: 'Yangi Hayot' },
]

// Slug parser
const slugArray = computed(() => {
  const p = route.params.slug
  if (!p) return []
  return Array.isArray(p) ? p : [p]
})

const firstSlug = computed(() => (slugArray.value[0] || '').toLowerCase())
const secondSlug = computed(() => (slugArray.value[1] || '').toLowerCase())

// Intent Detection
const pageType = computed(() => {
  if (slugArray.value.length === 0) return 'all_tashkent'

  const s = firstSlug.value
  if (s === 'arzon-kvartiralar') return 'cheap'
  if (s === 'sotiladigan-uylar') return 'sale'
  if (s === 'ijaraga-kvartiralar') return 'rent'
  if (s === '1-xonali-kvartiralar') return 'rooms_1'
  if (s === '2-xonali-kvartiralar') return 'rooms_2'
  if (s === '3-xonali-kvartiralar') return 'rooms_3'
  if (s === '4-xonali-kvartiralar') return 'rooms_4'

  if (DISTRICT_MAP[s]) {
    if (secondSlug.value === 'kvartiralar') return 'district_apartments'
    return 'district'
  }

  return 'generic'
})

const activeDistrict = computed(() => {
  const s = firstSlug.value
  return DISTRICT_MAP[s] || null
})

// Filtered Listings for this Landing Page
const matchedListings = computed(() => {
  const all = listings.value || []

  switch (pageType.value) {
    case 'district':
    case 'district_apartments': {
      if (!activeDistrict.value) return all
      const dbNames = activeDistrict.value.db
      return all.filter((x) => x.district && dbNames.includes(x.district))
    }
    case 'rooms_1':
      return all.filter((x) => x.rooms === 1)
    case 'rooms_2':
      return all.filter((x) => x.rooms === 2)
    case 'rooms_3':
      return all.filter((x) => x.rooms === 3)
    case 'rooms_4':
      return all.filter((x) => (x.rooms || 0) >= 4)
    case 'cheap':
      return all.filter(
        (x) => x.fair_price_category === 'BELOW_MARKET' || (x.price_uzs && x.price_uzs < 5000000)
      )
    case 'sale':
      return all.filter((x) => x.deal_type === 'sale')
    case 'rent':
      return all.filter((x) => x.deal_type === 'rent')
    case 'all_tashkent':
    default:
      return all
  }
})

// SEO Titles & Descriptions
const seoInfo = computed(() => {
  const count = matchedListings.value.length

  switch (pageType.value) {
    case 'district':
    case 'district_apartments': {
      const dName = activeDistrict.value ? activeDistrict.value.uz : 'Toshkent'
      return {
        h1: `${dName} tumanida kvartiralar`,
        title: `${dName}da kvartiralar va uylar (${count} ta e'lon) — Joyliy.uz`,
        description: `Toshkent shahri ${dName} tumanidagi barcha faol ijara va sotuv kvartiralari. Egasidan to'g'ridan-to'g'ri variantlar, fotosuratlar va batafsil xaritalar Joyliy.uz saytida.`,
        breadcrumb: dName,
      }
    }
    case 'rooms_1':
      return {
        h1: 'Toshkentda 1 xonali kvartiralar',
        title: `Toshkentda 1 xonali kvartiralar (${count} ta variant) — Joyliy.uz`,
        description: `Toshkent shahri bo'ylab eng yaxshi 1 xonali kvartiralar katalogi. Talabalar, yosh oilalar va mutaxassislar uchun qulay ijara va sotuv e'lonlari.`,
        breadcrumb: '1 xonali kvartiralar',
      }
    case 'rooms_2':
      return {
        h1: 'Toshkentda 2 xonali kvartiralar',
        title: `Toshkentda 2 xonali kvartiralar (${count} ta variant) — Joyliy.uz`,
        description: `Toshkent shahrida 2 xonali qulay xonadonlar. Narxlari, fotogalereyasi va tumanlar bo'yicha saralangan e'lonlar bazasi.`,
        breadcrumb: '2 xonali kvartiralar',
      }
    case 'rooms_3':
      return {
        h1: 'Toshkentda 3 xonali kvartiralar',
        title: `Toshkentda 3 xonali kvartiralar (${count} ta variant) — Joyliy.uz`,
        description: `Toshkentda keng va shinam 3 xonali kvartiralar. Oilalar uchun eng ma'qul narxlar va fotosuratlar Joyliy.uz da.`,
        breadcrumb: '3 xonali kvartiralar',
      }
    case 'rooms_4':
      return {
        h1: 'Toshkentda 4+ xonali katta kvartiralar',
        title: `Toshkentda 4+ xonali kvartiralar (${count} ta variant) — Joyliy.uz`,
        description: `Toshkent shahridagi premium va katta maydonli 4 va undan ortiq xonali kvartiralar.`,
        breadcrumb: '4+ xonali kvartiralar',
      }
    case 'cheap':
      return {
        h1: 'Toshkentda arzon va hamyonbop kvartiralar',
        title: `Toshkentda arzon kvartiralar (${count} ta variant) — Joyliy.uz`,
        description: `Bozor narxidan arzon, eng hamyonbop ijara va sotuv kvartiralari Toshkent bo'ylab Joyliy.uz da.`,
        breadcrumb: 'Arzon kvartiralar',
      }
    case 'sale':
      return {
        h1: 'Toshkentda sotiladigan uylar va kvartiralar',
        title: `Toshkentda sotiladigan kvartiralar (${count} ta taklif) — Joyliy.uz`,
        description: `Toshkent shahrida uy sotib olish uchun yangi bino va ikkilamchi bozor e'lonlari Joyliy.uz platformasida.`,
        breadcrumb: 'Sotiladigan uylar',
      }
    case 'rent':
      return {
        h1: 'Toshkentda ijaraga kvartiralar',
        title: `Toshkentda ijara kvartiralar (${count} ta taklif) — Joyliy.uz`,
        description: `Toshkent shahrida oylik ijara uchun barcha turdagi xonadonlar va uylar. Egasidan to'g'ridan-to'g'ri qidiruv.`,
        breadcrumb: 'Ijaraga kvartiralar',
      }
    case 'all_tashkent':
    default:
      return {
        h1: 'Toshkentda ko‘chmas mulk va kvartiralar',
        title: `Toshkentda kvartiralar (${count} ta e'lon) — Joyliy.uz`,
        description: `Toshkent shahridagi barcha faol ijara va sotuv e'lonlari. Tumanlar, xonalar soni va narxlar bo'yicha qulay qidiruv.`,
        breadcrumb: 'Barcha e‘lonlar',
      }
  }
})

const currentPath = computed(() => {
  const p = route.path
  return `https://joyliy.uz${p}`
})

// Indexing logic: Noindex thin or empty landing pages
const shouldIndex = computed(() => {
  return matchedListings.value.length >= 2
})

useSeoMeta({
  title: () => seoInfo.value.title,
  description: () => seoInfo.value.description,
  canonical: currentPath,
  ogTitle: () => seoInfo.value.title,
  ogDescription: () => seoInfo.value.description,
  ogImage: 'https://joyliy.uz/apple-touch-icon.png',
  ogUrl: currentPath,
  ogType: 'website',
  twitterCard: 'summary_large_image',
  twitterTitle: () => seoInfo.value.title,
  twitterDescription: () => seoInfo.value.description,
  robots: () => (shouldIndex.value ? 'index, follow' : 'noindex, follow'),
})

// Schema.org Structured Data
useHead(() => {
  const breadcrumbList = {
    '@context': 'https://schema.org',
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
    ],
  }

  if (slugArray.value.length > 0) {
    breadcrumbList.itemListElement.push({
      '@type': 'ListItem',
      position: 3,
      name: seoInfo.value.breadcrumb,
      item: currentPath.value,
    })
  }

  const collectionSchema = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: seoInfo.value.h1,
    description: seoInfo.value.description,
    url: currentPath.value,
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: matchedListings.value.length,
      itemListElement: matchedListings.value.slice(0, 20).map((item, idx) => ({
        '@type': 'ListItem',
        position: idx + 1,
        url: `https://joyliy.uz/elon/${item.id}`,
        name: item.title,
      })),
    },
  }

  return {
    link: [
      { rel: 'canonical', href: currentPath.value },
      { rel: 'alternate', hreflang: 'uz', href: currentPath.value },
      { rel: 'alternate', hreflang: 'ru', href: `${currentPath.value}?lang=ru` },
      { rel: 'alternate', hreflang: 'x-default', href: currentPath.value },
    ],
    script: [
      {
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@graph': [breadcrumbList, collectionSchema],
        }),
      },
    ],
  }
})
</script>

<template>
  <div class="seo-landing-container">
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
        <li v-if="slugArray.length > 0" class="breadcrumb-sep">/</li>
        <li v-if="slugArray.length > 0" class="breadcrumb-item current" aria-current="page">
          <span>{{ seoInfo.breadcrumb }}</span>
        </li>
      </ol>
    </nav>

    <!-- Hero Header -->
    <header class="seo-hero-header">
      <h1 class="landing-h1">{{ seoInfo.h1 }}</h1>
      <p class="landing-intro">{{ seoInfo.description }}</p>

      <!-- Quick Room Count Filter Chips -->
      <div class="category-pills-row">
        <NuxtLink
          to="/toshkent/1-xonali-kvartiralar"
          class="pill-link"
          :class="{ active: pageType === 'rooms_1' }"
        >
          1 xonali
        </NuxtLink>
        <NuxtLink
          to="/toshkent/2-xonali-kvartiralar"
          class="pill-link"
          :class="{ active: pageType === 'rooms_2' }"
        >
          2 xonali
        </NuxtLink>
        <NuxtLink
          to="/toshkent/3-xonali-kvartiralar"
          class="pill-link"
          :class="{ active: pageType === 'rooms_3' }"
        >
          3 xonali
        </NuxtLink>
        <NuxtLink
          to="/toshkent/arzon-kvartiralar"
          class="pill-link"
          :class="{ active: pageType === 'cheap' }"
        >
          Arzon narxlar
        </NuxtLink>
        <NuxtLink
          to="/toshkent/sotiladigan-uylar"
          class="pill-link"
          :class="{ active: pageType === 'sale' }"
        >
          Sotiladigan
        </NuxtLink>
        <NuxtLink
          to="/toshkent/ijaraga-kvartiralar"
          class="pill-link"
          :class="{ active: pageType === 'rent' }"
        >
          Ijara
        </NuxtLink>
      </div>

      <!-- Count Summary -->
      <div class="meta-counter-bar">
        <span class="counter-highlight">{{ matchedListings.length }} ta</span> e‘lon topildi
      </div>
    </header>

    <!-- Empty State if no listings -->
    <div v-if="matchedListings.length === 0" class="empty-results-card">
      <div class="empty-icon">🏠</div>
      <h2 class="empty-title">Bu mezon bo‘yicha hozircha e‘lonlar yo‘q</h2>
      <p class="empty-desc">
        Boshqa tuman yoki parametrlarni tanlab ko‘ring yoki barcha Toshkent e‘lonlarini ko‘ring.
      </p>
      <NuxtLink to="/toshkent" class="reset-link-btn">
        Barcha e‘lonlarni ko‘rish
      </NuxtLink>
    </div>

    <!-- Listings Grid -->
    <div v-else class="listings-catalog-grid">
      <ListingCard
        v-for="item in matchedListings"
        :key="item.id"
        :listing="item"
      />
    </div>

    <!-- Internal Linking: Explore Districts of Tashkent -->
    <section class="districts-link-directory">
      <h2 class="directory-heading">Toshkent tumanlari bo‘yicha qidiruv</h2>
      <div class="districts-link-grid">
        <NuxtLink
          v-for="d in DISTRICT_LIST"
          :key="d.slug"
          :to="'/toshkent/' + d.slug"
          class="district-anchor-card"
          :class="{ active: activeDistrict?.uz === d.name }"
        >
          <span class="d-name">{{ d.name }}</span>
          <span class="d-sub">tumanidagi kvartiralar</span>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.seo-landing-container {
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
}

.seo-hero-header {
  margin-bottom: 32px;
}

.landing-h1 {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  letter-spacing: -0.02em;
  margin: 0 0 12px;
}

.landing-intro {
  font-size: 15px;
  color: #4B5563;
  line-height: 1.6;
  max-width: 760px;
  margin: 0 0 20px;
}

.category-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.pill-link {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  text-decoration: none;
  transition: all 0.15s ease;
}

.pill-link:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
}

.pill-link.active {
  background: var(--blue-primary, #2878C8);
  border-color: var(--blue-primary, #2878C8);
  color: #FFFFFF;
}

.meta-counter-bar {
  font-size: 14px;
  color: #6B7280;
}

.counter-highlight {
  font-weight: 700;
  color: #111827;
}

.listings-catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.empty-results-card {
  text-align: center;
  padding: 60px 20px;
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  margin-bottom: 48px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #6B7280;
  margin-bottom: 20px;
}

.reset-link-btn {
  display: inline-flex;
  align-items: center;
  padding: 10px 20px;
  background: var(--blue-primary, #2878C8);
  color: #FFFFFF;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
}

.districts-link-directory {
  margin-top: 60px;
  padding-top: 36px;
  border-top: 1px solid #E5E7EB;
}

.directory-heading {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 20px;
}

.districts-link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.district-anchor-card {
  display: flex;
  flex-direction: column;
  padding: 14px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.15s ease;
}

.district-anchor-card:hover {
  border-color: var(--blue-primary, #2878C8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.district-anchor-card.active {
  border-color: var(--blue-primary, #2878C8);
  background: #F0F7FF;
}

.d-name {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
}

.d-sub {
  font-size: 11px;
  color: #6B7280;
  margin-top: 2px;
}
</style>
