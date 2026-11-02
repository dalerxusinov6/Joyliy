<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'

const props = defineProps<{
  listing: ListingItem
}>()

const emit = defineEmits(['select'])

const { t, tDistrict, formatPrice } = useI18n()
const { isFavorite, toggleFavorite } = useFavorites()
const { isInCompare, toggleCompare } = useListings()

const onBookmarkClick = (e: MouseEvent) => {
  e.stopPropagation()
  toggleFavorite(props.listing.id)
}

const onCompareClick = (e: MouseEvent) => {
  e.stopPropagation()
  toggleCompare(props.listing)
}

// Compute an Iconly score indicator (matching the circular 9.4 / 9.2 badge in Image 1)
const ratingScore = computed(() => {
  if (props.listing.match_percentage) {
    return (props.listing.match_percentage / 10).toFixed(1)
  }
  if (props.listing.fair_price_category === 'BELOW_MARKET') {
    return '9.5'
  }
  if (props.listing.is_owner) {
    return '9.2'
  }
  if (props.listing.scam_risk_score && props.listing.scam_risk_score > 60) {
    return '6.4'
  }
  return '8.8'
})

const scoreColorClass = computed(() => {
  const s = parseFloat(ratingScore.value)
  if (s >= 9.0) return 'score-excellent'
  if (s >= 8.0) return 'score-good'
  return 'score-caution'
})
</script>

<template>
  <article class="iconly-property-card" @click="$emit('select', listing)" tabindex="0">
    <!-- Photo Frame (Generous 20px radius) -->
    <div class="card-media-wrap">
      <img
        v-if="listing.image_urls && listing.image_urls.length"
        :src="listing.image_urls[0]"
        :alt="listing.title"
        loading="lazy"
        class="card-photo"
      />
      <div v-else class="card-photo-placeholder">
        <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" class="placeholder-svg">
          <rect width="400" height="300" fill="#EAECEF" />
          <circle cx="200" cy="150" r="40" fill="none" stroke="#D1D5DB" stroke-width="2" />
          <path d="M185 150 L200 135 L215 150 M192 145 V160 H208 V145" fill="none" stroke="#9CA3AF" stroke-width="2" />
          <text x="200" y="180" font-family="sans-serif" font-size="12" fill="#9CA3AF" text-anchor="middle" font-weight="600">
            Joyliy Real Estate
          </text>
        </svg>
      </div>

      <!-- Top Badges Overlay -->
      <div class="top-badges-row">
        <!-- Sale Badge -->
        <span v-if="listing.deal_type === 'sale'" class="iconly-badge sale-badge">
          {{ t('badge_for_sale') }}
        </span>

        <!-- AI Match / Owner Pill -->
        <span v-if="listing.match_percentage" class="iconly-badge match-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="badge-sparkle-svg">
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
          </svg>
          <span>{{ t('badge_match', { pct: listing.match_percentage }) }}</span>
        </span>
        <span v-else-if="listing.is_owner" class="iconly-badge owner-badge">
          {{ listing.deal_type === 'sale' ? t('from_owner') : t('no_agent') }}
        </span>

        <!-- Fair price tag -->
        <span v-if="listing.fair_price_category === 'BELOW_MARKET'" class="iconly-badge fair-badge">
          {{ listing.deal_type === 'sale' ? t('badge_cheap_price') : t('badge_below_market') }}
        </span>
      </div>

      <!-- Action Buttons (Favorite & Compare) -->
      <div class="media-actions">
        <!-- Compare -->
        <button
          type="button"
          class="media-action-circle compare-circle"
          :class="{ active: isInCompare(listing.id) }"
          @click="onCompareClick"
          :title="t('compare')"
          :aria-label="t('compare')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="action-svg">
            <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
            <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
            <path d="M7 21h10"/>
            <path d="M12 3v18"/>
            <path d="M3 7h18"/>
          </svg>
        </button>

        <!-- Circular White Favorite Button (Iconly Signature Element) -->
        <button
          type="button"
          class="media-action-circle favorite-circle"
          :class="{ active: isFavorite(listing.id) }"
          @click="onBookmarkClick"
          :aria-label="t('save')"
          :title="t('save')"
        >
          <svg viewBox="0 0 24 24" class="heart-icon">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        </button>
      </div>

      <!-- Photos Count Pill -->
      <span class="media-count-pill">
        {{ t('photos_count', { count: (listing.image_urls && listing.image_urls.length) || 1 }) }}
      </span>
    </div>

    <!-- Content Body -->
    <div class="card-body">
      <!-- Price & Circular Score Indicator Row (Matching Image 1) -->
      <div class="price-score-row">
        <div class="price-block">
          <span class="price-amount">{{ formatPrice(listing.price_uzs) }}</span>
          <span v-if="listing.deal_type !== 'sale'" class="price-period">{{ t('per_month_short') }}</span>
        </div>

        <!-- Circular Score Ring (Image 1 Style) -->
        <div class="score-indicator-badge" :class="scoreColorClass" title="Score">
          <span class="score-digit">{{ ratingScore }}</span>
        </div>
      </div>

      <!-- Property Title -->
      <h3 class="property-title">
        {{ listing.title }}
      </h3>

      <!-- Location Line -->
      <div class="location-row">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="pin-icon">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          <circle cx="12" cy="10" r="3" />
        </svg>
        <span class="district-name">{{ tDistrict(listing.district) }}</span>
        <span class="dot-sep">·</span>
        <span class="metro-transit">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="metro-svg">
            <rect width="16" height="16" x="4" y="3" rx="2"/>
            <path d="M4 11h16"/>
            <path d="M12 3v8"/>
            <path d="m8 19-2 3"/>
            <path d="m18 22-2-3"/>
            <circle cx="8" cy="15" r="1"/>
            <circle cx="16" cy="15" r="1"/>
          </svg>
          <span>{{ listing.metro_station || listing.metro_name || t('metro_near') }}</span>
        </span>
      </div>

      <!-- Architectural Specs (Pills) -->
      <div class="specs-pills-row">
        <span class="spec-pill">{{ listing.area }} m²</span>
        <span class="spec-pill">{{ t('rooms_spec', { rooms: listing.rooms }) }}</span>
        <span class="spec-pill">{{ t('floor_spec', { floor: listing.floor || '3/9' }) }}</span>
        <span v-if="listing.target_audience && listing.target_audience !== 'any'" class="spec-pill audience-pill">
          <svg v-if="listing.target_audience === 'family'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spec-audience-svg">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spec-audience-svg">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <span>{{ listing.target_audience === 'family' ? t('aud_family_short') : listing.target_audience === 'female' ? t('aud_female_short') : t('aud_male_short') }}</span>
        </span>
      </div>

      <!-- AI Match Insights Pill & Reasons (Grounded Joyliy AI Evaluation) -->
      <div v-if="listing.match_pros && listing.match_pros.length" class="ai-match-container">
        <div class="ai-match-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ai-spark-svg">
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
          </svg>
          <span class="ai-header-text">{{ t('ai_match_query', { pct: listing.match_percentage }) }}</span>
        </div>
        <div class="ai-points-list">
          <span v-for="(pro, idx) in listing.match_pros.slice(0, 2)" :key="idx" class="ai-pro-badge">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="ai-point-svg">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>{{ pro }}</span>
          </span>
          <span v-if="listing.match_cons && listing.match_cons.length" class="ai-con-badge">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="ai-warn-svg">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>{{ listing.match_cons[0] }}</span>
          </span>
        </div>
      </div>

      <!-- Card Bottom Row -->
      <div class="card-footer-row">
        <div class="status-left">
          <span v-if="listing.is_owner" class="verified-dot-label">
            <span class="green-dot"></span> {{ t('from_owner') }}
          </span>
          <span v-else class="regular-label">
            {{ t('verified_listing_tag') }}
          </span>
        </div>

        <span class="time-label">
          {{ (listing.days_ago === undefined || listing.days_ago === 0) ? t('today') : (listing.days_ago === 1 ? t('yesterday') : `${listing.days_ago} ${t('days_ago')}`) }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.iconly-property-card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-card);
  padding: 10px;
  display: flex;
  flex-direction: column;
  transition: all 0.25s var(--ease);
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(23, 25, 29, 0.04);
}

