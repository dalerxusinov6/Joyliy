<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useListings, type ListingItem } from '~/composables/useListings'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'selectListing'])

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

const formatPrice = (val: number) => {
  return (val || 0).toLocaleString('ru-RU').replace(/\u00a0/g, ' ') + ' so‘m'
}
</script>

<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-box">
      <!-- Head -->
      <div class="modal-head">
        <div class="head-title-wrap">
          <span class="head-badge">Shortlist Battle</span>
          <h2 class="head-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="head-svg">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="M7 21h10"/>
              <path d="M12 3v18"/>
              <path d="M3 7h18"/>
            </svg>
            <span>Kvartiralarni Taqqoslash</span>
          </h2>
        </div>
        <div class="head-actions">
          <button v-if="compareList.length" class="clear-btn" @click="clearCompare">Tozalash</button>
          <button class="close-btn" @click="$emit('close')" aria-label="Yopish">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="modal-close-svg">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <!-- If fewer than 2 items -->
        <div v-if="compareList.length < 2" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="empty-cmp-svg">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="M7 21h10"/>
              <path d="M12 3v18"/>
              <path d="M3 7h18"/>
            </svg>
          </div>
          <h3>Taqqoslash uchun kamida 2 ta kvartira tanlang</h3>
          <p>
            Katalogdagi istalgan e’lon ustidagi taqqoslash tugmasini bosib taqqoslash ro‘yxatiga qo‘shishingiz mumkin.
            AI narx/m², metro yaqinligi va sharoitlarni yonma-yon tahlil qilib beradi.
          </p>
          <div v-if="compareList.length === 1" class="selected-hint">
            Hozircha 1 ta e’lon tanlangan: <b>{{ compareList[0].title }}</b>
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
              <h4 class="winner-title">Joyliy AI G‘olibi: E’lon #{{ comparisonData.winner_listing_id }}</h4>
              <p class="winner-desc">{{ comparisonData.ai_winner_summary }}</p>
            </div>
          </div>

          <!-- Comparison Grid Columns -->
          <div class="compare-columns">
            <div v-for="item in compareList" :key="item.id" class="compare-col">
              <div class="col-head">
                <button class="remove-btn" @click="toggleCompare(item)" title="Olib tashlash" aria-label="Olib tashlash">
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
                  <div v-else class="placeholder">Rasm yo‘q</div>
                </div>
                <h4 class="col-title" :title="item.title">{{ item.title }}</h4>
                <div class="col-price">{{ formatPrice(item.price_uzs) }}</div>
              </div>

              <!-- Matrix Rows -->
              <div class="attr-list">
                <div class="attr-row">
                  <span class="attr-lbl">1 m² narxi</span>
                  <span class="attr-val highlight">
                    {{ formatPrice(Math.round(item.price_uzs / (item.area || 50))) }}
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Tuman</span>
                  <span class="attr-val">{{ item.district }}</span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Metro</span>
                  <span class="attr-val">
                    {{ item.metro_station || item.metro_name || 'Yaqin metro' }}
                    <small v-if="item.metro_distance_m">({{ item.metro_distance_m }}m)</small>
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Xonalar / Maydon</span>
                  <span class="attr-val">{{ item.rooms }} xona / {{ item.area }} m²</span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Manba</span>
                  <span class="attr-val" :class="{ 'owner-tag': item.is_owner }">
                    <template v-if="item.is_owner">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-svg-check">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      <span>Egasidan</span>
                    </template>
                    <template v-else>Rieltor/Agent</template>
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Bozor bahosi</span>
                  <span class="attr-val">
                    <span v-if="item.fair_price_category === 'BELOW_MARKET'" class="badge-good">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-badge-svg">
                        <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
                        <polyline points="17 18 23 18 23 12"/>
                      </svg>
                      <span>Bozordan arzon</span>
                    </span>
                    <span v-else-if="item.fair_price_category === 'ABOVE_MARKET'" class="badge-warn">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-badge-svg">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                        <polyline points="17 6 23 6 23 12"/>
                      </svg>
                      <span>Bozordan qimmat</span>
                    </span>
                    <span v-else class="badge-fair">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="inline-badge-svg">
                        <line x1="5" y1="9" x2="19" y2="9"/>
                        <line x1="5" y1="15" x2="19" y2="15"/>
                      </svg>
                      <span>Bozor narxida</span>
                    </span>
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Xavfsizlik</span>
                  <span class="attr-val">
                    <span v-if="(item.scam_risk_score || 0) < 40" class="badge-safe">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="inline-badge-svg">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="m9 12 2 2 4-4"/>
                      </svg>
                      <span>Xavfsiz</span>
                    </span>
                    <span v-else class="badge-risk">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="inline-badge-svg">
                        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                      </svg>
                      <span>Diqqat talab</span>
                    </span>
                  </span>
                </div>
              </div>

              <button
                type="button"
                class="view-listing-btn"
                @click="$emit('selectListing', item); $emit('close')"
              >
                E’lonni ochish
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(18, 17, 16, 0.65);
  backdrop-filter: blur(5px);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-box {
  background: var(--surf, #ffffff);
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-head {
  padding: 18px 24px;
  border-bottom: 1px solid var(--sand, #ebe5db);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.head-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #BC684B;
  letter-spacing: 0.5px;
}

.head-title {
  margin: 2px 0 0;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.head-svg {
  width: 20px;
  height: 20px;
  color: var(--blue-primary, #2878C8);
  flex-shrink: 0;
}

.modal-close-svg {
  width: 18px;
  height: 18px;
}

.empty-cmp-svg {
  width: 48px;
  height: 48px;
  color: var(--blue-primary, #2878C8);
  margin-bottom: 12px;
}

.trophy-svg {
  width: 32px;
  height: 32px;
  color: #F59E0B;
  flex-shrink: 0;
}

.remove-svg {
  width: 12px;
  height: 12px;
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

.head-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.clear-btn {
  background: none;
  border: 1px solid var(--sand, #ebe5db);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #72746b;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  max-width: 460px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
}

.empty-state p {
  color: #72746b;
  font-size: 14px;
  line-height: 1.5;
}

.selected-hint {
  margin-top: 16px;
  padding: 8px 14px;
  background: #f8f6f2;
  border-radius: 8px;
  font-size: 13px;
  color: #BC684B;
}

.winner-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #fdf8f5 0%, #fff6ee 100%);
  border: 1px solid #ffd4b8;
  border-radius: 12px;
  margin-bottom: 20px;
}

.winner-trophy {
  font-size: 30px;
}

.winner-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 700;
  color: #BC684B;
}

.winner-desc {
  margin: 0;
  font-size: 13px;
  color: #4a4a49;
  line-height: 1.45;
}

.compare-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.compare-col {
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 12px;
  padding: 14px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  position: relative;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0,0,0,0.5);
  color: #fff;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 12px;
  cursor: pointer;
  z-index: 2;
}

.img-wrap {
  aspect-ratio: 16/10;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 10px;
  cursor: pointer;
}

.img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.col-title {
  margin: 0 0 4px;
  font-size: 13.5px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-price {
  font-size: 16px;
  font-weight: 800;
  color: #BC684B;
  margin-bottom: 12px;
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
  border-bottom: 1px dashed #eee;
}

.attr-lbl {
  color: #72746b;
}

.attr-val {
  font-weight: 600;
  text-align: right;
}

.attr-val.highlight {
  color: #BC684B;
}

.owner-tag {
  color: #137333;
}

.badge-good {
  color: #137333;
  background: #e6f4ea;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-warn {
  color: #c5221f;
  background: #fce8e6;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-fair {
  color: #b06000;
  background: #fef7e0;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-safe {
  color: #137333;
}

.badge-risk {
  color: #c5221f;
}

.view-listing-btn {
  margin-top: auto;
  width: 100%;
  padding: 8px;
  border-radius: 8px;
  background: #BC684B;
  color: #ffffff;
  border: none;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}

@media (max-width: 640px) {
  .compare-columns {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    gap: 12px;
    padding-bottom: 8px;
    scrollbar-width: thin;
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

