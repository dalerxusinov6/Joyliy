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

const sourceLabel = computed(() => 'OLX')
const sourceClass = computed(() => 'src-olx')
</script>

<template>
  <article class="card" @click="$emit('select', listing)" tabindex="0">
    <div class="ph">
      <!-- Real photo or SVG illustration -->
      <img
        v-if="listing.image_urls && listing.image_urls.length"
        :src="listing.image_urls[0]"
        :alt="listing.title"
        loading="lazy"
      />
      <div v-else class="ph-placeholder">
        <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice">
          <rect width="400" height="300" fill="hsl(160, 30%, 90%)" />
          <rect x="120" y="70" width="160" height="180" fill="hsl(160, 40%, 65%)" rx="10" />
          <rect x="145" y="95" width="40" height="40" fill="#fff" opacity="0.8" rx="4" />
          <rect x="215" y="95" width="40" height="40" fill="#fff" opacity="0.8" rx="4" />
          <rect x="145" y="155" width="40" height="40" fill="#fff" opacity="0.8" rx="4" />
          <rect x="215" y="155" width="40" height="40" fill="#fff" opacity="0.8" rx="4" />
        </svg>
      </div>

      <!-- Badges Row (Maklersiz + Audience) -->
      <div class="tags-row">
        <!-- Maklersiz Badge -->
        <span v-if="listing.is_owner" class="tag">
          <svg class="i" style="width: 14px; height: 14px; color: #047857" viewBox="0 0 24 24">
            <path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          Maklersiz
        </span>

        <!-- Audience Badge -->
        <span
          v-if="listing.target_audience && listing.target_audience !== 'any'"
          class="aud-tag"
          :class="`aud-${listing.target_audience}`"
        >
          <template v-if="listing.target_audience === 'family'">👨‍👩‍👧 Oila</template>
          <template v-else-if="listing.target_audience === 'female'">👩 Qizlar</template>
          <template v-else-if="listing.target_audience === 'male'">👨 Yigitlar</template>
        </span>
      </div>

      <!-- Platform Source Badge -->
      <span class="source-tag" :class="sourceClass">
        {{ sourceLabel }}
      </span>

      <!-- Image counter -->
      <span class="cnt">
        {{ listing.image_urls && listing.image_urls.length ? `1/${listing.image_urls.length}` : '1/1' }}
      </span>

      <!-- Favorite button -->
      <button
        class="fav"
        :class="{ on: isFavorite(listing.id) }"
        @click="onHeartClick"
        :aria-label="t('save')"
      >
        <svg class="i" viewBox="0 0 24 24">
          <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
        </svg>
      </button>
    </div>

    <div class="cb">
      <div class="pr">
        {{ formatPrice(listing.price_uzs) }} <small>{{ t('per_month') }}</small>
      </div>
      <div class="mt" style="font-weight: 600; line-height: 1.3">
        {{ listing.title }}
      </div>
      <div class="mt">
        {{ listing.area }} m² · {{ listing.rooms }} xona · {{ listing.floor || '3/9' }} qavat
      </div>
      <div class="mu">
        {{ listing.district }}, metroga {{ listing.metro_minutes || 5 }} daqiqa
      </div>

      <div class="row">
        <span class="ok">
          <template v-if="listing.is_owner">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M5 12l5 5 9-10" />
            </svg>
            {{ t('verified_owner') }}
          </template>
          <template v-else>
            <span style="color: var(--mu)">{{ t('under_review') }}</span>
          </template>
        </span>
        <span class="mu">
          {{ (listing.days_ago === undefined || listing.days_ago === 0) ? t('today') : (listing.days_ago === 1 ? t('yesterday') : `${listing.days_ago} ${t('days_ago')}`) }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.ph-placeholder {
  width: 100%;
  height: 100%;
}

.source-tag {
  position: absolute;
  bottom: 8px;
  left: 8px;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3px;
  padding: 3px 8px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  z-index: 2;
  text-transform: uppercase;
}
.source-tag.src-olx {
  background: linear-gradient(135deg, #002f34 0%, #00464f 100%);
}

.tags-row {
  position: absolute;
  left: 10px;
  top: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
  z-index: 3;
}
.tags-row .tag {
  position: static;
}
.aud-tag {
  background: #ffffff;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 99px;
  display: inline-flex;
  gap: 4px;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  white-space: nowrap;
}
.aud-tag.aud-family {
  background: #eef2ff;
  color: #4338ca;
  border: 1px solid #c7d2fe;
}
.aud-tag.aud-female {
  background: #fdf2f8;
  color: #be185d;
  border: 1px solid #fbcfe8;
}
.aud-tag.aud-male {
  background: #f0f9ff;
  color: #0369a1;
  border: 1px solid #bae6fd;
}
</style>

