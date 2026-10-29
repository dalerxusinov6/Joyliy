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

const audienceBoxStyle = computed(() => {
  if (props.listing?.target_audience === 'family') {
    return 'background: #EEF6F2; color: #174D3A; border: 1px solid #B9F2D0;'
  } else if (props.listing?.target_audience === 'female') {
    return 'background: #FFF1F5; color: #9F1239; border: 1px solid #FECDD3;'
  } else if (props.listing?.target_audience === 'male') {
    return 'background: #F0F9FF; color: #0369A1; border: 1px solid #BAE6FD;'
  }
  return ''
})
</script>

<template>
  <div v-if="listing" class="ov show" @click.self="$emit('close')">
    <div class="sheet detail-sheet">
      <!-- Modal Header -->
      <div class="top detail-header">
        <div class="header-info">
          <span class="header-title">{{ listing.rooms }} {{ t('rooms_apartment') }}</span>
          <span class="header-district">📍 {{ listing.district }}</span>
        </div>
        <button class="ib close-btn" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="bd detail-body">
        <!-- Photo Gallery Carousel -->
        <div class="gallery-wrapper">
          <div v-if="listing.image_urls && listing.image_urls.length" class="main-photo-box">
            <img
              :src="listing.image_urls[activePhotoIndex] || listing.image_urls[0]"
              :alt="listing.title"
              class="main-photo"
            />
            <div class="photo-counter">
              {{ activePhotoIndex + 1 }} / {{ listing.image_urls.length }}
            </div>
          </div>
          <div v-else class="main-photo-placeholder">
            <svg class="i placeholder-icon" viewBox="0 0 24 24">
              <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="M21 15l-5-5L5 21" />
            </svg>
            <span>Fotosurat mavjud emas</span>
          </div>

          <!-- Thumbnails Row -->
          <div v-if="listing.image_urls && listing.image_urls.length > 1" class="thumb-strip">
            <button
              v-for="(img, idx) in listing.image_urls"
              :key="idx"
              type="button"
              class="thumb-btn"
              :class="{ active: activePhotoIndex === idx }"
              @click="activePhotoIndex = idx"
            >
              <img :src="img" :alt="`Thumbnail ${idx + 1}`" />
            </button>
          </div>
        </div>

        <!-- Price Banner -->
        <div class="detail-price-box">
          <div class="detail-price">
            {{ formatPrice(listing.price_uzs) }} <span class="price-period">{{ t('per_month') }}</span>
          </div>
          <div v-if="listing.is_owner" class="verified-pill">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <span>Maklersiz · Egasidan</span>
          </div>
        </div>

        <h2 class="detail-listing-title">{{ listing.title }}</h2>

        <!-- Key Architectural Facts Grid -->
        <div class="facts detail-facts">
          <div class="fact-card">
            <span class="fact-label">Maydon</span>
            <b class="fact-val">{{ listing.area }} m²</b>
          </div>
          <div class="fact-card">
            <span class="fact-label">Xonalar</span>
            <b class="fact-val">{{ listing.rooms }} xona</b>
          </div>
          <div class="fact-card">
            <span class="fact-label">Qavat</span>
            <b class="fact-val">{{ listing.floor || '3/9' }}</b>
          </div>
          <div class="fact-card">
            <span class="fact-label">Metrogacha</span>
            <b class="fact-val">{{ listing.metro_minutes || 5 }} daqiqa</b>
          </div>
        </div>

        <!-- Audience Tag Info -->
        <div
          v-if="listing.target_audience && listing.target_audience !== 'any'"
          class="audience-box"
          :style="audienceBoxStyle"
        >
          <span class="audience-emoji">
            <template v-if="listing.target_audience === 'family'">👨‍👩‍👧</template>
            <template v-else-if="listing.target_audience === 'female'">👩</template>
            <template v-else-if="listing.target_audience === 'male'">👨</template>
          </span>
          <div>
            <div class="audience-title">
              <template v-if="listing.target_audience === 'family'">Faqat oila uchun mo‘ljallangan</template>
              <template v-else-if="listing.target_audience === 'female'">Qizlar / Ayollar uchun mo‘ljallangan</template>
              <template v-else-if="listing.target_audience === 'male'">Yigitlar / Talabalar uchun mo‘ljallangan</template>
            </div>
            <div class="audience-desc">E’londa ijarachilar toifasi egasi tomonidan belgilangan</div>
          </div>
        </div>

        <!-- Description -->
        <div v-if="listing.description" class="description-section">
          <h4 class="section-subheading">Kvartira haqida batafsil</h4>
          <p class="description-text">
            {{ listing.description }}
          </p>
        </div>

        <!-- Trust & Source Notice -->
        <div class="trust-notice-card">
          <div class="trust-notice-row">
            <svg class="i trust-notice-icon" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <div class="trust-notice-text">
              <span class="trust-notice-source">Manba: <b>{{ listing.source_attribution || 'OLX.uz' }}</b></span>
              <p class="trust-notice-p">
                {{ listing.disclaimer || 'Ushbu e’lon ommaviy platformadan to‘g‘ridan-to‘g‘ri olingan. Har doim kvartirani joyida ko‘rib, hujjatlarni tekshirib keyin to‘lov qiling.' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Report Issue Button -->
        <div class="report-row">
          <button class="btn report-btn" type="button" @click="onReport">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
              <line x1="4" x2="4" y1="22" y2="15" />
            </svg>
            <span>Noto‘g‘ri ma’lumot haqida xabar berish</span>
          </button>
        </div>
      </div>

      <!-- Action Footer Buttons -->
      <div class="cbar detail-cbar">
        <a
          v-if="listing.contact_phone"
          class="btn p call-action-btn"
          :href="`tel:${listing.contact_phone}`"
        >
          📞 Qo‘ng‘iroq qilish
        </a>
        <a
          v-if="listing.contact_telegram"
          class="btn telegram-action-btn"
          :href="`https://t.me/${listing.contact_telegram.replace('@', '')}`"
          target="_blank"
          rel="noopener"
        >
          💬 Telegram orqali yozish
        </a>
        <a
          v-if="listing.canonical_url"
          class="btn source-action-btn"
          :class="{ p: !listing.contact_phone && !listing.contact_telegram }"
          :href="listing.canonical_url"
          target="_blank"
          rel="noopener"
        >
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
          {{ sourceViewLabel }}
        </a>
        <a
          v-if="!listing.contact_telegram && !listing.contact_phone"
          class="btn bot-action-btn"
          href="https://t.me/joyliy_bot"
          target="_blank"
          rel="noopener"
        >
          <svg class="i" viewBox="0 0 24 24">
            <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
          </svg>
          {{ t('telegram') }}
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-sheet {
  max-width: 680px;
}

.detail-header {
  padding: 16px 24px;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 17px;
  font-weight: 800;
  color: var(--tx);
  letter-spacing: -0.02em;
}

.header-district {
  font-size: 13px;
  color: var(--tx-muted);
  font-weight: 500;
}

.detail-body {
  padding: 24px;
}

.gallery-wrapper {
  margin-bottom: 20px;
}

.main-photo-box {
  position: relative;
  aspect-ratio: 16/10;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surf-muted);
}

.main-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-counter {
  position: absolute;
  right: 14px;
  bottom: 14px;
  background: rgba(17, 24, 20, 0.75);
  backdrop-filter: blur(8px);
  color: #FFFFFF;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.main-photo-placeholder {
  aspect-ratio: 16/10;
  border-radius: var(--radius-lg);
  background: var(--surf-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--tx-muted);
  font-size: 14px;
}

.placeholder-icon {
  width: 44px;
  height: 44px;
  opacity: 0.5;
}

.thumb-strip {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}

.thumb-strip::-webkit-scrollbar {
  display: none;
}

.thumb-btn {
  width: 64px;
  height: 48px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 2px solid transparent;
  flex: none;
  cursor: pointer;
  transition: all 0.18s ease;
  padding: 0;
}

.thumb-btn.active {
  border-color: var(--ac);
  transform: scale(1.05);
}

.thumb-btn img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-price-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 10px;
}

