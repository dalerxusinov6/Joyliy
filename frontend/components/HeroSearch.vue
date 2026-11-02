<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

const emit = defineEmits(['openFilters'])
const { t } = useI18n()
const {
  filterDistrict,
  filterRooms,
  filterMaxPrice,
  filterAudience,
  filterDealType,
  filterPropertyType,
  availableDistricts,
  aiSearchQuery,
  isAiSearching,
  aiSearchActive,
  runAiMatch,
  resetAiMatch,
} = useListings()

const searchMode = ref<'rent' | 'buy' | 'ai'>('rent')
const aiInput = ref('')

// Initialize searchMode to match filterDealType
if (filterDealType.value === 'sale') {
  searchMode.value = 'buy'
}

const setMode = (mode: 'rent' | 'buy' | 'ai') => {
  searchMode.value = mode
  if (mode === 'rent') {
    filterDealType.value = 'rent'
    filterMaxPrice.value = ''
    filterPropertyType.value = ''
  } else if (mode === 'buy') {
    filterDealType.value = 'sale'
    filterMaxPrice.value = ''
    filterAudience.value = 'all'
  }
}

const handleAiSearch = async () => {
  if (!aiInput.value.trim()) return
  await runAiMatch(aiInput.value)
  const el = document.getElementById('katalog')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const applyAiPrompt = async (prompt: string) => {
  aiInput.value = prompt
  searchMode.value = 'ai'
  await runAiMatch(prompt)
  const el = document.getElementById('katalog')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

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
  <section class="iconly-hero-section">
    <div class="wrap">
      <!-- Atmospheric Hero Dashboard Container (Iconly Large Rounded Banner) -->
      <div class="atmospheric-hero-card">
        <div class="hero-inner-grid">
          <!-- Left: Hero Headline, Tabs & Search Panel -->
          <div class="hero-left-content">
            <!-- Top Tag Pill -->
            <div class="hero-badge-pill">
              <span class="pulse-dot"></span>
              <span>Toshkentda 0% vositachilik komissiyasi</span>
            </div>

            <!-- Headline matching prompt -->
            <h1 class="hero-heading">
              Orzuingizdagi uyni <span class="heading-gradient">toping.</span>
            </h1>

            <p class="hero-subheading">
              O‘zbekistondagi uy-joylarni sotib oling yoki ijaraga oling. Xonadon egalaridan tekshirilgan e’lonlar va sun’iy intellekt tahlili.
            </p>

            <!-- Mode Switcher Tabs (Iconly Pill Tabs - Touch-Friendly Scrollable) -->
            <div class="mode-tabs-wrapper" role="tablist" aria-label="Qidiruv rejimlari">
              <button
                type="button"
                role="tab"
                class="mode-pill-tab"
                :class="{ active: searchMode === 'rent' }"
                @click="setMode('rent')"
              >
                Ijaraga olish
              </button>
              <button
                type="button"
                role="tab"
                class="mode-pill-tab"
                :class="{ active: searchMode === 'buy' }"
                @click="setMode('buy')"
              >
                Sotib olish
              </button>
              <button
                type="button"
                role="tab"
                class="mode-pill-tab ai-tab-special"
                :class="{ active: searchMode === 'ai' }"
                @click="setMode('ai')"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="tab-svg-icon">
                  <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
                </svg>
                <span class="tab-label-desktop">AI Aqlli Qidiruv</span>
                <span class="tab-label-mobile">AI Qidiruv</span>
                <span class="ai-chip-pill">Tezkor</span>
              </button>
            </div>

            <!-- Floating White Search Console (Iconly Card Surface) -->
            <div class="floating-search-console">
              <!-- AI Search Interface -->
              <div v-if="searchMode === 'ai'" class="ai-console-block">
                <div class="ai-input-wrapper">
                  <div class="ai-input-prefix">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="sparkle-icon">
                      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
                    </svg>
                  </div>
                  <input
                    v-model="aiInput"
                    type="text"
                    placeholder="Masalan: Chilonzor metro yaqinida 4 mln gacha 2 xonali kvartira..."
                    class="ai-search-input"
                    aria-label="AI qidiruv so‘rovi"
                    @keydown.enter.prevent="handleAiSearch"
                  />
                  <button
                    type="button"
                    class="btn-iconly-search"
                    :disabled="isAiSearching || !aiInput.trim()"
                    @click="handleAiSearch"
                  >
                    <span v-if="!isAiSearching">AI bilan topish</span>
                    <span v-else>Tahlil qilinmoqda...</span>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="arrow-icon">
                      <line x1="5" y1="12" x2="19" y2="12" />
                      <polyline points="12 5 19 12 12 19" />
                    </svg>
                  </button>
                </div>

                <!-- Quick Prompt Suggestions (Horizontal Scroll) -->
                <div class="ai-prompts-row">
                  <span class="prompts-title">Misollar:</span>
                  <div class="prompts-scroll">
                    <button type="button" class="prompt-pill" @click="applyAiPrompt('Chilonzorda metro yaqinida 4 mln gacha 2 xonali')">
                      <svg class="prompt-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect width="16" height="16" x="4" y="3" rx="2"/>
                        <path d="M4 11h16"/>
                        <path d="M12 3v8"/>
                        <path d="m8 19-2 3"/>
                        <path d="m18 22-2-3"/>
                        <circle cx="8" cy="15" r="1"/>
                        <circle cx="16" cy="15" r="1"/>
                      </svg>
                      <span>Chilonzor metro 4 mln</span>
                    </button>
                    <button type="button" class="prompt-pill" @click="applyAiPrompt('Yunusobodda maklersiz oila uchun')">
                      <svg class="prompt-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                      </svg>
                      <span>Yunusobod oila</span>
                    </button>
                    <button type="button" class="prompt-pill" @click="applyAiPrompt('Mirobodda 3 xonali jihozlangan')">
                      <svg class="prompt-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                      </svg>
                      <span>Mirobod jihozlangan</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Standard Filters Interface (Rent & Buy) -->
              <div v-else class="standard-console-block">
                <div class="console-fields-row">
                  <!-- District -->
                  <div class="field-item">
                    <label class="field-lbl">Tuman</label>
                    <div class="field-select-wrap">
                      <select v-model="filterDistrict" class="iconly-select" aria-label="Tuman tanlang">
                        <option value="">Barchasi</option>
                        <option v-for="d in availableDistricts" :key="d" :value="d">{{ d }}</option>
                      </select>
                    </div>
                  </div>

                  <!-- Rooms -->
                  <div class="field-item">
                    <label class="field-lbl">Xonalar soni</label>
                    <div class="field-select-wrap">
                      <select v-model="filterRooms" class="iconly-select" aria-label="Xonalar soni">
                        <option value="">Istalgan</option>
                        <option value="1">1 xonali</option>
                        <option value="2">2 xonali</option>
                        <option value="3">3 xonali</option>
                        <option value="4">4+ xonali</option>
                      </select>
                    </div>
                  </div>

                  <!-- Price: Rent vs Buy -->
                  <div class="field-item" v-if="searchMode === 'buy'">
                    <label class="field-lbl">Maksimal byudjet</label>
                    <div class="field-select-wrap">
                      <select v-model="filterMaxPrice" class="iconly-select" aria-label="Maksimal xarid byudjeti">
                        <option value="">Istalgan</option>
                        <option value="400000000">400 mln so‘m</option>
                        <option value="600000000">600 mln so‘m</option>
                        <option value="800000000">800 mln so‘m</option>
                        <option value="1200000000">1.2 mlrd so‘m</option>
                        <option value="2000000000">2.0 mlrd so‘m</option>
                        <option value="3500000000">3.5 mlrd so‘m</option>
                      </select>
                    </div>
                  </div>
                  <div class="field-item" v-else>
                    <label class="field-lbl">Maksimal byudjet</label>
                    <div class="field-select-wrap">
                      <select v-model="filterMaxPrice" class="iconly-select" aria-label="Maksimal ijara byudjeti">
                        <option value="">Istalgan</option>
                        <option value="3000000">3 000 000 so‘m</option>
                        <option value="4000000">4 000 000 so‘m</option>
                        <option value="6000000">6 000 000 so‘m</option>
                        <option value="8000000">8 000 000 so‘m</option>
                        <option value="12000000">12 000 000 so‘m</option>
                      </select>
                    </div>
                  </div>

                  <!-- Buy: Property Type vs Rent: Target Audience -->
                  <div class="field-item" v-if="searchMode === 'buy'">
                    <label class="field-lbl">Mulk turi</label>
                    <div class="field-select-wrap">
                      <select v-model="filterPropertyType" class="iconly-select" aria-label="Mulk turi">
                        <option value="">Barchasi</option>
                        <option value="new_building">Novostroyka</option>
                        <option value="secondary">Ikkilamchi</option>
                        <option value="house">Hovli / Dacha</option>
                      </select>
                    </div>
                  </div>
                  <div class="field-item" v-else>
                    <label class="field-lbl">Kim uchun</label>
                    <div class="field-select-wrap">
                      <select v-model="filterAudience" class="iconly-select" aria-label="Kim uchun">
                        <option value="all">Barchasi</option>
                        <option value="family">Oila uchun</option>
                        <option value="female">Qizlar uchun</option>
                        <option value="male">Yigitlar uchun</option>
                      </select>
                    </div>
                  </div>

                  <!-- Action Buttons (Responsive Layout) -->
                  <div class="field-actions">
                    <button
                      type="button"
                      class="btn-iconly-filter"
                      @click="$emit('openFilters')"
                      title="Qo‘shimcha filtrlar"
                      aria-label="Kengaytirilgan filtrlar"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="filter-icon">
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
                    </button>

                    <button type="button" class="btn-iconly-submit" @click="onSearch" aria-label="Qidirish">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="search-icon">
                        <circle cx="11" cy="11" r="8" />
                        <line x1="21" y1="21" x2="16.65" y2="16.65" />
                      </svg>
                      <span>Qidirish</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Active AI Search Filter Status -->
            <div v-if="aiSearchActive" class="ai-active-status">
              <div class="ai-status-left">
                <span class="ai-badge-live">
                  <svg class="ai-chip-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect width="16" height="16" x="4" y="4" rx="2" />
                    <rect width="6" height="6" x="9" y="9" rx="1" />
                    <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
                  </svg>
                  <span>Joyliy AI</span>
                </span>
                <span class="ai-query-text">«{{ aiSearchQuery }}»</span>
              </div>
              <button type="button" class="ai-reset-btn" @click="resetAiMatch" aria-label="Filtrni tozalash">
                <span>Filtrni tozalash</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="reset-svg">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Right: Hero Visual Showcase (Desktop Only) -->
          <div class="hero-right-visual">
            <div class="visual-stack">
              <!-- Background Architectural Photo with Glass Overlay -->
              <div class="visual-photo-card">
                <img
                  src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
                  alt="Toshkent premium xonadon"
                  class="visual-img"
                  loading="eager"
                />
                <div class="visual-photo-glass-bottom">
                  <div class="spec-col">
                    <span class="spec-label">Maydon</span>
                    <span class="spec-val">85 m²</span>
                  </div>
                  <div class="spec-sep"></div>
                  <div class="spec-col">
                    <span class="spec-label">Xonalar</span>
                    <span class="spec-val">3 xona</span>
                  </div>
                  <div class="spec-sep"></div>
                  <div class="spec-col">
                    <span class="spec-label">Qavat</span>
                    <span class="spec-val">4 / 9</span>
                  </div>
                </div>
              </div>

              <!-- Floating Circular Score Indicator Badge (Matching 9.4 Ring Badge in Image 1) -->
              <div class="floating-score-badge">
                <div class="score-ring">
                  <span class="score-number">9.4</span>
                </div>
                <div class="score-meta">
                  <span class="score-title">Moslik darajasi</span>
                  <span class="score-sub">Ajoyib joylashuv</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.iconly-hero-section {
  padding: 16px 0 24px;
}

@media (min-width: 640px) {
  .iconly-hero-section {
    padding: 24px 0 32px;
  }
}

@media (min-width: 1024px) {
  .iconly-hero-section {
    padding: 32px 0 44px;
  }
}

/* Atmospheric Hero Card */
.atmospheric-hero-card {
  background: var(--hero-gradient);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 16px 48px -8px rgba(40, 120, 200, 0.12), 0 4px 16px rgba(0, 0, 0, 0.02);
  padding: 16px 12px;
  position: relative;
  overflow: hidden;
}

@media (min-width: 375px) {
  .atmospheric-hero-card {
    padding: 18px 14px;
    border-radius: 24px;
  }
}

@media (min-width: 480px) {
  .atmospheric-hero-card {
    padding: 24px 18px;
    border-radius: 28px;
  }
}

@media (min-width: 768px) {
  .atmospheric-hero-card {
    padding: 36px 32px;
    border-radius: var(--radius-hero);
  }
}

@media (min-width: 1200px) {
  .atmospheric-hero-card {
    padding: 48px 44px;
  }
}

:root[data-theme="dark"] .atmospheric-hero-card {
  background: linear-gradient(135deg, #161B22 0%, #1A2332 60%, #151D29 100%);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 16px 48px -8px rgba(0, 0, 0, 0.4);
}

.hero-inner-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: center;
  width: 100%;
}

.hero-left-content {
  min-width: 0;
  max-width: 100%;
  width: 100%;
}

@media (min-width: 1024px) {
  .hero-inner-grid {
    grid-template-columns: 1.35fr 0.85fr;
    gap: 32px;
  }
}

@media (min-width: 1280px) {
  .hero-inner-grid {
    grid-template-columns: 1.4fr 0.8fr;
    gap: 40px;
  }
}

/* Badge Pill */
.hero-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--blue-deep);
  box-shadow: 0 2px 8px rgba(40, 120, 200, 0.08);
  margin-bottom: 12px;
  max-width: 100%;
}

