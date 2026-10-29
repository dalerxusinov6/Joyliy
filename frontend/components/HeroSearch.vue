<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

const emit = defineEmits(['openFilters'])
const { t } = useI18n()
const { filterDistrict, filterRooms, filterMaxPrice, availableDistricts } = useListings()

const onSearch = () => {
  const el = document.getElementById('natija')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

const onClear = () => {
  filterDistrict.value = ''
  filterRooms.value = ''
  filterMaxPrice.value = ''
}
</script>

<template>
  <section class="hero">
    <div class="wrap hero-in">
      <div>
        <h1>{{ t('hero_title') }}</h1>
        <p class="lead">{{ t('hero_sub') }}</p>

        <!-- Search Panel -->
        <div class="panel">
          <div class="fld">
            <label for="qd">{{ t('area_or_metro') }}</label>
            <select id="qd" v-model="filterDistrict">
              <option value="">{{ t('all_areas') }}</option>
              <option v-for="d in availableDistricts" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <div class="fld">
            <label for="qr">{{ t('rooms_count') }}</label>
            <select id="qr" v-model="filterRooms">
              <option value="">{{ t('any') }}</option>
              <option value="1">1 xona</option>
              <option value="2">2 xona</option>
              <option value="3">3 xona</option>
              <option value="4">4+ xona</option>
            </select>
          </div>

          <div class="fld">
            <label for="qp">{{ t('price_range') }}</label>
            <select id="qp" v-model="filterMaxPrice">
              <option value="">{{ t('any_price') }}</option>
              <option value="3000000">3 mln so‘mgacha</option>
              <option value="4000000">4 mln so‘mgacha</option>
              <option value="6000000">6 mln so‘mgacha</option>
            </select>
          </div>

          <button class="btn" type="button" @click="$emit('openFilters')">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0" />
              <circle cx="16" cy="6" r="2" />
              <circle cx="10" cy="12" r="2" />
              <circle cx="18" cy="18" r="2" />
            </svg>
            {{ t('filters') }}
          </button>

          <button class="btn p" type="button" @click="onSearch">
            <svg class="i" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            {{ t('search') }}
          </button>
        </div>
      </div>

      <!-- Interactive 3D City & Floating Elements (Frameless) -->
      <div class="hero-3d-container">
        <ClientOnly>
          <Hero3DScene />
          <template #fallback>
            <div class="vis-placeholder">
              <div class="spinner"></div>
              <span>3D muhit yuklanmoqda...</span>
            </div>
          </template>
        </ClientOnly>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-3d-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 440px;
  background: transparent;
  border: none;
  overflow: visible;
  display: flex;
  align-items: center;
  justify-content: center;
}

.vis-placeholder {
  width: 100%;
  height: 100%;
  min-height: 440px;
  background: transparent;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--mu, #64748b);
  font-size: 14px;
}
</style>

