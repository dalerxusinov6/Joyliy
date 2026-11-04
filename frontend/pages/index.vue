<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useModals } from '~/composables/useModals'
import HeroSearch from '~/components/HeroSearch.vue'
import ListingCard from '~/components/ListingCard.vue'
import HeroScene from '~/components/HeroScene.vue'
import AssistantChat from '~/components/AssistantChat.vue'
import DistrictMap from '~/components/DistrictMap.vue'
import RoommatesPanel from '~/components/RoommatesPanel.vue'
import { useNeighborhoods } from '~/composables/useNeighborhoods'

const { t, tDistrict } = useI18n()
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
  filterDealType,
  filterPropertyType,
  filterAmenities,
  filterSort,
  availableDistricts,
  fetchListings,
  totalCount,
  aiSearchActive,
  aiSearchQuery,
  aiParsedCriteria,
  isAiSearching,
  resetAiMatch,
  runAiMatch,
  marketDiff,
  isNewListing,
} = useListings()

const { showFilters, showPostAd, showNeighborhoods } = useModals()
const assistantPrefill = useState<string>('assistant_prefill', () => '')
const { load: loadNb, byName: nbByName } = useNeighborhoods()
onMounted(loadNb)
const { showToast } = useModals()

await useAsyncData('listings_ssr', async () => {
  await fetchListings()
  return true
})

useSeoMeta({
  title: 'Joyliy — Toshkentda maklersiz ijara va arzon kvartiralar',
  description: 'Toshkentda egasidan maklersiz ijara kvartiralar va arzon uylar qidiruv tizimi. Joyliy.uz orqali to‘g‘ridan-to‘g‘ri tekshirilgan e‘lonlar, narx tahlili va fotosuratlar.',
  canonical: 'https://joyliy.uz/',
  ogTitle: 'Joyliy — Toshkentda maklersiz ijara va arzon kvartiralar',
  ogDescription: 'Toshkentda egasidan maklersiz ijara kvartiralar va arzon uylar qidiruv tizimi. Joyliy.uz orqali to‘g‘ridan-to‘g‘ri tekshirilgan e‘lonlar.',
  ogImage: 'https://joyliy.uz/apple-touch-icon.png',
  ogUrl: 'https://joyliy.uz/',
  ogType: 'website',
  twitterCard: 'summary_large_image',
  twitterTitle: 'Joyliy — Toshkentda maklersiz ijara',
  twitterDescription: 'Toshkentda egasidan maklersiz ijara kvartiralar va arzon uylar qidiruv tizimi.',
  robots: 'index, follow',
})

useHead({
  link: [
    { rel: 'canonical', href: 'https://joyliy.uz/' },
    { rel: 'alternate', hreflang: 'uz', href: 'https://joyliy.uz/' },
    { rel: 'alternate', hreflang: 'ru', href: 'https://joyliy.uz/?lang=ru' },
    { rel: 'alternate', hreflang: 'x-default', href: 'https://joyliy.uz/' },
  ],
  script: [
    {
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@graph': [
          {
            '@type': 'WebSite',
            '@id': 'https://joyliy.uz/#website',
            'url': 'https://joyliy.uz/',
            'name': 'Joyliy.uz',
            'description': 'Toshkentda maklersiz ijara va arzon kvartiralar qidiruv platformasi',
            'potentialAction': {
              '@type': 'SearchAction',
              'target': 'https://joyliy.uz/toshkent?q={search_term_string}',
              'query-input': 'required name=search_term_string',
            },
          },
          {
            '@type': 'Organization',
            '@id': 'https://joyliy.uz/#organization',
            'name': 'Joyliy.uz',
            'url': 'https://joyliy.uz/',
            'logo': 'https://joyliy.uz/apple-touch-icon.png',
            'sameAs': ['https://t.me/joyliy_uz'],
          },
        ],
      }),
    },
  ],
})

/* ---------- catalog ---------- */
const rentCategories = computed(() => [
  { key: '', title: t('cat_all') },
  { key: 'mk', title: t('cat_no_agent') },
  { key: 'fair_cheap', title: t('cat_below_market') },
  { key: '3days', title: t('cat_new_listings') },
  { key: 'metro', title: t('metro_near') },
  { key: 'room', title: t('cat_roommates') },
])
const saleCategories = computed(() => [
  { key: '', title: t('cat_all') },
  { key: 'mk', title: t('cat_from_owner') },
  { key: 'fair_cheap', title: t('cat_cheap_price') },
  { key: '3days', title: t('cat_new_listings') },
  { key: 'metro', title: t('metro_near') },
])
const catCount = (key: string) => {
  const deal = filterDealType.value
  return listings.value.filter((l) => {
    if ((l.deal_type || 'rent') !== deal) return false
    if (key === 'mk') return l.is_owner
    if (key === 'fair_cheap') { const d = marketDiff(l); return d !== null && d <= -10 }
    if (key === '3days') return isNewListing(l)
    if (key === 'metro') return !!l.near_metro
    if (key === 'room') return l.is_shared_room
    return true
  }).length
}
const activeCategories = computed(() => (filterDealType.value === 'sale' ? saleCategories.value : rentCategories.value))

