<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Umumiy Ko‘rinish — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const stats = ref<any>(null)
const selectedGrowthView = ref<'daily' | 'weekly'>('daily')

const loadOverview = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/overview')
    if (res && res.success) {
      stats.value = res
    } else {
      showToast('Ma‘lumotlarni yuklab bo‘lmadi', 'error')
    }
  } catch (err: any) {
    showToast('Server bilan aloqa xatosi', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadOverview()
})

const formatNumber = (num: number = 0) => {
  return new Intl.NumberFormat('uz-UZ').format(num)
}

const formatPrice = (price: number = 0, currency: string = 'USD') => {
  const sym = currency === 'USD' ? '$' : 'so‘m'
  return `${new Intl.NumberFormat('uz-UZ').format(price)} ${sym}`
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleString('uz-UZ', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}

// Compute max for chart scaling
const maxGrowthCount = computed(() => {
  if (!stats.value?.growth?.daily?.length) return 10
  const max = Math.max(...stats.value.growth.daily.map((g: any) => g.count))
  return max > 0 ? max : 10
})
</script>

<template>
  <AdminShell title="Umumiy ko‘rinish">
    <div class="overview-dashboard">
      <!-- Top Title and Controls Bar -->
      <div class="page-title-row">
        <div>
          <h1 class="page-main-title">Boshqaruv Paneli</h1>
          <p class="page-sub-title">Joyliy.uz tizimi real vaqt holati, e‘lonlar tahlili va avtomatizatsiya monitoringi</p>
        </div>
        <div class="top-controls">
          <button class="refresh-data-btn" @click="loadOverview" :disabled="isLoading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="rf-icon" :class="{ 'spin-icon': isLoading }">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            Yangilash
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && !stats" class="dashboard-loading-box">
        <div class="spinner-circle" />
        <span>Tizim statistikasi tahlil qilinmoqda...</span>
      </div>

      <div v-else-if="stats" class="dashboard-content">
        <!-- 1. KPI Metric Cards Grid -->
        <div class="kpi-grid">
          <!-- Total Listings -->
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-label">Jami E‘lonlar</span>
              <div class="kpi-icon-box bg-blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 6h16M4 12h16M4 18h16"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value">{{ formatNumber(stats.listings?.total) }}</div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Faol: <strong>{{ formatNumber(stats.listings?.active) }}</strong></span>
              <span class="kpi-badge-green">100% cheklovsiz</span>
            </div>
          </div>

          <!-- Moderation Queue -->
          <NuxtLink to="/admin/listings?status=pending" class="kpi-card text-decoration-none">
            <div class="kpi-top">
              <span class="kpi-label">Moderatsiya Navbati</span>
              <div class="kpi-icon-box bg-amber">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value text-amber">{{ formatNumber(stats.listings?.pending || stats.summary?.pending_moderation) }}</div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Saytdan tushgan e‘lonlar</span>
              <span class="kpi-badge-amber">Tasdiqlash →</span>
            </div>
          </NuxtLink>

          <!-- Roommates Moderation Queue -->
          <NuxtLink to="/admin/roommates?status=pending" class="kpi-card text-decoration-none">
            <div class="kpi-top">
              <span class="kpi-label">Hamxona Anketalari</span>
              <div class="kpi-icon-box bg-purple">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value text-purple">{{ formatNumber(stats.roommates?.pending || 0) }}</div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Jami anketalar: <strong>{{ formatNumber(stats.roommates?.total || 0) }}</strong></span>
              <span class="kpi-badge-amber" v-if="stats.roommates?.pending">Tasdiqlash →</span>
              <span class="kpi-badge-green" v-else>Tekshirilgan</span>
            </div>
          </NuxtLink>

          <!-- New Today -->
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-label">Bugun Topilganlar</span>
              <div class="kpi-icon-box bg-emerald">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 5v14M5 12h14"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value text-emerald">+{{ formatNumber(stats.listings?.new_today) }}</div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Haftada: <strong>+{{ formatNumber(stats.listings?.published_this_week) }}</strong></span>
              <span class="kpi-badge-blue">Bugungi skan</span>
            </div>
          </div>

          <!-- Updated Today -->
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-label">Bugun Yangilangan</span>
              <div class="kpi-icon-box bg-amber">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value">{{ formatNumber(stats.listings?.updated_today) }}</div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Arxivlangan: <strong>{{ formatNumber(stats.listings?.archived) }}</strong></span>
              <span class="kpi-badge-gray">Narx o‘zgarishlari</span>
            </div>
          </div>

          <!-- Telegram Published -->
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-label">Telegram Nashr</span>
              <div class="kpi-icon-box bg-purple">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value text-purple">{{ formatNumber(stats.telegram?.total_published) }}</div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Bugun: <strong>{{ formatNumber(stats.telegram?.published_today) }}</strong></span>
              <span class="kpi-badge-purple">Kanal: @joyliy_uz</span>
            </div>
          </div>

          <!-- Registered Users -->
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-label">Foydalanuvchilar</span>
              <div class="kpi-icon-box bg-indigo">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value">{{ formatNumber(stats.users?.total) }}</div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Adminlar: <strong>{{ stats.users?.admins }}</strong></span>
              <span class="kpi-badge-blue">Telegram bot orqali</span>
            </div>
          </div>

          <!-- Parser Success Rate -->
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-label">Parser Samaradorligi</span>
              <div class="kpi-icon-box bg-emerald">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
            </div>
            <div class="kpi-value text-emerald">
              {{ stats.parser?.success_rate_percent }}%
            </div>
            <div class="kpi-footer">
              <span class="kpi-sub-text">Skanlar: <strong>{{ stats.parser?.successful_scans_30d }} muvaffaqiyatli</strong></span>
              <span class="kpi-badge-green">Barqaror</span>
            </div>
          </div>
        </div>

        <!-- 2. Charts Section (Growth & Distribution) -->
        <div class="analytics-row">
          <!-- A. Growth Chart (Last 30 Days) -->
          <div class="analytics-card flex-2">
            <div class="card-header-row">
              <div class="card-title-group">
                <h3 class="card-title">Yangi e‘lonlar o‘sish dinamikasi</h3>
                <span class="card-desc">So‘nggi 30 kunda bazaga qo‘shilgan kvartiralar soni</span>
              </div>
              <div class="chart-legend">
                <span class="legend-dot bg-blue" />
                <span class="legend-text">Kunlik yangi e‘lonlar</span>
              </div>
            </div>

            <!-- SVG Bar / Area visualization -->
            <div class="growth-chart-container">
              <div v-if="stats.growth?.daily?.length" class="bar-chart-flex">
                <div
                  v-for="(day, dIdx) in stats.growth.daily"
                  :key="dIdx"
                  class="chart-bar-col"
                  :title="`${day.date}: ${day.count} ta e‘lon`"
                >
                  <div class="bar-tooltip">{{ day.count }}</div>
                  <div class="bar-track">
                    <div
                      class="bar-fill"
                      :style="{ height: `${Math.max((day.count / maxGrowthCount) * 100, 4)}%` }"
                    />
                  </div>
                  <span class="bar-date-label">{{ day.date.slice(5) }}</span>
                </div>
              </div>
              <div v-else class="chart-empty">
                Ma‘lumotlar to‘planmoqda...
              </div>
            </div>
          </div>

          <!-- B. Deal Type & Room Distribution -->
          <div class="analytics-card flex-1">
            <div class="card-header-row">
              <div class="card-title-group">
                <h3 class="card-title">E‘lonlar tuzilmasi</h3>
                <span class="card-desc">Ijara vs Sotuv va xonalar taqsimoti</span>
              </div>
            </div>

            <!-- Deal Type Breakdown -->
            <div class="deal-type-breakdown">
              <div class="dt-item">
                <div class="dt-info">
                  <span class="dt-name">🔑 Ijara (Rent)</span>
                  <span class="dt-count">{{ formatNumber(stats.distribution?.deal_type?.rent || 0) }}</span>
                </div>
                <div class="dt-progress-track">
                  <div
                    class="dt-progress-bar bg-blue"
                    :style="{ width: `${stats.listings?.total ? ((stats.distribution?.deal_type?.rent || 0) / stats.listings.total) * 100 : 0}%` }"
                  />
                </div>
              </div>

              <div class="dt-item">
                <div class="dt-info">
                  <span class="dt-name">🏷️ Sotuv (Sale)</span>
                  <span class="dt-count">{{ formatNumber(stats.distribution?.deal_type?.sale || 0) }}</span>
                </div>
                <div class="dt-progress-track">
                  <div
                    class="dt-progress-bar bg-purple"
                    :style="{ width: `${stats.listings?.total ? ((stats.distribution?.deal_type?.sale || 0) / stats.listings.total) * 100 : 0}%` }"
                  />
                </div>
              </div>
            </div>

            <div class="divider-line" />

            <!-- Rooms breakdown -->
            <div class="rooms-breakdown-list">
              <div class="sub-heading">Xonalar bo‘yicha:</div>
              <div class="rooms-chips-grid">
                <div
                  v-for="(count, room) in stats.distribution?.rooms || {}"
                  :key="room"
                  class="room-chip"
                >
                  <span class="rc-label">{{ room }} xonali</span>
                  <span class="rc-val">{{ formatNumber(count) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. District Distribution Row -->
        <div class="analytics-card">
          <div class="card-header-row">
            <div class="card-title-group">
              <h3 class="card-title">Toshkent tumanlari bo‘yicha taqsimot</h3>
              <span class="card-desc">Eng ko‘p e‘lonlar joylashtirilgan hududlar</span>
            </div>
            <NuxtLink to="/admin/map" class="link-action">Xaritada ko‘rish →</NuxtLink>
          </div>

          <div class="districts-grid">
            <div
              v-for="(count, district) in stats.distribution?.districts || {}"
              :key="district"
              class="district-stat-card"
            >
              <div class="dst-name">{{ district }}</div>
              <div class="dst-count">{{ formatNumber(count) }} ta</div>
              <div class="dst-track">
                <div
                  class="dst-fill"
                  :style="{ width: `${stats.listings?.total ? Math.min((count / (stats.listings.total / 4)) * 100, 100) : 0}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Automation & Health Two-Column Row -->
        <div class="analytics-row">
          <!-- Parser Health Card -->
          <div class="analytics-card flex-1">
            <div class="card-header-row">
              <div class="card-title-group">
                <h3 class="card-title">Avtomatik Parser Holati</h3>
                <span class="card-desc">08:00, 14:00, 20:00 jadvalli skanerlash</span>
              </div>
              <span class="status-badge" :class="stats.parser?.is_running ? 'badge-green' : 'badge-gray'">
                {{ stats.parser?.is_running ? '🟢 Ishlamoqda' : '⚪ Kutish rejimida' }}
              </span>
            </div>

            <div class="health-meta-grid">
              <div class="meta-item">
                <span class="m-label">Oxirgi skanerlash:</span>
                <span class="m-val">{{ formatDate(stats.parser?.last_run_at) }}</span>
              </div>
              <div class="meta-item">
                <span class="m-label">O‘rtacha skan vaqti:</span>
                <span class="m-val">{{ stats.parser?.avg_duration_seconds }} soniya</span>
              </div>
              <div class="meta-item">
                <span class="m-label">Dublikatlar ushlandi:</span>
                <span class="m-val">{{ formatNumber(stats.parser?.duplicates_detected_30d) }} ta</span>
              </div>
              <div class="meta-item">
                <span class="m-label">Xatoliklar (30 kun):</span>
                <span class="m-val text-danger">{{ stats.parser?.failed_scans_30d }} ta</span>
              </div>
            </div>

            <div class="card-bottom-actions">
              <NuxtLink to="/admin/parser" class="secondary-link-btn">
                Batafsil boshqarish →
              </NuxtLink>
            </div>
          </div>

          <!-- Telegram Publishing Status -->
          <div class="analytics-card flex-1">
            <div class="card-header-row">
              <div class="card-title-group">
                <h3 class="card-title">Telegram Kanal Integratsiyasi</h3>
                <span class="card-desc">Kanal: <strong>@joyliy_uz</strong></span>
              </div>
              <span class="status-badge badge-blue">
                ⚡ Real vaqtda avto-post
              </span>
            </div>

            <div class="health-meta-grid">
              <div class="meta-item">
                <span class="m-label">Jami postlar:</span>
                <span class="m-val">{{ formatNumber(stats.telegram?.total_published) }} ta</span>
              </div>
              <div class="meta-item">
                <span class="m-label">Bugun post qilindi:</span>
                <span class="m-val text-emerald">+{{ formatNumber(stats.telegram?.published_today) }} ta</span>
              </div>
              <div class="meta-item">
                <span class="m-label">Navbatda kutilayotgan:</span>
                <span class="m-val">{{ formatNumber(stats.telegram?.pending_queue) }} ta</span>
              </div>
              <div class="meta-item">
                <span class="m-label">Xato berganlar:</span>
                <span class="m-val" :class="stats.telegram?.failed_publications > 0 ? 'text-danger' : ''">
                  {{ stats.telegram?.failed_publications }} ta
                </span>
              </div>
            </div>

            <div class="card-bottom-actions">
              <NuxtLink to="/admin/telegram" class="secondary-link-btn">
                Nashriyot navbatini boshqarish →
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- 5. Latest Listings & Recent Audit Events -->
        <div class="analytics-row">
          <!-- Latest Listings Table -->
          <div class="analytics-card flex-2">
            <div class="card-header-row">
              <div class="card-title-group">
                <h3 class="card-title">Oxirgi topilgan e‘lonlar</h3>
                <span class="card-desc">Bazaga oxirgi qo‘shilgan kvartiralar ro‘yxati</span>
              </div>
              <NuxtLink to="/admin/listings" class="link-action">Barchasini ko‘rish →</NuxtLink>
            </div>

            <div class="table-responsive">
              <table class="ad-table">
                <thead>
                  <tr>
                    <th>Rasm</th>
                    <th>Sarlavha</th>
                    <th>Narx</th>
                    <th>Tuman</th>
                    <th>Manba</th>
                    <th>Vaqt</th>
                    <th>Amallar</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in stats.latest_listings || []" :key="item.id">
                    <td>
                      <img
                        :src="item.image_url || '/placeholder.png'"
                        class="thumb-img"
                        alt="Kvartira"
                        loading="lazy"
                        onerror="this.src='/placeholder.png'"
                      />
                    </td>
                    <td>
                      <div class="table-title-cell">
                        <NuxtLink :to="`/admin/listings/${item.id}`" class="listing-title-link">
                          {{ item.title }}
                        </NuxtLink>
                        <span class="table-meta-sub">{{ item.rooms }} xona • {{ item.area_m2 || '-' }} m² • {{ item.floor || '-' }}/{{ item.total_floors || '-' }}-qavat</span>
                      </div>
                    </td>
                    <td class="font-mono font-semibold">
                      {{ formatPrice(item.price, item.currency) }}
                    </td>
                    <td>
                      <span class="district-badge">{{ item.district }}</span>
                    </td>
                    <td>
                      <span class="source-tag">{{ item.source }}</span>
                    </td>
                    <td class="text-muted text-xs">
                      {{ formatDate(item.created_at) }}
                    </td>
                    <td>
                      <NuxtLink :to="`/admin/listings/${item.id}`" class="row-action-btn" title="Tahrirlash">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                      </NuxtLink>
                    </td>
                  </tr>
                  <tr v-if="!stats.latest_listings?.length">
                    <td colspan="7" class="text-center text-muted py-4">
                      Hozircha e‘lonlar mavjud emas
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Recent Audit Events -->
          <div class="analytics-card flex-1">
            <div class="card-header-row">
              <div class="card-title-group">
                <h3 class="card-title">Tizim hodisalari</h3>
                <span class="card-desc">Adminlar va tizim harakatlari</span>
              </div>
              <NuxtLink to="/admin/logs" class="link-action">Jurnal →</NuxtLink>
            </div>

            <div class="activity-timeline">
              <div
                v-for="(log, lIdx) in stats.recent_activity || []"
                :key="lIdx"
                class="activity-event-item"
              >
                <div class="event-indicator-line">
                  <div class="event-dot" />
                </div>
                <div class="event-content">
                  <div class="event-top">
                    <span class="event-admin">{{ log.admin_username }}</span>
                    <span class="event-action-badge">{{ log.action }}</span>
                  </div>
                  <div class="event-desc">{{ log.target_type }}: {{ log.target_id || '-' }}</div>
                  <div class="event-time">{{ formatDate(log.created_at) }}</div>
                </div>
              </div>
              <div v-if="!stats.recent_activity?.length" class="text-center text-muted py-4 text-xs">
                Oxirgi tizim hodisalari qayd etilmagan
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Fallback State -->
      <div v-else class="dashboard-error-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="error-icon">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <p class="error-msg">Statistika ma‘lumotlarini yuklashda xatolik yuz berdi</p>
        <button class="retry-btn" @click="loadOverview">Qayta urinish</button>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.overview-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-main-title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin: 0;
  color: var(--ad-text-main);
}

.page-sub-title {
  font-size: 13.5px;
  color: var(--ad-text-muted);
  margin-top: 4px;
}

.refresh-data-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  padding: 8px 14px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  color: var(--ad-text-main);
  cursor: pointer;
  transition: all 0.15s;
}

.refresh-data-btn:hover:not(:disabled) {
  border-color: var(--ad-primary);
  color: var(--ad-primary);
}

.rf-icon {
  width: 15px;
  height: 15px;
}

.dashboard-loading-box {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 80px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--ad-text-muted);
}

