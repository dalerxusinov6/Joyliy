<script setup lang="ts">
import { useListings } from '~/composables/useListings'
import { useNeighborhoods } from '~/composables/useNeighborhoods'
import { useI18n } from '~/composables/useI18n'
import ModalShell from '~/components/ModalShell.vue'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'selectDistrict'])
const { filterDistrict, listings } = useListings()
const { items, load } = useNeighborhoods()
const { tDistrict } = useI18n()

watch(() => props.show, (v) => { if (v) load() }, { immediate: true })

const active = ref('')
const current = computed(() => items.value.find((d) => d.id === active.value) || items.value[0])
watch(items, (v) => { if (v.length && !active.value) active.value = v[0].id }, { immediate: true })

const LBL: Record<string, string> = { metro: 'Metro', transport: 'Transport', markets: 'Bozor va do‘konlar', education: 'Ta’lim', parks: 'Bog‘lar', healthcare: 'Sog‘liqni saqlash', safety: 'Xavfsizlik' }
const money = (v: number) => `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln`
const countFor = (name: string) => listings.value.filter((l) => l.district === (name === 'Yangihayot' ? 'Yangi Hayot' : name)).length

const choose = () => {
  if (!current.value) return
  const n = current.value.name_uz === 'Yangihayot' ? 'Yangi Hayot' : current.value.name_uz
  filterDistrict.value = n
  emit('selectDistrict', n)
  emit('close')
  document.getElementById('katalog')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <ModalShell :show="show" wide title="Tumanlar qo‘llanmasi" @close="emit('close')">
    <div class="tabs-row" role="group" aria-label="Tumanlar">
      <button v-for="d in items" :key="d.id" type="button" :aria-pressed="current && current.id === d.id" @click="active = d.id">{{ tDistrict(d.name_uz) }}</button>
    </div>
    <div v-if="!current" class="empty-box"><b>Ma’lumot yuklanmoqda…</b></div>
    <template v-else>
      <div class="meta">
        <span class="pbdg dark">{{ current.overall_score }} / 10</span>
        <span class="pbdg">{{ current.price_tier }}</span>
        <span class="pbdg">{{ countFor(current.name_uz) }} ta faol e’lon</span>
      </div>
      <p class="desc">{{ current.description_uz }}</p>
      <div class="scores">
        <div v-for="(v, k) in current.scores" :key="k"><span>{{ LBL[k] || k }}</span><span class="bar"><i :style="{ width: v * 10 + '%' }"></i></span><b>{{ v }}</b></div>
      </div>
      <dl class="rent">
        <div><dt>1 xonali ijara</dt><dd>~{{ money(current.avg_rent_1room_uzs) }}</dd></div>
        <div><dt>2 xonali ijara</dt><dd>~{{ money(current.avg_rent_2room_uzs) }}</dd></div>
        <div><dt>3 xonali ijara</dt><dd>~{{ money(current.avg_rent_3room_uzs) }}</dd></div>
      </dl>
      <div class="fld"><span>Diqqatga sazovor joylar</span><div class="tagrow"><span v-for="h in current.highlights_uz" :key="h">{{ h }}</span></div></div>
    </template>
    <template #footer>
      <button type="button" class="pbtn dark" :disabled="!current" @click="choose">{{ current ? tDistrict(current.name_uz) : '' }} e’lonlarini ko‘rish</button>
    </template>
  </ModalShell>
</template>

<style scoped>
.tabs-row { display: flex; gap: 6px; flex-wrap: wrap; }
.tabs-row button { border: 1px solid var(--brand-sand); background: transparent; border-radius: 999px; padding: 8px 14px; font: 700 13px var(--font-sans); cursor: pointer; color: var(--tx); }
.tabs-row button[aria-pressed="true"] { background: var(--accent-black); color: var(--on-ink); border-color: var(--accent-black); }
.meta { display: flex; gap: 8px; flex-wrap: wrap; }
.desc { margin: 0; color: var(--blue-primary); max-width: 66ch; }
.scores { display: grid; gap: 8px; }
.scores div { display: grid; grid-template-columns: 140px 1fr 36px; gap: 12px; align-items: center; font-size: 13px; }
.rent { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--bd); border: 1px solid var(--bd); border-radius: 20px; overflow: hidden; margin: 0; }
.rent div { background: var(--bg); padding: 14px 16px; display: grid; gap: 4px; }
.rent dt { font: 600 10px var(--font-sans); letter-spacing: .14em; text-transform: uppercase; color: var(--tx-muted); }
.rent dd { margin: 0; font: 700 17px var(--font-sans); }
@media (max-width: 600px) { .scores div { grid-template-columns: 100px 1fr 30px; } .rent { grid-template-columns: 1fr; } }
</style>
