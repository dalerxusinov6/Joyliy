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

const searchMode = ref<'ai' | 'standard'>('ai')
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
  <section class="editorial-hero">
    <div class="wrap">
      <div class="hero-grid">
        <!-- Left: Search & Headline -->
        <div class="hero-content">
          <!-- Trust Pill -->
          <div class="hero-badge">
            <svg class="badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <span>Toshkentda maklersiz to‘g‘ridan-to‘g‘ri ijara</span>
          </div>

          <h1 class="hero-title">
            Yangi uyingizni<br />
            <span class="hero-title-accent">vositachisiz</span> toping.
          </h1>

          <p class="hero-subtitle">
            To‘g‘ridan-to‘g‘ri xonadon egalaridan tekshirilgan e’lonlar. 0% rieltorlik komissiyasi va shaffof narxlar.
          </p>

          <!-- Mode Tabs -->
          <div class="search-mode-tabs">
            <button
              type="button"
              class="mode-tab-btn"
              :class="{ active: searchMode === 'ai' }"
              @click="searchMode = 'ai'"
            >
              <span class="tab-icon">🤖</span>
              <span>AI Aqlli Qidiruv</span>
              <span class="mode-badge">Tavsiya</span>
            </button>
            <button
              type="button"
              class="mode-tab-btn"
              :class="{ active: searchMode === 'standard' }"
              @click="searchMode = 'standard'"
            >
              <span class="tab-icon">🔍</span>
              <span>Filtrlar bo‘yicha</span>
            </button>
          </div>

          <!-- Search Console Card -->
          <div class="search-card">
            <!-- AI Mode View -->
            <div v-if="searchMode === 'ai'" class="ai-search-console">
              <div class="ai-input-wrap">
                <textarea
                  v-model="aiInput"
                  rows="2"
                  placeholder="Kvartirani o‘z so‘zlaringiz bilan tasvirlang... (masalan: Chilonzorda metro yaqinida 4 mln gacha 2 xonali kvartira oila uchun)"
                  class="ai-textarea"
                  @keydown.enter.prevent="handleAiSearch"
                ></textarea>
              </div>

              <div class="ai-console-footer">
                <div class="ai-chips">
                  <span class="ai-chip-label">Misol:</span>
                  <button type="button" class="ai-chip" @click="applyAiPrompt('Chilonzorda metro yaqinida 4 mln gacha 2 xonali')">
                    🚇 Chilonzor metro
                  </button>
                  <button type="button" class="ai-chip" @click="applyAiPrompt('Yunusobodda maklersiz oila uchun')">
                    👨‍👩‍👧 Yunusobod oila
                  </button>
                  <button type="button" class="ai-chip" @click="applyAiPrompt('Mirobodda 3 xonali jihozlangan')">
                    ✨ Mirobod
                  </button>
                </div>

                <button
                  type="button"
                  class="btn-search-submit ai-btn"
                  :disabled="isAiSearching || !aiInput.trim()"
                  @click="handleAiSearch"
                >
                  <svg v-if="!isAiSearching" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                  <span>{{ isAiSearching ? 'Tahlil qilinmoqda...' : 'AI bilan topish 🚀' }}</span>
                </button>
              </div>
            </div>

            <!-- Standard Mode View -->
            <template v-else>
              <div class="search-fields">
                <!-- District -->
                <div class="field-box field-district">
                  <div class="field-header">
                    <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                      <circle cx="12" cy="10" r="3" />
                    </svg>
                    <label class="field-title">Tuman</label>
                  </div>
                  <select v-model="filterDistrict" class="field-select">
                    <option value="">Barcha tumanlar</option>
                    <option v-for="d in availableDistricts" :key="d" :value="d">{{ d }}</option>
                  </select>
                </div>

                <!-- Rooms -->
                <div class="field-box">
                  <div class="field-header">
                    <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                      <polyline points="9 22 9 12 15 12 15 22" />
                    </svg>
                    <label class="field-title">Xonalar</label>
                  </div>
                  <select v-model="filterRooms" class="field-select">
                    <option value="">Istalgan</option>
                    <option value="1">1 xonali</option>
                    <option value="2">2 xonali</option>
                    <option value="3">3 xonali</option>
                    <option value="4">4+ xonali</option>
                  </select>
                </div>

                <!-- Budget -->
                <div class="field-box">
                  <div class="field-header">
                    <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <rect x="2" y="5" width="20" height="14" rx="2" />
                      <line x1="2" y1="10" x2="22" y2="10" />
                    </svg>
                    <label class="field-title">Maksimal narx</label>
                  </div>
                  <select v-model="filterMaxPrice" class="field-select">
                    <option value="">Istalgan narx</option>
                    <option value="3000000">3 000 000 so‘m</option>
                    <option value="4000000">4 000 000 so‘m</option>
                    <option value="6000000">6 000 000 so‘m</option>
                    <option value="8000000">8 000 000 so‘m</option>
                    <option value="12000000">12 000 000 so‘m</option>
                  </select>
                </div>

                <!-- Audience -->
                <div class="field-box">
                  <div class="field-header">
                    <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                    <label class="field-title">Kim uchun</label>
                  </div>
                  <select v-model="filterAudience" class="field-select">
                    <option value="all">Barchasi</option>
                    <option value="family">Oila uchun</option>
                    <option value="female">Qizlar uchun</option>
                    <option value="male">Yigitlar uchun</option>
                  </select>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="search-actions">
                <button
                  type="button"
                  class="btn-filters-toggle"
                  @click="$emit('openFilters')"
                  title="Barcha filtrlarni ochish"
                >
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
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

                <button type="button" class="btn-search-submit" @click="onSearch">
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                  <span>Qidirish</span>
                </button>
              </div>
            </template>
          </div>

          <!-- Active AI Indicator Banner -->
          <div v-if="aiSearchActive" class="ai-active-indicator">
            <div class="ind-left">
              <span class="ind-badge">🎯 AI Match</span>
              <span class="ind-query">«{{ aiSearchQuery }}»</span>
            </div>
            <button type="button" class="ind-reset" @click="resetAiMatch">
              Barcha e’lonlarga qaytish ✕
            </button>
          </div>

          <!-- Quick Filter Chips -->
          <div class="quick-chips">
            <span class="chips-label">Ommabop:</span>
            <div class="chips-list">
              <button type="button" class="chip-btn" @click="applyQuick('district', 'Chilonzor')">Chilonzor</button>
              <button type="button" class="chip-btn" @click="applyQuick('district', 'Yunusobod')">Yunusobod</button>
              <button type="button" class="chip-btn" @click="applyQuick('district', 'Mirzo Ulug‘bek')">Mirzo Ulug‘bek</button>
              <button type="button" class="chip-btn" @click="applyQuick('rooms', '1')">1 xonali</button>
              <button type="button" class="chip-btn" @click="applyQuick('audience', 'family')">Oila uchun</button>
            </div>
          </div>
        </div>

        <!-- Right: Modern Editorial Photography Showcase -->
        <div class="hero-visual">
          <div class="visual-card">
            <img
              src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
              alt="Toshkent zamonaviy xonadon interyeri"
              class="visual-photo"
              loading="eager"
            />
            <div class="visual-gradient-overlay"></div>

            <!-- Floating Pill 1: Verified Owner -->
            <div class="floating-badge badge-top">
              <div class="badge-icon-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="check-icon">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              <div class="badge-texts">
                <span class="badge-h">100% Egasidan</span>
                <span class="badge-s">0% vositachilik to‘lovi</span>
              </div>
            </div>

            <!-- Floating Card 2: Featured Apartment Snapshot -->
            <div class="floating-listing-card">
              <div class="fl-header">
                <span class="fl-district">Mirzo Ulug‘bek tumani</span>
                <span class="fl-status">
                  <span class="fl-pulse"></span>
                  Bo‘sh
                </span>
              </div>
              <div class="fl-price">5 500 000 so‘m<span>/oy</span></div>
              <div class="fl-meta">
                <span>3 xonali</span>
                <span class="dot">·</span>
                <span>85 m²</span>
                <span class="dot">·</span>
                <span>Metroga 4 daqiqa</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.editorial-hero {
  padding: 56px 0 72px;
  position: relative;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 48px;
  align-items: center;
}