@media (min-width: 480px) {
  .iconly-property-card {
    padding: 12px;
  }
}

.iconly-property-card:hover {
  border-color: rgba(40, 120, 200, 0.35);
  box-shadow: 0 16px 36px -4px rgba(40, 120, 200, 0.12), 0 4px 16px rgba(0, 0, 0, 0.04);
  transform: translateY(-3px);
}

/* Photo Media Frame (Generous 20px radius) */
.card-media-wrap {
  position: relative;
  aspect-ratio: 16/11;
  background: var(--surface-subtle);
  border-radius: 16px;
  overflow: hidden;
}

@media (min-width: 480px) {
  .card-media-wrap {
    border-radius: var(--radius-inner);
  }
}

.card-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.6s var(--ease);
}

.iconly-property-card:hover .card-photo {
  transform: scale(1.04);
}

.card-photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
}

.placeholder-svg {
  width: 100%;
  height: 100%;
}

/* Top Badges */
.top-badges-row {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: flex-start;
  z-index: 3;
}

@media (min-width: 480px) {
  .top-badges-row {
    top: 10px;
    left: 10px;
    gap: 6px;
  }
}

.iconly-badge {
  font-family: var(--font-sans);
  font-size: 10.5px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--radius-full);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  white-space: nowrap;
}

@media (min-width: 480px) {
  .iconly-badge {
    font-size: 11px;
    padding: 4px 10px;
  }
}

