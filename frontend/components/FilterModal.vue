<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close'])
const { t } = useI18n()
const { filterAmenities, filterSort, filterAudience } = useListings()

const sortOptions = [
  { value: 'new', label: 'Eng yangi' },
  { value: 'lo', label: 'Arzonroqdan' },
  { value: 'hi', label: 'Qimmatroqdan' },
]

const audienceList = [
  { value: 'all', label: 'Barchasi', icon: '🌐' },
  { value: 'family', label: 'Oila uchun', icon: '👨‍👩‍👧' },
  { value: 'female', label: 'Qizlar uchun', icon: '👩' },
  { value: 'male', label: 'Yigitlar uchun', icon: '👨' },
]

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
    <div class="sheet filter-sheet">
      <!-- Header -->
      <div class="top filter-header">
        <span class="filter-header-title">{{ t('filters') }}</span>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="bd filter-body">
        <!-- Sort Segmented Buttons -->
        <div class="filter-group">
          <label class="filter-group-label">Saralash tartibi</label>
          <div class="segmented-control">
            <button
              v-for="opt in sortOptions"
              :key="opt.value"
              type="button"
              class="segment-btn"
              :class="{ active: filterSort === opt.value }"
              @click="filterSort = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- Audience Selector -->
        <div class="filter-group">
          <label class="filter-group-label">Kimlar uchun (Ijarachi toifasi)</label>
          <div class="audience-grid">
            <button
              v-for="aud in audienceList"
              :key="aud.value"
              type="button"
              class="aud-select-btn"
              :class="{ active: filterAudience === aud.value }"
              @click="filterAudience = aud.value"
            >
              <span class="aud-select-icon">{{ aud.icon }}</span>
              <span class="aud-select-name">{{ aud.label }}</span>
            </button>
          </div>
        </div>

        <!-- Amenities & Requirements Checklist -->
        <div class="filter-group">
          <label class="filter-group-label">Qulayliklar va mezonlar</label>
          <div class="checklist-box">
            <!-- Owner only / Maklersiz -->
            <label class="chk-item owner-chk-item">
              <input type="checkbox" v-model="filterAmenities.owner_only" />
              <div class="chk-text">
                <span class="chk-name">Faqat egasidan (Maklersiz)</span>
                <span class="chk-sub">Vositachisiz to‘g‘ridan-to‘g‘ri e’lonlar</span>
              </div>
            </label>

            <!-- Mebel -->
            <label class="chk-item">
              <input type="checkbox" v-model="filterAmenities.mebel" />
              <div class="chk-text">
                <span class="chk-name">Mebel mavjud</span>
                <span class="chk-sub">Yashash uchun barcha kerakli mebellar</span>
              </div>
            </label>

            <!-- Konditsioner -->
            <label class="chk-item">
              <input type="checkbox" v-model="filterAmenities.kond" />
              <div class="chk-text">
                <span class="chk-name">Konditsioner</span>
                <span class="chk-sub">Yozgi salqinlik va qishki isitish</span>
              </div>
            </label>

            <!-- Kir yuvish -->
            <label class="chk-item">
              <input type="checkbox" v-model="filterAmenities.kir" />
              <div class="chk-text">
                <span class="chk-name">Kir yuvish mashinasi</span>
                <span class="chk-sub">Avtomat kir yuvish uskunasi</span>
              </div>
            </label>

            <!-- Wi-Fi -->
            <label class="chk-item">
              <input type="checkbox" v-model="filterAmenities.net" />
              <div class="chk-text">
                <span class="chk-name">Yuqori tezlikdagi Wi-Fi</span>
                <span class="chk-sub">Internet tarmog‘i ulangan</span>
              </div>
            </label>
          </div>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="cbar filter-cbar">
        <button class="btn" type="button" @click="onReset">{{ t('clear') }}</button>
        <button class="btn p" type="button" @click="onApply">Filtrlarni qo‘llash</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-sheet {
  max-width: 540px;
}

.filter-header-title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.filter-body {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.filter-group-label {
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--tx-muted);
  margin-bottom: 10px;
  display: block;
}

.segmented-control {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--surf-muted);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--bd);
}

.segment-btn {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--tx-muted);
  cursor: pointer;
  transition: all 0.18s ease;
  text-align: center;
}

.segment-btn.active {
  background: var(--card);
  color: var(--tx);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.audience-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.aud-select-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--surf);
  border: 1px solid var(--bd);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.18s ease;
}

.aud-select-btn:hover {
  border-color: var(--bd-hover);
  background: var(--surf-muted);
}

.aud-select-btn.active {
  border-color: var(--ac);
  background: var(--mint-subtle);
  color: var(--ac);
}

.aud-select-icon {
  font-size: 18px;
}

.aud-select-name {
  font-size: 13.5px;
  font-weight: 600;
}

.checklist-box {
  background: var(--surf);
  border: 1px solid var(--bd);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.chk-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--bd);
  cursor: pointer;
  transition: background 0.15s ease;
}

.chk-item:last-child {
  border-bottom: none;
}

.chk-item:hover {
  background: var(--surf-muted);
}

.owner-chk-item {
  background: var(--mint-subtle);
}

.chk-item input {
  width: 18px;
  height: 18px;
  accent-color: var(--ac);
  cursor: pointer;
}

.chk-text {
  display: flex;
  flex-direction: column;
}

.chk-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--tx);
}

.chk-sub {
  font-size: 11.5px;
  color: var(--tx-muted);
}

.filter-cbar {
  display: flex;
  gap: 10px;
}

.filter-cbar .btn.p {
  flex: 2;
  background: var(--ac);
  color: #FFFFFF;
}

.filter-cbar .btn:first-child {
  flex: 1;
}
</style>