@media (min-width: 480px) {
  .hero-badge-pill {
    font-size: 12.5px;
    padding: 6px 14px;
    margin-bottom: 16px;
  }
}

:root[data-theme="dark"] .hero-badge-pill {
  background: rgba(56, 139, 253, 0.15);
  border-color: rgba(56, 139, 253, 0.3);
  color: #58A6FF;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  flex-shrink: 0;
}

/* Responsive Headings */
.hero-heading {
  font-family: var(--font-sans);
  font-size: clamp(22px, 5.8vw, 48px);
  font-weight: 800;
  letter-spacing: -0.02em;
  word-spacing: 0.05em;
  line-height: 1.18;
  color: var(--text-primary);
  margin: 0 0 8px;
  word-break: normal;
  overflow-wrap: break-word;
}

.heading-gradient {
  color: var(--blue-primary);
  background: linear-gradient(135deg, #2878C8 0%, #175B9B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subheading {
  font-size: clamp(12.5px, 3.3vw, 15px);
  color: var(--text-secondary);
  line-height: 1.48;
  margin: 0 0 16px;
  max-width: 540px;
  width: 100%;
  word-break: normal;
  overflow-wrap: break-word;
}

@media (min-width: 768px) {
  .hero-subheading {
    margin-bottom: 22px;
  }
}

/* Mode Switcher Tabs (Scrollable on narrow mobile screens) */
.mode-tabs-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 4px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(255, 255, 255, 0.9);
  margin-bottom: 14px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  max-width: 100%;
  width: 100%;
  box-sizing: border-box;
}

