<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Telegram Nashriyot — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const data = ref<any>(null)
const manualListingId = ref<number | ''>('')
const isPublishing = ref(false)

const loadTelegramCenter = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/telegram')
    if (res && res.success) {
      data.value = res
    }
  } catch (err: any) {
    showToast('Telegram ma‘lumotlarini yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

const publishNow = async (listingId: number) => {
  isPublishing.value = true
  showToast('Telegramga post yuborilmoqda...', 'info')
  try {
    const res = await authFetch(`/api/admin/telegram/publish/${listingId}`, {
      method: 'POST',
    })
    if (res && res.success) {
      showToast('E‘lon muvaffaqiyatli post qilindi!', 'success')
      await loadTelegramCenter()
    } else {
      showToast(res?.message || 'Yuborish amalga oshmadi', 'warning')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Telegram xatosi', 'error')
  } finally {
    isPublishing.value = false
  }
}

const handleManualPublish = async () => {
  if (!manualListingId.value) return
  await publishNow(Number(manualListingId.value))
  manualListingId.value = ''
}

onMounted(() => {
  loadTelegramCenter()
})

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('uz-UZ', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <AdminShell
    title="Telegram nashriyot"
    :breadcrumbs="[
      { label: 'Avtomatizatsiya' },
      { label: 'Telegram nashriyot' }
    ]"
  >
    <div class="telegram-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Telegram Kanal Integratsiyasi</h1>
          <p class="page-sub">
            Yangi topilgan kvartiralarni avtomatik tarzda rasmiy <strong>@joyliy_uz</strong> kanaliga joylash navbati
          </p>
        </div>
        <div class="tg-ext-btn">
          <a href="https://t.me/joyliy_uz" target="_blank" class="channel-link-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="i-16">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            Kanalga o‘tish (@joyliy_uz)
          </a>
        </div>
      </div>

      <!-- KPI Metrics -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <span class="kpi-label">Jami chop etilgan</span>
          <span class="kpi-val text-purple">{{ data?.summary?.total_published || 0 }} ta</span>
          <span class="kpi-sub">Kanalda mavjud</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Bugun chop etildi</span>
          <span class="kpi-val text-emerald">+{{ data?.summary?.published_today || 0 }} ta</span>
          <span class="kpi-sub">Bugungi faollik</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Navbatda kutilayotgan</span>
          <span class="kpi-val text-blue">{{ data?.summary?.pending_queue || 0 }} ta</span>
          <span class="kpi-sub">Avtomatik chiqariladi</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Xatolik bilan to‘xtagan</span>
          <span class="kpi-val text-danger">{{ data?.summary?.failed_publications || 0 }} ta</span>
          <span class="kpi-sub">Qayta urinish lozim</span>
        </div>
      </div>

      <!-- Manual Publish Bar -->
      <div class="manual-publish-card">
        <div class="mp-info">
          <h4 class="mp-h4">Qo‘lda e‘lon yuborish</h4>
          <span class="mp-sub">Ixtiyoriy e‘lon ID raqamini kiritib, uni Telegram kanaliga to‘g‘ridan-to‘g‘ri post qiling</span>
        </div>
        <div class="mp-form">
          <input
            v-model.number="manualListingId"
            type="number"
            placeholder="E‘lon ID si (masalan, 15)"
            class="mp-input"
          />
          <button class="mp-btn" @click="handleManualPublish" :disabled="!manualListingId || isPublishing">
            Chiqarish
          </button>
        </div>
      </div>

      <!-- Queue Table -->
      <div class="table-card">
        <div class="tc-header">
          <h3 class="tc-title">Telegram Nashriyot Navbati</h3>
          <button class="rf-btn" @click="loadTelegramCenter" :disabled="isLoading">Yangilash</button>
        </div>

        <div class="table-responsive">
          <table class="ad-table">
            <thead>
              <tr>
                <th>Queue ID</th>
                <th>E‘lon ID</th>
                <th>Sarlavha</th>
                <th>Status</th>
                <th>Urinishlar</th>
                <th>Qo‘shilgan vaqt</th>
                <th>Xatolik</th>
                <th class="text-right">Amal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in data?.queue || []" :key="q.id">
                <td class="font-mono">#{{ q.id }}</td>
                <td class="font-mono">
                  <NuxtLink :to="`/admin/listings/${q.listing_id}`" class="link-id">
                    #{{ q.listing_id }}
                  </NuxtLink>
                </td>
                <td class="font-semibold">{{ q.title }}</td>
                <td>
                  <span class="status-pill" :class="q.status === 'published' ? 'st-done' : (q.status === 'failed' ? 'st-fail' : 'st-pend')">
                    {{ q.status === 'published' ? 'Chop etildi' : (q.status === 'failed' ? 'Xatolik' : 'Kutilmoqda') }}
                  </span>
                </td>
                <td>{{ q.attempts }} / 5</td>
                <td class="text-muted text-xs">{{ formatDate(q.created_at) }}</td>
                <td class="text-danger text-xs font-mono">{{ q.last_error || '-' }}</td>
                <td class="text-right">
                  <button class="action-btn" @click="publishNow(q.listing_id)" :disabled="isPublishing">
                    Hoziroq chiqarish
                  </button>
                </td>
              </tr>
              <tr v-if="!data?.queue?.length && !isLoading">
                <td colspan="8" class="text-center py-6 text-muted">
                  Navbatda hech qanday e‘lon mavjud emas
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.telegram-page { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 22px; font-weight: 800; color: var(--ad-text-main); margin: 0; }
.page-sub { font-size: 13.5px; color: var(--ad-text-muted); margin-top: 2px; }

.channel-link-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-purple-light);
  color: var(--ad-purple);
  border: 1px solid var(--ad-purple);
  padding: 8px 16px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.kpi-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: var(--ad-shadow-sm);
}

.kpi-label { font-size: 12.5px; color: var(--ad-text-muted); }
.kpi-val { font-size: 24px; font-weight: 800; }
.kpi-sub { font-size: 11.5px; color: var(--ad-text-light); }
.text-purple { color: #8b5cf6; }
.text-emerald { color: #10b981; }
.text-blue { color: var(--ad-primary); }
.text-danger { color: #ef4444; }

.manual-publish-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.mp-h4 { margin: 0; font-size: 14.5px; font-weight: 700; color: var(--ad-text-main); }
.mp-sub { font-size: 12.5px; color: var(--ad-text-muted); }

.mp-form { display: flex; gap: 8px; }
.mp-input {
  width: 200px;
  height: 36px;
  padding: 0 10px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  background: var(--ad-bg);
  font-size: 13px;
  outline: none;
}
.mp-btn {
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 0 16px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.table-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  box-shadow: var(--ad-shadow-sm);
  overflow: hidden;
}

.tc-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--ad-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tc-title { font-size: 15px; font-weight: 700; margin: 0; color: var(--ad-text-main); }
.rf-btn { background: var(--ad-bg); border: 1px solid var(--ad-border); padding: 5px 12px; border-radius: var(--ad-radius-sm); font-size: 12.5px; cursor: pointer; }

.table-responsive { overflow-x: auto; }
.ad-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.ad-table th { padding: 12px 14px; background: var(--ad-bg); color: var(--ad-text-muted); font-size: 11.5px; font-weight: 600; text-transform: uppercase; border-bottom: 1px solid var(--ad-border); }
.ad-table td { padding: 12px 14px; border-bottom: 1px solid var(--ad-border-subtle); vertical-align: middle; }

.link-id { color: var(--ad-primary); text-decoration: none; font-weight: 600; }
.status-pill { font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 4px; }
.st-done { background: var(--ad-success-light); color: var(--ad-success); }
.st-fail { background: var(--ad-danger-light); color: var(--ad-danger); }
.st-pend { background: var(--ad-primary-light); color: var(--ad-primary); }

.action-btn {
  background: var(--ad-border-subtle);
  border: 1px solid var(--ad-border);
  padding: 5px 10px;
  border-radius: var(--ad-radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.i-16 { width: 16px; height: 16px; }
</style>