.dashboard-error-box {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 60px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  text-align: center;
}

.error-icon {
  width: 36px;
  height: 36px;
  color: var(--ad-danger, #ef4444);
}

.error-msg {
  font-size: 14px;
  color: var(--ad-text-muted);
  margin: 0;
}

.retry-btn {
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s ease;
}
.retry-btn:hover { opacity: 0.9; }

.spinner-circle {
  width: 32px;
  height: 32px;
  border: 3px solid var(--ad-border);
  border-top-color: var(--ad-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.kpi-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: var(--ad-shadow-sm);
  transition: transform 0.15s, border-color 0.15s;
}

.kpi-card:hover {
  border-color: var(--ad-primary);
  transform: translateY(-2px);
}

.kpi-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kpi-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--ad-text-muted);
}

.kpi-icon-box {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon-box svg {
  width: 18px;
  height: 18px;
}

.bg-blue { background: rgba(40, 120, 200, 0.1); color: var(--ad-primary); }
.bg-emerald { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.bg-amber { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.bg-purple { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.bg-indigo { background: rgba(99, 102, 241, 0.1); color: #6366f1; }

.kpi-value {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--ad-text-main);
  line-height: 1;
}

.text-emerald { color: #10b981; }
.text-amber { color: #d97706; }
.text-purple { color: #8b5cf6; }
.text-danger { color: #ef4444; }

.kpi-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid var(--ad-border-subtle);
  font-size: 12px;
}

.kpi-sub-text {
  color: var(--ad-text-muted);
}

.kpi-badge-amber {
  background: rgba(245, 158, 11, 0.15);
  color: #d97706;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10.5px;
}

.kpi-badge-green {
  background: var(--ad-success-light);
  color: var(--ad-success);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10.5px;
}

.kpi-badge-blue {
  background: var(--ad-primary-light);
  color: var(--ad-primary);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10.5px;
}

.kpi-badge-gray {
  background: var(--ad-border-subtle);
  color: var(--ad-text-muted);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10.5px;
}

.kpi-badge-purple {
  background: var(--ad-purple-light);
  color: var(--ad-purple);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10.5px;
}

/* Analytics Cards & Grid */
.analytics-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.flex-1 { flex: 1; min-width: 320px; }
.flex-2 { flex: 2; min-width: 500px; }

.analytics-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: var(--ad-shadow-sm);
}

.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.card-title-group {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--ad-text-main);
  margin: 0;
  letter-spacing: -0.3px;
}

.card-desc {
  font-size: 12.5px;
  color: var(--ad-text-muted);
  margin-top: 2px;
}

.chart-legend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--ad-text-muted);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.link-action {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--ad-primary);
  text-decoration: none;
}

.link-action:hover {
  text-decoration: underline;
}

/* Growth Bar Chart */
.growth-chart-container {
  height: 200px;
  margin-top: 10px;
}

.bar-chart-flex {
  display: flex;
  align-items: flex-end;
  height: 100%;
  gap: 4px;
  padding-bottom: 24px;
  position: relative;
}

.chart-bar-col {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  position: relative;
  group: hover;
}

.bar-track {
  width: 100%;
  max-width: 14px;
  height: 100%;
  display: flex;
  align-items: flex-end;
  background: var(--ad-border-subtle);
  border-radius: 3px 3px 0 0;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  background: var(--ad-primary);
  border-radius: 3px 3px 0 0;
  transition: height 0.4s ease;
}

.chart-bar-col:hover .bar-fill {
  background: #1e5ba0;
}

.bar-date-label {
  position: absolute;
  bottom: -20px;
  font-size: 9px;
  color: var(--ad-text-light);
  transform: rotate(-45deg);
  white-space: nowrap;
}

.bar-tooltip {
  position: absolute;
  top: -24px;
  background: var(--ad-text-main);
  color: var(--ad-surface);
  font-size: 10px;
  padding: 2px 5px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.15s;
  pointer-events: none;
  font-weight: 600;
}

.chart-bar-col:hover .bar-tooltip {
  opacity: 1;
}

.chart-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ad-text-muted);
  font-size: 13px;
}

/* Deal Type & Rooms */
.deal-type-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dt-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dt-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
  color: var(--ad-text-main);
}

