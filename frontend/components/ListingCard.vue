<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'

const props = withDefaults(defineProps<{ listing: ListingItem; size?: '' | 'big' | 'mid' | 'wide' | 'rail' }>(), { size: '' })
const emit = defineEmits(['select'])

const { t, tDistrict } = useI18n()
const { isFavorite, toggleFavorite } = useFavorites()
const { isInCompare, toggleCompare, marketDiff } = useListings()

const imgFailed = ref(false)
const imgLoaded = ref(false)
const l = computed(() => props.listing)
const isSale = computed(() => l.value.deal_type === 'sale')

const money = (v: number) => {
  if (!v) return '—'
  if (v >= 1e9) return `${(v / 1e9).toLocaleString('ru-RU', { maximumFractionDigits: 2 })} mlrd`
  if (v >= 1e6) return `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: v < 1e8 ? 1 : 0 })} mln`
  return v.toLocaleString('ru-RU').replace(/ /g, ' ')
}

const market = computed(() => {
  const d = marketDiff(l.value)
  if (d === null) return null
  if (d <= -10) return { cls: 'good', label: `Bozordan ${Math.abs(d)}% arzon` }
  if (d >= 10) return { cls: 'high', label: `Bozordan ${d}% qimmat` }
  return { cls: '', label: t('at_market_label') }
})

const ago = computed(() => {
  const d = l.value.days_ago ?? 0
  return d <= 0 ? t('today') : d === 1 ? t('yesterday') : `${d} ${t('days_ago')}`
})

const typeLabel = computed(() => {
  const p = (l.value.property_type || '').toLowerCase()
  if (p === 'new_building') return t('type_new_building')
  if (p === 'house') return t('type_house')
  if (p === 'secondary') return t('type_secondary')
  return 'Kvartira'
})

const photoCount = computed(() => (l.value.image_urls || []).length)
const fav = computed(() => isFavorite(l.value.id))
const cmp = computed(() => isInCompare(l.value.id))

const onFav = (e: MouseEvent) => { e.stopPropagation(); toggleFavorite(l.value.id) }
const onCmp = (e: MouseEvent) => { e.stopPropagation(); toggleCompare(l.value) }
const onKey = (e: KeyboardEvent) => { if (e.key === 'Enter') emit('select', l.value) }
</script>

<template>
  <article
    class="pc"
    :class="size"
    tabindex="0"
    :aria-label="`${l.rooms} xonali, ${tDistrict(l.district)}`"
    @click="emit('select', l)"
    @keydown="onKey"
  >
    <div class="ph" :class="{ ok: imgLoaded, err: imgFailed || !photoCount }" :data-fb="tDistrict(l.district)">
      <img
        v-if="photoCount && !imgFailed"
        :src="l.image_urls[0]"
        :alt="`${l.title} — ${tDistrict(l.district) || 'Toshkent'}, Joyliy.uz`"
        loading="lazy"
        decoding="async"
        referrerpolicy="no-referrer"
        width="400"
        height="300"
        @load="imgLoaded = true"
        @error="imgFailed = true"
      />
      <div class="acts">
        <button type="button" :aria-pressed="cmp" :aria-label="cmp ? t('btn_compared') : t('btn_compare')" :class="{ on: cmp }" @click="onCmp">
          <svg viewBox="0 0 24 24"><path d="M7 4v16M17 4v16M3 8h8M13 16h8" /></svg>
        </button>
        <button type="button" :aria-pressed="fav" :aria-label="t('save')" :class="{ fav }" @click="onFav">
          <svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" /></svg>
        </button>
      </div>
      <div class="badges">
        <span v-if="l.match_percentage" class="bdg match">
          <svg viewBox="0 0 24 24" class="fillic"><path d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7z" /></svg>{{ t('badge_match', { pct: l.match_percentage }) }}
        </span>
        <span v-if="isSale" class="bdg">{{ t('badge_for_sale') }}</span>
        <span v-if="l.is_owner" class="bdg ok">
          <svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" /><path d="M9 12l2 2 4-4" /></svg>{{ t('badge_owner') }}
        </span>
        <span v-else-if="market?.cls === 'good'" class="bdg">{{ t('badge_below_market') }}</span>
        <span v-else-if="l.near_metro" class="bdg">{{ t('metro_near') }}</span>
      </div>
      <span v-if="photoCount > 1" class="bdg count">
        <svg viewBox="0 0 24 24"><path d="M4 8h3l2-3h6l2 3h3v11H4z" /><circle cx="12" cy="13" r="3.5" /></svg>{{ photoCount }}
      </span>
    </div>

    <div class="info">
      <div class="price">{{ money(l.price_uzs) }} <small>so‘m{{ isSale ? '' : ' / oy' }}</small></div>
      <h3>{{ l.title }}</h3>
      <div class="specs">
        <span><svg viewBox="0 0 24 24"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z" /><circle cx="12" cy="10" r="2.5" /></svg>{{ tDistrict(l.district) }}</span>
        <span><svg viewBox="0 0 24 24"><path d="M3 18V7M3 13h18v5M21 13a3 3 0 0 0-3-3h-7v3" /></svg>{{ t('rooms_spec', { rooms: l.rooms }) }}</span>
        <span v-if="l.area"><svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="1" /><path d="M4 9h5V4M20 15h-5v5" /></svg>{{ l.area }} m²</span>
        <span v-if="l.floor"><svg viewBox="0 0 24 24"><path d="M4 20h16M6 20V8l6-4 6 4v12" /></svg>{{ l.floor }}</span>
      </div>
      <div class="meta">
        <span>{{ typeLabel }} · {{ ago }}</span>
        <span v-if="market" class="mkt" :class="market.cls">{{ market.label }}</span>
      </div>
      <div v-if="l.match_percentage && size !== 'rail' && ((l.match_pros && l.match_pros.length) || (l.match_cons && l.match_cons.length))" class="why">
        <span v-if="l.match_pros && l.match_pros.length"><b>+</b> {{ l.match_pros.slice(0, 2).join(' · ') }}</span>
        <span v-if="l.match_cons && l.match_cons.length"><b>−</b> {{ l.match_cons.slice(0, 1).join(' · ') }}</span>
      </div>
      <p v-if="size === 'wide' && l.description" class="desc">{{ l.description }}</p>
    </div>
  </article>
