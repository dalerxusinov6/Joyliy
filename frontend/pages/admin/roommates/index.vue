<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Hamxona Anketalari — Joyliy Admin',
})

const route = useRoute()
const router = useRouter()
const { authFetch, showToast, hasRole } = useAdminAuth()

const isLoading = ref(true)
const roommates = ref<any[]>([])
const activeTab = ref<'all' | 'pending' | 'active' | 'inactive'>('all')
const searchQuery = ref('')
const districtFilter = ref('')
const genderFilter = ref('')

const counts = ref({
  total: 0,
  pending: 0,
  active: 0,
})

// Delete modal
const showDeleteConfirm = ref(false)
const deletingProfile = ref<any>(null)
const isDeleting = ref(false)

const districtsList = [
  'Chilonzor', 'Yunusobod', 'Mirzo Ulug‘bek', 'Yakkasaroy', 'Mirobod',
  'Shayxontohur', 'Olmazor', 'Uchtepa', 'Yashnobod', 'Sergeli', 'Bektemir', 'Yangihayot'
]

const loadRoommates = async () => {
  isLoading.value = true
  try {
    const params: Record<string, any> = {
      status: activeTab.value,
      limit: 100,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (districtFilter.value) params.district = districtFilter.value
    if (genderFilter.value) params.gender = genderFilter.value

    const queryStr = new URLSearchParams(params).toString()
    const res = await authFetch(`/api/admin/roommates?${queryStr}`)
    if (res && res.success) {
      roommates.value = res.items || []
      counts.value = {
        total: res.total || 0,
        pending: res.pending_count || 0,
        active: res.active_count || 0,
      }
    }
  } catch (err: any) {
    showToast('Hamxona anketalarini yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

// Watchers
watch(activeTab, () => {
  loadRoommates()
})

watch(() => route.query.status, (newStatus) => {
  if (newStatus && ['all', 'pending', 'active', 'inactive'].includes(newStatus as string)) {
    activeTab.value = newStatus as any
  }
})

onMounted(() => {
  if (route.query.status && ['all', 'pending', 'active', 'inactive'].includes(route.query.status as string)) {
    activeTab.value = route.query.status as any
  }
  loadRoommates()
})

// Actions
const approveProfile = async (item: any) => {
  try {
    const res = await authFetch(`/api/admin/roommates/${item.id}/approve`, {
      method: 'POST',
    })
    if (res && res.success) {
      showToast(`Anketa #${item.id} (${item.name}) muvaffaqiyatli tasdiqlandi va saytda faollashtirildi!`, 'success')
      await loadRoommates()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Tasdiqlashda xatolik yuz berdi', 'error')
  }
}

const rejectProfile = async (item: any) => {
  try {
    const res = await authFetch(`/api/admin/roommates/${item.id}/reject`, {
      method: 'POST',
      body: { reason: 'Admin tomonidan rad etildi' },
    })
    if (res && res.success) {
      showToast(`Anketa #${item.id} (${item.name}) nofaol qilindi`, 'info')
      await loadRoommates()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Rad etishda xatolik yuz berdi', 'error')
  }
}

const confirmDelete = (item: any) => {
  deletingProfile.value = item
  showDeleteConfirm.value = true
}

const deleteProfile = async () => {
  if (!deletingProfile.value) return
  isDeleting.value = true
  try {
    const res = await authFetch(`/api/admin/roommates/${deletingProfile.value.id}`, {
      method: 'DELETE',
    })
    if (res && res.success) {
      showToast('Anketa butunlay o‘chirildi', 'success')
      showDeleteConfirm.value = false
      deletingProfile.value = null
      await loadRoommates()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'O‘chirishda xatolik yuz berdi', 'error')
  } finally {
    isDeleting.value = false
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('uz-UZ', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <AdminShell title="Hamxona Anketalari" :breadcrumbs="[{ label: 'Boshqaruv' }, { label: 'Hamxona Anketalari' }]">
    <div class="roommates-admin-page">
      <!-- Title & Header Bar -->
      <div class="page-header-row">
        <div>
          <h1 class="page-title">Hamxona Anketalari</h1>
          <p class="page-subtitle">
            Saytdan foydalanuvchilar yuborgan hamxona qidiruv anketalari moderatsiyasi va boshqaruvi
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="loadRoommates" :disabled="isLoading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="rf-icon" :class="{ 'spin-icon': isLoading }">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            Yangilash
          </button>
        </div>
      </div>

      <!-- Metric Stats Cards -->
      <div class="stats-row">
        <div class="metric-card" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
          <div class="metric-label">Jami Anketalar</div>
          <div class="metric-value">{{ counts.total }}</div>
          <div class="metric-hint">Bazadagi barcha arizalar</div>
        </div>
        <div class="metric-card card-pending" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">
          <div class="metric-label">Moderatsiya Kutilmoqda</div>
          <div class="metric-value text-amber">{{ counts.pending }}</div>
          <div class="metric-hint">Saytdan tushgan, tasdiqlash kerak</div>
        </div>
        <div class="metric-card card-active" :class="{ active: activeTab === 'active' }" @click="activeTab = 'active'">
          <div class="metric-label">Faol / Tasdiqlangan</div>
          <div class="metric-value text-emerald">{{ counts.active }}</div>
          <div class="metric-hint">Saytda ommaviy ko‘rinmoqda</div>
        </div>
      </div>

      <!-- Filters & Search Toolbar -->
      <div class="filter-card">
        <!-- Status Tabs -->
        <div class="tabs-nav">
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'all' }"
            @click="activeTab = 'all'"
          >
            Barchasi ({{ counts.total }})
          </button>
          <button
            type="button"
            class="tab-btn tab-pending"
            :class="{ active: activeTab === 'pending' }"
            @click="activeTab = 'pending'"
          >
            <span class="dot-indicator bg-amber"></span>
            Moderatsiya ({{ counts.pending }})
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'active' }"
            @click="activeTab = 'active'"
          >
            Faol ({{ counts.active }})
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'inactive' }"
            @click="activeTab = 'inactive'"
          >
            Nofaol / Rad etilgan
          </button>
        </div>

        <!-- Search & Select Inputs -->
        <div class="filter-inputs-row">
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-svg">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Ism, Telegram, kasb yoki matn bo‘yicha qidirish..."
              @keyup.enter="loadRoommates"
            />
            <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''; loadRoommates()">×</button>
          </div>

          <div class="select-group">
            <select v-model="districtFilter" @change="loadRoommates" class="form-select">
              <option value="">Barcha tumanlar</option>
              <option v-for="d in districtsList" :key="d" :value="d">{{ d }}</option>
            </select>

            <select v-model="genderFilter" @change="loadRoommates" class="form-select">
              <option value="">Barcha jinslar</option>
              <option value="male">Erkak / Yigit</option>
              <option value="female">Ayol / Qiz</option>
            </select>

            <button class="btn btn-primary-outline" @click="loadRoommates">
              Filtrlash
            </button>
          </div>
        </div>
      </div>

      <!-- Main Content Table / List -->
      <div class="table-container">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner-circle"></div>
          <p>Anketalar yuklanmoqda...</p>
        </div>

        <div v-else-if="!roommates.length" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h3>Hech qanday anketa topilmadi</h3>
          <p>Ushbu toifa yoki filtrlarga mos keluvchi anketalar mavjud emas.</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nomzod</th>
              <th>Jinsi & Yoshi</th>
              <th>Tuman & Byudjet</th>
              <th>Kasbi & Qiziqishlar</th>
              <th>Telegram Aloqa</th>
              <th>Yaratilgan Sana</th>
              <th>Holat</th>
              <th class="text-right">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in roommates" :key="item.id" :class="{ 'row-pending': !item.is_active }">
              <td class="cell-id">#{{ item.id }}</td>
              <td class="cell-user">
                <div class="user-block">
                  <div class="user-avatar" :class="item.gender === 'female' ? 'avatar-pink' : 'avatar-blue'">
                    {{ item.name ? item.name[0].toUpperCase() : 'U' }}
                  </div>
                  <div>
                    <div class="user-name">
                      {{ item.name }}
                      <span v-if="item.is_verified" class="verified-check" title="Tasdiqlangan">✓</span>
                    </div>
                    <div class="user-bio" v-if="item.bio">«{{ item.bio.slice(0, 60) }}{{ item.bio.length > 60 ? '...' : '' }}»</div>
                  </div>
                </div>
              </td>
              <td class="cell-specs">
                <div class="gender-pill" :class="item.gender === 'female' ? 'gender-f' : 'gender-m'">
                  {{ item.gender === 'female' ? 'Qiz' : (item.gender === 'male' ? 'Yigit' : 'Ixtiyoriy') }}
                </div>
                <span class="age-text">{{ item.age || 20 }} yosh</span>
              </td>
              <td class="cell-location">
                <div class="district-badge">{{ item.preferred_district || (item.preferred_districts && item.preferred_districts[0]) || 'Toshkent' }}</div>
                <div class="budget-text">{{ item.budget_formatted || `${(item.budget_uzs || 0).toLocaleString()} so‘m` }}</div>
              </td>
              <td class="cell-occ">
                <div class="occ-title">{{ item.occupation || 'Talaba' }}</div>
                <div class="tags-wrap" v-if="item.lifestyle_tags && item.lifestyle_tags.length">
                  <span v-for="tag in item.lifestyle_tags.slice(0, 2)" :key="tag" class="mini-tag">
                    {{ tag }}
                  </span>
                  <span v-if="item.lifestyle_tags.length > 2" class="mini-tag tag-more">+{{ item.lifestyle_tags.length - 2 }}</span>
                </div>
              </td>
              <td class="cell-contact">
                <a
                  :href="`https://t.me/${(item.contact_telegram || '').replace(/^@/, '')}`"
                  target="_blank"
                  rel="noopener"
                  class="tg-btn-link"
                  title="Telegram profiliga o‘tish"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" class="tg-svg-icon">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.75-.55 2.92-1.27 4.86-2.11 5.83-2.52 2.77-1.18 3.35-1.39 3.73-1.39.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
                  </svg>
                  @{{ (item.contact_telegram || '').replace(/^@/, '') }}
                </a>
              </td>
              <td class="cell-date">{{ formatDate(item.created_at) }}</td>
              <td class="cell-status">
                <span v-if="!item.is_active" class="badge-status badge-pending">
                  <span class="status-dot dot-amber"></span>
                  Kutilmoqda
                </span>
                <span v-else class="badge-status badge-active">
                  <span class="status-dot dot-emerald"></span>
                  Faol
                </span>
              </td>
              <td class="cell-actions text-right">
                <div class="actions-group">
                  <!-- Approve button (if pending) -->
                  <button
                    v-if="!item.is_active"
                    class="btn-act btn-act-approve"
                    title="Tasdiqlash va saytda faollashtirish"
                    @click="approveProfile(item)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Tasdiqlash
                  </button>

                  <!-- Deactivate button (if active) -->
                  <button
                    v-else
                    class="btn-act btn-act-reject"
                    title="Nofaol qilish / To‘xtatish"
                    @click="rejectProfile(item)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="15" y1="9" x2="9" y2="15"/>
                    </svg>
                    To‘xtatish
                  </button>

                  <!-- Delete button -->
                  <button
                    class="btn-act btn-act-delete"
                    title="Butunlay o‘chirish"
                    @click="confirmDelete(item)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteConfirm" class="modal-backdrop" @click.self="showDeleteConfirm = false">
        <div class="modal-card">
          <div class="modal-icon-danger">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <h3>Anketani o‘chirmoqchimisiz?</h3>
          <p>
            Nomzod: <strong>{{ deletingProfile?.name }}</strong> (#{{ deletingProfile?.id }}).<br />
            Ushbu amalni ortga qaytarib bo‘lmaydi. Anketa va unga tegishli barcha so‘rovlar butunlay o‘chiriladi.
          </p>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDeleteConfirm = false" :disabled="isDeleting">
              Bekor qilish
            </button>
            <button class="btn btn-danger" @click="deleteProfile" :disabled="isDeleting">
              {{ isDeleting ? 'O‘chirilmoqda...' : 'Ha, o‘chirish' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.roommates-admin-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--ad-text-main, #0F172A);
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--ad-text-muted, #64748B);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Metric Cards */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.metric-card {
  background: var(--ad-surface, #FFFFFF);
  border: 1px solid var(--ad-border, #E2E8F0);
  border-radius: var(--ad-radius-md, 10px);
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.metric-card:hover,
.metric-card.active {
  border-color: var(--ad-primary, #2878C8);
  box-shadow: 0 4px 12px rgba(40, 120, 200, 0.08);
}

.metric-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--ad-text-muted, #64748B);
  margin-bottom: 6px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--ad-text-main, #0F172A);
  line-height: 1.2;
}

.metric-hint {
  font-size: 12px;
  color: var(--ad-text-light, #94A3B8);
  margin-top: 6px;
}

.text-amber {
  color: #D97706 !important;
}

.text-emerald {
  color: #059669 !important;
}

/* Filter Card */
.filter-card {
  background: var(--ad-surface, #FFFFFF);
  border: 1px solid var(--ad-border, #E2E8F0);
  border-radius: var(--ad-radius-md, 10px);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tabs-nav {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--ad-border-subtle, #F1F5F9);
  padding-bottom: 12px;
  overflow-x: auto;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--ad-radius-sm, 6px);
  font-size: 13px;
  font-weight: 600;
  color: var(--ad-text-muted, #64748B);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  background: var(--ad-primary-light, rgba(40, 120, 200, 0.06));
  color: var(--ad-primary, #2878C8);
}

.tab-btn.active {
  background: var(--ad-primary-light, rgba(40, 120, 200, 0.1));
  color: var(--ad-primary, #2878C8);
  border-color: rgba(40, 120, 200, 0.2);
}

.dot-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.bg-amber {
  background-color: #F59E0B;
}

.filter-inputs-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 260px;
}

.search-svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--ad-text-light, #94A3B8);
}

.search-box input {
  width: 100%;
  padding: 9px 36px 9px 36px;
  background: var(--ad-bg, #F8FAFC);
  border: 1px solid var(--ad-border, #E2E8F0);
  border-radius: var(--ad-radius-sm, 6px);
  font-size: 13px;
  color: var(--ad-text-main, #0F172A);
  outline: none;
  transition: border-color 0.15s ease;
}

.search-box input:focus {
  border-color: var(--ad-primary, #2878C8);
  background: #FFF;
}

.clear-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: none;
  font-size: 18px;
  color: var(--ad-text-muted, #64748B);
  cursor: pointer;
}

.select-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.form-select {
  padding: 9px 12px;
  background: var(--ad-bg, #F8FAFC);
  border: 1px solid var(--ad-border, #E2E8F0);
  border-radius: var(--ad-radius-sm, 6px);
  font-size: 13px;
  color: var(--ad-text-main, #0F172A);
  outline: none;
}

/* Data Table Container */
.table-container {
  background: var(--ad-surface, #FFFFFF);
  border: 1px solid var(--ad-border, #E2E8F0);
  border-radius: var(--ad-radius-md, 10px);
  overflow-x: auto;
  min-height: 280px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
}

.data-table th {
  background: var(--ad-bg, #F8FAFC);
  padding: 12px 16px;
  font-weight: 600;
  color: var(--ad-text-muted, #64748B);
  border-bottom: 1px solid var(--ad-border, #E2E8F0);
  white-space: nowrap;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--ad-border-subtle, #F1F5F9);
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background-color: rgba(40, 120, 200, 0.02);
}

.row-pending {
  background-color: rgba(245, 158, 11, 0.03);
}

.cell-id {
  font-weight: 600;
  color: var(--ad-text-light, #94A3B8);
  font-size: 12px;
}

.user-block {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.avatar-blue {
  background: #E0F2FE;
  color: #0284C7;
}

.avatar-pink {
  background: #FCE7F3;
  color: #DB2777;
}

.user-name {
  font-weight: 600;
  color: var(--ad-text-main, #0F172A);
  display: flex;
  align-items: center;
  gap: 4px;
}

.verified-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  background: #10B981;
  color: #FFF;
  border-radius: 50%;
  font-size: 9px;
  font-weight: bold;
}

.user-bio {
  font-size: 11px;
  color: var(--ad-text-light, #94A3B8);
  margin-top: 2px;
  max-width: 220px;
}

.gender-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.gender-m {
  background: #E0F2FE;
  color: #0284C7;
}

.gender-f {
  background: #FCE7F3;
  color: #BE185D;
}

.age-text {
  display: block;
  font-size: 11px;
  color: var(--ad-text-muted, #64748B);
  margin-top: 2px;
}

.district-badge {
  font-weight: 600;
  color: var(--ad-text-main, #0F172A);
}

.budget-text {
  font-size: 12px;
  color: #059669;
  font-weight: 600;
  margin-top: 2px;
}

.occ-title {
  font-weight: 500;
  color: var(--ad-text-main, #0F172A);
}

.tags-wrap {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.mini-tag {
  background: var(--ad-bg, #F1F5F9);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  color: var(--ad-text-muted, #64748B);
}

.tag-more {
  background: rgba(40, 120, 200, 0.08);
  color: var(--ad-primary, #2878C8);
  font-weight: 600;
}

.tg-btn-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #E0F2FE;
  color: #0369A1;
  border-radius: 6px;
  text-decoration: none;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.15s ease;
}

.tg-btn-link:hover {
  background: #0284C7;
  color: #FFFFFF;
}

.tg-svg-icon {
  width: 14px;
  height: 14px;
}

.cell-date {
  font-size: 11px;
  color: var(--ad-text-muted, #64748B);
  white-space: nowrap;
}

.badge-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-pending {
  background: #FFFBEB;
  color: #B45309;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.badge-active {
  background: #ECFDF5;
  color: #047857;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.dot-amber {
  background: #F59E0B;
}

.dot-emerald {
  background: #10B981;
}

.actions-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.btn-act {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-act svg {
  width: 14px;
  height: 14px;
}

.btn-act-approve {
  background: #10B981;
  color: #FFF;
}

.btn-act-approve:hover {
  background: #059669;
}

.btn-act-reject {
  background: #F3F4F6;
  color: #4B5563;
}

.btn-act-reject:hover {
  background: #E5E7EB;
  color: #1F2937;
}

.btn-act-delete {
  background: #FEE2E2;
  color: #DC2626;
  padding: 6px 8px;
}

.btn-act-delete:hover {
  background: #DC2626;
  color: #FFF;
}

.text-right {
  text-align: right;
}

/* Modal styles */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: var(--ad-surface, #FFFFFF);
  border: 1px solid var(--ad-border, #E2E8F0);
  border-radius: var(--ad-radius-lg, 14px);
  padding: 28px;
  max-width: 440px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-icon-danger {
  width: 52px;
  height: 52px;
  background: #FEE2E2;
  color: #DC2626;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.modal-icon-danger svg {
  width: 28px;
  height: 28px;
}

.modal-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--ad-text-main, #0F172A);
  margin: 0 0 8px;
}

.modal-card p {
  font-size: 13px;
  color: var(--ad-text-muted, #64748B);
  line-height: 1.5;
  margin: 0 0 20px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  color: var(--ad-text-muted, #64748B);
}

.empty-icon {
  color: var(--ad-text-light, #94A3B8);
  margin-bottom: 12px;
}

.spinner-circle {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(40, 120, 200, 0.15);
  border-top-color: var(--ad-primary, #2878C8);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spin-icon {
  animation: spin 0.8s linear infinite;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--ad-radius-sm, 6px);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.btn-secondary {
  background: var(--ad-surface, #FFFFFF);
  border: 1px solid var(--ad-border, #E2E8F0);
  color: var(--ad-text-main, #0F172A);
}

.btn-secondary:hover {
  background: var(--ad-bg, #F8FAFC);
}

.btn-primary-outline {
  background: transparent;
  border: 1px solid var(--ad-primary, #2878C8);
  color: var(--ad-primary, #2878C8);
}

.btn-primary-outline:hover {
  background: var(--ad-primary-light, rgba(40, 120, 200, 0.08));
}

.btn-danger {
  background: #DC2626;
  color: #FFF;
}

.btn-danger:hover {
  background: #B91C1C;
}

.rf-icon {
  width: 14px;
  height: 14px;
}
</style>

