<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useModals } from '~/composables/useModals'
import HeroSearch from '~/components/HeroSearch.vue'
import ListingCard from '~/components/ListingCard.vue'
import HeroScene from '~/components/HeroScene.vue'

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
} = useListings()

const { showFilters, showMap, showPostAd, showRoommates, showNeighborhoods, showAssistant } = useModals()
const assistantPrefill = useState<string>('assistant_prefill', () => '')

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
  { key: '1', title: t('cat_1room') },
  { key: '2', title: t('cat_2room') },
  { key: '3', title: t('cat_3room') },
  { key: 'room', title: t('cat_roommates') },
])
const saleCategories = computed(() => [
  { key: '', title: t('cat_all') },
  { key: 'mk', title: t('cat_from_owner') },
  { key: 'fair_cheap', title: t('cat_cheap_price') },
  { key: '3days', title: t('cat_new_listings') },
  { key: '1', title: t('cat_1room') },
  { key: '2', title: t('cat_2room') },
  { key: '3', title: t('cat_3room') },
])
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
const advisorQuestions = computed(() => [t('q_tax'), t('q_deposit'), t('q_utilities'), t('q_fraud')])
const askAdvisor = (q?: string) => {
  assistantPrefill.value = q || ''
  showAssistant.value = true
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
            <button type="button" class="btn-line" @click="showMap = true">
              <svg viewBox="0 0 24 24" class="ic"><path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4z" /><path d="M8 2v16M16 6v16" /></svg>{{ t('map') }}
            </button>
            <button type="button" class="btn-line" @click="showFilters = true">
              <svg viewBox="0 0 24 24" class="ic"><path d="M4 7h10M18 7h2M4 17h4M12 17h8" /><circle cx="16" cy="7" r="2" /><circle cx="10" cy="17" r="2" /></svg>{{ t('more_filters') }}
            </button>
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
            <button v-for="cat in activeCategories" :key="cat.key" type="button" class="chip" :aria-pressed="filterCategory === cat.key" @click="filterCategory = cat.key">{{ cat.title }}</button>
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
            <p class="sub">Shartnoma, zalog, kommunal to‘lovlar va firibgarlikdan himoya — Toshkent ijara amaliyoti bo‘yicha maslahat, qonuniy asos va amaliy tavsiyalar bilan.</p>
            <button type="button" class="btn-light" @click="askAdvisor()">
              <svg viewBox="0 0 24 24" class="spark"><path d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7z" /></svg>
              Maslahatchini ochish
            </button>
          </div>
          <div class="adv-qs">
            <p class="label lt">Ko‘p beriladigan savollar</p>
            <button v-for="q in advisorQuestions" :key="q" type="button" @click="askAdvisor(q)">
              <span>{{ q }}</span>
              <svg viewBox="0 0 24 24" class="ic"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- DISTRICTS -->
    <section id="tumanlar" class="sec pt0">
      <div class="wrap">
        <div class="head">
          <div><p class="label">Hududlar</p><h2>Qayerdan uy <em>qidiryapsiz?</em></h2></div>
          <button type="button" class="btn-line" @click="showNeighborhoods = true">Tumanlar qo‘llanmasi →</button>
        </div>
        <div class="loc">
          <button v-for="d in districtCards" :key="d.name" type="button" class="lc" @click="pickDistrict(d.name)">
            <img v-if="d.img" :src="d.img" alt="" loading="lazy" referrerpolicy="no-referrer" />
            <span class="t"><b>{{ tDistrict(d.name) }}</b><span>{{ t('district_apts_count', { count: d.count }) }}<template v-if="d.avg"> · ijara o‘rtacha {{ money(d.avg) }}</template></span></span>
          </button>
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

    <!-- MAP + ROOMMATES -->
    <section class="sec pt0">
      <div class="wrap duo">
        <div class="tile map-tile">
          <div class="map-art" aria-hidden="true">
            <svg viewBox="0 0 100 60" preserveAspectRatio="none">
              <polyline points="14,62 22,52 30,44 40,36 48,30 58,26 70,22 84,18" fill="none" stroke="#B5483A" stroke-width=".8" opacity=".6" />
              <polyline points="20,10 32,18 44,24 52,30 62,36 74,40 88,44" fill="none" stroke="#3D5F8C" stroke-width=".8" opacity=".6" />
              <polyline points="56,2 56,14 55,26 54,34 53,42" fill="none" stroke="#4F7A4A" stroke-width=".8" opacity=".6" />
            </svg>
            <span v-for="(d, i) in districtCards.slice(0, 6)" :key="d.name" class="pin" :style="{ left: [30, 58, 72, 46, 22, 64][i] + '%', top: [44, 26, 40, 60, 66, 72][i] + '%' }">{{ tDistrict(d.name) }} <small>{{ d.count }}</small></span>
          </div>
          <div class="tile-body">
            <p class="label">Xarita</p>
            <h3>Xaritadan o‘zingizga mos <em>uy toping.</em></h3>
            <button type="button" class="btn-dark" @click="showMap = true">Xaritani ochish</button>
          </div>
        </div>
        <div class="tile rm-tile">
          <p class="label">{{ t('roommates_tab') }}</p>
          <h3>Birga yashash uchun <em>sherik toping.</em></h3>
          <p class="muted">Talabalar va yosh mutaxassislar uchun anketa to‘ldiring, mos hamxonalar bilan bog‘laning.</p>
          <button type="button" class="btn-dark" @click="showRoommates = true">Hamxona qidirish</button>
        </div>
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

.adv { background: var(--panel); color: #F5F1E9; border-radius: clamp(24px, 4vw, 44px); padding: clamp(24px, 5.5vw, 76px); display: grid; grid-template-columns: 1fr 1fr; gap: clamp(28px, 5vw, 72px); align-items: center; }
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
.stat-panel { border-radius: 28px; padding: clamp(18px, 3vw, 32px); display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; width: 100%; background: var(--glass); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border: 1px solid var(--glass-line); }
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
