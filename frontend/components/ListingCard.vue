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

const onBookmarkClick = (e: MouseEvent) => {
  e.stopPropagation()
  toggleFavorite(props.listing.id)
}
</script>

<template>
  <article class="editorial-card" @click="$emit('select', listing)" tabindex="0">
    <!-- Architectural Photo Frame -->
    <div class="card-photo-frame">
      <img
        v-if="listing.image_urls && listing.image_urls.length"
        :src="listing.image_urls[0]"
        :alt="listing.title"
        loading="lazy"
        class="card-img"
      />
      <div v-else class="card-img-placeholder">
        <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" class="placeholder-art">
          <rect width="400" height="300" fill="#EBE5DB" />
          <line x1="0" y1="0" x2="400" y2="300" stroke="#DDD3C2" stroke-width="1.5" />
          <line x1="400" y1="0" x2="0" y2="300" stroke="#DDD3C2" stroke-width="1.5" />
          <circle cx="200" cy="150" r="45" fill="none" stroke="#DDD3C2" stroke-width="1.5" />
          <text x="200" y="154" font-family="serif" font-size="14" fill="#72746B" text-anchor="middle" font-style="italic">
            Joyliy Monograph
          </text>
        </svg>
      </div>

      <!-- Top Badges Overlay -->
      <div class="badges-overlay">
        <!-- Maklersiz Terracotta Pill -->
        <span v-if="listing.is_owner" class="editorial-badge maklersiz">
          Maklersiz
        </span>

        <!-- Audience Tag -->
        <span
          v-if="listing.target_audience && listing.target_audience !== 'any'"
          class="editorial-badge audience"
          :class="`aud-${listing.target_audience}`"
        >
          <template v-if="listing.target_audience === 'family'">
            <svg class="badge-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
            <span>Oila uchun</span>
          </template>
          <template v-else-if="listing.target_audience === 'female'">
            <svg class="badge-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <span>Qizlar uchun</span>
          </template>
          <template v-else-if="listing.target_audience === 'male'">
            <svg class="badge-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <span>Yigitlar uchun</span>
          </template>
        </span>
      </div>

      <!-- Photo Counter -->
      <span class="photo-index">
        {{ listing.image_urls && listing.image_urls.length ? `1 / ${listing.image_urls.length}` : '1 / 1' }}
      </span>

      <!-- Bookmark / Save Button -->
      <button
        class="bookmark-btn"
        :class="{ active: isFavorite(listing.id) }"
        @click="onBookmarkClick"
        :aria-label="t('save')"
        type="button"
        title="Saqlash"
      >
        <svg class="i" viewBox="0 0 24 24">
          <path d="m19 21-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
        </svg>
      </button>
    </div>

    <!-- Editorial Details Plate -->
    <div class="card-details">
      <!-- Price & Period -->
      <div class="price-line">
        <span class="price-val">{{ formatPrice(listing.price_uzs) }}</span>
        <span class="price-sub">{{ t('per_month') }}</span>
      </div>

      <!-- Title in clean editorial font -->
      <h3 class="card-title">
        {{ listing.title }}
      </h3>

      <!-- Architectural Specs (Area · Rooms · Floor) -->
      <div class="specs-line">
        <span class="spec-unit">{{ listing.area }} m²</span>
        <span class="spec-sep">/</span>
        <span class="spec-unit">{{ listing.rooms }} xona</span>
        <span class="spec-sep">/</span>
        <span class="spec-unit">{{ listing.floor || '3/9' }} qavat</span>
      </div>

      <!-- District & Metro Transit -->
      <div class="location-line">
        <span class="district-name">{{ listing.district }}</span>
        <span class="location-sep">·</span>
        <span class="transit-info">metroga {{ listing.metro_minutes || 5 }} daqiqa</span>
      </div>

      <!-- Bottom Status & Time -->
      <div class="card-bottom-line">
        <div class="owner-status">
          <template v-if="listing.is_owner">
            <span class="owner-dot"></span>
            <span class="owner-label">Egasidan</span>
          </template>
          <template v-else>
            <span class="under-review-label">Ochiq e’lon</span>
          </template>
        </div>

        <span class="time-stamp">
          {{ (listing.days_ago === undefined || listing.days_ago === 0) ? t('today') : (listing.days_ago === 1 ? t('yesterday') : `${listing.days_ago} ${t('days_ago')}`) }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.editorial-card {
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.25s var(--ease);
  cursor: pointer;
}

.editorial-card:hover {
  border-color: var(--ink);
  box-shadow: var(--sh-hover);
  transform: translateY(-2px);
}

.card-photo-frame {
  position: relative;
  aspect-ratio: 16/11;
  background: var(--sand-light);
  overflow: hidden;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s var(--ease);
}

.editorial-card:hover .card-img {
  transform: scale(1.03);
}

.card-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
}

.placeholder-art {
  width: 100%;
  height: 100%;
}

.badges-overlay {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
  z-index: 3;
}

.editorial-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
  font-weight: 700;
}

.editorial-badge.maklersiz {
  background: var(--terracotta);
  color: #FFFFFF;
}

.editorial-badge.audience {
  background: var(--surf);
  color: var(--ink);
  border: 1px solid var(--sand);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge-svg {
  width: 12px;
  height: 12px;
}

.editorial-badge.aud-family {
  border-color: var(--olive);
  color: var(--olive);
}

.editorial-badge.aud-female {
  border-color: #C07080;
  color: #C07080;
}

.editorial-badge.aud-male {
  border-color: #6A8CA8;
  color: #6A8CA8;
}

.photo-index {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(32, 38, 32, 0.85);
  color: #FFFFFF;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  padding: 3px 7px;
  border-radius: var(--radius-xs);
}

.bookmark-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-xs);
  background: rgba(243, 240, 232, 0.92);
  border: 1px solid var(--sand);
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s ease;
  z-index: 4;
}

.bookmark-btn:hover {
  border-color: var(--terracotta);
  color: var(--terracotta);
}

.bookmark-btn.active {
  background: var(--terracotta);
  border-color: var(--terracotta);
  color: #FFFFFF;
}

.bookmark-btn.active svg {
  fill: currentColor;
}

.card-details {
  padding: 18px 20px 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.price-line {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.price-val {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--ink);
  font-feature-settings: "tnum";
}

.price-sub {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.04em;
}

.card-title {
  margin: 0 0 10px;
  font-size: 14.5px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.specs-line {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
  margin-bottom: 6px;
}

.spec-sep {
  color: var(--sand);
}

.location-line {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--muted);
  margin-bottom: 16px;
}

.location-sep {
  color: var(--terracotta);
}

.card-bottom-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--sand-light);
}

.owner-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.owner-dot {
  width: 6px;
  height: 6px;
  background: var(--terracotta);
  border-radius: 50%;
}

.owner-label {
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink);
  font-weight: 700;
}

.under-review-label {
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--muted);
}

.time-stamp {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted);
}
</style>
