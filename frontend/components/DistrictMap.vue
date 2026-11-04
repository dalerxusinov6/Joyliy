<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useNeighborhoods } from '~/composables/useNeighborhoods'

const emit = defineEmits(['select', 'guide'])
const { tDistrict } = useI18n()
const { listings, availableDistricts } = useListings()
const { items, load, byName } = useNeighborhoods()
onMounted(load)

const LON0 = 69.14, LON1 = 69.38, LAT0 = 41.40, LAT1 = 41.18
const px = (lon: number) => ((lon - LON0) / (LON1 - LON0)) * 100
const py = (lat: number) => ((LAT0 - lat) / (LAT0 - LAT1)) * 100

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
</script>

<template>
  <div class="mapbox">
    <div class="map">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <path class="road" vector-effect="non-scaling-stroke" d="M0 52 C 30 50, 55 56, 100 48" />
        <path class="road" vector-effect="non-scaling-stroke" d="M52 0 C 50 30, 54 62, 49 100" />
        <path class="road" vector-effect="non-scaling-stroke" d="M10 14 C 35 36, 65 62, 92 90" />
        <circle class="road" cx="50" cy="52" r="26" vector-effect="non-scaling-stroke" />
        <path class="river" vector-effect="non-scaling-stroke" d="M30 0 C 36 26, 28 44, 38 64 S 42 90, 36 100" />
        <path class="river thin" vector-effect="non-scaling-stroke" d="M72 0 C 66 24, 78 44, 72 66 S 78 92, 74 100" />
      </svg>
      <button
        v-for="p in pins"
        :key="p.name"
        type="button"
        class="pin"
        :style="{ left: px(p.nb!.center_lon) + '%', top: py(p.nb!.center_lat) + '%' }"
        :aria-pressed="sel === p.name"
        @click="sel = p.name"
      >{{ tDistrict(p.name) }}<small>{{ p.count }}</small></button>
      <span class="note">Sxematik xarita · tuman markazlari haqiqiy koordinatalar bo‘yicha</span>
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
.map { position: relative; background: var(--surface-subtle); border-radius: 28px; overflow: hidden; min-height: 520px; }
.map svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.road { fill: none; stroke: var(--bd); stroke-width: 3; }
.river { fill: none; stroke: var(--brand-sand); stroke-width: 10; stroke-linecap: round; opacity: .7; }
.river.thin { stroke-width: 6; }
.pin { position: absolute; transform: translate(-50%, -100%); border: 0; background: var(--surface); color: var(--tx); border-radius: 999px; padding: 7px 12px; font: 700 12px var(--font-sans); box-shadow: 0 10px 24px -12px rgba(0, 0, 0, .5); cursor: pointer; white-space: nowrap; transition: transform .2s, background .2s; z-index: 1; }
.pin::after { content: ""; position: absolute; left: 50%; bottom: -5px; width: 10px; height: 10px; background: inherit; transform: translateX(-50%) rotate(45deg); }
.pin:hover, .pin[aria-pressed="true"] { background: var(--accent-black); color: var(--on-ink); transform: translate(-50%, -100%) scale(1.06); z-index: 3; }
.pin small { font-weight: 500; opacity: .7; margin-left: 4px; }
.note { position: absolute; left: 14px; bottom: 14px; font-size: 12px; color: var(--tx-muted); background: var(--glass-strong); padding: 6px 12px; border-radius: 999px; }
.side { background: var(--surface); border-radius: 28px; padding: 22px; display: flex; flex-direction: column; gap: 10px; min-width: 0; max-height: 560px; }
.side h3 { margin: 0; font: 600 28px var(--font-sans); letter-spacing: -.03em; }
.meta { margin: 0; color: var(--tx-muted); font-size: 14px; }
.guide { background: none; border: 0; padding: 0; font: 700 13px var(--font-sans); color: var(--blue-primary); cursor: pointer; text-align: left; }
.scroll { overflow-y: auto; display: grid; gap: 2px; margin-inline: -8px; }
@media (max-width: 960px) { .mapbox { grid-template-columns: 1fr; } .map { min-height: 420px; } }
</style>
