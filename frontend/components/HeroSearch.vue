<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'
import HeroScene from '~/components/HeroScene.vue'

const emit = defineEmits(['openFilters'])
const { t, tDistrict, currentLang } = useI18n()
const {
  listings,
  filteredListings,
  filterDistrict,
  filterRooms,
  filterMaxPrice,
  filterAudience,
  filterDealType,
  filterPropertyType,
  availableDistricts,
  isAiSearching,
  aiSearchActive,
  runAiMatch,
  resetAiMatch,
} = useListings()

const searchMode = ref<'ai' | 'rent' | 'buy'>('ai')
const aiInput = ref('')

const scrollToCatalog = () => {
  const el = document.getElementById('katalog')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const setMode = async (mode: 'ai' | 'rent' | 'buy') => {
  searchMode.value = mode
  if (mode === 'ai') return
  if (aiSearchActive.value) await resetAiMatch()
  filterMaxPrice.value = ''
  if (mode === 'rent') {
    filterDealType.value = 'rent'
    filterPropertyType.value = ''
  } else {
    filterDealType.value = 'sale'
    filterAudience.value = 'all'
  }
}

const handleAiSearch = async () => {
  const q = aiInput.value.trim()
  if (!q) return
  scrollToCatalog()
  await runAiMatch(q)
}

const applyAiPrompt = async (prompt: string) => {
  aiInput.value = prompt
  searchMode.value = 'ai'
  scrollToCatalog()
  await runAiMatch(prompt)
}

const examples = computed(() => [
  { label: t('ex_chilonzor'), prompt: t('prompt_chilonzor') },
  { label: t('ex_yunusobod'), prompt: t('prompt_yunusobod') },
  { label: t('ex_mirobod'), prompt: t('prompt_mirobod') },
])

const budgetOptions = computed(() =>
  filterDealType.value === 'sale'
    ? [300_000_000, 500_000_000, 800_000_000, 1_200_000_000, 2_000_000_000]
    : [3_000_000, 4_000_000, 6_000_000, 8_000_000, 12_000_000],
)

const money = (v: number) => {
  if (v >= 1e9) return `${(v / 1e9).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mlrd`
  return `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln`
}

/* ---------- Hero AI demo: types a query, shows what AI extracts, counts real listings ---------- */
const DEMOS = computed(() =>
  currentLang.value === 'ru'
    ? ['В Чиланзаре возле метро до 4 млн 2-комнатная', 'Юнусабад без маклера для семьи', 'Мирабад 3-комнатная с мебелью']
    : ['Chilonzorda metro yaqinida 4 mln gacha 2 xonali', 'Yunusobodda maklersiz oila uchun 3 xonali', 'Mirobodda 3 xonali jihozlangan'],
)
const DISTRICT_ALIASES: Record<string, string[]> = {
  Chilonzor: ['chilonzor', 'чиланзар'],
  Yunusobod: ['yunusobod', 'юнусабад'],
  'Mirzo Ulug‘bek': ['mirzo', 'улугбек'],
  Yakkasaroy: ['yakkasaroy', 'яккасарай'],
  Mirobod: ['mirobod', 'мирабад'],
  Shayxontohur: ['shayxontohur', 'шайхантахур'],
  Sergeli: ['sergeli', 'сергели'],
  Olmazor: ['olmazor', 'алмазар'],
  Yashnobod: ['yashnobod', 'яшнабад'],
  Uchtepa: ['uchtepa', 'учтепа'],
}
const parseDemo = (q: string) => {
  const s = q.toLowerCase()
  const tok: [string, string][] = []
  const f: any = {}
  for (const [n, al] of Object.entries(DISTRICT_ALIASES)) if (al.some((a) => s.includes(a))) { f.district = n; tok.push(['Hudud', tDistrict(n)]); break }
  const rm = /(\d)\s*-?\s*(xona|комн)/.exec(s)
  if (rm) { f.rooms = +rm[1]; tok.push(['Xonalar', rm[1]]) }
  const pm = /(\d+(?:[.,]\d+)?)\s*(mln|млн)/.exec(s)
  if (pm) { f.max = parseFloat(pm[1].replace(',', '.')) * 1e6; tok.push(['Byudjet', `${pm[1]} mln gacha`]) }
  if (/metro|метро/.test(s)) tok.push(['Joylashuv', 'Metro yaqin'])
  if (/maklersiz|без маклера/.test(s)) { f.owner = true; tok.push(['Manba', 'Maklersiz']) }
  if (/oila|семь/.test(s)) tok.push(['Kim uchun', 'Oila'])
  if (/jihoz|мебел/.test(s)) tok.push(['Qulaylik', 'Jihozlangan'])
  const count = listings.value.filter((l) =>
    (l.deal_type || 'rent') === 'rent' &&
    (!f.district || l.district === f.district) &&
    (!f.rooms || l.rooms === f.rooms) &&
    (!f.max || l.price_uzs <= f.max) &&
    (!f.owner || l.is_owner),
  ).length
  return { tok, count }
}
const typed = ref('')
const demoTokens = ref<[string, string][]>([])
const demoCount = ref<number | null>(null)
const demoQuery = ref('')
let timer: any = null
let idx = 0
const runDemo = () => {
  const q = DEMOS.value[idx % DEMOS.value.length]
  idx++
  demoQuery.value = q
  demoTokens.value = []
  demoCount.value = null
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const done = () => {
    const r = parseDemo(q)
    demoTokens.value = r.tok
    demoCount.value = r.count
    timer = setTimeout(runDemo, 4200)
  }
  if (reduce) { typed.value = q; return done() }
  let i = 0
  const type = () => {
    typed.value = q.slice(0, i++)
    if (i <= q.length) timer = setTimeout(type, 28)
    else timer = setTimeout(done, 250)
  }
  type()
}
onMounted(runDemo)
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <section id="top" class="p-hero">
    <ClientOnly><HeroScene variant="hero" /></ClientOnly>
    <div class="p-hero-fade" aria-hidden="true"></div>

    <div class="wrap p-hero-in">
      <div class="p-hero-copy">
        <p class="p-label">Toshkent · ijara va sotuv</p>
        <h1 class="p-h1">
          <span>Uyingizni toping.</span>
          <span class="l2">Yangi <em>hayotingizni</em> boshlang.</span>
        </h1>
        <p class="p-lede">Orzuyingizdagi uy, ishonchli e’lonlar va qulay qidiruv — barchasi bir joyda.</p>
        <div class="p-trust">
          <span class="p-glass"><svg viewBox="0 0 24 24"><path d="M4 12l5 5L20 6" /></svg>0% vositachilik</span>
          <span class="p-glass"><svg viewBox="0 0 24 24"><path d="M4 12l5 5L20 6" /></svg>AI narx tahlili</span>
          <span class="p-glass"><svg viewBox="0 0 24 24"><path d="M4 12l5 5L20 6" /></svg>Firibgarlik tekshiruvi</span>
        </div>
      </div>

      <button type="button" class="p-aidemo p-glass" aria-label="AI qidiruv misolini ishga tushirish" @click="applyAiPrompt(demoQuery)">
        <span class="p-aidemo-h">
          <span class="p-orb" aria-hidden="true"></span>
          <span><b>Joyliy AI qidiruv</b><small>Oddiy so‘z bilan yozing — AI tushunadi</small></span>
        </span>
        <span class="p-typed">{{ typed }}</span>
        <span class="p-toks">
          <span v-for="(tk, i) in demoTokens" :key="tk[0] + i" class="p-tok" :style="{ animationDelay: i * 80 + 'ms' }"><i>{{ tk[0] }}</i>{{ tk[1] }}</span>
        </span>
        <span class="p-aidemo-f">
          <span><b>{{ demoCount ?? '—' }}</b> ta mos uy</span>
          <span class="p-link">Sinab ko‘rish →</span>
        </span>
      </button>
    </div>

    <div class="wrap">
      <div class="p-search">
        <div class="p-modes" role="group" aria-label="Qidiruv rejimi">
          <button type="button" class="ai-tab" :aria-pressed="searchMode === 'ai'" @click="setMode('ai')">
            <svg viewBox="0 0 24 24" class="spark"><path d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7z" /></svg>
            {{ t('mode_ai') }}
          </button>
          <button type="button" :aria-pressed="searchMode === 'rent'" @click="setMode('rent')">{{ t('mode_rent') }}</button>
          <button type="button" :aria-pressed="searchMode === 'buy'" @click="setMode('buy')">{{ t('mode_buy') }}</button>
        </div>

        <form v-if="searchMode === 'ai'" role="search" aria-label="AI qidiruv" @submit.prevent="handleAiSearch">
          <div class="p-ai-row">
            <label class="p-ai-input" for="p-ai-in">
              <svg viewBox="0 0 24 24" class="spark"><path d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7z" /></svg>
              <input id="p-ai-in" v-model="aiInput" autocomplete="off" :placeholder="t('ai_search_placeholder')" />
            </label>
            <button class="p-btn-dark p-ai-go" type="submit" :disabled="isAiSearching">
              <svg viewBox="0 0 24 24" class="spark"><path d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7z" /></svg>
              {{ isAiSearching ? t('ai_analyzing') : t('ai_search_btn') }}
            </button>
          </div>
          <div class="p-ex">
            <span class="p-label">{{ t('examples') }}</span>
            <button v-for="ex in examples" :key="ex.label" type="button" class="p-chipbtn" @click="applyAiPrompt(ex.prompt)">{{ ex.label }}</button>
          </div>
        </form>

        <form v-else class="p-row" role="search" aria-label="Filtrlar bo‘yicha qidirish" @submit.prevent="scrollToCatalog">
          <div class="p-f">
            <label for="p-dist">{{ t('district') }}</label>
            <select id="p-dist" v-model="filterDistrict">
              <option value="">{{ t('all_districts') }}</option>
              <option v-for="d in availableDistricts" :key="d" :value="d">{{ tDistrict(d) }}</option>
            </select>
          </div>
          <div class="p-f">
            <label for="p-type">{{ t('property_type') }}</label>
            <select id="p-type" v-model="filterPropertyType">
              <option value="">{{ t('all') }}</option>
              <option value="new_building">{{ t('type_new_building') }}</option>
              <option value="secondary">{{ t('type_secondary') }}</option>
              <option value="house">{{ t('type_house') }}</option>
            </select>
          </div>
          <div class="p-f">
            <label for="p-budget">{{ t('max_budget') }}</label>
            <select id="p-budget" v-model="filterMaxPrice">
              <option value="">{{ t('any') }}</option>
              <option v-for="b in budgetOptions" :key="b" :value="String(b)">{{ money(b) }} so‘mgacha</option>
            </select>
          </div>
          <div class="p-f">
            <label for="p-rooms">{{ t('rooms_count') }}</label>
            <select id="p-rooms" v-model="filterRooms">
              <option value="">{{ t('any') }}</option>
              <option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4+</option>
            </select>
          </div>
          <div v-if="searchMode === 'rent'" class="p-f">
            <label for="p-aud">{{ t('for_whom') }}</label>
            <select id="p-aud" v-model="filterAudience">
              <option value="all">{{ t('aud_all') }}</option>
              <option value="family">{{ t('aud_family') }}</option>
              <option value="female">{{ t('aud_female') }}</option>
              <option value="male">{{ t('aud_male') }}</option>
            </select>
          </div>
          <button class="p-btn-dark p-go" type="submit">
            <svg viewBox="0 0 24 24" class="ic"><circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" /></svg>
            {{ t('search') }}
          </button>
        </form>

        <div class="p-foot">
          <button type="button" class="p-link" @click="emit('openFilters')">
            <svg viewBox="0 0 24 24" class="ic"><path d="M4 7h10M18 7h2M4 17h4M12 17h8" /><circle cx="16" cy="7" r="2" /><circle cx="10" cy="17" r="2" /></svg>
            {{ t('more_filters') }}
          </button>
          <span class="p-label">{{ filteredListings.length }} ta mos e’lon</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.p-hero { position: relative; z-index: 0; top: auto; min-height: min(940px, 100svh); display: flex; flex-direction: column; overflow: hidden; isolation: isolate; }
.p-hero > .wrap { width: 100%; }
.p-hero :deep(.hero-scene) { z-index: -2; }
.p-hero-fade { position: absolute; inset: 0; z-index: -1; background: linear-gradient(100deg, color-mix(in srgb, var(--bg) 94%, transparent) 0%, color-mix(in srgb, var(--bg) 60%, transparent) 36%, transparent 62%); }
.p-hero-in { flex: 1; display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 40px; align-items: center; padding-top: calc(130px + env(safe-area-inset-top, 0px)); padding-bottom: 28px; }
.p-label { font: 600 11px/1.2 var(--font-sans); letter-spacing: .16em; text-transform: uppercase; color: var(--tx-muted); margin: 0; }
.p-h1 { margin: 20px 0 0; font-family: var(--font-sans); font-size: clamp(2.1rem, 4.2vw, 4rem); font-weight: 300; line-height: 1.02; letter-spacing: -.05em; color: var(--tx); text-wrap: balance; }
.p-h1 span { display: block; }
.p-h1 em { font-style: normal; font-weight: 600; color: var(--blue-primary); }
.p-lede { margin: 22px 0 0; max-width: 46ch; font-size: clamp(15px, 1.3vw, 17px); color: var(--blue-primary); }
.p-trust { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 26px; }
.p-trust span { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; color: var(--tx); }
.p-trust svg { width: 15px; height: 15px; stroke: var(--ok); fill: none; stroke-width: 2; }

.p-aidemo { border-radius: 28px; padding: 22px; display: grid; gap: 16px; cursor: pointer; text-align: left; width: 100%; color: var(--tx); font: inherit; animation: p-rise .8s .2s both; }
.p-aidemo-h { display: flex; align-items: center; gap: 12px; }
.p-aidemo-h b { display: block; font-weight: 700; font-size: 15px; }
.p-aidemo-h small { font-size: 12px; color: var(--tx-muted); }
.p-orb { width: 40px; height: 40px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #FBF8F2, #D5C8B5 45%, #514437); flex: none; position: relative; animation: p-breathe 4s ease-in-out infinite; }
.p-orb::after { content: ""; position: absolute; inset: -6px; border-radius: 50%; border: 1px solid rgba(213, 200, 181, .7); animation: p-ring 2.6s ease-out infinite; }
.p-typed { font-size: 17px; font-weight: 500; line-height: 1.45; min-height: 3em; }
.p-typed::after { content: ""; display: inline-block; width: 2px; height: 1.1em; background: var(--blue-primary); margin-left: 2px; vertical-align: -.15em; animation: p-blink 1s steps(1) infinite; }
.p-toks { display: flex; flex-wrap: wrap; gap: 6px; min-height: 30px; }
.p-tok { display: inline-flex; gap: 6px; align-items: center; padding: 6px 11px; border-radius: 999px; background: var(--surface); font-size: 12px; font-weight: 700; animation: p-tokin .3s both; }
.p-tok i { font-style: normal; color: var(--tx-muted); font-weight: 500; }
.p-aidemo-f { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding-top: 12px; border-top: 1px solid var(--bd); font-size: 13px; }
.p-aidemo-f b { font-size: 20px; font-weight: 700; letter-spacing: -.02em; }

.p-search { border-radius: 28px; padding: 10px; margin-bottom: 28px; background: var(--glass-strong); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border: 1px solid var(--glass-line); box-shadow: var(--sh-floating); }
.p-modes { display: flex; gap: 4px; padding: 2px 2px 10px; flex-wrap: wrap; }
.p-modes button { border: 0; background: transparent; border-radius: 999px; padding: 9px 16px; font: 700 13px var(--font-sans); cursor: pointer; color: var(--tx-muted); display: inline-flex; gap: 8px; align-items: center; }
.p-modes button[aria-pressed="true"] { background: var(--accent-black); color: var(--on-ink); }
.p-modes .ai-tab[aria-pressed="false"] { color: var(--blue-primary); }
.spark { width: 16px; height: 16px; fill: currentColor; flex: none; }
.ic { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; flex: none; }
.p-ai-row { display: flex; gap: 8px; }
.p-ai-input { flex: 1; min-width: 0; display: flex; align-items: center; gap: 12px; background: var(--surface); border-radius: 20px; padding: 6px 8px 6px 18px; color: var(--blue-primary); }
.p-ai-input:focus-within { box-shadow: 0 0 0 2px var(--blue-primary); }
.p-ai-input .spark { width: 20px; height: 20px; }
.p-ai-input input { flex: 1; min-width: 0; border: 0; background: transparent; font: 500 16px var(--font-sans); padding: 14px 0; color: var(--tx); }
.p-ai-input input:focus { outline: none; }
.p-btn-dark { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border: 0; background: var(--accent-black); color: var(--on-ink); font: 600 14px var(--font-sans); cursor: pointer; white-space: nowrap; transition: background .2s; }
.p-btn-dark:hover { background: var(--blue-primary); }
.p-btn-dark:disabled { opacity: .6; cursor: progress; }
.p-ai-go { border-radius: 16px; padding: 0 24px; min-height: 56px; }
.p-ex { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; padding: 10px 6px 2px; }
.p-ex .p-label { margin-right: 4px; }
.p-chipbtn { border: 1px solid var(--brand-sand); background: transparent; border-radius: 999px; padding: 7px 13px; font: 600 13px var(--font-sans); cursor: pointer; color: var(--tx); }
.p-chipbtn:hover { background: var(--surface); }
.p-row { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)) auto; gap: 6px; }
.p-f { background: var(--surface); border-radius: 18px; padding: 10px 16px; display: grid; gap: 2px; min-width: 0; }
.p-f label { font: 600 10px var(--font-sans); letter-spacing: .14em; text-transform: uppercase; color: var(--tx-muted); }
.p-f select { appearance: none; border: 0; background: transparent; font: 600 14px var(--font-sans); color: var(--tx); padding: 0; cursor: pointer; width: 100%; min-width: 0; }
.p-f select:focus-visible { outline: none; }
.p-f:focus-within { box-shadow: 0 0 0 2px var(--blue-primary); }
.p-go { border-radius: 18px; padding: 0 26px; min-height: 58px; }
.p-foot { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 8px 2px; flex-wrap: wrap; }
.p-link { background: none; border: 0; padding: 4px 0; font: 700 13px var(--font-sans); cursor: pointer; display: inline-flex; gap: 6px; align-items: center; color: var(--blue-primary); }

