<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import type { ListingItem } from '~/composables/useListings'

const props = defineProps<{
  listing: ListingItem
}>()

const emit = defineEmits(['select'])

const { t } = useI18n()
const { isFavorite, toggleFavorite } = useFavorites()

const formatPrice = (val: number) => {
  return val.toLocaleString('ru-RU').replace(/\u00a0/g, ' ') + ' so‘m'
}

const onHeartClick = (e: MouseEvent) => {
  e.stopPropagation()
  toggleFavorite(props.listing.id)
}
</script>

<template>
  <article class="card property-card" @click="$emit('select', listing)" tabindex="0">
    <div class="ph">
      <!-- Real property photo or elegant architectural placeholder -->
      <img
        v-if="listing.image_urls && listing.image_urls.length"
        :src="listing.image_urls[0]"
        :alt="listing.title"
        loading="lazy"
        class="property-img"
      />
      <div v-else class="ph-placeholder">
        <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" class="placeholder-svg">
          <defs>
            <linearGradient id="propGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#EBF3EE" />
              <stop offset="100%" stop-color="#D7E5DD" />
            </linearGradient>
          </defs>
          <rect width="400" height="300" fill="url(#propGrad)" />
          <path d="M120 220 V110 L200 60 L280 110 V220 H120Z" fill="#174D3A" opacity="0.12" />
          <rect x="150" y="120" width="30" height="30" rx="4" fill="#FFFFFF" opacity="0.8" />
          <rect x="220" y="120" width="30" height="30" rx="4" fill="#FFFFFF" opacity="0.8" />
          <rect x="180" y="170" width="40" height="50" rx="4" fill="#174D3A" opacity="0.25" />
        </svg>
      </div>

      <!-- Top Badges Stack (Maklersiz + Target Audience) -->
      <div class="tags-row">
        <!-- Maklersiz Trust Badge -->
        <span v-if="listing.is_owner" class="tag maklersiz-pill">
          <svg class="i badge-icon-svg" viewBox="0 0 24 24">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          Maklersiz
        </span>

        <!-- Audience Badge -->
        <span
          v-if="listing.target_audience && listing.target_audience !== 'any'"
          class="aud-tag"
          :class="`aud-${listing.target_audience}`"
        >
          <template v-if="listing.target_audience === 'family'">👨‍👩‍👧 Oila uchun</template>
          <template v-else-if="listing.target_audience === 'female'">👩 Qizlar uchun</template>
          <template v-else-if="listing.target_audience === 'male'">👨 Yigitlar uchun</template>
        </span>
      </div>

      <!-- Platform Source Badge -->
      <span class="source-tag">
        OLX
      </span>

      <!-- Image counter -->
      <span class="cnt">
        {{ listing.image_urls && listing.image_urls.length ? `1 / ${listing.image_urls.length}` : '1 / 1' }}
      </span>

      <!-- Favorite heart button -->
      <button
        class="fav"
        :class="{ on: isFavorite(listing.id) }"
        @click="onHeartClick"
        :aria-label="t('save')"
        type="button"
      >
        <svg class="i" viewBox="0 0 24 24">
          <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
        </svg>
      </button>
    </div>

    <!-- Card Content Body -->
    <div class="cb">
      <!-- Price -->
      <div class="pr">
        {{ formatPrice(listing.price_uzs) }} <small>{{ t('per_month') }}</small>
      </div>

      <!-- Title -->
      <h3 class="card-title">
        {{ listing.title }}
      </h3>

      <!-- Specs row (Area · Rooms · Floor) -->
      <div class="specs-row">
        <span class="spec-item">{{ listing.area }} m²</span>
        <span class="spec-dot">·</span>
        <span class="spec-item">{{ listing.rooms }} xona</span>
        <span class="spec-dot">·</span>
        <span class="spec-item">{{ listing.floor || '3/9' }} qavat</span>
      </div>

      <!-- District & Metro -->
      <div class="location-row">
        <svg class="i loc-icon" viewBox="0 0 24 24">
          <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
          <circle cx="12" cy="10" r="3" />
        </svg>
        <span>{{ listing.district }}</span>
        <span class="spec-dot">·</span>
        <span>metroga {{ listing.metro_minutes || 5 }} daqiqa</span>
      </div>

      <!-- Footer Row: Verification & Date -->
      <div class="row card-footer-row">
        <span class="ok">
          <template v-if="listing.is_owner">
            <svg class="i verified-icon" viewBox="0 0 24 24">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <span>{{ t('verified_owner') }}</span>
          </template>
          <template v-else>
            <span style="color: var(--tx-muted)">{{ t('under_review') }}</span>
          </template>
        </span>

        <span class="mu time-tag">
          {{ (listing.days_ago === undefined || listing.days_ago === 0) ? t('today') : (listing.days_ago === 1 ? t('yesterday') : `${listing.days_ago} ${t('days_ago')}`) }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.property-card {
  border-radius: var(--radius-lg);
  position: relative;
}

.property-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.45s var(--ease-smooth);
}

.ph-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
}

.placeholder-svg {
  width: 100%;
  height: 100%;
}

.tags-row {
  position: absolute;
  left: 12px;
  top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
  z-index: 3;
}

.maklersiz-pill {
  background: var(--mint) !important;
  color: var(--ac-dark) !important;
  font-weight: 800;
  font-size: 11px;
  padding: 4px 10px;
  box-shadow: 0 2px 8px rgba(23, 77, 58, 0.2);
}

.badge-icon-svg {
  width: 13px;
  height: 13px;
  stroke-width: 2.2;
}

.aud-tag {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: var(--radius-full);
  display: inline-flex;
  gap: 4px;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  white-space: nowrap;
}

.aud-tag.aud-family {
  background: #EEF6F2;
  color: #174D3A;
  border: 1px solid #B9F2D0;
}

.aud-tag.aud-female {
  background: #FFF1F5;
  color: #9F1239;
  border: 1px solid #FECDD3;
}

.aud-tag.aud-male {
  background: #F0F9FF;
  color: #0369A1;
  border: 1px solid #BAE6FD;
}

.source-tag {
  position: absolute;
  bottom: 12px;
  left: 12px;
  color: #FFFFFF;
  background: #17231D;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.05em;
  padding: 3px 8px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  z-index: 2;
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
  color: var(--tx);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.specs-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--tx);
}

.spec-dot {
  color: var(--bd-hover);
  font-weight: 800;
}

.location-row {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: var(--tx-muted);
}

.loc-icon {
  width: 14px;
  height: 14px;
  color: var(--ac);
}

.card-footer-row {
  margin-top: auto;
  padding-top: 10px;
}

.verified-icon {
  width: 15px;
  height: 15px;
  stroke-width: 2;
}

.time-tag {
  font-size: 12px;
  font-weight: 500;
}
</style>
