<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useNeighborhoods } from '~/composables/useNeighborhoods'

const emit = defineEmits(['select', 'guide'])
const { tDistrict } = useI18n()
const { listings, availableDistricts } = useListings()
const { load, byName } = useNeighborhoods()
onMounted(load)

const counts = computed(() => {
  const m: Record<string, number> = {}
  for (const l of listings.value) m[l.district] = (m[l.district] || 0) + 1
  return m
})
const pins = computed(() =>
  availableDistricts.value
    .map((d) => ({ name: d, nb: byName(d), count: counts.value[d] || 0 }))
    .filter((p) => p.nb && p.count > 0),
)

const sel = ref('')
watchEffect(() => { if (!sel.value && pins.value.length) sel.value = [...pins.value].sort((a, b) => b.count - a.count)[0].name })

const info = computed(() => {
  const nb = byName(sel.value)
  const rent = listings.value.filter((l) => l.district === sel.value && (l.deal_type || 'rent') === 'rent')
  const avg = rent.length ? Math.round(rent.reduce((s, l) => s + l.price_uzs, 0) / rent.length) : 0
  return { nb, avg, count: counts.value[sel.value] || 0 }
})
const list = computed(() => listings.value.filter((l) => l.district === sel.value && !l.is_shared_room).slice(0, 40))
const money = (v: number) => (v >= 1e9 ? `${(v / 1e9).toLocaleString('ru-RU', { maximumFractionDigits: 2 })} mlrd` : `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln`)

/* ---------- Yandex Maps (warm, palette-matched) with schematic fallback ---------- */
const box = ref<HTMLElement | null>(null)
const fallback = ref(false)
const ready = ref(false)
const dark = ref(false)
let ymaps: any = null
let map: any = null

const loadSdk = (): Promise<any> => {
  const w = window as any
  if (w.ymaps && w.ymaps.Map) return new Promise((r) => w.ymaps.ready(() => r(w.ymaps)))
  const key = (useRuntimeConfig().public as any).yandexMapsApiKey || ''
  const src = `https://api-maps.yandex.ru/2.1/?lang=uz_UZ${key ? `&apikey=${key}` : ''}`
  return new Promise((resolve, reject) => {
    const done = () => w.ymaps.ready(() => resolve(w.ymaps))
    let s = document.getElementById('yandex-maps-sdk') as HTMLScriptElement | null
    if (s) { if (w.ymaps) done(); else { s.addEventListener('load', done); s.addEventListener('error', reject) } return }
    s = document.createElement('script')
    s.id = 'yandex-maps-sdk'; s.src = src; s.async = true
    s.onload = () => (w.ymaps ? done() : reject(new Error('ymaps missing')))
    s.onerror = reject
    document.head.appendChild(s)
  })
}

const makeLayout = () =>
  ymaps.templateLayoutFactory.createClass(
    '<div class="ymk $[properties.cls]"><span>$[properties.name]</span><small>$[properties.count]</small></div>',
    {
      build() {
        ;(this as any).constructor.superclass.build.call(this)
        const el = (this as any).getParentElement().firstElementChild as HTMLElement
        const r = el.getBoundingClientRect()
        ;(this as any).getData().options.set('shape', {
          type: 'Rectangle',
          coordinates: [[-r.width / 2, -r.height - 8], [r.width / 2, 0]],
        })
      },
    },
  )

const RADIUS: Record<string, number> = { Chilonzor: 3400, Yunusobod: 3800, 'Mirzo Ulug‘bek': 4400, Yakkasaroy: 2200, Mirobod: 2300, Shayxontohur: 2300, Olmazor: 2800, Uchtepa: 3000, Yashnobod: 2800, Sergeli: 4000, Bektemir: 3500, Yangihayot: 3500 }
let touched = false
const circles: Record<string, any> = {}
const pick = (name: string) => { touched = true; sel.value = name }