@media (min-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1.15fr 0.85fr;
    gap: 56px;
  }
}

/* Left Content */
.hero-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  align-self: flex-start;
  padding: 6px 14px;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  box-shadow: var(--sh-sm);
}

.badge-icon {
  width: 15px;
  height: 15px;
  color: var(--terracotta);
}

.hero-title {
  font-family: var(--font-sans);
  font-size: clamp(34px, 4.4vw, 54px);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.035em;
  color: var(--ink);
  margin: 0;
}

.hero-title-accent {
  color: var(--terracotta);
}

.hero-subtitle {
  font-size: 17px;
  line-height: 1.6;
  color: var(--muted);
  max-width: 540px;
  margin: 0;
}

/* Search Card */
.search-card {
  margin-top: 8px;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 10px 30px -10px rgba(32, 38, 32, 0.08);
}

.search-fields {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 560px) {
  .field-district {
    grid-column: span 2;
  }
}

@media (min-width: 900px) {
  .search-fields {
    grid-template-columns: repeat(4, 1fr);
  }
}

.field-box {
  background: var(--bg);
  border: 1px solid var(--sand);
  border-radius: 12px;
  padding: 12px 14px;
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  transition: all 0.18s ease;
}

.field-box:focus-within {
  border-color: var(--terracotta);
  background: var(--surf);
}

