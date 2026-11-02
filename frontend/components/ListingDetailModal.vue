<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'
import { useModals } from '~/composables/useModals'

const props = defineProps<{
  listing: ListingItem | null
}>()

const emit = defineEmits(['close', 'toast'])
const { t } = useI18n()
const { isInCompare, toggleCompare } = useListings()
const { openReportModal } = useModals()

const activePhotoIndex = ref(0)

watch(
  () => props.listing,
  () => {
    activePhotoIndex.value = 0
  }
)

const formatPrice = (val: number) => {
  return (val || 0).toLocaleString('ru-RU').replace(/\u00a0/g, ' ') + ' so‘m'
}

const onReport = () => {
  if (props.listing) {
    openReportModal(props.listing.id)
  }
}

const onToggleCompare = () => {
  if (props.listing) {
    toggleCompare(props.listing)
    emit('toast', isInCompare(props.listing.id) ? 'Taqqoslashga qo‘shildi' : 'Taqqoslashdan olindi')
  }
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

        <!-- AI Intelligence Dossier -->
        <div class="ai-intelligence-block">
          <div class="intel-header">
            <span class="intel-badge">Joyliy Fair Price & Safety AI</span>
          </div>

          <div class="intel-grid">
            <!-- Market valuation card -->
            <div class="intel-card">
              <span class="ic-lbl">Bozor Tahlili (Fair Price)</span>
              <div class="ic-status">
                <span v-if="listing.fair_price_category === 'BELOW_MARKET'" class="tag-status-icon tag-good">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="intel-svg">
                    <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
                    <polyline points="17 18 23 18 23 12"/>
                  </svg>
                  <span>Bozordan arzon {{ listing.price_diff_percent ? `(${listing.price_diff_percent > 0 ? '+' : ''}${listing.price_diff_percent}%)` : '' }}</span>
                </span>
                <span v-else-if="listing.fair_price_category === 'ABOVE_MARKET'" class="tag-status-icon tag-warn">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="intel-svg">
                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                    <polyline points="17 6 23 6 23 12"/>
                  </svg>
                  <span>Bozordan qimmat {{ listing.price_diff_percent ? `(+${listing.price_diff_percent}%)` : '' }}</span>
                </span>
                <span v-else class="tag-status-icon tag-fair">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="intel-svg">
                    <line x1="5" y1="9" x2="19" y2="9"/>
                    <line x1="5" y1="15" x2="19" y2="15"/>
                  </svg>
                  <span>Bozor narxida</span>
                </span>
              </div>
              <p class="ic-desc">
                Toshkent {{ listing.district }} tumanida o‘xshash xonadonlar o‘rtacha narxi: ~{{ formatPrice(listing.estimated_market_price || listing.price_uzs) }}
              </p>
            </div>

            <!-- Scam detector card -->
            <div class="intel-card">
              <span class="ic-lbl">Xavfsizlik Tahlili</span>
              <div class="ic-status">
                <span v-if="(listing.scam_risk_score || 0) < 40" class="tag-status-icon tag-safe">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="intel-svg">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="m9 12 2 2 4-4"/>
                  </svg>
                  <span>Xavfsiz e’lon ({{ 100 - (listing.scam_risk_score || 10) }}% ishonch)</span>
                </span>
                <span v-else class="tag-status-icon tag-danger">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="intel-svg">
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <span>Ehtiyot bo‘ling (Xavf darajasi: {{ listing.scam_risk_score }}%)</span>
                </span>
              </div>
              <p class="ic-desc">
                Avans to‘lamang, xonadonni va egalik kadastrini bevosita ko‘rishdan avval pul o‘tkazmang.
              </p>
            </div>
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
        <button
          type="button"
          class="btn cmp-btn"
          :class="{ active: isInCompare(listing.id) }"
          @click="onToggleCompare"
          :title="isInCompare(listing.id) ? 'Taqqoslangan' : 'Taqqoslash'"
          :aria-label="isInCompare(listing.id) ? 'Taqqoslangan' : 'Taqqoslash'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="cmp-svg-icon">
            <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
            <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
            <path d="M7 21h10"/>
            <path d="M12 3v18"/>
            <path d="M3 7h18"/>
          </svg>
          <span class="cmp-desktop-text">{{ isInCompare(listing.id) ? 'Taqqoslangan' : 'Taqqoslash' }}</span>
        </button>

        <a
          v-if="listing.contact_phone"
          class="btn p call-btn"
          :href="`tel:${listing.contact_phone}`"
        >
          <svg class="btn-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
          </svg>
          <span class="btn-text-full">Qo‘ng‘iroq qilish</span>
          <span class="btn-text-short">Qo‘ng‘iroq</span>
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
          <span class="btn-text-full">Telegram orqali yozish</span>
          <span class="btn-text-short">Telegram</span>
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
          v-if="!listing.contact_telegram && !listing.contact_phone && !listing.canonical_url"
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
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.exhibition-sheet::-webkit-scrollbar,
.exhibition-body::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
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

.cmp-btn {
  padding: 0 14px;
  background: var(--sand-light, #f4f0eb);
  border: 1px solid var(--sand, #ebe5db);
  color: var(--ink, #1c1c1b);
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}

.cmp-btn.active {
  background: #2b78e4;
  color: #ffffff;
  border-color: #2b78e4;
}

.ai-intelligence-block {
  margin-top: 20px;
  padding: 16px;
  background: var(--sand-light, #f8f6f2);
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 12px;
}

.intel-header {
  margin-bottom: 12px;
}

.intel-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #BC684B;
  letter-spacing: 0.5px;
}

.intel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.intel-card {
  background: #ffffff;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid #ebe5db;
}

.ic-lbl {
  display: block;
  font-size: 11.5px;
  color: #72746b;
  margin-bottom: 6px;
}

.ic-status {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 6px;
}

.ic-desc {
  font-size: 11.5px;
  color: #666;
  margin: 0;
  line-height: 1.4;
}

.tag-status-icon {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.intel-svg {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.tag-good {
  color: #137333;
}

.tag-warn {
  color: #c5221f;
}

.tag-fair {
  color: #b06000;
}

.tag-safe {
  color: #137333;
}

.tag-danger {
  color: #c5221f;
}

.cmp-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 0 14px;
  background: var(--sand-light, #f4f0eb);
  border: 1px solid var(--sand, #ebe5db);
  color: var(--ink, #1c1c1b);
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}

.cmp-svg-icon {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
}

.cmp-desktop-text {
  display: inline;
}

.btn-text-full {
  display: inline;
}

.btn-text-short {
  display: none;
}

@media (max-width: 640px) {
  .exhibition-header {
    padding: 14px 16px;
  }
  .exhibition-body {
    padding: 16px 16px 24px;
  }
  .exhibition-specs-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .large-price {
    font-size: 23px;
  }
  .exhibition-listing-title {
    font-size: 19px;
    margin-bottom: 14px;
  }
  .cmp-desktop-text {
    display: none;
  }
  .btn-text-full {
    display: none;
  }
  .btn-text-short {
    display: inline;
  }
  .exhibition-cbar {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 8px;
    padding: 10px 14px calc(12px + env(safe-area-inset-bottom, 0px));
    position: sticky;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid var(--sand, #ebe5db);
    z-index: 10;
  }
  .exhibition-cbar .btn {
    min-height: 46px;
    padding: 0 12px;
    font-size: 13px;
    font-weight: 600;
    border-radius: var(--radius-full, 9999px);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .exhibition-cbar .cmp-btn {
    width: 46px;
    height: 46px;
    padding: 0;
    flex: none;
    border-radius: 50%;
  }
  .exhibition-cbar .call-btn {
    flex: 1.3;
    font-weight: 700;
  }
  .exhibition-cbar .tg-btn,
  .exhibition-cbar .source-btn {
    flex: 1;
  }
}
</style>