const render = () => {
  if (!map || !ymaps) return
  map.geoObjects.removeAll()
  const ink = dark.value ? 'D5C8B5' : '514437'
  const Layout = makeLayout()
  for (const k of Object.keys(circles)) delete circles[k]
  for (const p of pins.value) {
    const on = p.name === sel.value
    const c = new ymaps.Circle([[p.nb!.center_lat, p.nb!.center_lon], RADIUS[p.nb!.id] || 3000], { hintContent: `${tDistrict(p.name)} · ${p.count} ta e’lon` }, {
      fillColor: ink + (on ? '33' : '0d'), strokeColor: ink, strokeOpacity: on ? 0.95 : 0.35, strokeWidth: on ? 2.5 : 1.2,
      strokeStyle: on ? 'solid' : 'shortdash', zIndex: on ? 200 : 100, cursor: 'pointer',
    })
    c.events.add('click', () => pick(p.name))
    c.events.add('mouseenter', () => { if (p.name !== sel.value) c.options.set('fillColor', ink + '26') })
    c.events.add('mouseleave', () => { if (p.name !== sel.value) c.options.set('fillColor', ink + '0d') })
    circles[p.name] = c
    map.geoObjects.add(c)
  }
  for (const p of pins.value) {
    const pm = new ymaps.Placemark(
      [p.nb!.center_lat, p.nb!.center_lon],
      { name: tDistrict(p.name), count: p.count, cls: p.name === sel.value ? 'on' : '', hintContent: `${tDistrict(p.name)} · ${p.count} ta e’lon` },
      { iconLayout: Layout, iconOffset: [0, 0], zIndex: p.name === sel.value ? 900 : 500, hasBalloon: false },
    )
    pm.events.add('click', () => pick(p.name))
    map.geoObjects.add(pm)
  }
}

const initMap = async () => {
  try {
    ymaps = await Promise.race([loadSdk(), new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 8000))])
    if (!box.value) return
    map = new ymaps.Map(box.value, { center: [41.3, 69.26], zoom: 11, controls: [] }, {
      suppressMapOpenBlock: true, yandexMapDisablePoiInteractivity: true, minZoom: 9, maxZoom: 17,
    })
    map.behaviors.disable('scrollZoom')
    ready.value = true
    render()
  } catch (e) {
    console.warn('Yandex Maps unavailable, using schematic map', e)
    fallback.value = true
  }
}

const zoom = (d: number) => map?.setZoom(Math.max(9, Math.min(17, map.getZoom() + d)), { duration: 250 })
const locate = () => {
  const c = circles[sel.value]
  if (map && c) map.setBounds(c.geometry.getBounds(), { checkZoomRange: true, duration: 400, zoomMargin: 36 })
}

let mo: MutationObserver | null = null
onMounted(() => {
  dark.value = document.documentElement.dataset.theme === 'dark'
  mo = new MutationObserver(() => { dark.value = document.documentElement.dataset.theme === 'dark' })
  mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
  initMap()
})
onBeforeUnmount(() => { mo?.disconnect(); if (map) { map.destroy(); map = null } })

watch([pins, sel, dark], () => {
  render()
  const c = circles[sel.value]
  if (map && c && touched) map.setBounds(c.geometry.getBounds(), { checkZoomRange: true, duration: 450, zoomMargin: 36 })
})

/* schematic fallback projection */
const LON0 = 69.14, LON1 = 69.38, LAT0 = 41.40, LAT1 = 41.18
const px = (lon: number) => ((lon - LON0) / (LON1 - LON0)) * 100
const py = (lat: number) => ((LAT0 - lat) / (LAT0 - LAT1)) * 100
</script>

