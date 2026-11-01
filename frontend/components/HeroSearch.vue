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
  availableDistricts,
  aiSearchQuery,
  isAiSearching,
  aiSearchActive,
  runAiMatch,
  resetAiMatch,
} = useListings()

const searchMode = ref<'rent' | 'buy' | 'ai'>('rent')
const aiInput = ref('')

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
                @click="searchMode = 'rent'"
              >
                Ijaraga olish
              </button>
              <button
                type="button"
                role="tab"
                class="mode-pill-tab"
                :class="{ active: searchMode === 'buy' }"
                @click="searchMode = 'buy'"
              >
                Sotib olish
              </button>
              <button
                type="button"
                role="tab"
                class="mode-pill-tab ai-tab-special"
                :class="{ active: searchMode === 'ai' }"
                @click="searchMode = 'ai'"
              >
                <span class="ai-sparkle">✨</span>
                <span>AI Aqlli Qidiruv</span>
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
                      🚇 Chilonzor metro 4 mln
                    </button>
                    <button type="button" class="prompt-pill" @click="applyAiPrompt('Yunusobodda maklersiz oila uchun')">
                      👨‍👩‍👧 Yunusobod oila
                    </button>
                    <button type="button" class="prompt-pill" @click="applyAiPrompt('Mirobodda 3 xonali jihozlangan')">
                      ✨ Mirobod jihozlangan
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
                        <option value="">Barcha tumanlar</option>
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

                  <!-- Price -->
                  <div class="field-item">
                    <label class="field-lbl">Maksimal byudjet</label>
                    <div class="field-select-wrap">
                      <select v-model="filterMaxPrice" class="iconly-select" aria-label="Maksimal byudjet">
                        <option value="">Istalgan narx</option>
                        <option value="3000000">3 000 000 so‘m</option>
                        <option value="4000000">4 000 000 so‘m</option>
                        <option value="6000000">6 000 000 so‘m</option>
                        <option value="8000000">8 000 000 so‘m</option>
                        <option value="12000000">12 000 000 so‘m</option>
                      </select>
                    </div>
                  </div>

                  <!-- Audience -->
                  <div class="field-item">
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
                <span class="ai-badge-live">🤖 Groq Qwen AI</span>
                <span class="ai-query-text">«{{ aiSearchQuery }}»</span>
              </div>
              <button type="button" class="ai-reset-btn" @click="resetAiMatch">
                Filtrni tozalash ✕
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

              <!-- Floating Pill Tags (Matching "Fair Price" & "Good Location" from Image 1) -->
              <div class="floating-pill-fair">
                <span class="pill-dot">🟢</span>
                <span>Fair Price / Adolatli narx</span>
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
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 16px 48px -8px rgba(40, 120, 200, 0.12), 0 4px 16px rgba(0, 0, 0, 0.02);
  padding: 20px 14px;
  position: relative;
  overflow: hidden;
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
  grid-template-columns: 1fr;
  gap: 28px;
  align-items: center;
}

@media (min-width: 1024px) {
  .hero-inner-grid {
    grid-template-columns: 1.15fr 0.85fr;
    gap: 44px;
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
  margin-bottom: 14px;
  max-width: 100%;
}

@media (min-width: 480px) {
  .hero-badge-pill {
    font-size: 12.5px;
    padding: 6px 14px;
    margin-bottom: 18px;
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
  font-size: clamp(23px, 6.5vw, 50px);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.16;
  color: var(--text-primary);
  margin: 0 0 10px;
  word-break: break-word;
}

.heading-gradient {
  color: var(--blue-primary);
  background: linear-gradient(135deg, #2878C8 0%, #175B9B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subheading {
  font-size: clamp(13px, 3.5vw, 16px);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 20px;
  max-width: 540px;
}

@media (min-width: 768px) {
  .hero-subheading {
    margin-bottom: 24px;
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
  margin-bottom: 16px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  max-width: 100%;
}

.mode-tabs-wrapper::-webkit-scrollbar {
  display: none;
}

:root[data-theme="dark"] .mode-tabs-wrapper {
  background: rgba(22, 27, 34, 0.7);
  border-color: rgba(255, 255, 255, 0.1);
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

@media (min-width: 375px) {
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

.ai-sparkle {
  font-size: 13px;
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

@media (min-width: 640px) {
  .console-fields-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (min-width: 1024px) {
  .console-fields-row {
    grid-template-columns: 1.1fr 1fr 1.2fr 1fr auto;
    align-items: flex-end;
  }
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-lbl {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-secondary);
  padding-left: 2px;
}

.field-select-wrap {
  position: relative;
}

.iconly-select {
  width: 100%;
  min-height: 44px;
  height: 44px;
  padding: 0 14px;
  background: var(--surface-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13.5px;
  font-weight: 600;
  outline: none;
  transition: all 0.18s ease;
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
  padding: 2px 8px;
  border-radius: var(--radius-full);
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

/* Floating Pill Tag */
.floating-pill-fair {
  position: absolute;
  bottom: -14px;
  left: 20px;
  background: #FEF3C7;
  color: #92400E;
  border: 1px solid #FDE68A;
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

.pill-dot {
  font-size: 10px;
}
</style>
