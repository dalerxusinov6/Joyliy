<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import type { ListingItem } from '~/composables/useListings'

const props = defineProps<{
  listing: ListingItem | null
}>()

const emit = defineEmits(['close', 'toast'])
const { t } = useI18n()

const activePhotoIndex = ref(0)

watch(
  () => props.listing,
  () => {
    activePhotoIndex.value = 0
  }
)

const formatPrice = (val: number) => {
  return val.toLocaleString('ru-RU').replace(/\u00a0/g, ' ') + ' so‘m'
}

const onReport = () => {
  emit('toast', t('report_received'))
}

const sourceViewLabel = computed(() => {
  return t('view_on_olx')
})
</script>

<template>
  <div v-if="listing" class="ov show" @click.self="$emit('close')">
    <div class="sheet exhibition-sheet">
      <!-- Top Exhibition Header -->
      <div class="top exhibition-header">
        <div class="exhibition-meta">
          <span class="exhibit-tag">XONADON HUJJATI</span>
          <span class="exhibit-sep">/</span>
          <span class="exhibit-title">{{ listing.rooms }} xonali · {{ listing.district }}</span>
        </div>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <div class="bd exhibition-body">
        <!-- Main Photography Gallery Carousel -->
        <div class="exhibition-gallery">
          <div v-if="listing.image_urls && listing.image_urls.length" class="hero-photo-wrapper">
            <img
              :src="listing.image_urls[activePhotoIndex] || listing.image_urls[0]"
              :alt="listing.title"
              class="hero-photo"
            />
            <div class="photo-indicator">
              {{ activePhotoIndex + 1 }} / {{ listing.image_urls.length }}
            </div>
          </div>
          <div v-else class="hero-photo-placeholder">
            <span>Fotosurat mavjud emas</span>
          </div>

          <!-- Thumbnails Strip -->
          <div v-if="listing.image_urls && listing.image_urls.length > 1" class="gallery-thumbs">
            <button
              v-for="(img, idx) in listing.image_urls"
              :key="idx"
              type="button"
              class="gallery-thumb-btn"
              :class="{ active: activePhotoIndex === idx }"
              @click="activePhotoIndex = idx"
            >
              <img :src="img" :alt="`Rasm ${idx + 1}`" />
            </button>
          </div>
        </div>

        <!-- Price & Trust Masthead -->
        <div class="exhibition-price-bar">
          <div class="price-cluster">
            <span class="large-price">{{ formatPrice(listing.price_uzs) }}</span>
            <span class="period-label">{{ t('per_month') }}</span>
          </div>
          <div v-if="listing.is_owner" class="terracotta-status-badge">
            <span class="status-badge-dot"></span>
            <span>100% Maklersiz · Egasidan</span>
          </div>
        </div>

        <!-- Title -->
        <h2 class="exhibition-listing-title">
          {{ listing.title }}
        </h2>

        <!-- Architectural Specifications Grid -->
        <div class="exhibition-specs-grid">
          <div class="spec-cell">
            <span class="cell-k">Umumiy Maydon</span>
            <span class="cell-v">{{ listing.area }} m²</span>
          </div>
          <div class="spec-cell">
            <span class="cell-k">Xonalar Soni</span>
            <span class="cell-v">{{ listing.rooms }} xona</span>
          </div>
          <div class="spec-cell">
            <span class="cell-k">Joylashgan Qavat</span>
            <span class="cell-v">{{ listing.floor || '3/9' }}</span>
          </div>
          <div class="spec-cell">
            <span class="cell-k">Metro Masofasi</span>
            <span class="cell-v">{{ listing.metro_minutes || 5 }} daqiqa</span>
          </div>
        </div>

        <!-- Audience Tag Notice -->
        <div v-if="listing.target_audience && listing.target_audience !== 'any'" class="target-audience-card">
          <div class="target-left">
            <span class="target-icon">
              <svg v-if="listing.target_audience === 'family'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="detail-svg">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              <svg v-else-if="listing.target_audience === 'female'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="detail-svg">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              <svg v-else-if="listing.target_audience === 'male'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="detail-svg">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </span>
          </div>
          <div class="target-right">
            <div class="target-headline">
              <template v-if="listing.target_audience === 'family'">Faqat oila uchun mo‘ljallangan</template>
              <template v-else-if="listing.target_audience === 'female'">Qizlar / Ayollar uchun mo‘ljallangan</template>
              <template v-else-if="listing.target_audience === 'male'">Yigitlar / Talabalar uchun mo‘ljallangan</template>
            </div>
            <div class="target-hint">E’lon matnida ijarachilar toifasi egasi tomonidan alohida belgilangan</div>
          </div>
        </div>

        <!-- Description Text -->
        <div v-if="listing.description" class="exhibition-description-block">
          <h4 class="description-heading">Tavsif va shartlar</h4>
          <p class="description-body">
            {{ listing.description }}
          </p>
        </div>

        <!-- Provenance & Disclaimer -->
        <div class="provenance-block">
          <div class="prov-top">
            <span class="prov-label">Manba: {{ listing.source_attribution || 'OLX.uz' }}</span>
          </div>
          <p class="prov-text">
            {{ listing.disclaimer || 'Ushbu e’lon ommaviy platformadan to‘g‘ridan-to‘g‘ri olingan. To‘lovdan avval xonadonni o‘z ko‘zingiz bilan ko‘rib, hujjatlarni tekshirib olishingizni tavsiya qilamiz.' }}
          </p>
        </div>

        <!-- Report Issue -->
        <div class="report-action-wrap">
          <button class="btn report-action-btn" type="button" @click="onReport">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
              <line x1="4" y1="22" x2="4" y2="15" />
            </svg>
            <span>Noto‘g‘ri ma’lumot haqida xabar berish</span>
          </button>
        </div>
      </div>

      <!-- Action Footer Bar -->
      <div class="cbar exhibition-cbar">
        <a
          v-if="listing.contact_phone"
          class="btn p call-btn"
          :href="`tel:${listing.contact_phone}`"
        >
          <svg class="btn-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
          </svg>
          <span>Qo‘ng‘iroq qilish</span>
        </a>
        <a
          v-if="listing.contact_telegram"
          class="btn tg-btn"
          :href="`https://t.me/${listing.contact_telegram.replace('@', '')}`"
          target="_blank"
          rel="noopener"
        >
          <svg class="btn-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
          </svg>
          <span>Telegram orqali yozish</span>
        </a>
        <a
          v-if="listing.canonical_url"
          class="btn source-btn"
          :class="{ p: !listing.contact_phone && !listing.contact_telegram }"
          :href="listing.canonical_url"
          target="_blank"
          rel="noopener"
        >
          <span>{{ sourceViewLabel }}</span>
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
        </a>
        <a
          v-if="!listing.contact_telegram && !listing.contact_phone"
          class="btn"
          href="https://t.me/joyliy_bot"
          target="_blank"
          rel="noopener"
        >
          <svg class="btn-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
          </svg>
          <span>Telegram Bot</span>
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.exhibition-sheet {
  max-width: 720px;
}

