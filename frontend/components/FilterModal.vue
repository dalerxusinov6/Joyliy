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
  { value: 'all', label: 'Barchasi' },
  { value: 'family', label: 'Oila uchun' },
  { value: 'female', label: 'Qizlar uchun' },
  { value: 'male', label: 'Yigitlar uchun' },
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
        <div class="filter-header-left">
          <span class="filter-heading-text">Kengaytirilgan filtrlar</span>
        </div>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <div class="bd filter-body">
        <!-- Sort Segment -->
        <div class="filter-section">
          <span class="editorial-meta">Saralash tartibi</span>
          <div class="sort-segmented">
            <button
              v-for="opt in sortOptions"
              :key="opt.value"
              type="button"
              class="sort-tab"
              :class="{ active: filterSort === opt.value }"
              @click="filterSort = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- Audience Grid -->
        <div class="filter-section">
          <span class="editorial-meta">Ijarachi toifasi</span>
          <div class="audience-select-grid">
            <button
              v-for="aud in audienceList"
              :key="aud.value"
              type="button"
              class="audience-select-card"
              :class="{ active: filterAudience === aud.value }"
              @click="filterAudience = aud.value"
            >
              <span class="aud-icon">
                <svg v-if="aud.value === 'all'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="f-svg">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <svg v-else-if="aud.value === 'family'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="f-svg">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                <svg v-else-if="aud.value === 'female'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="f-svg">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                <svg v-else-if="aud.value === 'male'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="f-svg">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </span>
              <span class="aud-text">{{ aud.label }}</span>
            </button>
          </div>
        </div>

        <!-- Amenities Checklist -->
        <div class="filter-section">
          <span class="editorial-meta">Qulayliklar va mezonlar</span>
          <div class="amenities-container">
            <!-- Owner Only -->
            <label class="amenity-row owner-highlight">
              <input type="checkbox" v-model="filterAmenities.owner_only" />
              <div class="amenity-desc">
                <span class="amenity-title">Faqat egasidan (Maklersiz)</span>
                <span class="amenity-sub">100% vositachilik komissiyasisiz e’lonlar</span>
              </div>
            </label>

            <!-- Mebel -->
            <label class="amenity-row">
              <input type="checkbox" v-model="filterAmenities.mebel" />
              <div class="amenity-desc">
                <span class="amenity-title">Mebel mavjud</span>
                <span class="amenity-sub">Yashash uchun to‘liq jihozlangan</span>
              </div>
            </label>

            <!-- Konditsioner -->
            <label class="amenity-row">
              <input type="checkbox" v-model="filterAmenities.kond" />
              <div class="amenity-desc">
                <span class="amenity-title">Konditsioner</span>
                <span class="amenity-sub">Sovutish va isitish iqlim uskunasi</span>
              </div>
            </label>

            <!-- Kir yuvish -->
            <label class="amenity-row">
              <input type="checkbox" v-model="filterAmenities.kir" />
              <div class="amenity-desc">
                <span class="amenity-title">Kir yuvish mashinasi</span>
                <span class="amenity-sub">Avtomat kir yuvish texnikasi</span>
              </div>
            </label>

            <!-- Wi-Fi -->
            <label class="amenity-row">
              <input type="checkbox" v-model="filterAmenities.net" />
              <div class="amenity-desc">
                <span class="amenity-title">Wi-Fi Internet</span>
                <span class="amenity-sub">Tezkor internet tarmog‘i</span>
              </div>
            </label>
          </div>
        </div>
      </div>

      <!-- Action Footer Bar -->
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

.filter-header {
  padding: 18px 24px;
}

.filter-header-left {
  display: flex;
  flex-direction: column;
}

.filter-heading-text {
  font-family: var(--font-serif);
  font-size: 19px;
  font-weight: 600;
  color: var(--ink);
}

.filter-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sort-segmented {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--sand-light);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  padding: 3px;
}

.sort-tab {
  padding: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
  border-radius: var(--radius-xs);
  transition: all 0.15s ease;
  text-align: center;
}

.sort-tab.active {
  background: var(--surf);
  color: var(--ink);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.audience-select-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.audience-select-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: all 0.18s ease;
}

.audience-select-card:hover {
  border-color: var(--ink);
}

.audience-select-card.active {
  background: var(--terracotta-subtle);
  border-color: var(--terracotta);
  color: var(--terracotta);
}

.aud-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.f-svg {
  width: 16px;
  height: 16px;
}

.aud-text {
  font-size: 13px;
  font-weight: 600;
}

.amenities-container {
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  overflow: hidden;
}

.amenity-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--sand-light);
  cursor: pointer;
  transition: background 0.15s ease;
}

.amenity-row:last-child {
  border-bottom: none;
}

.amenity-row:hover {
  background: var(--ivory);
}

.owner-highlight {
  background: var(--terracotta-subtle);
}

.amenity-row input {
  width: 17px;
  height: 17px;
  accent-color: var(--terracotta);
}

.amenity-desc {
  display: flex;
  flex-direction: column;
}

.amenity-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
}

.amenity-sub {
  font-size: 11px;
  color: var(--muted);
}

.filter-cbar {
  display: flex;
  gap: 10px;
}

.filter-cbar .btn.p {
  flex: 2;
}

.filter-cbar .btn:first-child {
  flex: 1;
}
</style>
