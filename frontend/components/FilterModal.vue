<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close'])
const { t } = useI18n()
const { filterAmenities, filterSort, filterAudience } = useListings()

const onReset = () => {
  filterAmenities.value.mebel = false
  filterAmenities.value.kond = false
  filterAmenities.value.kir = false
  filterAmenities.value.net = false
  filterAmenities.value.owner_only = false
  filterAudience.value = 'all'
  filterSort.value = 'new'
}

const onApply = () => {
  emit('close')
}
</script>

<template>
  <div v-if="show" class="ov show" @click.self="$emit('close')">
    <div class="sheet">
      <div class="top">
        <span>{{ t('filters') }}</span>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="bd">
        <h4 style="margin: 0 0 12px; font-size: 15px">Saralash</h4>
        <div class="fi">
          <select v-model="filterSort" id="sort">
            <option value="new">Eng yangi e'lonlar</option>
            <option value="lo">Arzonroqdan boshlab</option>
            <option value="hi">Qimmatroqdan boshlab</option>
          </select>
        </div>

        <h4 style="margin: 20px 0 12px; font-size: 15px">Ijara oluvchilar (Kimlar uchun)</h4>
        <div class="fi">
          <select v-model="filterAudience" id="aud">
            <option value="all">🌐 Barchasi (Farqi yo‘q)</option>
            <option value="family">👨‍👩‍👧 Faqat oila uchun</option>
            <option value="female">👩 Qizlar / Ayollar uchun</option>
            <option value="male">👨 Yigitlar / Talabalar uchun</option>
          </select>
        </div>

        <h4 style="margin: 20px 0 12px; font-size: 15px">Qulayliklar va mezonlar</h4>

        <label class="chk">
          <input type="checkbox" v-model="filterAmenities.owner_only" />
          <span><b>Faqat egasidan (Maklersiz)</b></span>
        </label>

        <label class="chk">
          <input type="checkbox" v-model="filterAmenities.mebel" />
          <span>Mebel mavjud</span>
        </label>

        <label class="chk">
          <input type="checkbox" v-model="filterAmenities.kond" />
          <span>Konditsioner</span>
        </label>

        <label class="chk">
          <input type="checkbox" v-model="filterAmenities.kir" />
          <span>Kir yuvish mashinasi</span>
        </label>

        <label class="chk">
          <input type="checkbox" v-model="filterAmenities.net" />
          <span>Wi-Fi Internet</span>
        </label>
      </div>

      <div class="cbar">
        <button class="btn" type="button" @click="onReset">{{ t('clear') }}</button>
        <button class="btn p" type="button" @click="onApply">Saqlash</button>
      </div>
    </div>
  </div>
</template>

