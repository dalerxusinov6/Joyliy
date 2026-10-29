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
  const el = document.getElementById('katalog')
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
  <section class="editorial-hero">
    <div class="wrap">
      <!-- Masthead Metadata Bar -->
      <div class="masthead-bar">
        <div class="masthead-left">
          <span class="masthead-issue">MONOGRAFIYA № 01</span>
          <span class="masthead-dot">·</span>
          <span class="masthead-city">TOSHKENT IJARA BOZORI</span>
          <span class="masthead-dot">·</span>
          <span class="masthead-year">2026</span>
        </div>
        <div class="masthead-right">
          <span class="status-marker"></span>
          <span>Vositachisiz to‘g‘ridan-to‘g‘ri aloqa</span>
        </div>
      </div>

      <!-- Main Asymmetrical Hero Grid -->
      <div class="hero-composition">
        <!-- Left Column: Typography & Integrated Search -->
        <div class="hero-left">
          <div class="hero-tagline-wrap">
            <span class="hero-category-label">Turar-joy kolleksiyasi</span>
          </div>

          <h1 class="hero-title editorial-headline">
            Uy topishning<br />
            <em>yangi usuli.</em>
          </h1>

          <p class="hero-lead">
            Ortiqcha vositachilarsiz. Sizga mos xonadon, to‘g‘ridan-to‘g‘ri mulk egasidan. Toshkentning markaziy va qulay tumanlarida shaffof narxlar hamda tekshirilgan e’lonlar.
          </p>

          <!-- Architectural Search Console -->
          <div class="architectural-console">
            <div class="console-fields">
              <!-- District -->
              <div class="console-cell">
                <span class="cell-label">01 / Tuman yoki metro</span>
                <select v-model="filterDistrict" class="cell-select">
                  <option value="">Barcha tumanlar</option>
                  <option v-for="d in availableDistricts" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>

              <!-- Rooms -->
              <div class="console-cell">
                <span class="cell-label">02 / Xonalar</span>
                <select v-model="filterRooms" class="cell-select">
                  <option value="">Istalgan</option>
                  <option value="1">1 xona</option>
                  <option value="2">2 xona</option>
                  <option value="3">3 xona</option>
                  <option value="4">4+ xona</option>
                </select>
              </div>

              <!-- Budget -->
              <div class="console-cell">
                <span class="cell-label">03 / Byudjet</span>
                <select v-model="filterMaxPrice" class="cell-select">
                  <option value="">Istalgan narx</option>
                  <option value="3000000">3 mln so‘mgacha</option>
                  <option value="4000000">4 mln so‘mgacha</option>
                  <option value="6000000">6 mln so‘mgacha</option>
                  <option value="8000000">8 mln so‘mgacha</option>
                </select>
              </div>

              <!-- Audience -->
              <div class="console-cell">
                <span class="cell-label">04 / Kimlar uchun</span>
                <select v-model="filterAudience" class="cell-select">
                  <option value="all">Barchasi</option>
                  <option value="family">Oila uchun</option>
                  <option value="female">Qizlar uchun</option>
                  <option value="male">Yigitlar uchun</option>
                </select>
              </div>
            </div>

            <!-- Console Actions -->
            <div class="console-actions">
              <button
                type="button"
                class="console-filter-btn"
                @click="$emit('openFilters')"
                title="Barcha filtrlarni ochish"
              >
                <svg class="i" viewBox="0 0 24 24">
                  <line x1="4" y1="21" x2="4" y2="14" />
                  <line x1="4" y1="10" x2="4" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12" y2="3" />
                  <line x1="20" y1="21" x2="20" y2="16" />
                  <line x1="20" y1="12" x2="20" y2="3" />
                  <line x1="1" y1="14" x2="7" y2="14" />
                  <line x1="9" y1="8" x2="15" y2="8" />
                  <line x1="17" y1="16" x2="23" y2="16" />
                </svg>
                <span>Filtrlar</span>
              </button>

              <button type="button" class="console-submit-btn" @click="onSearch">
                <span>Izlash</span>
                <svg class="i" viewBox="0 0 24 24">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Quick Curated Coordinates -->
          <div class="quick-coordinates">
            <span class="quick-label">Mashhur koordinatalar:</span>
            <div class="quick-buttons">
              <button type="button" class="coord-btn" @click="applyQuick('district', 'Chilonzor')">Chilonzor</button>
              <button type="button" class="coord-btn" @click="applyQuick('district', 'Yunusobod')">Yunusobod</button>
              <button type="button" class="coord-btn" @click="applyQuick('district', 'Mirzo Ulug‘bek')">Mirzo Ulug‘bek</button>
              <button type="button" class="coord-btn" @click="applyQuick('rooms', '1')">1 xonali</button>
              <button type="button" class="coord-btn" @click="applyQuick('audience', 'family')">Oila uchun</button>
            </div>
          </div>
        </div>

        <!-- Right Column: Editorial Architecture Visual & Plate -->
        <div class="hero-right">
          <div class="architectural-frame">
            <!-- 3D Scene / Visual Canvas -->
            <div class="visual-canvas">
              <ClientOnly>
                <Hero3DScene />
                <template #fallback>
                  <div class="canvas-fallback">
                    <span class="fallback-spinner"></span>
                    <span>3D arxitektura yuklanmoqda...</span>
                  </div>
                </template>
              </ClientOnly>
            </div>

            <!-- Monograph Architectural Caption Plate -->
            <div class="monograph-plate">
              <div class="plate-top">
                <span class="plate-tag">TURAR JOY HUJJATI</span>
                <span class="plate-geo">41.3110° N, 69.2405° E</span>
              </div>
              <p class="plate-desc">
                Toshkent zamonaviy me’morchiligi va qulay ijara yechimlari.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.editorial-hero {
  padding: 32px 0 54px;
  position: relative;
}

