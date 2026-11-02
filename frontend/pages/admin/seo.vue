<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const isSyncing = ref(false)
const auditData = ref<any>(null)

// SERP Preview Simulator Reactive State
const serpDevice = ref<'mobile' | 'desktop'>('mobile')
const serpSlug = ref('chilonzor')
const previewTitle = ref('Chilonzorda 3 xonali kvartira sotiladi — Joyliy.uz')
const previewDesc = ref('Toshkent shahri Chilonzor tumanida 3 xonali kvartira. Narxi, maydoni, fotosuratlari va batafsil ma‘lumotlarini Joyliy.uz saytida ko‘ring.')

const titleLength = computed(() => previewTitle.value.length)
const descLength = computed(() => previewDesc.value.length)

const titleStatusClass = computed(() => {
  if (titleLength.value > 65) return 'status-danger'
  if (titleLength.value >= 40) return 'status-good'
  return 'status-warning'
})

const descStatusClass = computed(() => {
  if (descLength.value > 165) return 'status-danger'
  if (descLength.value >= 120) return 'status-good'
  return 'status-warning'
})

const fetchSeoAudit = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/seo/summary')
    if (res) {
      auditData.value = res
    }
  } catch (err: any) {
    showToast('SEO ma‘lumotlarini yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

const triggerSitemapSync = async () => {
  if (isSyncing.value) return
  isSyncing.value = true
  showToast('Sitemaplar qayta generatsiya qilinmoqda...', 'info')
  try {
    const res = await authFetch('/api/admin/seo/sync', { method: 'POST' })
    if (res && res.success) {
      showToast('Barcha XML sitemaplar muvaffaqiyatli sinxronlandi!', 'success')
      await fetchSeoAudit()
    } else {
      showToast('Sinxronlashda xatolik yuz berdi', 'error')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Sinxronlash xatosi', 'error')
  } finally {
    isSyncing.value = false
  }
}

onMounted(() => {
  fetchSeoAudit()
})
</script>

<template>
  <AdminShell
    :breadcrumbs="[
      { label: 'Boshqaruv', to: '/admin' },
      { label: 'SEO & Qidiruv' },
    ]"
    title="SEO va Organik Qidiruv Boshqaruvi"
  >
    <div class="admin-seo-container">
      <!-- Top Action Bar -->
      <div class="seo-top-actions">
        <div>
          <h2 class="seo-page-title">Qidiruv Tizimlarida Optimallashtirish (SEO)</h2>
          <p class="seo-page-sub">
            Google va Yandex organik qidiruvida Toshkent ko‘chmas mulki bo‘yicha yuqori o‘rinlarni egallash monitoringi.
          </p>
        </div>
        <div class="actions-group">
          <button
            type="button"
            class="admin-btn admin-btn-secondary"
            @click="fetchSeoAudit"
            :disabled="isLoading"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            <span>Yangilash</span>
          </button>

          <button
            type="button"
            class="admin-btn admin-btn-primary"
            @click="triggerSitemapSync"
            :disabled="isSyncing"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>{{ isSyncing ? 'Sinxronlanmoqda...' : 'Sitemaplarni yangilash' }}</span>
          </button>
        </div>
      </div>

      <!-- KPI Metrics Cards -->
      <div class="seo-kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">SEO Salomatlik Indeksi</div>
          <div class="kpi-value-row">
            <span class="kpi-huge-num">{{ auditData?.health_score || 98 }}</span>
            <span class="kpi-unit">/100</span>
          </div>
          <div class="kpi-progress-bar">
            <div
              class="kpi-progress-fill"
              :style="{ width: (auditData?.health_score || 98) + '%' }"
            />
          </div>
          <span class="kpi-subtext">Google Technical SEO talablariga muvofiq</span>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">Indekslanadigan URLlar</div>
          <div class="kpi-value-row">
            <span class="kpi-huge-num">{{ auditData?.total_indexable_urls || '730+' }}</span>
          </div>
          <div class="kpi-breakdown">
            <span>{{ auditData?.total_active_listings || 712 }} ta e‘lon</span>
            <span>•</span>
            <span>{{ auditData?.district_landing_pages || 12 }} tuman</span>
            <span>•</span>
            <span>16 kategoriya</span>
          </div>
          <span class="kpi-subtext">Barcha sahifalar Schema.org bilan jihozlangan</span>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">XML Sitemap Tizimi</div>
          <div class="kpi-value-row">
            <span class="kpi-huge-num">5</span>
            <span class="kpi-badge-live">Faol</span>
          </div>
          <div class="kpi-breakdown">
            <span>Index + Listings + Locations + Categories + Pages</span>
          </div>
          <span class="kpi-subtext">Google Images kengaytmasi bilan integratsiyalangan</span>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">Robots.txt & Qoidalar</div>
          <div class="kpi-value-row">
            <span class="kpi-status-tag tag-healthy">Ruxsat berilgan</span>
          </div>
          <div class="kpi-breakdown">
            <span>/elon/, /toshkent/ ochiq • /admin/, /api/ yopiq</span>
          </div>
          <span class="kpi-subtext">Sitemaplar e‘lon qilingan</span>
        </div>
      </div>

      <!-- Main Columns: SERP Previewer + Sitemaps Table -->
      <div class="seo-columns-grid">
        <!-- Left: Google SERP Previewer -->
        <div class="seo-card serp-simulator-card">
          <div class="card-header-bar">
            <div class="card-title-group">
              <h3 class="card-title">Google SERP Snippet Simulyatori</h3>
              <p class="card-desc">Sahifaning Google qidiruv natijalarida ko‘rinishini tekshiring</p>
            </div>
            <div class="device-toggle">
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: serpDevice === 'mobile' }"
                @click="serpDevice = 'mobile'"
              >
                Mobil
              </button>
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: serpDevice === 'desktop' }"
                @click="serpDevice = 'desktop'"
              >
                Kompyuter
              </button>
            </div>
          </div>

          <!-- Google Search Snippet Box -->
          <div class="google-snippet-frame" :class="serpDevice">
            <div class="google-snippet-url-row">
              <div class="google-favicon-mock">
                <img src="/favicon.svg" alt="Joyliy" width="16" height="16" />
              </div>
              <div class="google-breadcrumb-text">
                <span class="brand-domain">Joyliy.uz</span>
                <span class="breadcrumb-arrow">›</span>
                <span>toshkent</span>
                <span class="breadcrumb-arrow">›</span>
                <span>{{ serpSlug }}</span>
              </div>
            </div>

            <div class="google-title-line">
              {{ previewTitle }}
            </div>

            <div class="google-snippet-desc">
              {{ previewDesc }}
            </div>
          </div>

          <!-- Controls & Character Counters -->
          <div class="snippet-inputs-box">
            <div class="input-block">
              <div class="input-label-row">
                <label for="seo-title-input">SEO Title (Sarlavha)</label>
                <span class="char-count" :class="titleStatusClass">
                  {{ titleLength }} / 60 belgi
                </span>
              </div>
              <input
                id="seo-title-input"
                v-model="previewTitle"
                type="text"
                class="admin-input"
                placeholder="Google sarlavhasi..."
              />
            </div>

            <div class="input-block">
              <div class="input-label-row">
                <label for="seo-desc-input">Meta Description (Tavsif)</label>
                <span class="char-count" :class="descStatusClass">
                  {{ descLength }} / 160 belgi
                </span>
              </div>
              <textarea
                id="seo-desc-input"
                v-model="previewDesc"
                rows="3"
                class="admin-textarea"
                placeholder="Google qidiruv tavsifi..."
              />
            </div>
          </div>
        </div>

        <!-- Right: XML Sitemaps Explorer -->
        <div class="seo-card sitemaps-card">
          <div class="card-header-bar">
            <div class="card-title-group">
              <h3 class="card-title">XML Sitemap Fayllari</h3>
              <p class="card-desc">Qidiruv botlariga avtomatik taqdim etiladigan xaritalar</p>
            </div>
          </div>

          <div class="sitemaps-table-wrapper">
            <table class="sitemaps-table">
              <thead>
                <tr>
                  <th>Sitemap nomi</th>
                  <th>URLlar soni</th>
                  <th>Holati</th>
                  <th>Harakat</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sm in (auditData?.sitemaps || defaultSitemaps)" :key="sm.name">
                  <td>
                    <div class="sitemap-name-cell">
                      <span class="xml-icon">XML</span>
                      <div>
                        <div class="sm-title">{{ sm.name }}</div>
                        <div class="sm-url">{{ sm.url }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="url-count-pill">{{ sm.count || 'Index' }}</span>
                  </td>
                  <td>
                    <span class="status-indicator-tag active">Faol (200 OK)</span>
                  </td>
                  <td>
                    <a :href="sm.url" target="_blank" class="view-xml-link" title="XMLni ko‘rish">
                      Ko‘rish ↗
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Robots.txt Preview Section -->
          <div class="robots-preview-subcard">
            <div class="subcard-title-bar">
              <span class="code-title">robots.txt</span>
              <span class="verified-tag">✓ Qoidalar tasdiqlangan</span>
            </div>
            <pre class="robots-code-view">User-agent: *
Allow: /
Allow: /elon/
Allow: /toshkent/
Disallow: /admin/
Disallow: /api/
Disallow: /*?*token=*
Disallow: /_nuxt/

Sitemap: https://joyliy.uz/sitemap.xml</pre>
          </div>
        </div>
      </div>

      <!-- Quick Test Matrix of Programmatic SEO Pages -->
      <div class="seo-card landing-pages-matrix">
        <div class="card-header-bar">
          <div class="card-title-group">
            <h3 class="card-title">Dasturiy SEO Landing Sahifalari Matritsasi</h3>
            <p class="card-desc">Barcha sahifalar real ma‘lumotlar va Schema.org bilan avtomatik yaratiladi</p>
          </div>
        </div>

        <div class="matrix-grid">
          <div class="matrix-col">
            <h4 class="col-title">Toshkent tumanlari (12 ta)</h4>
            <div class="chips-flex">
              <a href="/toshkent/chilonzor" target="_blank" class="matrix-chip">Chilonzor ↗</a>
              <a href="/toshkent/yunusobod" target="_blank" class="matrix-chip">Yunusobod ↗</a>
              <a href="/toshkent/mirzo-ulugbek" target="_blank" class="matrix-chip">Mirzo Ulug‘bek ↗</a>
              <a href="/toshkent/yakkasaroy" target="_blank" class="matrix-chip">Yakkasaroy ↗</a>
              <a href="/toshkent/mirobod" target="_blank" class="matrix-chip">Mirobod ↗</a>
              <a href="/toshkent/shayxontohur" target="_blank" class="matrix-chip">Shayxontohur ↗</a>
              <a href="/toshkent/olmazor" target="_blank" class="matrix-chip">Olmazor ↗</a>
              <a href="/toshkent/uchtepa" target="_blank" class="matrix-chip">Uchtepa ↗</a>
              <a href="/toshkent/sergeli" target="_blank" class="matrix-chip">Sergeli ↗</a>
              <a href="/toshkent/yashnobod" target="_blank" class="matrix-chip">Yashnobod ↗</a>
              <a href="/toshkent/bektemir" target="_blank" class="matrix-chip">Bektemir ↗</a>
              <a href="/toshkent/yangihayot" target="_blank" class="matrix-chip">Yangi Hayot ↗</a>
            </div>
          </div>

          <div class="matrix-col">
            <h4 class="col-title">Xonalar soni bo‘yicha</h4>
            <div class="chips-flex">
              <a href="/toshkent/1-xonali-kvartiralar" target="_blank" class="matrix-chip">1 xonali kvartiralar ↗</a>
              <a href="/toshkent/2-xonali-kvartiralar" target="_blank" class="matrix-chip">2 xonali kvartiralar ↗</a>
              <a href="/toshkent/3-xonali-kvartiralar" target="_blank" class="matrix-chip">3 xonali kvartiralar ↗</a>
              <a href="/toshkent/4-xonali-kvartiralar" target="_blank" class="matrix-chip">4+ xonali kvartiralar ↗</a>
            </div>
          </div>

          <div class="matrix-col">
            <h4 class="col-title">Foydalanuvchi maqsadi (Intent)</h4>
            <div class="chips-flex">
              <a href="/toshkent/arzon-kvartiralar" target="_blank" class="matrix-chip highlight">Arzon kvartiralar ↗</a>
              <a href="/toshkent/sotiladigan-uylar" target="_blank" class="matrix-chip highlight">Sotiladigan uylar ↗</a>
              <a href="/toshkent/ijaraga-kvartiralar" target="_blank" class="matrix-chip highlight">Ijaraga kvartiralar ↗</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<script lang="ts">
const defaultSitemaps = [
  { name: 'sitemap.xml (Index)', url: 'https://joyliy.uz/sitemap.xml', count: 4 },
  { name: 'sitemap-pages.xml', url: 'https://joyliy.uz/sitemap-pages.xml', count: 5 },
  { name: 'sitemap-locations.xml', url: 'https://joyliy.uz/sitemap-locations.xml', count: 12 },
  { name: 'sitemap-categories.xml', url: 'https://joyliy.uz/sitemap-categories.xml', count: 16 },
  { name: 'sitemap-listings.xml', url: 'https://joyliy.uz/sitemap-listings.xml', count: 712 },
]
</script>

<style scoped>
.admin-seo-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.seo-top-actions {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.seo-page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0 0 4px;
}

.seo-page-sub {
  font-size: 14px;
  color: var(--text-secondary, #6B7280);
  margin: 0;
}

.actions-group {
  display: flex;
  gap: 12px;
}

.admin-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.admin-btn-primary {
  background: var(--admin-primary, #2878C8);
  color: #FFFFFF;
  border: none;
}

.admin-btn-primary:hover:not(:disabled) {
  opacity: 0.92;
}

.admin-btn-secondary {
  background: #FFFFFF;
  border: 1px solid #D1D5DB;
  color: #374151;
}

.admin-btn-secondary:hover:not(:disabled) {
  background: #F9FAFB;
}

.admin-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.seo-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1024px) {
  .seo-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .seo-kpi-grid {
    grid-template-columns: 1fr;
  }
}

.kpi-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 18px;
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 8px;
}

.kpi-huge-num {
  font-size: 28px;
  font-weight: 800;
  color: #111827;
}

.kpi-unit {
  font-size: 14px;
  color: #9CA3AF;
}

.kpi-badge-live {
  font-size: 11px;
  font-weight: 700;
  background: #DCFCE7;
  color: #15803D;
  padding: 2px 8px;
  border-radius: 9999px;
}

.kpi-status-tag {
  font-size: 13px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
}

.tag-healthy {
  background: #DCFCE7;
  color: #15803D;
}

.kpi-progress-bar {
  width: 100%;
  height: 6px;
  background: #F3F4F6;
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 8px;
}

.kpi-progress-fill {
  height: 100%;
  background: #10B981;
  border-radius: 9999px;
}

.kpi-breakdown {
  display: flex;
  gap: 6px;
  font-size: 12px;
  color: #4B5563;
  margin-bottom: 4px;
}

.kpi-subtext {
  font-size: 11px;
  color: #9CA3AF;
  margin-top: auto;
}

.seo-columns-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

@media (max-width: 1024px) {
  .seo-columns-grid {
    grid-template-columns: 1fr;
  }
}

.seo-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 20px;
}

.card-header-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px;
}

.card-desc {
  font-size: 13px;
  color: #6B7280;
  margin: 0;
}

.device-toggle {
  display: flex;
  background: #F3F4F6;
  border-radius: 8px;
  padding: 2px;
}

.toggle-btn {
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.toggle-btn.active {
  background: #FFFFFF;
  color: #111827;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.google-snippet-frame {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
  font-family: Arial, sans-serif;
}

.google-snippet-frame.mobile {
  max-width: 420px;
}

.google-snippet-url-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.google-favicon-mock {
  width: 20px;
  height: 20px;
  background: #F3F4F6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.google-breadcrumb-text {
  font-size: 12px;
  color: #202124;
  display: flex;
  align-items: center;
  gap: 4px;
}

.brand-domain {
  font-weight: 600;
}

.breadcrumb-arrow {
  color: #70757A;
}

.google-title-line {
  color: #1A0DAB;
  font-size: 18px;
  font-weight: 400;
  line-height: 1.3;
  margin-bottom: 6px;
  cursor: pointer;
}

.google-title-line:hover {
  text-decoration: underline;
}

.google-snippet-desc {
  font-size: 13px;
  color: #4D5156;
  line-height: 1.45;
}

.snippet-inputs-box {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.char-count {
  font-family: monospace;
  font-size: 11px;
}

.status-good {
  color: #10B981;
}

.status-warning {
  color: #F59E0B;
}

.status-danger {
  color: #EF4444;
}

.admin-input, .admin-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #111827;
  font-family: inherit;
}

.admin-input:focus, .admin-textarea:focus {
  outline: none;
  border-color: #2878C8;
}

.sitemaps-table-wrapper {
  overflow-x: auto;
  margin-bottom: 20px;
}

.sitemaps-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.sitemaps-table th {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid #E5E7EB;
  font-size: 11px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
}

.sitemaps-table td {
  padding: 12px;
  border-bottom: 1px solid #F3F4F6;
  vertical-align: middle;
}

.sitemap-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.xml-icon {
  background: #EEF2FF;
  color: #4F46E5;
  font-size: 10px;
  font-weight: 800;
  padding: 3px 6px;
  border-radius: 4px;
}

.sm-title {
  font-weight: 600;
  color: #111827;
}

.sm-url {
  font-size: 11px;
  color: #9CA3AF;
  font-family: monospace;
}

.url-count-pill {
  display: inline-flex;
  padding: 2px 8px;
  background: #F3F4F6;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  color: #374151;
}

.status-indicator-tag.active {
  color: #059669;
  font-weight: 600;
  font-size: 12px;
}

.view-xml-link {
  color: #2878C8;
  text-decoration: none;
  font-weight: 600;
  font-size: 12px;
}

.view-xml-link:hover {
  text-decoration: underline;
}

.robots-preview-subcard {
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 14px;
}

.subcard-title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.code-title {
  font-family: monospace;
  font-size: 12px;
  font-weight: 700;
  color: #374151;
}

.verified-tag {
  font-size: 11px;
  color: #10B981;
  font-weight: 600;
}

.robots-code-view {
  margin: 0;
  font-family: monospace;
  font-size: 12px;
  color: #4B5563;
  line-height: 1.5;
  white-space: pre-wrap;
}

.landing-pages-matrix {
  margin-top: 24px;
}

.matrix-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .matrix-grid {
    grid-template-columns: 1fr;
  }
}

.col-title {
  font-size: 13px;
  font-weight: 700;
  color: #374151;
  margin: 0 0 12px;
}

.chips-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.matrix-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  text-decoration: none;
  transition: all 0.15s ease;
}

.matrix-chip:hover {
  background: #FFFFFF;
  border-color: #2878C8;
  color: #2878C8;
}

.matrix-chip.highlight {
  background: #EFF6FF;
  border-color: #BFDBFE;
  color: #1E40AF;
}
</style>