.mode-tabs-wrapper::-webkit-scrollbar {
  display: none;
}

:root[data-theme="dark"] .mode-tabs-wrapper {
  background: rgba(22, 27, 34, 0.7);
  border-color: rgba(255, 255, 255, 0.1);
}

.tab-label-desktop {
  display: inline;
}

.tab-label-mobile {
  display: none;
}

.mode-pill-tab {
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  padding: 7px 12px;
  border-radius: var(--radius-full);
  transition: all 0.2s var(--ease);
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  flex-shrink: 0;
  min-height: 36px;
}

@media (max-width: 480px) {
  .tab-label-desktop {
    display: none;
  }
  .tab-label-mobile {
    display: inline;
  }
  .mode-pill-tab {
    padding: 7px 11px;
    font-size: 12px;
    gap: 4px;
  }
}

@media (min-width: 481px) {
  .mode-pill-tab {
    font-size: 13px;
    padding: 8px 16px;
  }
}

.mode-pill-tab:hover {
  color: var(--text-primary);
}

.mode-pill-tab.active {
  background: #17191D;
  color: #FFFFFF;
  box-shadow: 0 3px 10px rgba(23, 25, 29, 0.18);
}

:root[data-theme="dark"] .mode-pill-tab.active {
  background: var(--blue-primary);
}

