<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'selectListing'])

const { t, tDistrict, formatPrice } = useI18n()
const { compareList, toggleCompare, clearCompare } = useListings()

interface CompareResult {
  listings: any[]
  comparison_matrix: Record<string, any>
  winner_listing_id?: number
  ai_winner_summary?: string
}

const comparisonData = ref<CompareResult | null>(null)
const isLoading = ref(false)

const runComparison = async () => {
  if (compareList.value.length < 2) {
    comparisonData.value = null
    return
  }

  isLoading.value = true
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    const ids = compareList.value.map(x => x.id)
    const res: any = await $fetch(`${base}/api/listings/compare`, {
      method: 'POST',
      body: { listing_ids: ids },
    })
    comparisonData.value = res
  } catch (err) {
    console.error('Comparison API failed, fallback local calculation:', err)
  } finally {
    isLoading.value = false
  }
}

watch(() => props.show, (val) => {
  if (val) runComparison()
})

watch(() => compareList.value.length, () => {
  if (props.show) runComparison()
})
</script>

<template>
  <div v-if="show" class="ov show" @click.self="$emit('close')">
    <div class="sheet compare-sheet">
      <!-- Head -->
      <div class="top modal-header">
        <div class="header-left">
          <span class="modal-title">{{ t('compare_title') }}</span>
        </div>
        <div class="head-actions">
          <button v-if="compareList.length" class="clear-btn" @click="clearCompare">{{ t('clear') }}</button>
          <button class="ib" @click="$emit('close')" :aria-label="t('close')">
            <svg class="i" viewBox="0 0 24 24">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="bd modal-body">
        <!-- If fewer than 2 items -->
        <div v-if="compareList.length < 2" class="compare-empty-box">
          <span class="numeral-accent">00</span>
          <h3 class="empty-title">{{ t('compare_need_2') }}</h3>
          <p class="empty-desc">
            {{ t('compare_need_2_desc') }}
          </p>
          <div v-if="compareList.length === 1" class="selected-hint">
            {{ t('compare_1_selected', { title: compareList[0].title }) }}
          </div>
        </div>

        <!-- Comparison Table View -->
        <div v-else class="comparison-container">
          <!-- AI Winner Banner -->
          <div v-if="comparisonData && comparisonData.winner_listing_id" class="winner-banner">
            <div class="winner-trophy">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="trophy-svg">
                <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>
                <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>
                <path d="M4 22h16"/>
                <path d="M10 14.66V17c0 .55-.45 1-1 1H7v4h10v-4h-2c-.55 0-1-.45-1-1v-2.34"/>
                <path d="M6 2h12v7a6 6 0 0 1-12 0V2Z"/>
              </svg>
            </div>
            <div class="winner-text">
              <h4 class="winner-title">{{ t('compare_winner_title', { id: comparisonData.winner_listing_id }) }}</h4>
              <p class="winner-desc">{{ comparisonData.ai_winner_summary }}</p>
            </div>
          </div>

          <!-- Comparison Grid Columns -->
          <div class="compare-columns">
            <div v-for="item in compareList" :key="item.id" class="compare-col">
              <div class="col-head">
                <button class="remove-btn" @click="toggleCompare(item)" :title="t('remove_from_compare')" :aria-label="t('remove_from_compare')">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="remove-svg">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
                <div class="img-wrap" @click="$emit('selectListing', item); $emit('close')">
                  <img
                    v-if="item.image_urls && item.image_urls.length"
                    :src="item.image_urls[0]"
                    :alt="item.title"
                  />
                  <div v-else class="placeholder">{{ t('no_photo') }}</div>
                </div>
                <h4 class="col-title" :title="item.title">{{ item.title }}</h4>
                <div class="col-price">{{ formatPrice(item.price_uzs) }}</div>
              </div>

              <!-- Matrix Rows -->
              <div class="attr-list">
                <div class="attr-row">
                  <span class="attr-lbl">{{ t('price_per_m2') }}</span>
                  <span class="attr-val highlight">
                    {{ formatPrice(Math.round(item.price_uzs / (item.area || 50))) }}
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">{{ t('district') }}</span>
                  <span class="attr-val">{{ tDistrict(item.district) }}</span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">{{ t('metro') }}</span>
                  <span class="attr-val">
                    {{ item.metro_station || item.metro_name || t('near_metro') }}
                    <small v-if="item.metro_distance_m">({{ item.metro_distance_m }}m)</small>
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">{{ t('rooms_and_area') }}</span>
                  <span class="attr-val">{{ t('rooms_spec', { rooms: item.rooms }) }} / {{ item.area }} m²</span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">{{ t('source_label') }}</span>
                  <span class="attr-val" :class="{ 'owner-tag': item.is_owner }">
                    <template v-if="item.is_owner">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-svg-check">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      <span>{{ t('from_owner') }}</span>
                    </template>
                    <template v-else>{{ t('realtor_agent') }}</template>
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">{{ t('fair_market_label') }}</span>
                  <span class="attr-val">
                    <span v-if="item.fair_price_category === 'BELOW_MARKET'" class="badge-good">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-badge-svg">
                        <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
                        <polyline points="17 18 23 18 23 12"/>
                      </svg>
                      <span>{{ t('below_market_label') }}</span>
                    </span>
                    <span v-else-if="item.fair_price_category === 'ABOVE_MARKET'" class="badge-warn">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-badge-svg">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                        <polyline points="17 6 23 6 23 12"/>
                      </svg>
                      <span>{{ t('above_market_label') }}</span>
                    </span>
                    <span v-else class="badge-fair">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-badge-svg">
                        <line x1="5" y1="9" x2="19" y2="9"/>
                        <line x1="5" y1="15" x2="19" y2="15"/>
                      </svg>
                      <span>{{ t('at_market_label') }}</span>
                    </span>
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">{{ t('safety_label') }}</span>
                  <span class="attr-val">
                    <span v-if="(item.scam_risk_score || 0) < 40" class="badge-safe">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="inline-badge-svg">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="m9 12 2 2 4-4"/>
                      </svg>
                      <span>{{ t('safe_label') }}</span>
                    </span>
                    <span v-else class="badge-risk">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="inline-badge-svg">
                        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                      </svg>
                      <span>{{ t('caution_label') }}</span>
                    </span>
                  </span>
                </div>
              </div>

              <button
                type="button"
                class="view-listing-btn"
                @click="$emit('selectListing', item); $emit('close')"
              >
                {{ t('open_listing') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.compare-sheet {
  max-width: 960px;
}

.modal-header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--sand, #DDD3C2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--ivory, #F3F0E8);
}

.modal-title {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.clear-btn {
  background: var(--surf, #FFFFFF);
  border: 1px solid var(--sand, #DDD3C2);
  padding: 6px 12px;
  border-radius: var(--radius-xs, 4px);
  font-size: 12.5px;
  font-weight: 500;
  color: var(--ink);
  cursor: pointer;
  transition: all 0.15s ease;
}

.clear-btn:hover {
  background: var(--sand-light, #EBE5DB);
}

.modal-body {
  padding: 24px;
}

.compare-empty-box {
  text-align: center;
  padding: 64px 20px;
  border: 1px dashed var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  background: var(--surf, #FFFFFF);
}

.empty-title {
  font-family: var(--font-serif);
  font-size: 22px;
  margin: 12px 0 8px;
  color: var(--ink);
}

.empty-desc {
  font-size: 14.5px;
  color: var(--muted, #72746B);
  max-width: 440px;
  margin: 0 auto 20px;
  line-height: 1.6;
}

.numeral-accent {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--muted, #72746B);
  background: var(--sand-light, #EBE5DB);
  padding: 3px 8px;
  border-radius: var(--radius-xs, 2px);
}

.selected-hint {
  margin-top: 16px;
  padding: 8px 14px;
  background: var(--ivory, #F3F0E8);
  border: 1px solid var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  font-size: 13px;
  color: var(--ink);
  display: inline-block;
}

.winner-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 20px;
  background: #F0FDF4;
  border: 1px solid #BBF7D0;
  border-radius: var(--radius-xs, 4px);
  margin-bottom: 24px;
}

.winner-trophy {
  font-size: 28px;
  color: #10B981;
}

.trophy-svg {
  width: 28px;
  height: 28px;
  color: #10B981;
}

.winner-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 700;
  color: #065F46;
}

.winner-desc {
  margin: 0;
  font-size: 13px;
  color: #374151;
  line-height: 1.45;
}

.compare-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
}

.compare-col {
  border: 1px solid var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  padding: 16px;
  background: var(--surf, #FFFFFF);
  display: flex;
  flex-direction: column;
  position: relative;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(18, 17, 16, 0.6);
  color: #ffffff;
  border: none;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 12px;
  cursor: pointer;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
}

.remove-btn:hover {
  background: rgba(18, 17, 16, 0.85);
}

.remove-svg {
  width: 12px;
  height: 12px;
}

.img-wrap {
  aspect-ratio: 16/10;
  border-radius: var(--radius-xs, 2px);
  overflow: hidden;
  margin-bottom: 12px;
  cursor: pointer;
  background: var(--sand-light, #EBE5DB);
}

.img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 12px;
  color: var(--muted);
}

.col-title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--blue-primary, #514437);
  margin-bottom: 14px;
}

.attr-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 12.5px;
}

.attr-row {
  display: flex;
  justify-content: space-between;
  padding-bottom: 6px;
  border-bottom: 1px dashed var(--sand-light, #EBE5DB);
}

.attr-lbl {
  color: var(--muted, #72746B);
}

.attr-val {
  font-weight: 600;
  color: var(--ink);
  text-align: right;
}

.attr-val.highlight {
  color: var(--blue-primary, #514437);
}

.inline-svg-check {
  width: 13px;
  height: 13px;
  color: #10B981;
  display: inline-block;
  vertical-align: -2px;
  margin-right: 3px;
}

.inline-badge-svg {
  width: 12px;
  height: 12px;
  display: inline-block;
  vertical-align: -1px;
  margin-right: 3px;
}

.owner-tag {
  color: #10B981;
}

.badge-good {
  color: #065F46;
  background: #ECFDF5;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-warn {
  color: #991B1B;
  background: #FEF2F2;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-fair {
  color: #1E40AF;
  background: #EFF6FF;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-safe {
  color: #065F46;
}

.badge-risk {
  color: #991B1B;
}

.view-listing-btn {
  margin-top: auto;
  width: 100%;
  padding: 9px 12px;
  border-radius: var(--radius-xs, 4px);
  background: var(--blue-primary, #514437);
  color: #ffffff;
  border: none;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.view-listing-btn:hover {
  background: var(--blue-deep, #1E60A5);
}

@media (max-width: 640px) {
  .modal-header {
    padding: 14px 16px;
  }
  .modal-body {
    padding: 16px 14px;
  }
  .compare-columns {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    gap: 12px;
    padding-bottom: 8px;
    scrollbar-width: none;
  }
  .compare-col {
    min-width: 260px;
    max-width: 82vw;
    flex: none;
    scroll-snap-align: start;
  }
  .winner-banner {
    flex-direction: column;
    gap: 8px;
    padding: 12px 14px;
  }
}
</style>

