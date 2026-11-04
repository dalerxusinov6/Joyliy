<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'
import ModalShell from '~/components/ModalShell.vue'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'selectListing'])
const { t, tDistrict } = useI18n()
const { compareList, toggleCompare } = useListings()

interface Card {
  id: number; title: string; price_uzs: number; district: string; rooms: number; area: number; floor: string
  is_owner: boolean; owner_label?: string; metro_station?: string; fair_price_label?: string; scam_risk_label?: string
  price_per_sqm_uzs?: number; composite_score?: number; is_winner?: boolean
}
const data = ref<{ items: Card[]; winner_listing_id?: number; ai_comparison_summary?: string } | null>(null)
const isLoading = ref(false)

const run = async () => {
  if (compareList.value.length < 2) { data.value = null; return }
  isLoading.value = true
  try {
    const base = (useRuntimeConfig().public.apiBase as string) || ''
    data.value = await $fetch(`${base}/api/listings/compare`, { method: 'POST', body: { listing_ids: compareList.value.map((x) => x.id) } }) as any
  } catch (e) {
    data.value = {
      items: compareList.value.map((l) => ({
        id: l.id, title: l.title, price_uzs: l.price_uzs, district: l.district, rooms: l.rooms, area: l.area, floor: l.floor || '—',
        is_owner: l.is_owner, metro_station: l.metro_station || '—', price_per_sqm_uzs: l.area ? Math.round(l.price_uzs / l.area) : 0,
      })),
    }
  } finally { isLoading.value = false }
}
watch(() => props.show, (v) => { if (v) run() }, { immediate: true })
watch(() => compareList.value.length, () => { if (props.show) run() })

const items = computed(() => data.value?.items || [])
const winner = computed(() => items.value.find((i) => i.id === data.value?.winner_listing_id))
const fmt = (v?: number) => (v ? v.toLocaleString('ru-RU').replace(/ /g, ' ') + ' so‘m' : '—')

const rows = computed(() => [
  { k: 'Narx', f: (i: Card) => fmt(i.price_uzs), best: (i: Card) => i.price_uzs, dir: 'min' },
  { k: 'Tuman', f: (i: Card) => tDistrict(i.district) },
  { k: 'Xonalar / maydon', f: (i: Card) => `${i.rooms} xona · ${i.area} m²`, best: (i: Card) => i.area, dir: 'max' },
  { k: '1 m² narxi', f: (i: Card) => fmt(i.price_per_sqm_uzs), best: (i: Card) => i.price_per_sqm_uzs || 1e15, dir: 'min' },
  { k: 'Qavat', f: (i: Card) => i.floor || '—' },
  { k: 'Metro', f: (i: Card) => i.metro_station || '—' },
  { k: 'Bozor bahosi', f: (i: Card) => i.fair_price_label || '—' },
  { k: 'Xavfsizlik', f: (i: Card) => i.scam_risk_label || '—' },
  { k: 'Manba', f: (i: Card) => i.owner_label || (i.is_owner ? 'Egasidan' : 'Aniqlanmagan') },
])
const isBest = (r: any, i: Card) => {
  if (!r.best) return false
  const vals = items.value.map(r.best)
  return r.best(i) === (r.dir === 'min' ? Math.min(...vals) : Math.max(...vals))
}
const open = (id: number) => {
  const l = compareList.value.find((x) => x.id === id)
  if (l) { emit('close'); emit('selectListing', l) }
}
const remove = (id: number) => { const l = compareList.value.find((x) => x.id === id); if (l) toggleCompare(l) }
</script>

<template>
  <ModalShell :show="show" wide :title="t('compare_title')" @close="emit('close')">
    <div v-if="compareList.length < 2" class="empty-box">
      <b>Kamida 2 ta e’lon tanlang</b>
      <p class="p-muted">Kartadagi taqqoslash belgisini bosing. Ko‘pi bilan 4 ta e’lonni solishtirish mumkin.</p>
    </div>
    <div v-else-if="isLoading && !items.length" class="empty-box"><b>{{ t('ai_analyzing') }}</b></div>
    <template v-else>
      <div v-if="winner" class="winner">
        <span class="orb" aria-hidden="true"></span>
        <div>
          <b>{{ t('compare_winner_title', { id: winner.id }) }}</b>
          <p class="p-note">{{ data?.ai_comparison_summary }}</p>
        </div>
      </div>
      <div class="cmp-wrap">
        <table class="cmp">
          <thead>
            <tr><th></th>
              <th v-for="i in items" :key="i.id">
                {{ i.rooms }} xonali · {{ tDistrict(i.district) }}
                <div class="acts"><button type="button" @click="open(i.id)">{{ t('open_listing') }}</button> · <button type="button" @click="remove(i.id)">{{ t('remove_from_compare') }}</button></div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rows" :key="r.k">
              <th>{{ r.k }}</th>
              <td v-for="i in items" :key="i.id" :class="{ best: isBest(r, i) }">{{ r.f(i) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </ModalShell>
</template>

<style scoped>
.winner { display: flex; gap: 14px; align-items: center; padding: 16px; border-radius: 20px; background: var(--surface); }
.winner b { display: block; }
.orb { width: 34px; height: 34px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #FBF8F2, #D5C8B5 45%, #514437); flex: none; }
.cmp-wrap { overflow-x: auto; }
.cmp { border-collapse: collapse; width: 100%; min-width: 560px; font-size: 14px; }
.cmp th, .cmp td { text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--bd); vertical-align: top; }
.cmp tbody th { color: var(--tx-muted); font-weight: 600; width: 22%; }
.cmp thead th { color: var(--tx); }
.cmp td.best { color: var(--ok); font-weight: 700; }
.acts { font-weight: 500; font-size: 12px; margin-top: 4px; color: var(--tx-muted); }
.acts button { background: none; border: 0; padding: 0; font: 700 12px var(--font-sans); color: var(--blue-primary); cursor: pointer; }
</style>