.dt-progress-track {
  height: 8px;
  background: var(--ad-border-subtle);
  border-radius: 4px;
  overflow: hidden;
}

.dt-progress-bar {
  height: 100%;
  border-radius: 4px;
}

.divider-line {
  height: 1px;
  background: var(--ad-border-subtle);
  margin: 6px 0;
}

.rooms-breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sub-heading {
  font-size: 12px;
  font-weight: 600;
  color: var(--ad-text-muted);
}

.rooms-chips-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.room-chip {
  background: var(--ad-border-subtle);
  padding: 6px 10px;
  border-radius: var(--ad-radius-md);
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.rc-label {
  color: var(--ad-text-muted);
}

.rc-val {
  font-weight: 700;
  color: var(--ad-text-main);
}

/* Districts Grid */
.districts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.district-stat-card {
  background: var(--ad-bg);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dst-name {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--ad-text-main);
}

.dst-count {
  font-size: 14px;
  font-weight: 700;
  color: var(--ad-primary);
}

.dst-track {
  height: 4px;
  background: var(--ad-border);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}

.dst-fill {
  height: 100%;
  background: var(--ad-primary);
}

/* Health Cards */
.health-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  background: var(--ad-bg);
  padding: 14px;
  border-radius: var(--ad-radius-md);
  border: 1px solid var(--ad-border-subtle);
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.m-label {
  font-size: 11.5px;
  color: var(--ad-text-muted);
}

.m-val {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ad-text-main);
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 12px;
}