.ai-tab-special {
  position: relative;
}

.tab-svg-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.ai-chip-pill {
  font-size: 9.5px;
  font-weight: 700;
  background: rgba(40, 120, 200, 0.18);
  color: var(--blue-primary);
  padding: 2px 6px;
  border-radius: var(--radius-full);
}

.mode-pill-tab.active .ai-chip-pill {
  background: rgba(255, 255, 255, 0.22);
  color: #ffffff;
}

/* Floating White Search Console */
.floating-search-console {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 36px rgba(40, 120, 200, 0.09), 0 2px 10px rgba(0, 0, 0, 0.03);
  padding: 12px;
  transition: all 0.25s var(--ease);
}

@media (min-width: 480px) {
  .floating-search-console {
    padding: 16px;
  }
}

@media (min-width: 768px) {
  .floating-search-console {
    padding: 18px 22px;
  }
}

:root[data-theme="dark"] .floating-search-console {
  background: rgba(22, 27, 34, 0.92);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4);
}

/* AI Mode Console */
.ai-console-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-input-wrapper {
  display: flex;
  align-items: center;
  background: var(--surface-subtle);
  border: 1.5px solid var(--border-subtle);
  border-radius: var(--radius-full);
  padding: 5px 6px 5px 16px;
  transition: all 0.2s var(--ease);
}