</template>

<style scoped>
.pc { position: relative; display: flex; flex-direction: column; gap: 14px; cursor: pointer; min-width: 0; color: var(--tx); outline: none; }
.pc:focus-visible .ph { box-shadow: 0 0 0 3px var(--blue-primary); }
.ph { position: relative; aspect-ratio: 4 / 3; border-radius: 20px; overflow: hidden; background: linear-gradient(110deg, var(--surface-subtle) 30%, var(--bg) 50%, var(--surface-subtle) 70%) 0 0 / 300% 100%; animation: shim 1.6s linear infinite; }
.ph.ok, .ph.err { animation: none; }
.ph img { width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: transform .8s cubic-bezier(.2, .7, .2, 1), opacity .4s; display: block; }
.ph.ok img { opacity: 1; }
.pc:hover .ph img { transform: scale(1.04); }
.ph.err::after { content: attr(data-fb); position: absolute; inset: 0; display: flex; align-items: flex-end; padding: 16px; font: 700 15px/1 var(--font-sans); color: var(--blue-primary);
  background: repeating-linear-gradient(90deg, transparent 0 22px, rgba(81, 68, 55, .08) 22px 23px), repeating-linear-gradient(0deg, transparent 0 30px, rgba(81, 68, 55, .08) 30px 31px), linear-gradient(160deg, var(--surface-subtle), var(--brand-sand)); }
@keyframes shim { to { background-position: -300% 0; } }
.acts { position: absolute; top: 12px; right: 12px; display: flex; gap: 6px; z-index: 2; }
.acts button { width: 36px; height: 36px; border-radius: 50%; border: 0; background: var(--glass-strong); backdrop-filter: blur(8px); display: grid; place-items: center; cursor: pointer; color: var(--tx); }
.acts svg { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 1.8; }
.acts .on { background: var(--accent-black); color: var(--on-ink); }
.acts .fav svg { fill: var(--blue-primary); stroke: var(--blue-primary); }
.badges { position: absolute; top: 12px; left: 12px; z-index: 2; display: flex; flex-wrap: wrap; gap: 5px; max-width: calc(100% - 100px); }
.bdg { display: inline-flex; align-items: center; gap: 5px; padding: 5px 9px; border-radius: 999px; background: var(--glass-strong); backdrop-filter: blur(8px); font: 700 11px var(--font-sans); color: var(--tx); }
.bdg svg { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 2.2; }
.bdg .fillic { fill: currentColor; stroke: none; }
.bdg.ok { color: var(--ok); }
.bdg.match { background: var(--accent-black); color: var(--on-ink); }
.bdg.count { position: absolute; right: 12px; bottom: 12px; z-index: 2; }
.info { display: grid; gap: 6px; min-width: 0; }
.price { font: 700 22px/1.1 var(--font-sans); letter-spacing: -.02em; }
.price small { font: 500 13px var(--font-sans); color: var(--tx-muted); letter-spacing: 0; }
h3 { margin: 0; font: 600 15px/1.35 var(--font-sans); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.specs { display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 13px; color: var(--tx-muted); }
.specs span { display: inline-flex; align-items: center; gap: 5px; }
.specs svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 1.7; }
.meta { display: flex; justify-content: space-between; gap: 10px; font-size: 12px; color: var(--tx-muted); }
.mkt { font-weight: 700; }
.mkt.good { color: var(--ok); }
.mkt.high { color: var(--bad); }
.why { display: grid; gap: 2px; font-size: 12px; color: var(--blue-primary); background: var(--surface-subtle); padding: 8px 10px; border-radius: 12px; line-height: 1.45; }
.desc { margin: 0; color: var(--tx-muted); font-size: 14px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

.pc.big { grid-column: span 7; grid-row: span 2; }
.pc.big .ph { aspect-ratio: 4 / 3.4; flex: 1; }
.pc.big .price { font-size: 30px; }
.pc.mid { grid-column: span 5; }
.pc.mid .ph { aspect-ratio: 16 / 10; }
.pc.wide { grid-column: span 12; flex-direction: row; gap: 28px; align-items: center; background: var(--surface); border-radius: 28px; padding: 12px; }
.pc.wide .ph { width: 52%; aspect-ratio: 16 / 9; flex: none; }
.pc.wide .info { padding: 12px 16px 12px 0; gap: 12px; }
.pc.wide .price { font-size: 30px; }
.pc.rail .ph { aspect-ratio: 4 / 5; }
@media (max-width: 900px) {
  .pc.big, .pc.mid { grid-column: span 12; }
  .pc.wide { flex-direction: column; align-items: stretch; }
  .pc.wide .ph { width: 100%; }
  .pc.wide .info { padding: 4px 8px 12px; }
}
@media (prefers-reduced-motion: reduce) { .ph { animation: none; } .ph img { transition: none; } }
</style>