<template>
  <div class="mapbox">
    <div class="map ymap-wrap" :class="{ dark, fallback }">
      <div v-show="!fallback" ref="box" class="ybox" aria-label="Toshkent xaritasi"></div>

      <template v-if="fallback">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <path class="road" vector-effect="non-scaling-stroke" d="M0 52 C 30 50, 55 56, 100 48" />
          <path class="road" vector-effect="non-scaling-stroke" d="M52 0 C 50 30, 54 62, 49 100" />
          <path class="road" vector-effect="non-scaling-stroke" d="M10 14 C 35 36, 65 62, 92 90" />
          <circle class="road" cx="50" cy="52" r="26" vector-effect="non-scaling-stroke" />
          <path class="river" vector-effect="non-scaling-stroke" d="M30 0 C 36 26, 28 44, 38 64 S 42 90, 36 100" />
        </svg>
        <button v-for="p in pins" :key="p.name" type="button" class="pin" :style="{ left: px(p.nb!.center_lon) + '%', top: py(p.nb!.center_lat) + '%' }" :aria-pressed="sel === p.name" @click="pick(p.name)">{{ tDistrict(p.name) }}<small>{{ p.count }}</small></button>
      </template>

      <div v-if="ready && !fallback" class="zoom">
        <button type="button" aria-label="Yaqinlashtirish" @click="zoom(1)"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></svg></button>
        <button type="button" aria-label="Uzoqlashtirish" @click="zoom(-1)"><svg viewBox="0 0 24 24"><path d="M5 12h14" /></svg></button>
        <button type="button" aria-label="Tanlangan tumanga" @click="locate"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.5" /><path d="M12 2v4M12 18v4M2 12h4M18 12h4" /></svg></button>
      </div>
      <span class="note">{{ fallback ? 'Sxematik xarita · tuman markazlari' : 'Tumanni bosing · xaritani suring' }}</span>
    </div>

    <div class="side" aria-live="polite">
      <p class="p-label">Tuman</p>
      <h3>{{ tDistrict(sel) }}</h3>
      <p class="meta">{{ info.count }} ta faol e’lon<template v-if="info.avg"> · o‘rtacha ijara {{ money(info.avg) }} so‘m</template><template v-if="info.nb"> · bahosi {{ info.nb.overall_score }}/10</template></p>
      <button type="button" class="guide" @click="emit('guide', sel)">Tuman qo‘llanmasi →</button>
      <div class="scroll">
        <button v-for="l in list" :key="l.id" type="button" class="mrow" @click="emit('select', l as ListingItem)">
          <span class="th"><img v-if="l.image_urls && l.image_urls[0]" :src="l.image_urls[0]" alt="" loading="lazy" referrerpolicy="no-referrer" /></span>
          <span><b>{{ l.rooms }} xonali · {{ l.area }} m²</b><small>{{ l.floor }} qavat · {{ (l.deal_type || 'rent') === 'sale' ? 'Sotuv' : 'Ijara' }}</small></span>
          <span class="pr">{{ money(l.price_uzs) }}</span>
        </button>
        <p v-if="!list.length" class="p-note" style="padding: 8px">Bu tumandan e’lon yo‘q.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mapbox { display: grid; grid-template-columns: 1.3fr .7fr; gap: 20px; }
.map { position: relative; background: var(--surface-subtle); border-radius: 28px; overflow: hidden; min-height: 560px; isolation: isolate; }
.ybox { position: absolute; inset: 0; }
.map > svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.road { fill: none; stroke: var(--bd); stroke-width: 3; }
.river { fill: none; stroke: var(--brand-sand); stroke-width: 10; stroke-linecap: round; opacity: .7; }
.pin { position: absolute; transform: translate(-50%, -100%); border: 0; background: var(--surface); color: var(--tx); border-radius: 999px; padding: 7px 12px; font: 700 12px var(--font-sans); box-shadow: 0 10px 24px -12px rgba(0, 0, 0, .5); cursor: pointer; white-space: nowrap; z-index: 1; }
.pin[aria-pressed="true"] { background: var(--accent-black); color: var(--on-ink); z-index: 3; }
.pin small { font-weight: 500; opacity: .7; margin-left: 4px; }
.zoom { position: absolute; right: 14px; top: 14px; z-index: 5; display: grid; gap: 8px; }
.zoom button { width: 44px; height: 44px; border-radius: 50%; border: 1px solid var(--glass-line); background: var(--glass-strong); -webkit-backdrop-filter: blur(20px); backdrop-filter: blur(20px); box-shadow: var(--sh-floating); display: grid; place-items: center; cursor: pointer; color: var(--tx); }
.zoom button:hover { background: var(--surface); }
.zoom svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; }
.note { position: absolute; left: 14px; bottom: 14px; z-index: 5; font-size: 12px; font-weight: 600; color: var(--tx-muted); background: var(--glass-strong); -webkit-backdrop-filter: blur(20px); backdrop-filter: blur(20px); border: 1px solid var(--glass-line); padding: 7px 12px; border-radius: 999px; }
.side { background: var(--surface); border-radius: 28px; padding: 22px; display: flex; flex-direction: column; gap: 10px; min-width: 0; max-height: 600px; }
.side h3 { margin: 0; font: 600 28px var(--font-sans); letter-spacing: -.03em; }
.meta { margin: 0; color: var(--tx-muted); font-size: 14px; }
.guide { background: none; border: 0; padding: 0; font: 700 13px var(--font-sans); color: var(--blue-primary); cursor: pointer; text-align: left; }
.scroll { overflow-y: auto; display: grid; gap: 2px; margin-inline: -8px; }
@media (max-width: 960px) { .mapbox { grid-template-columns: 1fr; } .map { min-height: 440px; } }
@media (max-width: 640px) { .zoom { right: 10px; top: 10px; gap: 6px; } .zoom button { width: 38px; height: 38px; } .note { left: 10px; bottom: 10px; max-width: calc(100% - 20px); } .side { max-height: none; } .scroll { max-height: 420px; } }
</style>