.field-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.f-icon {
  width: 15px;
  height: 15px;
  color: var(--terracotta);
  flex-shrink: 0;
}

.field-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
}

.field-select {
  width: 100%;
  border: none;
  background: transparent;
  padding: 3px 0 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  outline: none;
  cursor: pointer;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.btn-filters-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  height: 50px;
  background: var(--bg);
  border: 1px solid var(--sand);
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  transition: all 0.18s var(--ease);
}

.btn-filters-toggle:hover {
  border-color: var(--ink);
}

.btn-search-submit {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 50px;
  background: var(--terracotta);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.01em;
  transition: all 0.18s var(--ease);
  box-shadow: 0 4px 14px rgba(188, 104, 75, 0.28);
}

.btn-search-submit:hover {
  background: var(--terracotta-hover);
  transform: translateY(-1px);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* Quick Chips */
.quick-chips {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 6px;
}

.chips-label {
  font-size: 13.5px;
  color: var(--muted);
  font-weight: 600;
}

.chips-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-btn {
  padding: 8px 16px;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: 999px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  min-height: 38px;
  transition: all 0.15s;
}

.chip-btn:hover {
  border-color: var(--terracotta);
  color: var(--terracotta);
}

/* Right Visual */
.hero-visual {
  position: relative;
}

.visual-card {
  position: relative;
  width: 100%;
  height: 460px;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid var(--sand);
  box-shadow: 0 20px 40px -15px rgba(32, 38, 32, 0.12);
}

.visual-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s var(--ease);
}

.visual-card:hover .visual-photo {
  transform: scale(1.025);
}

.visual-gradient-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(32, 38, 32, 0.1) 0%, rgba(32, 38, 32, 0.45) 100%);
  pointer-events: none;
}

/* Floating Elements */
.floating-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 2;
}

.badge-icon-wrap {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #10b981;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.check-icon {
  width: 16px;
  height: 16px;
}

.badge-texts {
  display: flex;
  flex-direction: column;
}

.badge-h {
  font-size: 13px;
  font-weight: 700;
  color: #17231d;
  line-height: 1.2;
}

.badge-s {
  font-size: 11px;
  color: #64748b;
  line-height: 1.2;
}

.floating-listing-card {
  position: absolute;
  bottom: 20px;
  right: 20px;
  left: 20px;
  max-width: 340px;
  margin-left: auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 2;
}

.fl-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.fl-district {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.fl-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  color: #059669;
  background: #ecfdf5;
  padding: 2px 8px;
  border-radius: 999px;
}

.fl-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.fl-price {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.fl-price span {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}

.fl-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
}

.dot {
  color: #cbd5e1;
}

@media (max-width: 640px) {
  .visual-card {
    height: 320px;
  }
  .floating-listing-card {
    max-width: 100%;
    left: 12px;
    right: 12px;
    bottom: 12px;
  }
}

/* AI Mode Tabs & Search Console */
.search-mode-tabs {
  display: inline-flex;
  gap: 6px;
  background: var(--sand-light, #f4f0eb);
  padding: 4px;
  border-radius: 12px;
  align-self: flex-start;
  margin-bottom: -10px;
}

.mode-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  border: none;
  background: transparent;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-light, #72746b);
  cursor: pointer;
  transition: all 0.2s;
}

.mode-tab-btn.active {
  background: #ffffff;
  color: #BC684B;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.mode-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  background: #BC684B;
  color: #ffffff;
  padding: 1px 6px;
  border-radius: 10px;
}

.ai-search-console {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-input-wrap {
  width: 100%;
}

.ai-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 10px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.45;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
  background: #ffffff;
}

.ai-textarea:focus {
  border-color: #BC684B;
}

.ai-console-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.ai-chips {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.ai-chip-label {
  font-size: 12px;
  color: #888;
}

.ai-chip {
  padding: 4px 10px;
  border-radius: 16px;
  border: 1px solid var(--sand, #ebe5db);
  background: var(--sand-light, #f8f6f2);
  font-size: 11.5px;
  cursor: pointer;
  color: var(--ink, #1c1c1b);
  transition: all 0.15s;
}

.ai-chip:hover {
  background: #BC684B;
  color: #ffffff;
  border-color: #BC684B;
}

.ai-btn {
  margin-left: auto;
  white-space: nowrap;
}

.ai-active-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #fdf5f2;
  border: 1px solid #ffd4b8;
  border-radius: 10px;
  font-size: 13px;
  margin-top: -6px;
}

.ind-badge {
  font-weight: 700;
  color: #BC684B;
  margin-right: 8px;
}

.ind-query {
  font-style: italic;
  color: #333;
}

.ind-reset {
  background: none;
  border: none;
  color: #BC684B;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
}
</style>
