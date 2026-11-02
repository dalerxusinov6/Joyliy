<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Skanerlash Tarixi — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const history = ref<any[]>([])

const loadHistory = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/parser/status')
    if (res && res.history) {
      history.value = res.history
    }
  } catch (err: any) {
    showToast('Tarixni yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadHistory()
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
    title="Skanerlash tarixi"
    :breadcrumbs="[
      { label: 'Avtomatizatsiya' },
      { label: 'Parser', to: '/admin/parser' },
      { label: 'Skanerlash tarixi' }
    ]"
  >
    <div class="history-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Skanerlash Tarixi</h1>
          <p class="page-sub">O‘tgan skanerlash jarayonlari, topilgan e‘lonlar va davomiylik jurnali</p>
        </div>
      </div>

      <div class="table-card">
        <div class="table-responsive">
          <table class="ad-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Manba</th>
                <th>Status</th>
                <th>Yangi e‘lonlar</th>
                <th>Dublikatlar</th>
                <th>Davomiyligi</th>
                <th>Boshlangan vaqt</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in history" :key="item.id">
                <td class="font-mono">#{{ item.id }}</td>
                <td class="font-bold">{{ item.source }}</td>
                <td>
                  <span class="status-badge" :class="item.status === 'success' ? 'badge-green' : 'badge-red'">
                    {{ item.status === 'success' ? 'Muvaffaqiyatli' : 'Xatolik' }}
                  </span>
                </td>
                <td class="text-emerald font-bold">+{{ item.new_listings || 0 }} ta</td>
                <td>{{ item.duplicate_listings || 0 }} ta</td>
                <td>{{ item.duration_seconds || 0 }}s</td>
                <td class="text-muted text-xs">{{ formatDate(item.created_at) }}</td>
              </tr>
              <tr v-if="!history.length && !isLoading">
                <td colspan="7" class="text-center py-4 text-muted">
                  Tarix ma‘lumotlari topilmadi
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
.history-page { display: flex; flex-direction: column; gap: 20px; }
.page-title { font-size: 22px; font-weight: 800; color: var(--ad-text-main); margin: 0; }
.page-sub { font-size: 13.5px; color: var(--ad-text-muted); margin-top: 2px; }

.table-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  box-shadow: var(--ad-shadow-sm);
  overflow: hidden;
}

.table-responsive { overflow-x: auto; }
.ad-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.ad-table th { padding: 12px 14px; background: var(--ad-bg); color: var(--ad-text-muted); font-size: 11.5px; font-weight: 600; text-transform: uppercase; border-bottom: 1px solid var(--ad-border); }
.ad-table td { padding: 12px 14px; border-bottom: 1px solid var(--ad-border-subtle); vertical-align: middle; }

.status-badge { font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 4px; }
.badge-green { background: var(--ad-success-light); color: var(--ad-success); }
.badge-red { background: var(--ad-danger-light); color: var(--ad-danger); }
.text-emerald { color: #10b981; }
</style>