const audienceOptions = computed(() => [
  { key: 'all', title: t('aud_all') },
  { key: 'family', title: t('aud_family') },
  { key: 'female', title: t('aud_female') },
  { key: 'male', title: t('aud_male') },
])

const onSelectListing = (item: ListingItem) => { selectedListing.value = item }

const clearFilters = async () => {
  if (aiSearchActive.value) await resetAiMatch()
  filterDistrict.value = ''
  filterRooms.value = ''
  filterMaxPrice.value = ''
  filterCategory.value = ''
  filterAudience.value = 'all'
  filterPropertyType.value = ''
  filterAmenities.value.owner_only = false
  filterAmenities.value.mebel = false
  filterAmenities.value.kond = false
  filterAmenities.value.kir = false
  filterAmenities.value.net = false
  filterSort.value = 'new'
}

const hasActiveFilters = computed(() =>
  aiSearchActive.value ||
  !!filterDistrict.value || !!filterRooms.value || !!filterMaxPrice.value || !!filterCategory.value || !!filterPropertyType.value ||
  filterAudience.value !== 'all' || filterAmenities.value.owner_only || filterAmenities.value.mebel ||
  filterAmenities.value.kond || filterAmenities.value.kir || filterAmenities.value.net || filterSort.value !== 'new',
)

const PAGE_SIZE = 12
const displayCount = ref(PAGE_SIZE)
const visibleListings = computed(() => filteredListings.value.slice(0, displayCount.value))
const hasMore = computed(() => filteredListings.value.length > displayCount.value)
const nextBatch = computed(() => Math.min(PAGE_SIZE, filteredListings.value.length - displayCount.value))
watch(
  [filterDistrict, filterRooms, filterMaxPrice, filterCategory, filterAudience, filterDealType, filterPropertyType, filterSort, aiSearchActive, () => ({ ...filterAmenities.value })],
  () => { displayCount.value = PAGE_SIZE },
)

const aiTokens = computed(() => {
  const c: any = aiParsedCriteria.value || {}
  const out: [string, string][] = []
  if (c.district) out.push(['Hudud', tDistrict(c.district)])
  if (c.rooms) out.push(['Xonalar', String(c.rooms)])
  if (c.max_price_uzs) out.push(['Byudjet', `${(c.max_price_uzs / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln gacha`])
  if (c.target_audience && c.target_audience !== 'any') out.push(['Kim uchun', t(`aud_${c.target_audience}`)])
  if (c.owner_only) out.push(['Manba', t('cat_no_agent')])
  if (c.near_metro) out.push(['Joylashuv', t('metro_near')])
  return out
})

const catalogTitle = computed(() => {
  if (aiSearchActive.value) return `AI: ${filteredListings.value.length} ta mos uy`
  return filterDealType.value === 'sale' ? t('catalog_title_sale') : t('catalog_title_rent')
})

/* ---------- featured / latest ---------- */
const featuredDeal = ref<'rent' | 'sale'>('rent')
const featured = computed(() => {
  const pool = listings.value
    .filter((l) => (l.deal_type || 'rent') === featuredDeal.value && (l.image_urls || []).length >= 3 && l.area >= 40 && l.area <= 220 && !l.is_shared_room && (l.scam_risk_score ?? 0) <= 25)
    .sort((a, b) => Number(b.is_owner) - Number(a.is_owner) || b.price_uzs - a.price_uzs)
  const seen = new Set<string>()
  const pick: ListingItem[] = []
  for (const l of pool) { if (seen.has(l.district)) continue; seen.add(l.district); pick.push(l); if (pick.length === 4) break }
  return pick
})
const latest = computed(() => [...listings.value].filter((l) => !l.is_shared_room && (l.image_urls || []).length).sort((a, b) => (a.days_ago ?? 0) - (b.days_ago ?? 0) || b.id - a.id).slice(0, 14))
const rail = ref<HTMLElement | null>(null)
const railBy = (d: number) => rail.value?.scrollBy({ left: d * 320, behavior: 'smooth' })

/* ---------- districts ---------- */
const districtCards = computed(() =>
  availableDistricts.value
    .map((d) => {
      const ls = listings.value.filter((x) => x.district === d)
      const rent = ls.filter((x) => (x.deal_type || 'rent') === 'rent')
      const avg = rent.length ? Math.round(rent.reduce((s, x) => s + x.price_uzs, 0) / rent.length) : 0
      const img = ls.find((x) => (x.image_urls || []).length && !x.is_shared_room)?.image_urls[0]
      return { name: d, count: ls.length, avg, img }
    })
    .filter((d) => d.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, 8),
)
const pickDistrict = async (d: string) => {
  if (aiSearchActive.value) await resetAiMatch()
  filterDistrict.value = d
  filterCategory.value = ''
  document.getElementById('katalog')?.scrollIntoView({ behavior: 'smooth' })
}

