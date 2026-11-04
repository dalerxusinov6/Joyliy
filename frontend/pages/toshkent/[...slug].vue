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
const goListing = (l: ListingItem) => navigateTo(`/elon/${l.id}`)
</script>

<template>
  <div class="seo">
    <div class="wrap">
      <nav aria-label="Breadcrumb" class="bc">
        <ol>
          <li><NuxtLink to="/">{{ t('home') }}</NuxtLink></li>
          <li aria-hidden="true">/</li>
          <li><NuxtLink to="/toshkent">Toshkent</NuxtLink></li>
          <template v-if="slugArray.length > 0">
            <li aria-hidden="true">/</li>
            <li class="cur" aria-current="page">{{ seoInfo.breadcrumb }}</li>
          </template>
        </ol>
      </nav>

      <header class="hd">
        <p class="p-label">Toshkent · katalog</p>
        <h1>{{ seoInfo.h1 }}</h1>
        <p class="intro">{{ seoInfo.description }}</p>
        <div class="chips">
          <NuxtLink v-for="c in [['rooms_1', '/toshkent/1-xonali-kvartiralar', '1 xonali'], ['rooms_2', '/toshkent/2-xonali-kvartiralar', '2 xonali'], ['rooms_3', '/toshkent/3-xonali-kvartiralar', '3 xonali'], ['cheap', '/toshkent/arzon-kvartiralar', 'Arzon narxlar'], ['sale', '/toshkent/sotiladigan-uylar', 'Sotiladigan'], ['rent', '/toshkent/ijaraga-kvartiralar', 'Ijara']]" :key="c[0]" :to="c[1]" class="chip" :class="{ on: pageType === c[0] }">{{ c[2] }}</NuxtLink>
        </div>
        <p class="count"><b>{{ matchedListings.length }} ta</b> e’lon topildi</p>
      </header>

      <div v-if="matchedListings.length === 0" class="empty">
        <b>Bu mezon bo‘yicha hozircha e’lonlar yo‘q</b>
        <p>Boshqa tuman yoki parametrlarni tanlab ko‘ring yoki barcha Toshkent e’lonlarini ko‘ring.</p>
        <NuxtLink to="/toshkent" class="pbtn dark">Barcha e’lonlarni ko‘rish</NuxtLink>
      </div>
      <div v-else class="grid">
        <ListingCard v-for="item in matchedListings" :key="item.id" :listing="item" @select="goListing" />
      </div>

      <section class="dirs">
        <h2>Toshkent tumanlari bo‘yicha qidiruv</h2>
        <div class="dg">
          <NuxtLink v-for="d in DISTRICT_LIST" :key="d.slug" :to="'/toshkent/' + d.slug" class="da" :class="{ on: activeDistrict?.uz === d.name }">
            <b>{{ tDistrict(d.name) }}</b><span>tumanidagi kvartiralar</span>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.seo { padding-top: 110px; padding-bottom: 96px; }
.bc ol { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; font-size: 13px; color: var(--tx-muted); }
.bc a { color: inherit; text-decoration: none; }
.bc a:hover { color: var(--tx); }
.bc .cur { color: var(--tx); font-weight: 600; }
.hd { display: grid; gap: 14px; margin: 28px 0 40px; }
h1 { margin: 0; font: 300 clamp(2rem, 4.4vw, 3.6rem)/1.06 var(--font-sans); letter-spacing: -.04em; max-width: 22ch; text-wrap: balance; }
.intro { margin: 0; color: var(--tx-muted); max-width: 64ch; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { border: 1px solid var(--brand-sand); border-radius: 999px; padding: 9px 16px; font: 700 13px var(--font-sans); color: var(--tx); text-decoration: none; }
.chip:hover { border-color: var(--blue-primary); }
.chip.on { background: var(--accent-black); color: var(--on-ink); border-color: var(--accent-black); }
.count { margin: 0; color: var(--tx-muted); font-size: 14px; }
.count b { color: var(--tx); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 30px 20px; }
.empty { padding: 56px 20px; text-align: center; border: 1px dashed var(--brand-sand); border-radius: 28px; display: grid; gap: 12px; justify-items: center; }
.empty b { font: 600 22px var(--font-sans); }
.empty p { margin: 0; color: var(--tx-muted); max-width: 44ch; }
.dirs { margin-top: 80px; }
.dirs h2 { margin: 0 0 20px; font: 300 clamp(1.6rem, 3vw, 2.4rem)/1.1 var(--font-sans); letter-spacing: -.03em; }
.dg { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px; }
.da { display: grid; gap: 2px; padding: 16px; border-radius: 20px; background: var(--surface); text-decoration: none; color: var(--tx); }
.da:hover { background: var(--surface-subtle); }
.da.on { background: var(--accent-black); color: var(--on-ink); }
.da b { font-weight: 700; }
.da span { font-size: 12px; opacity: .7; }
</style>