@keyframes p-rise { from { transform: translateY(16px); } to { transform: none; } }
@keyframes p-breathe { 50% { transform: scale(.93); } }
@keyframes p-ring { from { transform: scale(.85); opacity: 1; } to { transform: scale(1.35); opacity: 0; } }
@keyframes p-blink { 50% { opacity: 0; } }
@keyframes p-tokin { from { transform: scale(.9); } to { transform: none; } }

@media (max-width: 1100px) { .p-row { grid-template-columns: repeat(2, minmax(0, 1fr)); } .p-go { grid-column: 1 / -1; } }
@media (max-width: 1023px) { .p-hero-in { grid-template-columns: minmax(0, 1fr); } .p-aidemo { display: none; } }
@media (max-width: 1023px) { .p-hero { min-height: auto; } .p-hero-in { flex: none; } .p-search { margin-bottom: calc(var(--mobile-nav-height) + var(--mobile-nav-bottom) + 32px); } }
@media (max-width: 767px) {
  .p-hero-fade { background: linear-gradient(180deg, color-mix(in srgb, var(--bg) 95%, transparent) 0%, color-mix(in srgb, var(--bg) 75%, transparent) 50%, color-mix(in srgb, var(--bg) 20%, transparent) 80%); }
  .p-hero-in { padding-top: calc(100px + env(safe-area-inset-top, 0px)); }
}
@media (max-width: 600px) { .p-ai-row { flex-direction: column; } .p-ai-go { min-height: 50px; } }
@media (prefers-reduced-motion: reduce) { .p-aidemo, .p-orb, .p-orb::after, .p-typed::after, .p-tok { animation: none !important; } }
</style>
