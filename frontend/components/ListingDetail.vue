<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useModals } from '~/composables/useModals'
import { useNeighborhoods } from '~/composables/useNeighborhoods'
import { useAssistant } from '~/composables/useAssistant'
import ListingCard from '~/components/ListingCard.vue'

const props = withDefaults(defineProps<{ listing: ListingItem; page?: boolean }>(), { page: false })
const emit = defineEmits(['close', 'select', 'toast'])

const { t, tDistrict } = useI18n()
const { isFavorite, toggleFavorite } = useFavorites()
const { isInCompare, toggleCompare, listings } = useListings()
const { openReportModal, showAssistant, showNeighborhoods } = useModals()
const { load, byName } = useNeighborhoods()
const { send } = useAssistant()
onMounted(load)

const l = computed(() => props.listing)
const isSale = computed(() => l.value.deal_type === 'sale')
const photos = computed(() => l.value.image_urls || [])
const nb = computed(() => byName(l.value.district))

const money = (v: number) => (v >= 1e9 ? `${(v / 1e9).toLocaleString('ru-RU', { maximumFractionDigits: 2 })} mlrd` : v >= 1e6 ? `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: v < 1e8 ? 1 : 0 })} mln` : v.toLocaleString('ru-RU'))
const MON = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr']
const dateTxt = computed(() => {
  const s = l.value.published_at
  if (!s) return '—'
  const d = new Date(s)
  return isNaN(d.getTime()) ? '—' : `${d.getDate()}-${MON[d.getMonth()]}, ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
})

const TYPE: Record<string, string> = { apartment: 'Kvartira', house: t('type_house'), new_building: t('type_new_building'), secondary: t('type_secondary') }
const typeLabel = computed(() => TYPE[l.value.property_type || ''] || 'Kvartira')
const floorParts = computed(() => (l.value.floor || '').split('/'))

/* market + safety */
const market = computed(() => {
  let d = l.value.price_diff_percent as number | null | undefined
  let bench = l.value.estimated_market_price || 0
  if (!bench && !isSale.value && nb.value) {
    const k = Math.max(1, Math.min(l.value.rooms || 2, 3))
    bench = (nb.value as any)[`avg_rent_${k}room_uzs`] || 0
  }
  if ((d == null || d === 0) && bench) d = Math.round(((l.value.price_uzs - bench) / bench) * 100)
  if (d == null) return null
  const cls = d <= -10 ? 'good' : d >= 10 ? 'high' : ''
  const label = d <= -10 ? `Bozordan ${Math.abs(d)}% arzon` : d >= 10 ? `Bozordan ${d}% qimmat` : t('at_market_label')
  return { d, cls, label, bench, pos: Math.max(4, Math.min(96, 50 + d * 1.5)) }
})
const reasons = computed<string[]>(() => {
  const r: any = l.value.scam_risk_reasons
  if (Array.isArray(r)) return r
  try { return JSON.parse(r || '[]') } catch { return [] }
})
const risk = computed(() => {
  const lvl = (l.value.scam_risk_level || 'low').toLowerCase()
  const sc = l.value.scam_risk_score ?? 10
  if (lvl === 'high') return { lvl, label: 'Yuqori xavf', pct: sc }
  if (lvl === 'medium') return { lvl, label: 'Ehtiyot bo‘ling', pct: sc }
  return { lvl: 'low', label: 'Xavfsiz e’lon', pct: 100 - sc }
})

const amenities = computed(() => {
  const out: string[] = [typeLabel.value]
  if (l.value.near_metro && l.value.metro_station) out.push(`Metro: ${l.value.metro_station}`)
  const A: Record<string, string> = { mebel: t('amenity_furniture_title'), kond: t('amenity_ac_title'), kir: t('amenity_wm_title'), net: t('amenity_wifi_title') }
  for (const a of l.value.amenities || []) if (A[a]) out.push(A[a])
  return out
})

const audLabel = computed(() => ({ family: t('aud_only_family'), female: t('aud_only_female'), male: t('aud_only_male') } as Record<string, string>)[l.value.target_audience || ''])

/* similar + recently viewed */
const similar = computed(() => listings.value.filter((x) => x.id !== l.value.id && x.district === l.value.district && (x.deal_type || 'rent') === (l.value.deal_type || 'rent') && !x.is_shared_room).sort((a, b) => Math.abs(a.price_uzs - l.value.price_uzs) - Math.abs(b.price_uzs - l.value.price_uzs)).slice(0, 4))
const recent = ref<ListingItem[]>([])
const recordView = () => {
  if (!import.meta.client) return
  try {
    const ids: number[] = JSON.parse(localStorage.getItem('joyliy_rv') || '[]').filter((x: number) => x !== l.value.id)
    recent.value = ids.map((id) => listings.value.find((x) => x.id === id)).filter(Boolean).slice(0, 4) as ListingItem[]
    localStorage.setItem('joyliy_rv', JSON.stringify([l.value.id, ...ids].slice(0, 8)))
  } catch {}
}
onMounted(recordView)
watch(() => l.value.id, () => { lb.value = false; recordView() })

/* actions */
const fav = computed(() => isFavorite(l.value.id))
const cmp = computed(() => isInCompare(l.value.id))
const onFav = () => { const add = toggleFavorite(l.value.id); emit('toast', add ? 'Saqlanganlarga qo‘shildi' : 'Saqlanganlardan olindi') }
const onCmp = () => { toggleCompare(l.value); emit('toast', isInCompare(l.value.id) ? t('toast_added_compare') : t('toast_removed_compare')) }
const askAi = () => { showAssistant.value = true; send(`E’lon #${l.value.id} haqida baho bering`, l.value.id) }
const tel = computed(() => (l.value.contact_phone ? 'tel:' + l.value.contact_phone.replace(/[^\d+]/g, '') : ''))
const tg = computed(() => (l.value.contact_telegram ? `https://t.me/${l.value.contact_telegram.replace('@', '')}` : 'https://t.me/joyliy_bot'))

/* lightbox */
const lb = ref(false)
const idx = ref(0)
const openLb = (i: number) => { idx.value = i; lb.value = true }
const move = (d: number) => { idx.value = (idx.value + d + photos.value.length) % photos.value.length }
let x0: number | null = null
const onKey = (e: KeyboardEvent) => {
  if (lb.value) { if (e.key === 'Escape') lb.value = false; if (e.key === 'ArrowRight') move(1); if (e.key === 'ArrowLeft') move(-1); return }
  if (e.key === 'Escape' && !props.page) emit('close')
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
const failed = ref<Record<number, boolean>>({})
</script>

<template>
  <div class="dt" :class="{ overlay: !page }" role="dialog" :aria-modal="!page" :aria-label="l.title">
    <div class="top">
      <div class="wrap row">
        <button v-if="!page" type="button" class="ib" aria-label="Orqaga" @click="emit('close')"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6" /></svg></button>
        <NuxtLink v-else to="/" class="ib" aria-label="Orqaga"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6" /></svg></NuxtLink>
        <span class="crumb">Bosh sahifa / {{ isSale ? 'Sotuv' : 'Ijara' }} / {{ tDistrict(l.district) }}</span>
        <span class="sp">
          <button type="button" class="ib" :class="{ on: cmp }" :aria-pressed="cmp" aria-label="Taqqoslash" @click="onCmp"><svg viewBox="0 0 24 24"><path d="M7 4v16M17 4v16M3 8h8M13 16h8" /></svg></button>
          <button type="button" class="ib" :class="{ favon: fav }" :aria-pressed="fav" aria-label="Saqlash" @click="onFav"><svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" /></svg></button>
          <button type="button" class="ib" aria-label="Shikoyat qilish" @click="openReportModal(l.id)"><svg viewBox="0 0 24 24"><path d="M5 21V4h11l-2 4 2 4H5" /></svg></button>
        </span>
      </div>
    </div>

    <div class="wrap">
      <div v-if="photos.length" class="gal">
        <button v-for="(p, i) in photos.slice(0, 3)" :key="p" type="button" class="gp" :aria-label="`Rasm ${i + 1}ni kattalashtirish`" @click="openLb(i)">
          <img v-if="!failed[i]" :src="p" :alt="`${l.title}, rasm ${i + 1}`" referrerpolicy="no-referrer" @error="failed[i] = true" />
          <span v-else class="fb">{{ tDistrict(l.district) }}</span>
          <span v-if="i === 2 && photos.length > 3" class="more">+{{ photos.length - 3 }} rasm</span>
        </button>
      </div>
      <div v-else class="gal single"><span class="gp fb">{{ t('no_photo') }}</span></div>

      <div class="body">
        <div class="main">
          <p class="p-label">{{ typeLabel }} · {{ isSale ? 'Sotuv' : 'Ijara' }}</p>
          <h1>{{ l.title }}</h1>
          <p class="addr">
            <svg viewBox="0 0 24 24" class="p-ic"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z" /><circle cx="12" cy="10" r="2.5" /></svg>
            {{ tDistrict(l.district) }} tumani, Toshkent<template v-if="l.metro_station && (l.metro_distance_m || 99999) <= 1500"> · {{ l.metro_station }} metrosi ({{ l.metro_distance_m }} m)</template>
          </p>
          <div class="price">{{ money(l.price_uzs) }} <small>so‘m{{ isSale ? '' : ' / oy' }}</small></div>

          <dl class="specs">
            <div><dt>{{ t('spec_total_area') }}</dt><dd>{{ l.area ? l.area + ' m²' : '—' }}</dd></div>
            <div><dt>{{ t('spec_rooms_count') }}</dt><dd>{{ l.rooms }}</dd></div>
            <div><dt>Qavat</dt><dd>{{ floorParts[0] || '—' }}</dd></div>
            <div><dt>Qavatlar soni</dt><dd>{{ floorParts[1] || '—' }}</dd></div>
            <div><dt>Mulk turi</dt><dd>{{ typeLabel }}</dd></div>
            <div><dt>1 m² narxi</dt><dd>{{ l.area ? money(l.price_uzs / l.area) : '—' }}</dd></div>
          </dl>
          <p v-if="audLabel" class="ver ok"><svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20c1-3.5 3.5-5 6.5-5s5.5 1.5 6.5 5" /></svg><span><b>{{ audLabel }}</b><br />{{ t('aud_hint') }}</span></p>

          <section class="sec">
            <div class="intel">
              <div class="ih"><span class="orb" aria-hidden="true"></span><b>{{ t('ai_intel_title') }}</b></div>
              <div class="ig">
                <div class="ic2">
                  <span class="k">{{ t('market_analysis') }}</span>
                  <template v-if="market">
                    <span class="v" :class="market.cls">{{ market.label }}</span>
                    <div class="gauge"><i :style="{ left: market.pos + '%' }"></i></div>
                    <span v-if="market.bench" class="p-note">{{ t('avg_market_in_district', { district: tDistrict(l.district), price: money(market.bench) + ' so‘m' }) }}</span>
                  </template>
                  <span v-else class="p-note">Bu e’lon uchun taqqoslash ma’lumoti yetarli emas.</span>
                </div>
                <div class="ic2">
                  <span class="k">{{ t('safety_analysis') }}</span>
                  <span class="risk" :class="risk.lvl"><svg viewBox="0 0 24 24" class="p-ic"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" /><path d="M9 12l2 2 4-4" /></svg>{{ risk.lvl === 'low' ? t('safe_listing', { pct: risk.pct }) : t('caution_listing', { pct: risk.pct }) }}</span>
                  <ul><li v-for="r in (reasons.length ? reasons : ['Barcha asosiy xavfsizlik tekshiruvlaridan o‘tdi'])" :key="r">{{ r }}</li></ul>
                  <span class="p-note">{{ t('safety_tip') }}</span>
                </div>
              </div>
              <button type="button" class="pbtn line askai" @click="askAi">
                <svg viewBox="0 0 24 24" class="spark"><path d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7z" /></svg>AI’dan bu e’lon haqida so‘rash
              </button>
            </div>
          </section>

          <section v-if="l.description" class="sec"><h2>{{ t('description_heading') }}</h2><p class="desc">{{ l.description }}</p></section>

          <section class="sec"><h2>Qulayliklar</h2>
            <div class="amen"><span v-for="a in amenities" :key="a">{{ a }}</span></div>
            <p class="p-note">E’lon matnidan avtomatik ajratilgan.</p></section>

          <section v-if="nb" class="sec"><h2>Joylashuv: {{ tDistrict(l.district) }}</h2>
            <p class="desc">{{ nb.description_uz }}</p>
            <div class="tagrow"><span v-for="h in nb.highlights_uz" :key="h">{{ h }}</span></div>
            <button type="button" class="guide" @click="showNeighborhoods = true">To‘liq tuman qo‘llanmasi →</button></section>

          <p class="p-note disc">{{ l.disclaimer || t('disclaimer_text') }} <button type="button" class="guide" @click="openReportModal(l.id)">{{ t('report_issue') }}</button></p>
        </div>

        <aside class="contact" aria-label="Bog‘lanish">
          <div class="price sm">{{ money(l.price_uzs) }} <small>so‘m{{ isSale ? '' : ' / oy' }}</small></div>
          <div class="seller"><span class="ava">{{ l.is_owner ? 'E' : 'S' }}</span><div><b>{{ l.is_owner ? 'Mulk egasi' : 'Sotuvchi' }}</b><span>{{ l.source_attribution || 'OLX.uz' }} · {{ dateTxt }}</span></div></div>
          <div v-if="l.is_owner" class="ver ok"><svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" /><path d="M9 12l2 2 4-4" /></svg><div><b>{{ t('verified_owner_tag') }}</b><br />Matnda egasidan joylanganini ko‘rsatuvchi belgilar topildi. Mustaqil tasdiqlanmagan.</div></div>
          <div v-else class="ver rev"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg><div><b>Tekshirilmoqda</b><br />Sotuvchi turi aniq emas. Uchrashuvdan oldin hujjatlarni tekshiring.</div></div>
          <a class="pbtn dark full" :href="tel || l.canonical_url || '#'" :target="tel ? undefined : '_blank'" rel="noopener"><svg viewBox="0 0 24 24" class="p-ic"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" /></svg>{{ t('call_owner') }}</a>
          <div class="b2">
            <a v-if="l.canonical_url" class="pbtn line" :href="l.canonical_url" target="_blank" rel="noopener">{{ t('view_on_olx') }}</a>
            <a class="pbtn line" :href="tg" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" class="p-ic"><path d="M21 4L3 11l6 2 2 6 3-4 5 4z" /><path d="M9 13l9-7" /></svg>{{ t('telegram_short') }}</a>
          </div>
          <button type="button" class="pbtn line full" :aria-pressed="cmp" @click="onCmp"><svg viewBox="0 0 24 24" class="p-ic"><path d="M7 4v16M17 4v16M3 8h8M13 16h8" /></svg>{{ cmp ? t('btn_compared') : t('btn_compare') }}</button>
          <dl class="kv"><dt>E’lon raqami</dt><dd>#{{ l.id }}</dd><dt>Joylangan</dt><dd>{{ dateTxt }}</dd><dt>Rasmlar</dt><dd>{{ photos.length }} ta</dd></dl>
          <p class="p-note">Telefon raqami asl e’lon sahifasida ko‘rsatilishi mumkin.</p>
        </aside>
      </div>

      <section v-if="similar.length" class="sec wide"><h2>O‘xshash uylar</h2><div class="sim"><ListingCard v-for="x in similar" :key="x.id" :listing="x" @select="emit('select', $event)" /></div></section>
      <section v-if="recent.length" class="sec wide"><h2>Yaqinda ko‘rilganlar</h2><div class="sim"><ListingCard v-for="x in recent" :key="x.id" :listing="x" @select="emit('select', $event)" /></div></section>
      <div style="height: 72px"></div>
    </div>

    <div v-if="lb" class="lbox" role="dialog" aria-modal="true" aria-label="Rasmlar" @pointerdown="x0 = $event.clientX" @pointerup="(e) => { if (x0 !== null && Math.abs(e.clientX - x0) > 50) move(e.clientX < x0 ? 1 : -1); x0 = null }">
      <div class="lbar"><span>{{ idx + 1 }} / {{ photos.length }}</span><button type="button" aria-label="Yopish" @click="lb = false"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" /></svg></button></div>
      <div class="stage">
        <img :key="idx" :src="photos[idx]" :alt="`${l.title}, rasm ${idx + 1}`" referrerpolicy="no-referrer" />
        <button v-if="photos.length > 1" type="button" class="nv l" aria-label="Oldingi" @click="move(-1)"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6" /></svg></button>
        <button v-if="photos.length > 1" type="button" class="nv r" aria-label="Keyingi" @click="move(1)"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" /></svg></button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dt { color: var(--tx); }
.dt.overlay { position: fixed; inset: 0; z-index: var(--z-modal); background: var(--bg); overflow-y: auto; overscroll-behavior: contain; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); animation: pagein .35s cubic-bezier(.2, .7, .2, 1); }
.dt:not(.overlay) { padding-top: 84px; }
@keyframes pagein { from { transform: translateY(24px); opacity: .6; } to { transform: none; opacity: 1; } }
.top { position: sticky; top: 0; z-index: 3; padding-block: 10px; background: color-mix(in srgb, var(--bg) 85%, transparent); -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px); border-bottom: 1px solid var(--bd); }
.dt:not(.overlay) .top { position: static; background: transparent; border: 0; backdrop-filter: none; padding-top: 8px; }
.row { display: flex; align-items: center; gap: 8px; }
.crumb { font-size: 13px; color: var(--tx-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.sp { margin-left: auto; display: flex; gap: 2px; }
.ib { width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center; border: 0; background: transparent; cursor: pointer; color: var(--tx); flex: none; }
.ib:hover { background: var(--surface-subtle); }
.ib.on { background: var(--accent-black); color: var(--on-ink); }
.ib svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.ib.favon svg { fill: var(--blue-primary); stroke: var(--blue-primary); }
.gal { display: grid; grid-template-columns: 2fr 1fr; grid-template-rows: 1fr 1fr; gap: 10px; height: clamp(300px, 58vh, 620px); margin-top: 20px; }
.gal.single { display: block; }
.gp { position: relative; border-radius: 20px; overflow: hidden; border: 0; padding: 0; cursor: zoom-in; background: var(--surface-subtle); }
.gp:first-child { grid-row: span 2; }
.gp img { width: 100%; height: 100%; object-fit: cover; display: block; }
.fb { display: flex; align-items: flex-end; padding: 16px; width: 100%; height: 100%; font: 700 15px var(--font-sans); color: var(--blue-primary); background: linear-gradient(160deg, var(--surface-subtle), var(--brand-sand)); }
.more { position: absolute; right: 12px; bottom: 12px; padding: 5px 10px; border-radius: 999px; background: var(--glass-strong); font: 700 11px var(--font-sans); }
.body { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: clamp(24px, 4vw, 64px); margin-top: 34px; align-items: start; }
h1 { margin: 12px 0 0; font: 600 clamp(1.5rem, 2.8vw, 2.3rem)/1.18 var(--font-sans); letter-spacing: -.03em; }
.addr { display: flex; align-items: center; gap: 8px; color: var(--tx-muted); margin: 12px 0 0; flex-wrap: wrap; }
.price { font: 700 clamp(1.9rem, 3.2vw, 2.6rem)/1 var(--font-sans); letter-spacing: -.03em; margin-top: 16px; }
.price.sm { font-size: 28px; margin: 0; }
.price small { font: 500 15px var(--font-sans); color: var(--tx-muted); letter-spacing: 0; }
.specs { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1px; background: var(--bd); border: 1px solid var(--bd); border-radius: 20px; overflow: hidden; margin: 28px 0 0; }
.specs div { background: var(--bg); padding: 16px 18px; display: grid; gap: 4px; }
.specs dt { font: 600 10px var(--font-sans); letter-spacing: .14em; text-transform: uppercase; color: var(--tx-muted); }
.specs dd { margin: 0; font: 700 17px/1.2 var(--font-sans); }
.ver { display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; border-radius: 14px; background: var(--bg); font-size: 13px; margin: 16px 0 0; }
.ver svg { flex: none; width: 18px; height: 18px; margin-top: 1px; fill: none; stroke-width: 2; stroke: var(--warn); stroke-linecap: round; stroke-linejoin: round; }
.ver.ok svg { stroke: var(--ok); }
.contact .ver { margin: 0; }
.sec { margin-top: 44px; display: grid; gap: 14px; }
.sec.wide { margin-top: 64px; }
.sec h2 { margin: 0; font: 600 24px var(--font-sans); letter-spacing: -.02em; max-width: none; }
.desc { white-space: pre-line; color: var(--blue-primary); max-width: 70ch; margin: 0; }
.amen { display: flex; flex-wrap: wrap; gap: 8px; }
.amen span { padding: 9px 14px; border-radius: 999px; background: var(--surface); font: 600 13px var(--font-sans); }
.intel { border-radius: 28px; background: var(--surface); padding: clamp(18px, 2.5vw, 28px); display: grid; gap: 18px; }
.ih { display: flex; align-items: center; gap: 12px; }
.orb { width: 30px; height: 30px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #FBF8F2, #D5C8B5 45%, #514437); flex: none; }
.ig { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.ic2 { border-radius: 20px; padding: 16px; display: grid; gap: 10px; background: var(--bg); align-content: start; }
.k { font: 700 11px var(--font-sans); letter-spacing: .12em; text-transform: uppercase; color: var(--tx-muted); }
.v { font: 700 20px/1.2 var(--font-sans); letter-spacing: -.02em; }
.v.good { color: var(--ok); } .v.high { color: var(--bad); }
.gauge { position: relative; height: 8px; border-radius: 8px; background: linear-gradient(90deg, var(--ok), color-mix(in srgb, var(--ok) 40%, var(--warn)) 50%, var(--bad)); }
.gauge i { position: absolute; top: -5px; width: 18px; height: 18px; border-radius: 50%; background: var(--surface); border: 3px solid var(--accent-black); transform: translateX(-50%); }
.gauge::after { content: ""; position: absolute; left: 50%; top: -4px; bottom: -4px; width: 2px; background: var(--accent-black); opacity: .3; }
.risk { display: flex; gap: 10px; align-items: center; padding: 10px 12px; border-radius: 12px; font: 700 13px var(--font-sans); }
.risk.low { background: var(--ok-bg); color: var(--ok); } .risk.medium { background: var(--warn-bg); color: var(--warn); } .risk.high { background: var(--bad-bg); color: var(--bad); }
.ic2 ul { margin: 0; padding-left: 18px; font-size: 13px; color: var(--blue-primary); }
.askai { justify-self: start; }
.spark { width: 16px; height: 16px; fill: currentColor; }
.guide { background: none; border: 0; padding: 0; font: 700 13px var(--font-sans); color: var(--blue-primary); cursor: pointer; text-align: left; }
.disc { margin-top: 28px; }
.contact { position: sticky; top: 84px; border-radius: 28px; padding: 24px; display: grid; gap: 14px; background: var(--surface); box-shadow: var(--sh-floating); }
.seller { display: flex; gap: 14px; align-items: center; }
.ava { width: 52px; height: 52px; border-radius: 50%; background: var(--surface-subtle); display: grid; place-items: center; font: 700 19px var(--font-sans); flex: none; }
.seller b { display: block; }
.seller span:not(.ava) { font-size: 13px; color: var(--tx-muted); }
.b2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.b2 .pbtn { padding-inline: 12px; }
.kv { display: grid; grid-template-columns: auto 1fr; gap: 8px 16px; font-size: 13px; margin: 0; }
.kv dt { color: var(--tx-muted); } .kv dd { margin: 0; text-align: right; font-weight: 700; }
.sim { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 24px 18px; }
.lbox { position: fixed; inset: 0; z-index: 1400; background: rgba(18, 17, 15, .96); display: flex; flex-direction: column; padding: calc(12px + env(safe-area-inset-top, 0px)) 12px calc(12px + env(safe-area-inset-bottom, 0px)); color: #F5F1E9; touch-action: pan-y; }
.lbar { display: flex; justify-content: space-between; align-items: center; }
.lbar button { width: 40px; height: 40px; border-radius: 50%; border: 0; background: transparent; color: inherit; cursor: pointer; display: grid; place-items: center; }
.lbar svg, .nv svg { width: 20px; height: 20px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.stage { flex: 1; display: grid; place-items: center; min-height: 0; position: relative; }
.stage img { max-height: 100%; max-width: 100%; object-fit: contain; border-radius: 8px; }
.nv { position: absolute; top: 50%; transform: translateY(-50%); width: 52px; height: 52px; border-radius: 50%; border: 0; background: rgba(255, 255, 255, .12); color: #F5F1E9; cursor: pointer; display: grid; place-items: center; }
.nv.l { left: 0; } .nv.r { right: 0; }
@media (max-width: 1023px) { .body { grid-template-columns: minmax(0, 1fr); } .contact { position: static; } }
@media (max-width: 767px) {
  .gal { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; height: auto; gap: 8px; }
  .gp, .gp:first-child { flex: 0 0 88%; aspect-ratio: 4 / 3; scroll-snap-align: center; }
  .ig { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) { .dt.overlay { animation: none; } }
</style>
