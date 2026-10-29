<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import type { ListingItem } from '~/composables/useListings'

const props = defineProps<{
  listing: ListingItem | null
}>()

const emit = defineEmits(['close', 'toast'])
const { t } = useI18n()

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
    <div class="sheet">
      <div class="top">
        <span>{{ listing.rooms }} {{ t('rooms_apartment') }} — {{ listing.district }}</span>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="bd">
        <!-- Photo Gallery -->
        <div class="gal">
          <div v-if="listing.image_urls && listing.image_urls.length">
            <img
              v-for="(img, i) in listing.image_urls"
              :key="i"
              :src="img"
              :alt="listing.title"
              style="width: 100%; height: 100%; object-fit: cover"
            />
          </div>
          <div v-else>
            <div style="background: var(--surf); display: grid; place-items: center; width: 100%; height: 100%">
              <svg class="i" style="width: 48px; height: 48px; color: var(--mu)" viewBox="0 0 24 24">
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <path d="M21 15l-5-5L5 21" />
              </svg>
            </div>
          </div>
        </div>

        <div class="pr" style="font-size: 26px; margin-top: 16px">
          {{ formatPrice(listing.price_uzs) }} <small>{{ t('per_month') }}</small>
        </div>

        <h3 style="margin: 8px 0; font-size: 18px">{{ listing.title }}</h3>

        <div class="mt" style="font-weight: 500">
          📍 {{ listing.district }}, metroga {{ listing.metro_minutes || 5 }} daqiqa
        </div>

        <!-- Facts -->
        <div class="facts">
          <div>
            <span class="mu">Maydon</span>
            <b>{{ listing.area }} m²</b>
          </div>
          <div>
            <span class="mu">Xonalar</span>
            <b>{{ listing.rooms }} xona</b>
          </div>
          <div>
            <span class="mu">Qavat</span>
            <b>{{ listing.floor || '3/9' }}</b>
          </div>
          <div>
            <span class="mu">E’lon sanasi</span>
            <b>{{ t('today') }}</b>
          </div>
        </div>

        <!-- Verification status -->
        <div style="margin: 12px 0">
          <p v-if="listing.is_owner">
            <span class="ok" style="font-size: 14px">
              <svg class="i" viewBox="0 0 24 24">
                <path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
              {{ t('verified_owner') }}
            </span>
          </p>
          <p v-else class="mu">
            {{ t('under_review') }}
          </p>
          <p style="font-size: 12px; color: var(--mu); margin-top: 4px">
            ⚠️ {{ listing.disclaimer || 'Egasidan ekanligi mustaqil tasdiqlanmagan. Asl manba havolasi saqlangan.' }}
          </p>
          <p style="font-size: 13px; color: var(--mu); margin-top: 6px">
            🌐 Manba: <b style="color: var(--tx)">{{ listing.source_attribution || 'OLX.uz' }}</b>
          </p>
        </div>

        <!-- Description -->
        <div v-if="listing.description" style="margin-top: 16px">
          <h4 style="margin: 0 0 6px; font-size: 15px">Tavsif</h4>
          <p style="white-space: pre-line; color: var(--tx); line-height: 1.6; margin: 0">
            {{ listing.description }}
          </p>
        </div>

        <!-- Contact Box -->
        <div style="background: var(--surf); padding: 14px 18px; border-radius: 14px; margin-top: 16px; border: 1px solid var(--bd)">
          <h4 style="margin: 0 0 8px; font-size: 15px">Aloqa va bog‘lanish</h4>
          <div style="display: flex; flex-direction: column; gap: 8px">
            <div v-if="listing.contact_phone" style="display: flex; align-items: center; gap: 8px">
              <span>📞 Telefon:</span>
              <a :href="`tel:${listing.contact_phone}`" style="font-weight: 700; color: var(--ac)">
                {{ listing.contact_phone }}
              </a>
            </div>
            <div v-if="listing.contact_telegram" style="display: flex; align-items: center; gap: 8px">
              <span>💬 Telegram:</span>
              <a :href="`https://t.me/${listing.contact_telegram.replace('@', '')}`" target="_blank" rel="noopener" style="font-weight: 700; color: var(--ac)">
                {{ listing.contact_telegram }}
              </a>
            </div>
            <div v-if="!listing.contact_phone && !listing.contact_telegram" style="color: var(--mu); font-size: 13px">
              Aloqa raqami bevosita asl e'lon sahifasida keltirilgan.
            </div>
          </div>
        </div>

        <!-- Report button -->
        <div style="margin-top: 20px">
          <button class="btn" type="button" @click="onReport">
            <svg class="i" viewBox="0 0 24 24">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
              <line x1="4" x2="4" y1="22" y2="15" />
            </svg>
            {{ t('report') }}
          </button>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="cbar">
        <a
          v-if="listing.contact_phone"
          class="btn p"
          :href="`tel:${listing.contact_phone}`"
        >
          📞 Qo‘ng‘iroq
        </a>
        <a
          v-if="listing.contact_telegram"
          class="btn"
          :href="`https://t.me/${listing.contact_telegram.replace('@', '')}`"
          target="_blank"
          rel="noopener"
        >
          💬 Telegram
        </a>
        <a
          v-if="listing.canonical_url"
          class="btn"
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
        <a v-if="!listing.contact_telegram && !listing.contact_phone" class="btn" href="https://t.me/joyliy_bot" target="_blank" rel="noopener">
          <svg class="i" viewBox="0 0 24 24">
            <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
          </svg>
          {{ t('telegram') }}
        </a>
      </div>
    </div>
  </div>
</template>