.owner-badge {
  background: #17191D;
  color: #FFFFFF;
}

.match-badge {
  background: var(--blue-primary);
  color: #FFFFFF;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge-sparkle-svg {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.action-svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
}

.fair-badge {
  background: #10B981;
  color: #FFFFFF;
}

/* Media Actions (Compare & Circular Favorite) */
.media-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 4;
}

@media (min-width: 480px) {
  .media-actions {
    top: 10px;
    right: 10px;
  }
}

.media-action-circle {
  min-width: 36px;
  min-height: 36px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  transition: all 0.18s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.media-action-circle:hover {
  transform: scale(1.06);
}

.media-action-circle:active {
  transform: scale(0.92);
}

.compare-circle {
  font-size: 13px;
}

.compare-circle.active {
  background: #17191D;
  color: #FFFFFF;
}

.favorite-circle {
  color: #858B93;
}

.heart-icon {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  transition: all 0.15s ease;
}

.favorite-circle:hover {
  color: #EF4444;
}

.favorite-circle.active {
  color: #EF4444;
  background: #FFFFFF;
}

.favorite-circle.active .heart-icon {
  fill: #EF4444;
  stroke: #EF4444;
}

.media-count-pill {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(23, 25, 29, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #FFFFFF;
  font-size: 10px;
  font-weight: 600;
  padding: 3px 7px;
  border-radius: var(--radius-full);
}

/* Card Body */
.card-body {
  padding: 12px 4px 4px;
  display: flex;
  flex-direction: column;
  gap: 7px;
  flex: 1;
}

@media (min-width: 480px) {
  .card-body {
    padding: 14px 6px 4px;
    gap: 8px;
  }
}

/* Price & Circular Score Row */
.price-score-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.price-block {
  display: flex;
  align-items: baseline;
  gap: 3px;
  min-width: 0;
}

.price-amount {
  font-family: var(--font-sans);
  font-size: clamp(17px, 4.8vw, 20px);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  white-space: nowrap;
}

.price-period {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Score Ring (Matching Image 1's 9.4 Circular Ring) */
.score-indicator-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-subtle);
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.score-digit {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-primary);
  font-family: var(--font-sans);
}

.score-excellent {
  border: 2.5px solid #10B981;
}

.score-good {
  border: 2.5px solid var(--blue-primary);
}

.score-caution {
  border: 2.5px solid #F59E0B;
}

/* Title */
.property-title {
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

@media (min-width: 480px) {
  .property-title {
    font-size: 14.5px;
  }
}

/* Location */
.location-row {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-secondary);
}

.pin-icon {
  width: 14px;
  height: 14px;
  color: var(--blue-primary);
  flex-shrink: 0;
}

.dot-sep {
  color: var(--text-tertiary);
}

.district-name {
  font-weight: 600;
  white-space: nowrap;
}

.metro-transit {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.metro-svg {
  width: 13px;
  height: 13px;
  color: var(--blue-primary);
  flex-shrink: 0;
}

/* Specs Pills (Wrap gracefully on 320px screens) */
.specs-pills-row {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
  padding: 2px 0;
}

.spec-pill {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--surface-subtle);
  border: 1px solid var(--border-subtle);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.spec-audience-svg {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.audience-pill {
  color: var(--blue-deep);
  background: rgba(40, 120, 200, 0.08);
  border-color: rgba(40, 120, 200, 0.15);
}

/* AI Match Insights Container */
.ai-match-container {
  background: rgba(40, 120, 200, 0.06);
  border: 1px solid rgba(40, 120, 200, 0.14);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 2px;
}

.ai-match-header {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--blue-deep);
}

:root[data-theme="dark"] .ai-match-header {
  color: #58A6FF;
}

.ai-spark-svg {
  width: 14px;
  height: 14px;
  color: var(--blue-primary);
  flex-shrink: 0;
}

.ai-points-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.ai-pro-badge {
  font-size: 10.5px;
  font-weight: 500;
  color: #065F46;
  background: #D1FAE5;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  word-break: break-word;
}

.ai-point-svg {
  width: 11px;
  height: 11px;
  flex-shrink: 0;
}

:root[data-theme="dark"] .ai-pro-badge {
  color: #A7F3D0;
  background: rgba(16, 185, 129, 0.15);
}

.ai-con-badge {
  font-size: 10.5px;
  font-weight: 500;
  color: #92400E;
  background: #FEF3C7;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  word-break: break-word;
}

.ai-warn-svg {
  width: 11px;
  height: 11px;
  flex-shrink: 0;
}

/* Footer Row */
.card-footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid var(--border-subtle);
  margin-top: auto;
  font-size: 11px;
  color: var(--text-secondary);
}

.verified-dot-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-weight: 600;
  color: #10B981;
}

.green-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
}

.regular-label {
  color: var(--text-secondary);
}

.time-label {
  font-size: 11px;
}
</style>