.badge-green { background: var(--ad-success-light); color: var(--ad-success); }
.badge-blue { background: var(--ad-primary-light); color: var(--ad-primary); }
.badge-gray { background: var(--ad-border-subtle); color: var(--ad-text-muted); }

.card-bottom-actions {
  display: flex;
  justify-content: flex-end;
}

.secondary-link-btn {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--ad-primary);
  text-decoration: none;
}

.secondary-link-btn:hover {
  text-decoration: underline;
}

/* Table */
.table-responsive {
  overflow-x: auto;
}

.ad-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.ad-table th {
  padding: 10px 12px;
  font-weight: 600;
  color: var(--ad-text-muted);
  border-bottom: 1px solid var(--ad-border);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.ad-table td {
  padding: 12px;
  border-bottom: 1px solid var(--ad-border-subtle);
  vertical-align: middle;
}

.thumb-img {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  object-fit: cover;
  background: var(--ad-border-subtle);
}

.table-title-cell {
  display: flex;
  flex-direction: column;
  max-width: 240px;
}

.listing-title-link {
  font-weight: 600;
  color: var(--ad-text-main);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.listing-title-link:hover {
  color: var(--ad-primary);
}

.table-meta-sub {
  font-size: 11px;
  color: var(--ad-text-muted);
}

.district-badge {
  background: var(--ad-border-subtle);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11.5px;
  color: var(--ad-text-main);
}

.source-tag {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--ad-text-muted);
}

.row-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--ad-border);
  color: var(--ad-text-muted);
  text-decoration: none;
  transition: all 0.15s;
}

.row-action-btn:hover {
  background: var(--ad-primary-light);
  color: var(--ad-primary);
  border-color: var(--ad-primary);
}

.row-action-btn svg {
  width: 14px;
  height: 14px;
}

/* Activity Timeline */
.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.activity-event-item {
  display: flex;
  gap: 12px;
}

.event-indicator-line {
  position: relative;
  display: flex;
  justify-content: center;
  width: 14px;
}

.event-dot {
  width: 8px;
  height: 8px;
  background: var(--ad-primary);
  border-radius: 50%;
  margin-top: 4px;
}

.event-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-admin {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--ad-text-main);
}

.event-action-badge {
  font-size: 10px;
  font-weight: 600;
  background: var(--ad-border-subtle);
  color: var(--ad-text-muted);
  padding: 1px 5px;
  border-radius: 4px;
  text-transform: uppercase;
}

.event-desc {
  font-size: 12px;
  color: var(--ad-text-muted);
}

.event-time {
  font-size: 11px;
  color: var(--ad-text-light);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .analytics-row {
    flex-direction: column;
  }
}
</style>

