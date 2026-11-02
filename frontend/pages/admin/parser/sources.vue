<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Parser Manbalari — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const sources = ref<any[]>([
  {
    id: 'olx',
    name: 'OLX.uz (Toshkent)',
    url: 'https://www.olx.uz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/',
    status: 'active',
    deal_types: ['rent', 'sale'],
    last_scanned: new Date().toISOString(),
    scan_interval: '08:00, 14:00, 20:00',
    parser_type: 'HTTPX + BeautifulSoup / JSON API',
  },
  {
    id: 'manual',
    name: 'Qo‘lda kiritish (Manual / Direct)',
    url: 'https://joyliy.uz/admin/listings',
    status: 'active',
    deal_types: ['rent', 'sale'],
    last_scanned: new Date().toISOString(),
    scan_interval: 'Instant',
    parser_type: 'Admin / Direct API',
  },
])

const isTesting = ref(false)

const testConnection = async (sourceId: string) => {
  isTesting.value = true
  showToast(`${sourceId} manbasi bilan ulanish sinovdan o‘tkazilmoqda...`, 'info')
  try {
    const res = await authFetch('/api/admin/parser/run', {
      method: 'POST',
      body: { source: sourceId, force: true },
    })
    if (res && res.success) {
      showToast(`${sourceId} muvaffaqiyatli sinovdan o‘tdi!`, 'success')
    } else {
      showToast('Sinov javobi olindi', 'info')
    }
  } catch (err: any) {
    showToast('Sinovda xatolik yuz berdi', 'error')
  } finally {
    isTesting.value = false
  }
}
</script>

<template>
  <AdminShell
    title="Parser manbalari"
    :breadcrumbs="[
      { label: 'Avtomatizatsiya' },
      { label: 'Parser', to: '/admin/parser' },
      { label: 'Manbalar' }
    ]"
  >
    <div class="sources-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Skanerlash Manbalari</h1>
          <p class="page-sub">Joyliy platformasiga e‘lonlar yuklab olinuvchi tashqi portallar va sozlamalar</p>
        </div>
      </div>

      <div class="sources-grid">
        <div v-for="s in sources" :key="s.id" class="source-card">
          <div class="sc-top">
            <div class="sc-title-group">
              <span class="sc-name">{{ s.name }}</span>
              <span class="sc-status-badge">🟢 Aktiv</span>
            </div>
            <button class="test-btn" @click="testConnection(s.id)" :disabled="isTesting">
              Aloqani sinash
            </button>
          </div>

          <div class="sc-body">
            <div class="sc-row">
              <span class="sc-k">URL:</span>
              <a :href="s.url" target="_blank" class="sc-link">{{ s.url }}</a>
            </div>
            <div class="sc-row">
              <span class="sc-k">Dvigatel turi:</span>
              <span class="sc-v font-mono">{{ s.parser_type }}</span>
            </div>
            <div class="sc-row">
              <span class="sc-k">Bitim turlari:</span>
              <span class="sc-v">Ijara va Sotuv (Rent & Sale)</span>
            </div>
            <div class="sc-row">
              <span class="sc-k">Jadval:</span>
              <span class="sc-v">{{ s.scan_interval }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.sources-page { display: flex; flex-direction: column; gap: 20px; }
.page-title { font-size: 22px; font-weight: 800; color: var(--ad-text-main); margin: 0; }
.page-sub { font-size: 13.5px; color: var(--ad-text-muted); margin-top: 2px; }

.sources-grid { display: flex; flex-direction: column; gap: 16px; }

.source-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 20px;
  box-shadow: var(--ad-shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sc-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sc-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--ad-text-main);
}

.sc-status-badge {
  font-size: 11.5px;
  font-weight: 600;
  background: var(--ad-success-light);
  color: var(--ad-success);
  padding: 2px 8px;
  border-radius: 4px;
}

.test-btn {
  background: var(--ad-border-subtle);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  padding: 6px 12px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}

.sc-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  background: var(--ad-bg);
  padding: 12px 16px;
  border-radius: var(--ad-radius-md);
}

.sc-row {
  display: flex;
  gap: 12px;
}

.sc-k { width: 140px; color: var(--ad-text-muted); }
.sc-v { color: var(--ad-text-main); }
.sc-link { color: var(--ad-primary); text-decoration: none; word-break: break-all; }
</style>

