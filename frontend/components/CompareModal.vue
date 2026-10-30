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
        <div>
          <span class="head-badge">Shortlist Battle</span>
          <h2 class="head-title">⚖️ Kvartiralarni Taqqoslash</h2>
        </div>
        <div class="head-actions">
          <button v-if="compareList.length" class="clear-btn" @click="clearCompare">Tozalash</button>
          <button class="close-btn" @click="$emit('close')" aria-label="Yopish">✕</button>
        </div>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <!-- If fewer than 2 items -->
        <div v-if="compareList.length < 2" class="empty-state">
          <div class="empty-icon">⚖️</div>
          <h3>Taqqoslash uchun kamida 2 ta kvartira tanlang</h3>
          <p>
            Katalogdagi istalgan e’lon ustidagi <b>«⚖️»</b> tugmasini bosib taqqoslash ro‘yxatiga qo‘shishingiz mumkin.
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
            <div class="winner-trophy">🏆</div>
            <div class="winner-text">
              <h4 class="winner-title">Joyliy AI G‘olibi: E’lon #{{ comparisonData.winner_listing_id }}</h4>
              <p class="winner-desc">{{ comparisonData.ai_winner_summary }}</p>
            </div>
          </div>

          <!-- Comparison Grid Columns -->
          <div class="compare-columns">
            <div v-for="item in compareList" :key="item.id" class="compare-col">
              <div class="col-head">
                <button class="remove-btn" @click="toggleCompare(item)" title="Olib tashlash">✕</button>
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
                    {{ item.is_owner ? '✅ Egasidan' : 'Rieltor/Agent' }}
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Bozor bahosi</span>
                  <span class="attr-val">
                    <span v-if="item.fair_price_category === 'BELOW_MARKET'" class="badge-good">
                      🟢 Bozordan arzon
                    </span>
                    <span v-else-if="item.fair_price_category === 'ABOVE_MARKET'" class="badge-warn">
                      🔴 Bozordan qimmat
                    </span>
                    <span v-else class="badge-fair">
                      🟡 Bozor narxida
                    </span>
                  </span>
                </div>

                <div class="attr-row">
                  <span class="attr-lbl">Xavfsizlik</span>
                  <span class="attr-val">
                    <span v-if="(item.scam_risk_score || 0) < 40" class="badge-safe">
                      🛡 Xavfsiz
                    </span>
                    <span v-else class="badge-risk">
                      ⚠️ Diqqat talab
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
</style>

