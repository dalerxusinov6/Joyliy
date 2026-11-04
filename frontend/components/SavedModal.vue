<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'
import ModalShell from '~/components/ModalShell.vue'

defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'select'])
const { t, tDistrict } = useI18n()
const { favorites } = useFavorites()
const { listings, compareList, toggleCompare } = useListings()
const { showCompare } = useModals()

const saved = computed(() => listings.value.filter((l) => favorites.value.includes(l.id)))
const money = (v: number) => (v >= 1e9 ? `${(v / 1e9).toLocaleString('ru-RU', { maximumFractionDigits: 2 })} mlrd` : `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln`)

const compareAll = () => {
  compareList.value = []
  saved.value.slice(0, 3).forEach((l) => toggleCompare(l))
  emit('close')
  showCompare.value = true
}
const pick = (l: ListingItem) => { emit('close'); emit('select', l) }
</script>

<template>
  <ModalShell :show="show" drawer :title="t('saved_title_with_count', { count: saved.length })" @close="emit('close')">
    <div v-if="!saved.length" class="empty-box">
      <b>{{ t('saved_empty_title') }}</b>
      <p class="p-muted">{{ t('saved_empty_desc') }}</p>
      <button type="button" class="pbtn dark" @click="emit('close')">{{ t('back_to_catalog') }}</button>
    </div>
    <template v-else>
      <button v-for="l in saved" :key="l.id" type="button" class="mrow" @click="pick(l)">
        <span class="th"><img v-if="l.image_urls && l.image_urls[0]" :src="l.image_urls[0]" alt="" loading="lazy" referrerpolicy="no-referrer" /></span>
        <span><b>{{ l.rooms }} xonali · {{ tDistrict(l.district) }}</b><small>{{ l.area }} m² · {{ l.floor }}</small></span>
        <span class="pr">{{ money(l.price_uzs) }}</span>
      </button>
      <button v-if="saved.length > 1" type="button" class="pbtn line" @click="compareAll">{{ t('compare') }}</button>
    </template>
  </ModalShell>
</template>
