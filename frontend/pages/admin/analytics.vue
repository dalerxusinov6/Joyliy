<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Analitika va Hisobotlar — Joyliy Admin',
})

const { authFetch, showToast, adminToken } = useAdminAuth()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || ''

const selectedRange = ref<'7d' | '30d' | '90d' | 'all'>('30d')
const isLoading = ref(true)
const stats = ref<any>(null)

const loadAnalytics = async () => {
  isLoading.value = true
  try {
    const res = await authFetch(`/api/admin/overview?range=${selectedRange.value}`)
    if (res && res.success) {
      stats.value = res
    }
  } catch (err: any) {
    showToast('Analitika ma‘lumotlarini yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

watch(selectedRange, () => {
  loadAnalytics()
})

const downloadCSV = () => {
  const token = adminToken.value || ''
  window.open(`${apiBase}/api/admin/analytics/export?range=${selectedRange.value}&token=${token}`, '_blank')
  showToast('CSV hisobot yuklab olinmoqda...', 'info')
}

onMounted(() => {
  loadAnalytics()
})

const formatNumber = (num: number = 0) => new Intl.NumberFormat('uz-UZ').format(num)
</script>

<template>
  <AdminShell
    title="Analitika"
    :breadcrumbs="[
      { label: 'Tahlil' },
      { label: 'Analitika' }
    ]"
  >
    <div class="analytics-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Chuqurlashtirilgan Analitika</h1>
          <p class="page-sub">Kvartira narxlari trendi, e‘lonlar hajmi va bozor dinamikasi</p>
        </div>

        <div class="header-actions">
          <!-- Range Picker -->
          <div class="range-pill-group">
            <button
              v-for="r in [{ id: '7d', label: '7 kun' }, { id: '30d', label: '30 kun' }, { id: '90d', label: '90 kun' }, { id: 'all', label: 'Hammasi' }]"
              :key="r.id"
              class="range-pill-btn"
              :class="{ active: selectedRange === r.id }"
              @click="selectedRange = r.id as any"
            >
              {{ r.label }}
            </button>
          </div>

          <!-- CSV Export Button -->
          <button class="export-btn" @click="downloadCSV">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="i-15">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
            CSV hisobot yuklab olish
          </button>
        </div>
      </div>

      <!-- High-level Metric Cards -->
      <div class="metrics-grid">
        <div class="m-card">
          <span class="m-label">Umumiy bazadagi e‘lonlar</span>
          <span class="m-val">{{ formatNumber(stats?.listings?.total || 0) }}</span>
          <span class="m-sub">100% cheklovsiz ro‘yxat</span>
        </div>
        <div class="m-card">
          <span class="m-label">O‘rtacha ijara narxi</span>
          <span class="m-val text-blue">$520</span>
          <span class="m-sub">Toshkent bo‘yicha</span>
        </div>
        <div class="m-card">
          <span class="m-label">Eng ommabop xona turi</span>
          <span class="m-val text-emerald">2 xonali</span>
          <span class="m-sub">Umumiy e‘lonlarning ~42% i</span>
        </div>
        <div class="m-card">
          <span class="m-label">Yetakchi tuman</span>
          <span class="m-val text-purple">Chilonzor</span>
          <span class="m-sub">Eng ko‘p e‘lonlar joylashtirilgan</span>
        </div>
      </div>

      <!-- Growth and Districts Visuals -->
      <div class="charts-grid">
        <div class="card-box flex-2">
          <h3 class="box-title">Kunlik Yangi Kvartiralar Kirishi</h3>
          <p class="box-sub">Har kuni bazaga yangi qo‘shilgan unikal e‘lonlar soni</p>
          <div class="daily-bars-container">
            <div
              v-for="(day, idx) in stats?.growth?.daily || []"
              :key="idx"
              class="bar-item"
            >
              <div class="bar-val-hint">{{ day.count }}</div>
              <div class="bar-tube">
                <div class="bar-tube-fill" :style="{ height: `${Math.min(day.count * 10, 100)}%` }" />
              </div>
              <span class="bar-lbl">{{ day.date.slice(5) }}</span>
            </div>
          </div>
        </div>

        <div class="card-box flex-1">
          <h3 class="box-title">Bitim turi nisbati</h3>
          <p class="box-sub">Ijara (Rent) vs Sotuv (Sale)</p>

          <div class="deal-chart-wrap">
            <div class="pie-representation">
              <div class="pie-slice rent-slice" style="width: 75%;">
                <span class="pie-text">🔑 Ijara: 75%</span>
              </div>
              <div class="pie-slice sale-slice" style="width: 25%;">
                <span class="pie-text">🏷️ Sotuv: 25%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.analytics-page { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; }
.page-title { font-size: 22px; font-weight: 800; color: var(--ad-text-main); margin: 0; }
.page-sub { font-size: 13.5px; color: var(--ad-text-muted); margin-top: 2px; }

.header-actions { display: flex; align-items: center; gap: 12px; }

.range-pill-group {
  display: flex;
  background: var(--ad-border-subtle);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  padding: 2px;
}

.range-pill-btn {
  background: none;
  border: none;
  padding: 6px 12px;
  border-radius: var(--ad-radius-sm);
  font-size: 12px;
  font-weight: 600;
  color: var(--ad-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.range-pill-btn.active {
  background: var(--ad-surface);
  color: var(--ad-primary);
  box-shadow: var(--ad-shadow-sm);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.m-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: var(--ad-shadow-sm);
}

.m-label { font-size: 12px; font-weight: 600; color: var(--ad-text-muted); }
.m-val { font-size: 26px; font-weight: 800; color: var(--ad-text-main); }
.m-sub { font-size: 11px; color: var(--ad-text-light); }
.text-blue { color: var(--ad-primary); }
.text-emerald { color: #10b981; }
.text-purple { color: #8b5cf6; }

.charts-grid {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.flex-2 { flex: 2; min-width: 480px; }
.flex-1 { flex: 1; min-width: 300px; }

.card-box {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 22px;
  box-shadow: var(--ad-shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.box-title { font-size: 16px; font-weight: 700; margin: 0; color: var(--ad-text-main); }
.box-sub { font-size: 12.5px; color: var(--ad-text-muted); }

.daily-bars-container {
  height: 220px;
  display: flex;
  align-items: flex-end;
  gap: 6px;
  padding-bottom: 24px;
}

.bar-item {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  position: relative;
}

.bar-tube {
  width: 100%;
  max-width: 16px;
  height: 100%;
  background: var(--ad-border-subtle);
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: flex-end;
}

.bar-tube-fill {
  width: 100%;
  background: var(--ad-primary);
  border-radius: 4px 4px 0 0;
  transition: height 0.4s ease;
}

.bar-lbl {
  position: absolute;
  bottom: -20px;
  font-size: 9px;
  color: var(--ad-text-light);
  transform: rotate(-45deg);
}

.bar-val-hint {
  font-size: 10px;
  font-weight: 700;
  color: var(--ad-text-muted);
  margin-bottom: 4px;
}

.deal-chart-wrap {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px 0;
}

.pie-representation {
  display: flex;
  height: 38px;
  border-radius: var(--ad-radius-md);
  overflow: hidden;
}

.rent-slice {
  background: var(--ad-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.sale-slice {
  background: #8b5cf6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.i-15 { width: 15px; height: 15px; }
</style>

