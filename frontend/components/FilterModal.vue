<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'
import ModalShell from '~/components/ModalShell.vue'

defineProps<{ show: boolean }>()
const emit = defineEmits(['close'])
const { t } = useI18n()
const { filterAmenities, filterSort, filterAudience } = useListings()

const sortOptions = computed(() => [
  { value: 'new', label: t('sort_new') },
  { value: 'lo', label: t('sort_low') },
  { value: 'hi', label: t('sort_high') },
])
const audienceList = computed(() => [
  { value: 'all', label: t('aud_all') },
  { value: 'family', label: t('aud_family') },
  { value: 'female', label: t('aud_female') },
  { value: 'male', label: t('aud_male') },
])
const amenityList = computed(() => [
  { key: 'owner_only', title: t('amenity_owner_title'), sub: t('amenity_owner_sub') },
  { key: 'mebel', title: t('amenity_furniture_title'), sub: t('amenity_furniture_sub') },
  { key: 'kond', title: t('amenity_ac_title'), sub: t('amenity_ac_sub') },
  { key: 'kir', title: t('amenity_wm_title'), sub: t('amenity_wm_sub') },
  { key: 'net', title: t('amenity_wifi_title'), sub: t('amenity_wifi_sub') },
])

const onReset = () => {
  filterAmenities.value.mebel = false
  filterAmenities.value.kond = false
  filterAmenities.value.kir = false
  filterAmenities.value.net = false
  filterAmenities.value.owner_only = false
  filterAudience.value = 'all'
  filterSort.value = 'new'
}
</script>

<template>
  <ModalShell :show="show" :title="t('filter_advanced_title')" @close="emit('close')">
    <div class="fld">
      <span>{{ t('sort_order') }}</span>
      <div class="togs">
        <button v-for="o in sortOptions" :key="o.value" type="button" :aria-pressed="filterSort === o.value" @click="filterSort = o.value as any">{{ o.label }}</button>
      </div>
    </div>
    <div class="fld">
      <span>{{ t('tenant_category') }}</span>
      <div class="togs">
        <button v-for="o in audienceList" :key="o.value" type="button" :aria-pressed="filterAudience === o.value" @click="filterAudience = o.value">{{ o.label }}</button>
      </div>
    </div>
    <div class="fld">
      <span>{{ t('amenities_criteria') }}</span>
      <div class="checks">
        <label v-for="a in amenityList" :key="a.key">
          <input v-model="(filterAmenities as any)[a.key]" type="checkbox" />
          <span><b>{{ a.title }}</b><span>{{ a.sub }}</span></span>
        </label>
      </div>
      <p class="p-note">Qulayliklar e’lon matnidan aniqlanadi.</p>
    </div>
    <template #footer>
      <button type="button" class="pbtn line" @click="onReset">{{ t('clear') }}</button>
      <button type="button" class="pbtn dark" @click="emit('close')">{{ t('apply_filters') }}</button>
    </template>
  </ModalShell>
</template>