@media (max-width: 639px) {
  .ai-input-wrapper {
    flex-direction: column;
    align-items: stretch;
    border-radius: var(--radius-md);
    padding: 8px 10px;
    gap: 8px;
  }
}

.ai-input-wrapper:focus-within {
  border-color: var(--blue-primary);
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(40, 120, 200, 0.15);
}

:root[data-theme="dark"] .ai-input-wrapper:focus-within {
  background: #1C222B;
}

.ai-input-prefix {
  display: flex;
  align-items: center;
  color: var(--blue-primary);
  margin-right: 10px;
}

@media (max-width: 639px) {
  .ai-input-prefix {
    display: none;
  }
}

.sparkle-icon {
  width: 20px;
  height: 20px;
}

.ai-search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
  min-width: 0;
  min-height: 40px;
}

.ai-search-input::placeholder {
  color: var(--text-secondary);
}

.btn-iconly-search {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  height: 44px;
  padding: 0 20px;
  border-radius: var(--radius-full);
  background: #17191D;
  color: #FFFFFF;
  font-size: 13.5px;
  font-weight: 700;
  border: none;
  white-space: nowrap;
  box-shadow: 0 4px 14px rgba(23, 25, 29, 0.2);
  transition: all 0.2s var(--ease);
}

@media (max-width: 639px) {
  .btn-iconly-search {
    width: 100%;
  }
}

:root[data-theme="dark"] .btn-iconly-search {
  background: var(--blue-primary);
}

.btn-iconly-search:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn-iconly-search:active {
  transform: scale(0.98);
}

.btn-iconly-search:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.arrow-icon {
  width: 15px;
  height: 15px;
}

/* AI Prompts Row (Horizontal Touch Scroll) */
.ai-prompts-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 2px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.prompts-title {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.prompts-scroll {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
}

.prompts-scroll::-webkit-scrollbar {
  display: none;
}

.prompt-pill {
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-secondary);
  background: rgba(40, 120, 200, 0.08);
  border: 1px solid rgba(40, 120, 200, 0.12);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  white-space: nowrap;
  transition: all 0.15s ease;
  min-height: 30px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.prompt-svg {
  width: 13px;
  height: 13px;
  color: var(--blue-primary);
  flex-shrink: 0;
}

.prompt-pill:hover {
  background: rgba(40, 120, 200, 0.15);
  color: var(--blue-deep);
}

/* Standard Console Grid */
.console-fields-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

@media (max-width: 639px) {
  .console-fields-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px 8px;
  }
}