.detail-price {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.035em;
  color: var(--tx);
}

.price-period {
  font-size: 15px;
  font-weight: 500;
  color: var(--tx-muted);
}

.verified-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--mint-subtle);
  color: var(--ac);
  border: 1px solid rgba(23, 77, 58, 0.18);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: var(--radius-full);
}

.verified-pill svg {
  width: 14px;
  height: 14px;
}

.detail-listing-title {
  margin: 0 0 18px;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--tx);
}

.detail-facts {
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.fact-card {
  background: var(--surf);
  border: 1px solid var(--bd);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  text-align: center;
}

.fact-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--tx-muted);
  font-weight: 700;
  display: block;
}

.fact-val {
  font-size: 16px;
  font-weight: 800;
  color: var(--tx);
  margin-top: 4px;
  display: block;
}

.audience-box {
  padding: 14px 18px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.audience-emoji {
  font-size: 26px;
  line-height: 1;
}

.audience-title {
  font-size: 14.5px;
  font-weight: 700;
}

.audience-desc {
  font-size: 12px;
  opacity: 0.85;
  margin-top: 2px;
}

.description-section {
  margin-bottom: 20px;
}

.section-subheading {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--tx);
}

.description-text {
  white-space: pre-line;
  color: var(--tx);
  line-height: 1.65;
  font-size: 14.5px;
  margin: 0;
}

.trust-notice-card {
  background: var(--surf);
  border: 1px solid var(--bd);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  margin-bottom: 20px;
}

.trust-notice-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.trust-notice-icon {
  width: 18px;
  height: 18px;
  color: var(--ac);
  margin-top: 2px;
  flex: none;
}

.trust-notice-source {
  font-size: 13px;
  color: var(--tx);
  display: block;
  margin-bottom: 4px;
}

.trust-notice-p {
  font-size: 12px;
  color: var(--tx-muted);
  line-height: 1.5;
  margin: 0;
}

.report-row {
  margin-top: 10px;
}

.report-btn {
  font-size: 12.5px;
  color: var(--tx-muted);
  border-color: var(--bd);
}

.report-btn:hover {
  color: #E11D48;
  border-color: #FECDD3;
}

.detail-cbar {
  display: flex;
  gap: 10px;
}

.call-action-btn {
  background: var(--ac) !important;
  color: #FFFFFF !important;
  flex: 1.2;
}

.telegram-action-btn {
  background: var(--surf) !important;
  border-color: var(--bd) !important;
  flex: 1;
}

.source-action-btn {
  flex: 1;
}

@media (max-width: 640px) {
  .detail-facts {
    grid-template-columns: repeat(2, 1fr);
  }
  .detail-cbar {
    flex-direction: column;
  }
}
</style>
