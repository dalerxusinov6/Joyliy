<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Audit Jurnali — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const logs = ref<any[]>([])
const search = ref('')

const loadLogs = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/overview')
    if (res && res.recent_activity) {
      logs.value = res.recent_activity
    }
  } catch (err: any) {
    showToast('Jurnalni yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadLogs()
})

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('uz-UZ', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <AdminShell
    title="Audit jurnali"
    :breadcrumbs="[
      { label: 'Boshqaruv' },
      { label: 'Audit jurnali' }
    ]"
  >
    <div class="logs-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Xavfsizlik va Audit Jurnali</h1>
          <p class="page-sub">Administratorlar va tizim botlari tomonidan amalga oshirilgan barcha harakatlar rekordi</p>
        </div>
      </div>

      <div class="table-card">
        <div class="table-responsive">
          <table class="ad-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Administrator</th>
                <th>Amal (Action)</th>
                <th>Obyekt turi</th>
                <th>Obyekt ID</th>
                <th>Tafsilotlar</th>
                <th>IP Manzil</th>
                <th>Vaqti</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="l in logs" :key="l.id">
                <td class="font-mono">#{{ l.id }}</td>
                <td class="font-semibold">{{ l.admin_username }}</td>
                <td>
                  <span class="action-tag">{{ l.action }}</span>
                </td>
                <td class="text-muted">{{ l.target_type }}</td>
                <td class="font-mono">{{ l.target_id || '-' }}</td>
                <td class="text-xs font-mono">{{ l.details ? JSON.stringify(l.details) : '-' }}</td>
                <td class="text-xs text-muted font-mono">{{ l.ip_address || '127.0.0.1' }}</td>
                <td class="text-xs text-muted">{{ formatDate(l.created_at) }}</td>
              </tr>
              <tr v-if="!logs.length && !isLoading">
                <td colspan="8" class="text-center py-6 text-muted">
                  Audit yozuvlari topilmadi
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
.logs-page { display: flex; flex-direction: column; gap: 20px; }
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

.action-tag {
  font-size: 11px;
  font-weight: 700;
  background: var(--ad-primary-light);
  color: var(--ad-primary);
  padding: 2px 7px;
  border-radius: 4px;
  text-transform: uppercase;
}
</style>