@media (min-width: 640px) {
  .console-fields-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (min-width: 1024px) {
  .console-fields-row {
    grid-template-columns: 1.15fr 1fr 1.25fr 1.1fr auto;
    gap: 8px;
    align-items: flex-end;
  }
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.field-lbl {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-secondary);
  padding-left: 2px;
}

.field-select-wrap {
  position: relative;
  min-width: 0;
}

.iconly-select {
  width: 100%;
  min-width: 0;
  min-height: 44px;
  height: 44px;
  padding: 0 24px 0 10px;
  background-color: var(--surface-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  outline: none;
  transition: all 0.18s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 12px;
  cursor: pointer;
}

@media (max-width: 639px) {
  .iconly-select {
    min-height: 42px;
    height: 42px;
    padding: 0 22px 0 9px;
    font-size: 12.5px;
    border-radius: 10px;
    background-position: right 6px center;
  }
}

.iconly-select:focus {
  border-color: var(--blue-primary);
  background: #FFFFFF;
}

.field-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 639px) {
  .field-actions {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: 46px 1fr;
    gap: 8px;
    width: 100%;
    margin-top: 4px;
  }
}

.btn-iconly-filter {
  min-width: 44px;
  min-height: 44px;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  background: var(--surface);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s ease;
  flex-shrink: 0;
}

@media (max-width: 639px) {
  .btn-iconly-filter {
    width: 46px;
    height: 46px;
  }
}

.btn-iconly-filter:hover {
  border-color: var(--blue-primary);
  color: var(--blue-primary);
}

.filter-icon {
  width: 18px;
  height: 18px;
}

.btn-iconly-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 44px;
  height: 44px;
  padding: 0 22px;
  border-radius: var(--radius-full);
  background: #17191D;
  color: #FFFFFF;
  font-size: 13.5px;
  font-weight: 700;
  border: none;
  white-space: nowrap;
  box-shadow: 0 4px 14px rgba(23, 25, 29, 0.18);
  transition: all 0.2s var(--ease);
}

@media (max-width: 639px) {
  .btn-iconly-submit {
    width: 100%;
    height: 46px;
  }
}

:root[data-theme="dark"] .btn-iconly-submit {
  background: var(--blue-primary);
}

.btn-iconly-submit:hover {
  transform: translateY(-1px);
}

.btn-iconly-submit:active {
  transform: scale(0.98);
}

.search-icon {
  width: 16px;
  height: 16px;
}

/* Active Status Pill */
.ai-active-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(40, 120, 200, 0.1);
  border: 1px solid rgba(40, 120, 200, 0.2);
  border-radius: var(--radius-full);
  padding: 8px 16px;
  margin-top: 14px;
  font-size: 12.5px;
  gap: 8px;
}

@media (max-width: 639px) {
  .ai-active-status {
    flex-direction: column;
    align-items: flex-start;
    border-radius: var(--radius-sm);
    padding: 10px 14px;
  }
  .ai-reset-btn {
    align-self: flex-end;
  }
}

.ai-status-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.ai-badge-live {
  background: var(--blue-primary);
  color: #ffffff;
  font-size: 10.5px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.ai-chip-svg {
  width: 13px;
  height: 13px;
}

.ai-query-text {
  color: var(--blue-deep);
  font-weight: 600;
  word-break: break-word;
}

.ai-reset-btn {
  color: var(--blue-deep);
  font-size: 12px;
  font-weight: 700;
  border: none;
  background: none;
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.reset-svg {
  width: 13px;
  height: 13px;
}

/* Right: Visual Showcase (Desktop Only) */
.hero-right-visual {
  display: none;
}

@media (min-width: 1024px) {
  .hero-right-visual {
    display: block;
    position: relative;
  }
}

.visual-stack {
  position: relative;
}

.visual-photo-card {
  position: relative;
  border-radius: var(--radius-card);
  overflow: hidden;
  box-shadow: 0 20px 48px -12px rgba(40, 120, 200, 0.25);
  border: 3px solid rgba(255, 255, 255, 0.95);
  aspect-ratio: 4/3;
}

.visual-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.visual-photo-glass-bottom {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: var(--radius-inner);
  padding: 10px 18px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

:root[data-theme="dark"] .visual-photo-glass-bottom {
  background: rgba(22, 27, 34, 0.85);
}

.spec-col {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spec-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.spec-val {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.spec-sep {
  width: 1px;
  height: 20px;
  background: var(--border-subtle);
}

/* Floating Circular Score Badge */
.floating-score-badge {
  position: absolute;
  top: -16px;
  right: -16px;
  background: #FFFFFF;
  border-radius: var(--radius-full);
  padding: 6px 14px 6px 6px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 10px 28px rgba(40, 120, 200, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.9);
}

:root[data-theme="dark"] .floating-score-badge {
  background: #1C222B;
}

.score-ring {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 3px solid #10B981;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13.5px;
  font-weight: 800;
  color: var(--text-primary);
}

.score-meta {
  display: flex;
  flex-direction: column;
}

.score-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
}

.score-sub {
  font-size: 10.5px;
  color: var(--text-secondary);
}
</style>
