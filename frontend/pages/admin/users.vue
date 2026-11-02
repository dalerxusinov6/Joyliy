<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Foydalanuvchilar va Rollar — Joyliy Admin',
})

const { authFetch, showToast, hasRole } = useAdminAuth()

const isLoading = ref(true)
const users = ref<any[]>([])
const selectedUser = ref<any>(null)
const showRoleModal = ref(false)
const selectedRole = ref('viewer')

const rolesList = [
  { id: 'super_admin', label: 'Super Admin', desc: 'Barcha ruxsatlar va sozlamalarga to‘liq egalik' },
  { id: 'admin', label: 'Admin', desc: 'E‘lonlar, parser va telegramni boshqarish' },
  { id: 'editor', label: 'Editor', desc: 'E‘lonlarni tahrirlash va tasdiqlash' },
  { id: 'analyst', label: 'Analyst', desc: 'Faqat statistik hisobotlarni ko‘rish' },
  { id: 'viewer', label: 'Viewer', desc: 'Faqat ko‘rish huquqi' },
  { id: 'none', label: 'Oddiy foydalanuvchi', desc: 'Admin huquqlari yo‘q' },
]

const loadUsers = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/users')
    if (res && res.success) {
      users.value = res.items || []
    }
  } catch (err: any) {
    showToast('Foydalanuvchilarni yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

const openRoleModal = (user: any) => {
  selectedUser.value = user
  selectedRole.value = user.admin_role || 'viewer'
  showRoleModal.value = true
}

const saveUserRole = async () => {
  if (!selectedUser.value) return
  try {
    const res = await authFetch(`/api/admin/users/${selectedUser.value.id}/role`, {
      method: 'POST',
      body: { role: selectedRole.value },
    })
    if (res && res.success) {
      showToast('Rol muvaffaqiyatli o‘zgartirildi!', 'success')
      showRoleModal.value = false
      await loadUsers()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Rolni o‘zgartirishda xatolik', 'error')
  }
}

onMounted(() => {
  loadUsers()
})

const roleBadgeClass = (role?: string) => {
  switch (role) {
    case 'super_admin': return 'badge-purple'
    case 'admin': return 'badge-blue'
    case 'editor': return 'badge-emerald'
    case 'analyst': return 'badge-amber'
    default: return 'badge-gray'
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <AdminShell
    title="Foydalanuvchilar"
    :breadcrumbs="[
      { label: 'Boshqaruv' },
      { label: 'Foydalanuvchilar' }
    ]"
  >
    <div class="users-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Foydalanuvchilar va Rollar (RBAC)</h1>
          <p class="page-sub">Tizim administratorlari, xodimlar rollari va ro‘yxatdan o‘tgan Telegram foydalanuvchilari</p>
        </div>
      </div>

      <div class="table-card">
        <div class="table-responsive">
          <table class="ad-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Ism / Foydalanuvchi</th>
                <th>Telegram ID</th>
                <th>Admin Roli</th>
                <th>Oxirgi kirish</th>
                <th>A‘zo bo‘lgan sana</th>
                <th class="text-right">Amal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td class="font-mono">#{{ u.id }}</td>
                <td>
                  <div class="user-row-cell">
                    <div class="user-avatar-sm">{{ (u.first_name || u.username || 'U')[0].toUpperCase() }}</div>
                    <div class="user-names">
                      <span class="user-fn">{{ u.first_name || u.username || 'Foydalanuvchi' }}</span>
                      <span v-if="u.username" class="user-un">@{{ u.username }}</span>
                    </div>
                  </div>
                </td>
                <td class="font-mono text-muted">{{ u.telegram_id || '-' }}</td>
                <td>
                  <span class="role-pill" :class="roleBadgeClass(u.admin_role)">
                    {{ u.admin_role || 'Oddiy foydalanuvchi' }}
                  </span>
                </td>
                <td class="text-muted text-xs">{{ formatDate(u.last_login_at) }}</td>
                <td class="text-muted text-xs">{{ formatDate(u.created_at) }}</td>
                <td class="text-right">
                  <button class="edit-role-btn" @click="openRoleModal(u)">
                    Rolni o‘zgartirish
                  </button>
                </td>
              </tr>
              <tr v-if="!users.length && !isLoading">
                <td colspan="7" class="text-center py-6 text-muted">
                  Foydalanuvchilar topilmadi
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ROLE CHANGE MODAL -->
      <div v-if="showRoleModal" class="ad-modal-backdrop" @click.self="showRoleModal = false">
        <div class="ad-modal-card">
          <div class="ad-modal-header">
            <h3 class="modal-h3">Rolni o‘zgartirish: {{ selectedUser?.first_name || selectedUser?.username }}</h3>
            <button class="modal-close-x" @click="showRoleModal = false">×</button>
          </div>
          <div class="ad-modal-body">
            <div class="roles-choice-list">
              <label
                v-for="r in rolesList"
                :key="r.id"
                class="role-choice-item"
                :class="{ selected: selectedRole === r.id }"
              >
                <input v-model="selectedRole" type="radio" :value="r.id" class="radio-input" />
                <div class="role-choice-info">
                  <span class="rc-label">{{ r.label }}</span>
                  <span class="rc-desc">{{ r.desc }}</span>
                </div>
              </label>
            </div>
          </div>
          <div class="modal-footer-btns">
            <button class="btn-cancel" @click="showRoleModal = false">Bekor qilish</button>
            <button class="btn-save" @click="saveUserRole">Saqlash</button>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.users-page { display: flex; flex-direction: column; gap: 20px; }
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

.user-row-cell { display: flex; align-items: center; gap: 10px; }
.user-avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--ad-primary-light);
  color: var(--ad-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
}
.user-names { display: flex; flex-direction: column; }
.user-fn { font-weight: 600; color: var(--ad-text-main); }
.user-un { font-size: 11px; color: var(--ad-text-muted); }

.role-pill { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }
.badge-purple { background: var(--ad-purple-light); color: var(--ad-purple); }
.badge-blue { background: var(--ad-primary-light); color: var(--ad-primary); }
.badge-emerald { background: var(--ad-success-light); color: var(--ad-success); }
.badge-amber { background: var(--ad-warning-light); color: var(--ad-warning); }
.badge-gray { background: var(--ad-border-subtle); color: var(--ad-text-muted); }

.edit-role-btn {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-sm);
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.edit-role-btn:hover { border-color: var(--ad-primary); color: var(--ad-primary); }

/* Modal */
.ad-modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.45); backdrop-filter: blur(4px); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 20px; }
.ad-modal-card { width: 480px; max-width: 95vw; background: var(--ad-surface); border: 1px solid var(--ad-border); border-radius: var(--ad-radius-lg); box-shadow: var(--ad-shadow-lg); overflow: hidden; }
.ad-modal-header { padding: 16px 20px; border-bottom: 1px solid var(--ad-border); display: flex; align-items: center; justify-content: space-between; }
.modal-h3 { font-size: 15px; font-weight: 700; margin: 0; color: var(--ad-text-main); }
.modal-close-x { background: none; border: none; font-size: 20px; color: var(--ad-text-muted); cursor: pointer; }
.ad-modal-body { padding: 16px 20px; max-height: 60vh; overflow-y: auto; }

.roles-choice-list { display: flex; flex-direction: column; gap: 8px; }
.role-choice-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 14px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  cursor: pointer;
  transition: all 0.15s;
}
.role-choice-item.selected {
  border-color: var(--ad-primary);
  background: var(--ad-primary-light);
}
.role-choice-info { display: flex; flex-direction: column; gap: 2px; }
.rc-label { font-size: 13.5px; font-weight: 600; color: var(--ad-text-main); }
.rc-desc { font-size: 12px; color: var(--ad-text-muted); }

.modal-footer-btns { display: flex; justify-content: flex-end; gap: 10px; padding: 14px 20px; border-top: 1px solid var(--ad-border); }
.btn-cancel { background: var(--ad-bg); border: 1px solid var(--ad-border); padding: 7px 14px; border-radius: var(--ad-radius-sm); font-size: 13px; cursor: pointer; }
.btn-save { background: var(--ad-primary); color: #fff; border: none; padding: 7px 18px; border-radius: var(--ad-radius-sm); font-size: 13px; font-weight: 600; cursor: pointer; }
</style>