.exhibition-header {
  padding: 18px 24px;
}

.exhibition-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.exhibit-tag {
  color: var(--terracotta);
  font-weight: 700;
  letter-spacing: 0.1em;
}

.exhibit-sep {
  color: var(--sand);
}

.exhibit-title {
  color: var(--ink);
  font-weight: 600;
}

.exhibition-body {
  padding: 24px;
}

.exhibition-gallery {
  margin-bottom: 24px;
}

.hero-photo-wrapper {
  position: relative;
  aspect-ratio: 16/10;
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  overflow: hidden;
  background: var(--sand-light);
}

.hero-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-indicator {
  position: absolute;
  right: 14px;
  bottom: 14px;
  background: rgba(32, 38, 32, 0.85);
  color: #FFFFFF;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
}

.hero-photo-placeholder {
  aspect-ratio: 16/10;
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  background: var(--sand-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--muted);
}

.gallery-thumbs {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}

.gallery-thumbs::-webkit-scrollbar {
  display: none;
}

.gallery-thumb-btn {
  width: 64px;
  height: 48px;
  border-radius: var(--radius-xs);
  overflow: hidden;
  border: 1px solid var(--sand);
  flex: none;
  cursor: pointer;
  padding: 0;
  transition: all 0.18s ease;
}

.gallery-thumb-btn.active {
  border-color: var(--terracotta);
  box-shadow: 0 0 0 2px var(--terracotta);
}

.gallery-thumb-btn img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.exhibition-price-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 12px;
}

.price-cluster {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.large-price {
  font-family: var(--font-sans);
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--ink);
  font-feature-settings: "tnum";
}

.period-label {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--muted);
}

.terracotta-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--terracotta-subtle);
  color: var(--terracotta);
  border: 1px solid var(--terracotta);
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  font-weight: 700;
}

.status-badge-dot {
  width: 6px;
  height: 6px;
  background: var(--terracotta);
  border-radius: 50%;
}

.exhibition-listing-title {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 500;
  line-height: 1.35;
  color: var(--ink);
  margin: 0 0 20px;
}

.exhibition-specs-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--sand);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  overflow: hidden;
  margin-bottom: 24px;
}

.spec-cell {
  background: var(--surf);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
}

.cell-k {
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}

.cell-v {
  font-size: 15.5px;
  font-weight: 700;
  color: var(--ink);
  margin-top: 2px;
}

.target-audience-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  margin-bottom: 24px;
}

.target-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--terracotta-subtle);
  color: var(--terracotta);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-svg {
  width: 20px;
  height: 20px;
}

.btn-action-icon {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
}

.target-headline {
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
}

.target-hint {
  font-size: 12px;
  color: var(--muted);
}

.exhibition-description-block {
  margin-bottom: 24px;
}

.description-body {
  white-space: pre-line;
  font-size: 14.5px;
  line-height: 1.7;
  color: var(--ink);
  margin: 8px 0 0;
}

.provenance-block {
  background: var(--sand-light);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  padding: 14px 18px;
  margin-bottom: 24px;
}

.prov-top {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.prov-label {
  color: var(--muted);
}

.prov-source {
  color: var(--terracotta);
  font-weight: 700;
}

.prov-text {
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
}

.report-action-btn {
  font-size: 12px;
  color: var(--muted);
}

.report-action-btn:hover {
  color: var(--terracotta);
}

.exhibition-cbar {
  display: flex;
  gap: 10px;
}

.call-btn {
  flex: 1.2;
}

.tg-btn {
  flex: 1;
}

.source-btn {
  flex: 1;
}

@media (max-width: 640px) {
  .exhibition-specs-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .exhibition-cbar {
    flex-direction: column;
  }
}
</style>
