<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Xatoliklar & Qayta Urinish — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const failedTasks = ref<any[]>([])

const loadFailed = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/parser/status')
    if (res && res.history) {
      failedTasks.value = res.history.filter((h: any) => h.status === 'failed')
    }
  } catch (err: any) {
    showToast('Xatoliklarni yuklashda muammo', 'error')
  } finally {
    isLoading.value = false
  }
}

const retryTask = async (task: any) => {
  showToast(`Qayta urinish boshlandi: ${task.source}...`, 'info')
  try {
    const res = await authFetch('/api/admin/parser/run', {
      method: 'POST',
      body: { source: task.source, force: true },
    })
    if (res && res.success) {
      showToast('Qayta urinish muvaffaqiyatli!', 'success')
      await loadFailed()
    }
  } catch (err: any) {
    showToast('Qayta urinishda xatolik', 'error')
  }
}

onMounted(() => {
  loadFailed()
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
    title="Xatoliklar va Qayta urinish"
    :breadcrumbs="[
      { label: 'Avtomatizatsiya' },
      { label: 'Parser', to: '/admin/parser' },
      { label: 'Xatoliklar' }
    ]"
  >
    <div class="failed-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Muvaffaqiyatsiz Skanlar va Qayta Urinish</h1>
          <p class="page-sub">Tarmoq yoki manba xatoliklari sababli to‘xtab qolgan vazifalarni qayta tiklash</p>
        </div>
      </div>

      <div class="table-card">
        <div class="table-responsive">
          <table class="ad-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Manba</th>
                <th>Xatolik xabari</th>
                <th>Vaqti</th>
                <th class="text-right">Amal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in failedTasks" :key="item.id">
                <td class="font-mono">#{{ item.id }}</td>
                <td class="font-bold">{{ item.source }}</td>
                <td class="text-danger text-xs font-mono">{{ item.error_message || 'Tarmoq xatosi yoki manba javob bermadi' }}</td>
                <td class="text-muted text-xs">{{ formatDate(item.created_at) }}</td>
                <td class="text-right">
                  <button class="retry-btn" @click="retryTask(item)">
                    Qayta urinish
                  </button>
                </td>
              </tr>
              <tr v-if="!failedTasks.length && !isLoading">
                <td colspan="5" class="text-center py-6 text-muted">
                  Ajoyib! Hozirda hech qanday xatolik yuz bergan vazifa yo‘q.
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
.failed-page { display: flex; flex-direction: column; gap: 20px; }
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

.retry-btn {
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 5px 12px;
  border-radius: var(--ad-radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.text-danger { color: #ef4444; }
</style>
