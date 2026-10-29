<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

const emit = defineEmits(['openFilters'])
const { t } = useI18n()
const {
  filterDistrict,
  filterRooms,
  filterMaxPrice,
  filterAudience,
  availableDistricts,
} = useListings()

const onSearch = () => {
  const el = document.getElementById('natija')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

const applyQuick = (type: string, val: string) => {
  if (type === 'district') filterDistrict.value = val
  if (type === 'rooms') filterRooms.value = val
  if (type === 'audience') filterAudience.value = val
  onSearch()
}
</script>

<template>
  <section class="hero">
    <div class="wrap hero-in">
      <div class="hero-content">
        <!-- Trust Eyebrow -->
        <div class="hero-eyebrow">
          <span class="eyebrow-badge">
            <span class="eyebrow-pulse"></span>
            100% Egasidan e’lonlar
          </span>
          <span class="eyebrow-sub">0% vositachilik to‘lovi</span>
        </div>

        <!-- Main Headline -->
        <h1>
          Toshkentda yangi uyingizni <span class="highlight-forest">maklersiz</span> toping.
        </h1>

        <!-- Supporting Lead -->
        <p class="lead">
          Ortiqcha to‘lovlarsiz, vositachilarsiz va toza e’lonlar bazasi. Kvartira egasi bilan to‘g‘ridan-to‘g‘ri gaplashib, vaqtingizni va mablag‘ingizni tejang.
        </p>

        <!-- Search Console -->
        <div class="panel search-console">
          <!-- District field -->
          <div class="fld">
            <label for="qd">
              <svg class="i fld-icon" viewBox="0 0 24 24">
                <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              {{ t('area_or_metro') }}
            </label>
            <select id="qd" v-model="filterDistrict">
              <option value="">{{ t('all_areas') }}</option>
              <option v-for="d in availableDistricts" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <!-- Rooms count -->
          <div class="fld">
            <label for="qr">
              <svg class="i fld-icon" viewBox="0 0 24 24">
                <path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9" />
              </svg>
              {{ t('rooms_count') }}
            </label>
            <select id="qr" v-model="filterRooms">
              <option value="">{{ t('any') }}</option>
              <option value="1">1 xona</option>
              <option value="2">2 xona</option>
              <option value="3">3 xona</option>
              <option value="4">4+ xona</option>
            </select>
          </div>

          <!-- Budget field -->
          <div class="fld">
            <label for="qp">
              <svg class="i fld-icon" viewBox="0 0 24 24">
                <rect x="2" y="6" width="20" height="12" rx="2" />
                <circle cx="12" cy="12" r="2" />
                <path d="M6 12h.01M18 12h.01" />
              </svg>
              {{ t('price_range') }}
            </label>
            <select id="qp" v-model="filterMaxPrice">
              <option value="">{{ t('any_price') }}</option>
              <option value="3000000">3 mln so‘mgacha</option>
              <option value="4000000">4 mln so‘mgacha</option>
              <option value="6000000">6 mln so‘mgacha</option>
              <option value="8000000">8 mln so‘mgacha</option>
            </select>
          </div>

          <!-- Audience target -->
          <div class="fld">
            <label for="qa">
              <svg class="i fld-icon" viewBox="0 0 24 24">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              Kimlar uchun
            </label>
            <select id="qa" v-model="filterAudience">
              <option value="all">Barchasi</option>
              <option value="family">👨‍👩‍👧 Oila uchun</option>
              <option value="female">👩 Qizlar uchun</option>
              <option value="male">👨 Yigitlar uchun</option>
            </select>
          </div>

          <!-- Filters Sheet Button -->
          <button class="btn filter-trigger-btn" type="button" @click="$emit('openFilters')" :aria-label="t('filters')">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0" />
              <circle cx="16" cy="6" r="2" />
              <circle cx="10" cy="12" r="2" />
              <circle cx="18" cy="18" r="2" />
            </svg>
            <span class="btn-text">{{ t('filters') }}</span>
          </button>

          <!-- Search Action -->
          <button class="btn p search-btn" type="button" @click="onSearch">
            <svg class="i" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <span>{{ t('search') }}</span>
          </button>
        </div>

        <!-- Quick Suggestions Row -->
        <div class="hero-quick-links">
          <span class="quick-title">Tezkor:</span>
          <button type="button" class="quick-pill" @click="applyQuick('district', 'Chilonzor')">Chilonzor</button>
          <button type="button" class="quick-pill" @click="applyQuick('district', 'Yunusobod')">Yunusobod</button>
          <button type="button" class="quick-pill" @click="applyQuick('district', 'Mirzo Ulug‘bek')">Mirzo Ulug‘bek</button>
          <button type="button" class="quick-pill" @click="applyQuick('rooms', '1')">1 xonali</button>
          <button type="button" class="quick-pill" @click="applyQuick('audience', 'family')">👨‍👩‍👧 Oila uchun</button>
        </div>
      </div>

      <!-- Interactive 3D Architectural Scene (Frameless) -->
      <div class="hero-3d-container">
        <ClientOnly>
          <Hero3DScene />
          <template #fallback>
            <div class="vis-placeholder">
              <div class="spinner"></div>
              <span>Interaktiv arxitektura yuklanmoqda...</span>
            </div>
          </template>
        </ClientOnly>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-content {
  display: flex;
  flex-direction: column;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.eyebrow-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--mint-subtle);
  color: var(--ac);
  border: 1px solid rgba(23, 77, 58, 0.15);
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.eyebrow-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ac);
  box-shadow: 0 0 0 0 rgba(23, 77, 58, 0.7);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0% { box-shadow: 0 0 0 0 rgba(23, 77, 58, 0.7); }
  70% { box-shadow: 0 0 0 6px rgba(23, 77, 58, 0); }
  100% { box-shadow: 0 0 0 0 rgba(23, 77, 58, 0); }
}

.eyebrow-sub {
  font-size: 13px;
  font-weight: 600;
  color: var(--tx-muted);
}

.highlight-forest {
  color: var(--ac);
  position: relative;
  display: inline-block;
}

.fld-icon {
  width: 14px;
  height: 14px;
  color: var(--ac);
  display: inline-block;
  vertical-align: -2px;
  margin-right: 2px;
}

.search-console {
  margin-bottom: 16px;
}

.filter-trigger-btn {
  background: var(--surf-muted);
  border-color: var(--bd);
}

.search-btn {
  background: var(--ac) !important;
  color: #FFFFFF !important;
  border-color: var(--ac) !important;
  font-weight: 700;
  padding: 0 22px;
}

.hero-quick-links {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--tx-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.quick-pill {
  font-size: 12px;
  font-weight: 600;
  color: var(--tx-muted);
  background: var(--card);
  border: 1px solid var(--bd);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  transition: all 0.18s ease;
  cursor: pointer;
}

.quick-pill:hover {
  color: var(--ac);
  border-color: var(--ac);
  background: var(--mint-subtle);
}

.hero-3d-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 460px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.vis-placeholder {
  width: 100%;
  height: 100%;
  min-height: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--tx-muted);
  font-size: 14px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--bd);
  border-top-color: var(--ac);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1023px) {
  .hero-3d-container {
    min-height: 320px;
  }
}
</style>