.masthead-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  margin-bottom: 36px;
  border-bottom: 1px solid var(--sand);
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.12em;
  color: var(--muted);
}

.masthead-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.masthead-dot {
  color: var(--terracotta);
}

.masthead-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-marker {
  width: 6px;
  height: 6px;
  background: var(--terracotta);
  border-radius: 50%;
}

.hero-composition {
  display: grid;
  gap: 48px;
  align-items: center;
}

.hero-left {
  display: flex;
  flex-direction: column;
}

.hero-tagline-wrap {
  margin-bottom: 12px;
}

.hero-category-label {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--olive);
  font-weight: 600;
}

.hero-title {
  font-size: clamp(38px, 6vw, 68px);
  margin: 0 0 20px;
  letter-spacing: -0.03em;
  line-height: 1.04;
}

.hero-lead {
  font-size: 16.5px;
  line-height: 1.65;
  color: var(--muted);
  max-width: 560px;
  margin: 0 0 36px;
}

/* Architectural Search Console */
.architectural-console {
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--sh-card);
}

.console-fields {
  display: grid;
  grid-template-columns: 1fr;
  border-bottom: 1px solid var(--sand);
}

.console-cell {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-bottom: 1px solid var(--sand-light);
  transition: background 0.15s ease;
}

.console-cell:last-child {
  border-bottom: none;
}

.console-cell:hover {
  background: var(--ivory);
}

.cell-label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  font-weight: 600;
}

.cell-select {
  border: 0;
  background: transparent;
  outline: none;
  font-size: 14.5px;
  font-weight: 600;
  color: var(--ink);
  cursor: pointer;
  padding: 2px 0;
  width: 100%;
}

.console-actions {
  display: flex;
  align-items: stretch;
}

.console-filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  border-right: 1px solid var(--sand);
  color: var(--ink);
  font-size: 13.5px;
  font-weight: 600;
  background: var(--surf);
  transition: background 0.18s ease;
}

.console-filter-btn:hover {
  background: var(--ivory);
}

.console-submit-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 24px;
  background: var(--terracotta);
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  transition: background 0.2s ease;
}

.console-submit-btn:hover {
  background: var(--terracotta-hover);
}

/* Quick Coordinates */
.quick-coordinates {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  flex-wrap: wrap;
}

.quick-label {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--muted);
}

.quick-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.coord-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink);
  background: var(--surf);
  border: 1px solid var(--sand);
  padding: 3px 10px;
  border-radius: var(--radius-xs);
  transition: all 0.15s ease;
}

.coord-btn:hover {
  border-color: var(--terracotta);
  color: var(--terracotta);
  background: var(--terracotta-subtle);
}

/* Right Architectural Frame */
.hero-right {
  display: flex;
  justify-content: center;
}

.architectural-frame {
  width: 100%;
  max-width: 520px;
  border: 1px solid var(--sand);
  border-radius: var(--radius-sm);
  background: var(--surf);
  overflow: hidden;
  box-shadow: var(--sh-card);
}

.visual-canvas {
  width: 100%;
  height: 380px;
  position: relative;
  background: var(--ivory);
}

.canvas-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--muted);
  font-family: var(--font-mono);
  font-size: 12px;
}

.fallback-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--sand);
  border-top-color: var(--terracotta);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.monograph-plate {
  padding: 16px 20px;
  border-top: 1px solid var(--sand);
  background: var(--surf);
}

.plate-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
}

.plate-tag {
  color: var(--terracotta);
  font-weight: 700;
}

.plate-geo {
  color: var(--muted);
}

.plate-desc {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.45;
}

@media (min-width: 768px) {
  .console-fields {
    grid-template-columns: repeat(2, 1fr);
  }
  .console-cell:nth-child(1),
  .console-cell:nth-child(2) {
    border-bottom: 1px solid var(--sand-light);
  }
  .console-cell:nth-child(3),
  .console-cell:nth-child(4) {
    border-bottom: none;
  }
}

@media (min-width: 1024px) {
  .hero-composition {
    grid-template-columns: 1.15fr 0.85fr;
  }
  .console-fields {
    grid-template-columns: repeat(4, 1fr);
  }
  .console-cell {
    border-bottom: none !important;
    border-right: 1px solid var(--sand-light);
  }
  .console-cell:last-child {
    border-right: none;
  }
  .visual-canvas {
    height: 440px;
  }
}
</style>