/* ---------- stats (live from loaded listings) ---------- */
const stats = computed(() => {
  const all = listings.value
  return {
    total: totalCount.value || all.length,
    today: all.filter((x) => (x.days_ago ?? 99) === 0).length,
    districts: new Set(all.map((x) => x.district).filter(Boolean)).size,
    owner: all.filter((x) => x.is_owner).length,
  }
})

/* ---------- AI advisor ---------- */
const onShowAll = async (q: string) => {
  await runAiMatch(q)
  document.getElementById('katalog')?.scrollIntoView({ behavior: 'smooth' })
}

const toTop = () => { if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' }) }
const money = (v: number) => `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln`
</script>

<template>
  <div class="home">
    <HeroSearch @openFilters="showFilters = true" />

    <!-- CATALOG -->
    <section id="katalog" class="sec">
      <div class="wrap">
        <div class="head">
          <div>
            <p class="label">{{ aiSearchActive ? 'AI qidiruv natijalari' : 'Katalog' }}</p>
            <h2>{{ catalogTitle }}</h2>
          </div>
          <div class="head-acts">
            <a class="btn-line" href="#xarita">
              <svg viewBox="0 0 24 24" class="ic"><path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4z" /><path d="M8 2v16M16 6v16" /></svg>{{ t('map') }}
            </a>
            <button type="button" class="btn-line" @click="showFilters = true">
              <svg viewBox="0 0 24 24" class="ic"><path d="M4 7h10M18 7h2M4 17h4M12 17h8" /><circle cx="16" cy="7" r="2" /><circle cx="10" cy="17" r="2" /></svg>{{ t('more_filters') }}
            </button>
            <a class="btn-line" href="https://t.me/joyliy_bot" target="_blank" rel="noopener" title="Yangi e’lonlar xabarnomasini Telegram bot orqali yoqing">
              <svg viewBox="0 0 24 24" class="ic"><path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z" /><path d="M10 20a2 2 0 0 0 4 0" /></svg>Qidiruvni kuzatish
            </a>
            <button v-if="hasActiveFilters" type="button" class="btn-line" @click="clearFilters">{{ t('reset_filter') }} ×</button>
          </div>
        </div>

        <div v-if="aiSearchActive" class="ai-banner">
          <span class="orb" aria-hidden="true"></span>
          <div class="toks">
            <span class="tok q">“{{ aiSearchQuery }}”</span>
            <span v-for="(tk, i) in aiTokens" :key="i" class="tok"><i>{{ tk[0] }}</i>{{ tk[1] }}</span>
          </div>
          <button type="button" class="link" @click="clearFilters">Oddiy katalogga qaytish</button>
        </div>

        <template v-else>
          <div class="chips" role="group" aria-label="Toifalar">
            <button v-for="cat in activeCategories" :key="cat.key" type="button" class="chip" :aria-pressed="filterCategory === cat.key" @click="filterCategory = cat.key">{{ cat.title }}<small>{{ catCount(cat.key) }}</small></button>
          </div>
          <div v-if="filterDealType === 'rent'" class="aud">
            <span class="label">{{ t('tenants_lbl') }}</span>
            <button v-for="a in audienceOptions" :key="a.key" type="button" class="chip sm" :aria-pressed="filterAudience === a.key" @click="filterAudience = a.key">{{ a.title }}</button>
            <label class="sort">
              <span class="sr">{{ t('sort_order') }}</span>
              <select v-model="filterSort">
                <option value="new">{{ t('sort_new') }}</option>
                <option value="lo">{{ t('sort_low') }}</option>
                <option value="hi">{{ t('sort_high') }}</option>
              </select>
            </label>
          </div>
        </template>

        <p v-if="!isLoading && !isAiSearching" class="sum">{{ filteredListings.length }} ta e’lon</p>
        <div v-if="isLoading || isAiSearching" class="grid">
          <div v-for="n in 8" :key="n" class="skel"><div class="sk-ph"></div><div class="sk-l"></div><div class="sk-l s"></div></div>
        </div>
        <div v-else-if="visibleListings.length" class="grid">
          <ListingCard v-for="item in visibleListings" :key="item.id" :listing="item" @select="onSelectListing" />
        </div>
        <div v-else class="empty">
          <b>{{ t('empty_listings_title') }}</b>
          <p>{{ t('empty_listings_desc') }}</p>
          <button type="button" class="btn-dark" @click="clearFilters">{{ t('reset_filter') }}</button>
        </div>
        <div v-if="hasMore && !isLoading" class="more">
          <button type="button" class="btn-line" @click="displayCount += PAGE_SIZE">{{ t('load_more_btn', { count: nextBatch }) }}</button>
        </div>
      </div>
    </section>

    <!-- FEATURED -->
    <section v-if="featured.length" class="sec pt0">
      <div class="wrap">
        <div class="head">
          <div><p class="label">Tanlov</p><h2>Tavsiya etilgan <em>uylar</em></h2></div>
          <div class="tabs" role="group" aria-label="Tavsiyalar turi">
            <button type="button" :aria-pressed="featuredDeal === 'rent'" @click="featuredDeal = 'rent'">Ijara</button>
            <button type="button" :aria-pressed="featuredDeal === 'sale'" @click="featuredDeal = 'sale'">Sotuv</button>
          </div>
        </div>
        <div class="ed">
          <ListingCard v-if="featured[0]" :listing="featured[0]" size="big" @select="onSelectListing" />
          <ListingCard v-if="featured[1]" :listing="featured[1]" size="mid" @select="onSelectListing" />
          <ListingCard v-if="featured[2]" :listing="featured[2]" size="mid" @select="onSelectListing" />
          <ListingCard v-if="featured[3]" :listing="featured[3]" size="wide" @select="onSelectListing" />
        </div>
      </div>
    </section>

    <!-- AI ADVISOR -->
    <section id="maslahatchi" class="sec pt0">
      <div class="wrap">
        <div class="adv">
          <div>
            <p class="label lt">Joyliy AI maslahatchi</p>
            <h2>Ijara bo‘yicha savolingizga <em>darhol javob.</em></h2>
            <p class="sub">Shartnoma, zalog, kommunal to‘lovlar va firibgarlikdan himoya — Toshkent ijara amaliyoti bo‘yicha maslahat. Uy qidirish so‘rovlarini ham tushunadi.</p>
            <div class="cap">
              <div><svg viewBox="0 0 24 24" class="ic"><path d="M6 3h9l4 4v14H6z" /><path d="M9 12h7M9 16h7M14 3v5h5" /></svg><span><b>Shartnoma va soliq</b>ijara.soliq.uz orqali ro‘yxatdan o‘tkazish tartibi</span></div>
              <div><svg viewBox="0 0 24 24" class="ic"><circle cx="12" cy="12" r="9" /><path d="M12 6v12M15 9.5c-.5-1-1.6-1.5-3-1.5-1.7 0-3 .9-3 2s1.3 1.8 3 2 3 .9 3 2-1.3 2-3 2c-1.4 0-2.5-.5-3-1.5" /></svg><span><b>Zalog va kommunal</b>Depozit qaytarilishi va to‘lovlar kimning zimmasida</span></div>
              <div><svg viewBox="0 0 24 24" class="ic"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" /><path d="M9 12l2 2 4-4" /></svg><span><b>Firibgarlikdan himoya</b>Oldindan to‘lov, avans va soxta e’lon belgilari</span></div>
              <div><svg viewBox="0 0 24 24" class="ic"><circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" /></svg><span><b>Uy topish</b>“Yakkasaroyda 2 xonali, 8 mln gacha” kabi so‘rovlar</span></div>
            </div>
          </div>
          <div class="inline-chat">
            <div class="ihd"><span class="orb lg" aria-hidden="true"></span><div><b>Joyliy AI</b><span>{{ t('bot_subtitle') }}</span></div></div>
            <AssistantChat class="ichat" @select="onSelectListing" @showAll="onShowAll" />
          </div>
        </div>
      </div>
    </section>

    <!-- DISTRICTS -->
    <section id="tumanlar" class="sec pt0">
      <div class="wrap">
        <div class="head">
          <div><p class="label">Hududlar</p><h2>Qayerdan uy <em>qidiryapsiz?</em></h2></div>
          <p class="muted">Har bir tumanning infratuzilma bahosi, narx darajasi va faol e’lonlari. Tumanni bosib e’lonlarini oching.</p>
        </div>
        <div class="loc">
          <button v-for="d in districtCards" :key="d.name" type="button" class="lc" @click="pickDistrict(d.name)">
            <img v-if="d.img" :src="d.img" alt="" loading="lazy" referrerpolicy="no-referrer" />
            <span v-if="nbByName(d.name)" class="score">{{ nbByName(d.name)!.overall_score }} / 10</span>
            <span class="t"><b>{{ tDistrict(d.name) }}</b><span>{{ t('district_apts_count', { count: d.count }) }}<template v-if="nbByName(d.name)"> · {{ nbByName(d.name)!.price_tier.split(' (')[0] }}</template></span></span>
          </button>
        </div>
        <div class="cities" aria-label="Shaharlar">
          <span class="city on">Toshkent shahri <small>{{ stats.total }} e’lon</small></span>
          <span v-for="c in ['Samarqand', 'Buxoro', 'Farg‘ona', 'Andijon', 'Namangan']" :key="c" class="city">{{ c }} <small>tez kunda</small></span>
        </div>
      </div>
    </section>

    <!-- LATEST -->
    <section v-if="latest.length" class="sec pt0">
      <div class="wrap">
        <div class="head">
          <div><p class="label">So‘nggi kunlar</p><h2>Yangi <em>e’lonlar</em></h2></div>
          <div class="rail-ctrl">
            <button type="button" aria-label="Oldingi" @click="railBy(-1)"><svg viewBox="0 0 24 24" class="ic"><path d="M15 6l-6 6 6 6" /></svg></button>
            <button type="button" aria-label="Keyingi" @click="railBy(1)"><svg viewBox="0 0 24 24" class="ic"><path d="M9 6l6 6-6 6" /></svg></button>
          </div>
        </div>
        <div ref="rail" class="rail">
          <ListingCard v-for="item in latest" :key="item.id" :listing="item" size="rail" @select="onSelectListing" />
        </div>
      </div>
    </section>

    <!-- MAP -->
    <section id="xarita" class="sec pt0">
      <div class="wrap">
        <div class="head">
          <div><p class="label">Xarita</p><h2>Xaritadan o‘zingizga mos <em>uy toping.</em></h2></div>
          <p class="muted">Tuman markazlari haqiqiy koordinatalar bo‘yicha joylashtirilgan. Tumanni bosing — e’lonlar o‘ng tomonda chiqadi.</p>
        </div>
        <DistrictMap @select="onSelectListing" @guide="showNeighborhoods = true" />
      </div>
    </section>

    <!-- ROOMMATES -->
    <section id="hamxona" class="sec pt0">
      <div class="wrap">
        <div class="head">
          <div><p class="label">{{ t('roommates_tab') }}</p><h2>Birga yashash uchun <em>sherik toping.</em></h2></div>
          <p class="muted">Talabalar va yosh mutaxassislar uchun: anketa to‘ldiring yoki mos hamxonalar bilan bog‘laning.</p>
        </div>
        <RoommatesPanel @toast="showToast" />
      </div>
    </section>

    <!-- STATS + WHY -->
    <section class="sec pt0">
      <div class="wrap">
        <div class="head"><div><p class="label">{{ t('why_title') }}</p><h2>Uy-joy ijarasining <em>yangi standarti</em></h2></div></div>
        <div class="stats">
          <ClientOnly><HeroScene variant="stats" /></ClientOnly>
          <div class="stat-panel">
            <div><b>{{ stats.total.toLocaleString('ru-RU') }}</b><span>Faol e’lonlar</span></div>
            <div><b>{{ stats.today }}</b><span>Bugun qo‘shilgan</span></div>
            <div><b>{{ stats.districts }}</b><span>Qamrab olingan tumanlar</span></div>
            <div><b>{{ stats.owner }}</b><span>Egasidan deb aniqlangan</span></div>
          </div>
        </div>
        <div class="why">
          <div><b>0%</b><h3>Vositachilik to‘lovi yo‘q</h3><p>Makler va ortiqcha komissiyasiz. Mulk egasi bilan to‘g‘ridan-to‘g‘ri, shaffof shartnoma tuzing.</p></div>
          <div><b>AI</b><h3>Bozor narxi tahlili</h3><p>Har bir e’lon tumandagi o‘xshash xonadonlar bilan solishtiriladi: arzonmi, bozor narxidami yoki qimmatmi.</p></div>
          <div><b>Xavfsiz</b><h3>Firibgarlik tekshiruvi</h3><p>Oldindan to‘lov, avans, karta talabi, takroriy rasmlar va shubhali havolalar avtomatik aniqlanadi.</p></div>
        </div>
      </div>
    </section>

    <!-- CTA + OWNERS -->
    <section class="sec pt0">
      <div class="wrap owners">
        <div class="cta-box">
          <ClientOnly><HeroScene variant="cta" /></ClientOnly>
          <div class="cta-in">
            <p class="label lt">Joyliy</p>
            <h2>Yangi manzilingiz <em>shu yerdan</em> boshlanadi.</h2>
            <div class="row">
              <a href="#top" class="btn-light" @click.prevent="toTop">Uy topish</a>
              <button type="button" class="btn-ghost" @click="showPostAd = true">{{ t('post_ad') }}</button>
            </div>
          </div>
        </div>
        <div class="own">
          <p class="label">{{ t('cta_landlord_badge') }}</p>
          <h3>{{ t('cta_landlord_title') }}</h3>
          <p class="muted">{{ t('cta_landlord_desc') }}</p>
          <ol>
            <li>Turi va manzilni tanlang</li>
            <li>Narx, xonalar va rasmlarni qo‘shing</li>
            <li>Moderatsiyadan so‘ng e’lon sayt va Telegram kanalda chiqadi</li>
          </ol>
          <button type="button" class="btn-dark" @click="showPostAd = true">{{ t('cta_landlord_btn') }}</button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.chip small { font-weight: 500; opacity: .7; margin-left: 6px; }
.sum { margin: 0 0 18px; font-size: 14px; color: var(--tx-muted); }
.cap { display: grid; gap: 2px; margin-top: 28px; }
.cap div { display: grid; grid-template-columns: 28px 1fr; gap: 12px; padding: 12px 0; border-top: 1px solid rgba(213, 200, 181, .16); font-size: 14px; color: #CFC6B8; }
.cap b { display: block; color: #F5F1E9; font-weight: 700; }
.cap .ic { color: var(--brand-sand); margin-top: 2px; width: 20px; height: 20px; }
.inline-chat { background: var(--bg); color: var(--tx); border-radius: 28px; height: 560px; overflow: hidden; box-shadow: 0 30px 60px -30px rgba(0, 0, 0, .6); display: flex; flex-direction: column; min-width: 0; }
.ihd { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--bd); flex: none; }
.ihd b { display: block; font-weight: 700; }
.ihd span:not(.orb) { font-size: 12px; color: var(--tx-muted); }
.orb.lg { width: 32px; height: 32px; }
.ichat { flex: 1; min-height: 0; }
.lc .score { position: absolute; top: 14px; left: 14px; z-index: 1; padding: 6px 10px; border-radius: 999px; background: rgba(245, 241, 233, .92); color: #262521; font: 700 12px var(--font-sans); }
.cities { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 22px; }
.city { padding: 9px 15px; border-radius: 999px; border: 1px solid var(--brand-sand); font: 600 14px var(--font-sans); }
.city.on { background: var(--accent-black); color: var(--on-ink); border-color: var(--accent-black); }
.city small { font-weight: 500; opacity: .7; margin-left: 6px; }

.home { overflow-x: clip; }
.sec { padding-block: clamp(64px, 8vw, 112px); }
.sec.pt0 { padding-top: 0; }
.label { font: 600 11px/1.2 var(--font-sans); letter-spacing: .16em; text-transform: uppercase; color: var(--tx-muted); margin: 0; }
.label.lt { color: var(--brand-sand); }
.sr { position: absolute; left: -9999px; }
h2 { margin: 12px 0 0; font: 300 clamp(2rem, 4vw, 3.4rem)/1.06 var(--font-sans); letter-spacing: -.04em; color: var(--tx); text-wrap: balance; max-width: 18ch; }
h3 { margin: 0; font: 400 clamp(1.5rem, 2.4vw, 2.1rem)/1.15 var(--font-sans); letter-spacing: -.03em; text-wrap: balance; }
h2 em, h3 em { font-style: normal; font-weight: 600; color: var(--blue-primary); }
.muted { color: var(--tx-muted); margin: 0; }
.ic { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; flex: none; }
.spark { width: 16px; height: 16px; fill: currentColor; flex: none; }
.head { display: flex; justify-content: space-between; align-items: end; gap: 20px; flex-wrap: wrap; margin-bottom: clamp(22px, 3vw, 40px); }
.head-acts { display: flex; gap: 8px; flex-wrap: wrap; }
@media (max-width: 640px) { .head-acts { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; max-width: 100%; margin-inline: -2px; padding-bottom: 2px; } .head-acts > * { flex: none; } .head > div:first-child { min-width: 0; } }
.btn-line, .btn-dark, .btn-light, .btn-ghost { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border-radius: 999px; padding: 12px 20px; font: 600 14px var(--font-sans); cursor: pointer; text-decoration: none; white-space: nowrap; transition: background .2s, border-color .2s; }
.btn-line { background: transparent; border: 1px solid var(--brand-sand); color: var(--tx); }
.btn-line:hover { border-color: var(--blue-primary); }
.btn-dark { background: var(--accent-black); color: var(--on-ink); border: 0; }
.btn-dark:hover { background: var(--blue-primary); }
.btn-light { background: #F5F1E9; color: #262521; border: 0; }
.btn-ghost { background: transparent; color: #F5F1E9; border: 1px solid rgba(245, 241, 233, .5); }

.chips { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px; scrollbar-width: none; margin-bottom: 14px; }
.chip { flex: none; border: 1px solid var(--brand-sand); background: transparent; border-radius: 999px; padding: 9px 16px; font: 700 13px var(--font-sans); cursor: pointer; color: var(--tx); }
.chip.sm { padding: 7px 13px; font-size: 12px; }
.chip[aria-pressed="true"] { background: var(--accent-black); color: var(--on-ink); border-color: var(--accent-black); }
.aud { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-bottom: 24px; }
.aud .label { margin-right: 4px; }
.sort { margin-left: auto; }
.sort select { appearance: none; border: 1px solid var(--brand-sand); background: var(--surface); border-radius: 999px; padding: 8px 16px; font: 600 13px var(--font-sans); color: var(--tx); cursor: pointer; }
.ai-banner { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; padding: 14px 18px; border-radius: 20px; background: var(--surface); margin-bottom: 24px; }
.orb { width: 30px; height: 30px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #FBF8F2, #D5C8B5 45%, #514437); flex: none; }
.toks { display: flex; flex-wrap: wrap; gap: 6px; flex: 1; min-width: 0; }
.tok { display: inline-flex; gap: 6px; align-items: center; padding: 6px 11px; border-radius: 999px; background: var(--surface-subtle); font: 700 12px var(--font-sans); }
.tok i { font-style: normal; color: var(--tx-muted); font-weight: 500; }
.tok.q { font-weight: 600; }
.link { background: none; border: 0; padding: 4px 0; font: 700 13px var(--font-sans); cursor: pointer; color: var(--blue-primary); }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 30px 20px; }
.skel { display: grid; gap: 10px; }
.sk-ph { aspect-ratio: 4 / 3; border-radius: 20px; }
.sk-l { height: 14px; border-radius: 8px; }
.sk-l.s { width: 60%; }
.sk-ph, .sk-l { background: linear-gradient(110deg, var(--surface-subtle) 30%, var(--bg) 50%, var(--surface-subtle) 70%) 0 0 / 300% 100%; animation: shim 1.6s linear infinite; }
@keyframes shim { to { background-position: -300% 0; } }
.empty { padding: 56px 20px; text-align: center; border: 1px dashed var(--brand-sand); border-radius: 28px; display: grid; gap: 12px; justify-items: center; }
.empty b { font: 600 22px var(--font-sans); }
.empty p { color: var(--tx-muted); max-width: 44ch; margin: 0; }
.more { display: flex; justify-content: center; margin-top: 36px; }

.tabs { display: flex; gap: 4px; background: var(--surface-subtle); padding: 4px; border-radius: 999px; }
.tabs button { border: 0; background: transparent; border-radius: 999px; padding: 9px 18px; font: 700 13px var(--font-sans); cursor: pointer; color: var(--tx-muted); }
.tabs button[aria-pressed="true"] { background: var(--surface); color: var(--tx); }
.ed { display: grid; grid-template-columns: repeat(12, 1fr); gap: 20px; }

.adv { background: var(--panel); color: #F5F1E9; border-radius: clamp(24px, 4vw, 44px); padding: clamp(24px, 5.5vw, 76px); display: grid; grid-template-columns: .9fr 1.1fr; gap: clamp(28px, 5vw, 72px); align-items: center; }
.adv h2 { color: #F5F1E9; margin-bottom: 16px; }
.adv h2 em { color: var(--brand-sand); }
.adv .sub { color: #CFC6B8; max-width: 42ch; margin: 0 0 26px; }
.adv-qs { display: grid; gap: 8px; }
.adv-qs .label { margin-bottom: 6px; }
.adv-qs button { text-align: left; border: 1px solid rgba(213, 200, 181, .25); background: rgba(255, 255, 255, .03); color: #F5F1E9; border-radius: 16px; padding: 14px 16px; cursor: pointer; font: 500 14px var(--font-sans); display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.adv-qs button:hover { border-color: var(--brand-sand); background: rgba(255, 255, 255, .06); }
@media (max-width: 900px) { .adv { grid-template-columns: 1fr; } }

.loc { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; }
.lc { position: relative; border-radius: 20px; overflow: hidden; text-align: left; border: 0; padding: 0; cursor: pointer; min-height: 230px; display: flex; color: #F5F1E9; background: linear-gradient(160deg, #6B5A48, #3B3229); }
.lc img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .8s; }
.lc:hover img { transform: scale(1.05); }
.lc::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(38, 37, 33, 0) 30%, rgba(38, 37, 33, .82)); }
.lc .t { position: relative; z-index: 1; margin-top: auto; padding: 18px; display: grid; gap: 4px; }
.lc .t b { font: 700 22px/1.1 var(--font-sans); letter-spacing: -.02em; }
.lc .t span { font-size: 13px; opacity: .92; }
.lc:nth-child(1), .lc:nth-child(2) { grid-column: span 3; min-height: 320px; }
.lc:nth-child(n+3) { grid-column: span 2; }
@media (max-width: 900px) { .loc { grid-template-columns: 1fr 1fr; } .lc:nth-child(n) { grid-column: span 1; min-height: 190px; } .lc:nth-child(1) { grid-column: span 2; } }

.rail { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(250px, 290px); gap: 18px; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 12px; scrollbar-width: thin; scrollbar-color: var(--brand-sand) transparent; }
.rail > * { scroll-snap-align: start; }
.rail-ctrl { display: flex; gap: 8px; }
.rail-ctrl button { width: 46px; height: 46px; border-radius: 50%; border: 1px solid var(--brand-sand); background: transparent; cursor: pointer; display: grid; place-items: center; color: var(--tx); }
.rail-ctrl button:hover { background: var(--surface); }

.duo { display: grid; grid-template-columns: 1.3fr .7fr; gap: 20px; }
@media (max-width: 900px) { .duo { grid-template-columns: 1fr; } }
.tile { border-radius: 28px; background: var(--surface); padding: clamp(22px, 3vw, 36px); display: grid; gap: 14px; align-content: end; }
.map-tile { position: relative; overflow: hidden; min-height: 380px; background: var(--surface-subtle); }
.map-art { position: absolute; inset: 0; }
.map-art svg { width: 100%; height: 100%; }
.pin { position: absolute; transform: translate(-50%, -100%); background: var(--surface); color: var(--tx); border-radius: 999px; padding: 6px 11px; font: 700 12px var(--font-sans); box-shadow: 0 10px 24px -12px rgba(0, 0, 0, .45); white-space: nowrap; }
.pin small { font-weight: 500; opacity: .7; margin-left: 4px; }
.tile-body { position: relative; display: grid; gap: 14px; justify-items: start; background: var(--glass-strong); backdrop-filter: blur(12px); border-radius: 20px; padding: 18px; max-width: 420px; }
.rm-tile { justify-items: start; }

.stats { position: relative; border-radius: 28px; overflow: hidden; isolation: isolate; padding: clamp(18px, 4vw, 56px); min-height: 360px; display: flex; align-items: flex-end; }
.stats :deep(.hero-scene) { z-index: -1; }
.stat-panel { border-radius: 28px; padding: clamp(18px, 3vw, 32px); display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; width: 100%; background: var(--glass); backdrop-filter: blur(28px) saturate(1.35); -webkit-backdrop-filter: blur(28px) saturate(1.35); border: 1px solid var(--glass-line); }
.stat-panel div { display: grid; gap: 6px; }
.stat-panel b { font: 300 clamp(2rem, 4vw, 3.2rem)/1 var(--font-sans); letter-spacing: -.05em; color: var(--tx); }
.stat-panel span { font-size: 13px; color: var(--blue-primary); font-weight: 600; }
@media (max-width: 900px) { .stat-panel { grid-template-columns: 1fr 1fr; } }
.why { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }
@media (max-width: 900px) { .why { grid-template-columns: 1fr; } }
.why div { padding: 26px; border-radius: 28px; background: var(--surface); display: grid; gap: 10px; align-content: start; }
.why b { font: 300 44px/1 var(--font-sans); letter-spacing: -.05em; color: var(--blue-primary); }
.why h3 { font: 700 17px/1.3 var(--font-sans); letter-spacing: 0; }
.why p { color: var(--tx-muted); font-size: 14px; margin: 0; }

.owners { display: grid; grid-template-columns: 1.1fr .9fr; gap: 24px; }
@media (max-width: 960px) { .owners { grid-template-columns: 1fr; } }
.cta-box { position: relative; border-radius: clamp(24px, 4vw, 44px); overflow: hidden; isolation: isolate; min-height: 440px; display: flex; align-items: center; }
.cta-box :deep(.hero-scene) { z-index: -2; }
.cta-box::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(90deg, rgba(28, 26, 23, .78), rgba(28, 26, 23, .2) 75%); }
.cta-in { padding: clamp(24px, 5vw, 72px); color: #F5F1E9; display: grid; gap: 24px; max-width: 640px; }
.cta-in h2 { color: #F5F1E9; margin: 0; font-size: clamp(2.1rem, 4.4vw, 3.8rem); }
.cta-in h2 em { color: var(--brand-sand); }
.cta-in .row { display: flex; gap: 12px; flex-wrap: wrap; }
.own { background: var(--surface); border-radius: clamp(24px, 4vw, 44px); padding: clamp(24px, 4vw, 48px); display: grid; gap: 16px; align-content: center; justify-items: start; }
.own ol { margin: 0; padding: 0; list-style: none; display: grid; gap: 10px; counter-reset: s; }
.own li { display: grid; grid-template-columns: 32px 1fr; gap: 12px; align-items: center; font-size: 14px; counter-increment: s; }
.own li::before { content: counter(s); width: 32px; height: 32px; border-radius: 50%; display: grid; place-items: center; background: var(--surface-subtle); font-weight: 700; }
@media (prefers-reduced-motion: reduce) { .sk-ph, .sk-l { animation: none; } .lc img { transition: none; } }
</style>
