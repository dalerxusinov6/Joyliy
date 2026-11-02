<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

interface BreadcrumbItem {
  label: string
  to?: string
}

const props = defineProps<{
  title?: string
  breadcrumbs?: BreadcrumbItem[]
}>()

const router = useRouter()
const route = useRoute()
const {
  adminUser,
  isAuthenticated,
  adminTheme,
  toasts,
  removeToast,
  showToast,
  toggleTheme,
  initAuth,
  logout,
  authFetch,
} = useAdminAuth()

const isSidebarCollapsed = ref(false)
const isMobileOpen = ref(false)
const isCommandKOpen = ref(false)
const searchQuery = ref('')
const isQuickScanning = ref(false)
const showUserMenu = ref(false)
const showNotifMenu = ref(false)

const systemHealth = ref<{ status: string; uptime: string }>({
  status: 'online',
  uptime: '99.9%',
})

onMounted(async () => {
  await initAuth()
  if (!isAuthenticated.value) {
    router.push('/admin/login')
  }

  if (import.meta.client) {
    const savedCollapse = localStorage.getItem('joyliy_admin_sidebar_collapsed')
    if (savedCollapse === 'true') {
      isSidebarCollapsed.value = true
    }

    window.addEventListener('keydown', handleGlobalKeydown)
  }
})

onUnmounted(() => {
  if (import.meta.client) {
    window.removeEventListener('keydown', handleGlobalKeydown)
  }
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  if (import.meta.client) {
    localStorage.setItem('joyliy_admin_sidebar_collapsed', String(isSidebarCollapsed.value))
  }
}

const handleGlobalKeydown = (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    isCommandKOpen.value = !isCommandKOpen.value
  } else if (e.key === 'Escape' && isCommandKOpen.value) {
    isCommandKOpen.value = false
  }
}

// Quick trigger scan
const triggerQuickScan = async () => {
  if (isQuickScanning.value) return
  isQuickScanning.value = true
  showToast('Avtomatik skanerlash boshlandi...', 'info')
  try {
    const res = await authFetch('/api/admin/parser/run', {
      method: 'POST',
      body: { source: 'all', force: true },
    })
    if (res && res.success) {
      showToast('Skanerlash muvaffaqiyatli yakunlandi!', 'success')
    } else {
      showToast(res?.message || 'Skanerlash xabari olindi', 'info')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Skanerlashda xatolik yuz berdi', 'error')
  } finally {
    isQuickScanning.value = false
  }
}

const navSections = [
  {
    title: 'ASOSIY',
    items: [
      {
        label: 'Umumiy ko‘rinish',
        to: '/admin',
        icon: 'dashboard',
        badge: null,
      },
      {
        label: 'E‘lonlar bazasi',
        to: '/admin/listings',
        icon: 'listings',
        badge: null,
      },
      {
        label: 'Xarita ko‘rinishi',
        to: '/admin/map',
        icon: 'map',
        badge: null,
      },
    ],
  },
  {
    title: 'AVTOMATIZATSIYA',
    items: [
      {
        label: 'Parser boshqaruvi',
        to: '/admin/parser',
        icon: 'cpu',
        badge: 'Auto',
      },
      {
        label: 'Manbalar',
        to: '/admin/parser/sources',
        icon: 'globe',
        badge: null,
      },
      {
        label: 'Skanerlash tarixi',
        to: '/admin/parser/history',
        icon: 'history',
        badge: null,
      },
      {
        label: 'Xatoliklar & Qayta urinish',
        to: '/admin/parser/failed',
        icon: 'alert',
        badge: null,
      },
      {
        label: 'Telegram nashriyot',
        to: '/admin/telegram',
        icon: 'send',
        badge: 'Live',
      },
    ],
  },
  {
    title: 'BOSHQARUV',
    items: [
      {
        label: 'Foydalanuvchilar',
        to: '/admin/users',
        icon: 'users',
        badge: null,
      },
      {
        label: 'Audit jurnali',
        to: '/admin/logs',
        icon: 'shield',
        badge: null,
      },
    ],
  },
  {
    title: 'TAHLIL VA SOZLAMALAR',
    items: [
      {
        label: 'Analitika',
        to: '/admin/analytics',
        icon: 'chart',
        badge: null,
      },
      {
        label: 'Tizim sozlamalari',
        to: '/admin/settings',
        icon: 'settings',
        badge: null,
      },
    ],
  },
]

const commandLinks = [
  { label: 'Umumiy boshqaruv paneli', to: '/admin', category: 'Sahifalar' },
  { label: 'Barcha e‘lonlarni ko‘rish', to: '/admin/listings', category: 'Sahifalar' },
  { label: 'Yangi e‘lon qo‘shish', to: '/admin/listings?action=new', category: 'Amallar' },
  { label: 'Parserni hozir ishga tushirish', action: 'scan', category: 'Amallar' },
  { label: 'Telegram nashr navbati', to: '/admin/telegram', category: 'Sahifalar' },
  { label: 'Foydalanuvchilar va rollar', to: '/admin/users', category: 'Sahifalar' },
  { label: 'Xarita orqali saralash', to: '/admin/map', category: 'Sahifalar' },
  { label: 'Audit xavfsizlik jurnali', to: '/admin/logs', category: 'Sahifalar' },
  { label: 'Tizim sozlamalari', to: '/admin/settings', category: 'Sahifalar' },
]

const filteredCommandLinks = computed(() => {
  if (!searchQuery.value.trim()) return commandLinks
  const q = searchQuery.value.toLowerCase()
  return commandLinks.filter(
    (c) => c.label.toLowerCase().includes(q) || c.category.toLowerCase().includes(q)
  )
})

const handleCommandSelect = (cmd: any) => {
  isCommandKOpen.value = false
  searchQuery.value = ''
  if (cmd.to) {
    router.push(cmd.to)
  } else if (cmd.action === 'scan') {
    triggerQuickScan()
  }
}

const roleBadgeColor = (role?: string) => {
  switch (role) {
    case 'super_admin':
      return 'badge-purple'
    case 'admin':
      return 'badge-blue'
    case 'editor':
      return 'badge-emerald'
    case 'analyst':
      return 'badge-amber'
    default:
      return 'badge-gray'
  }
}
</script>

<template>
  <div class="admin-root" :data-admin-theme="adminTheme">
    <div class="ad-shell" :class="{ 'is-collapsed': isSidebarCollapsed, 'mobile-open': isMobileOpen }">
      <!-- Backdrop for Mobile -->
      <div v-if="isMobileOpen" class="ad-mobile-backdrop" @click="isMobileOpen = false" />

      <!-- SIDEBAR -->
      <aside class="ad-sidebar">
        <!-- Sidebar Brand -->
        <div class="ad-sidebar-brand">
          <NuxtLink to="/admin" class="brand-link">
            <div class="brand-logo-mark">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="brand-icon">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
            </div>
            <div v-if="!isSidebarCollapsed" class="brand-info">
              <span class="brand-title">Joyliy<span class="brand-uz">.uz</span></span>
              <span class="brand-badge">ADMIN v2.0</span>
            </div>
          </NuxtLink>

          <button
            class="sidebar-toggle-btn"
            @click="toggleSidebar"
            :title="isSidebarCollapsed ? 'Kengaytirish' : 'Kichraytirish'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="toggle-icon">
              <path v-if="!isSidebarCollapsed" d="m15 18-6-6 6-6" />
              <path v-else d="m9 18 6-6-6-6" />
            </svg>
          </button>
        </div>

        <!-- Sidebar Navigation -->
        <nav class="ad-sidebar-nav">
          <div v-for="(sec, sIdx) in navSections" :key="sIdx" class="nav-section">
            <div v-if="!isSidebarCollapsed" class="section-title">
              {{ sec.title }}
            </div>
            <div v-else class="section-divider" />

            <ul class="nav-list">
              <li v-for="(item, iIdx) in sec.items" :key="iIdx">
                <NuxtLink
                  :to="item.to"
                  class="nav-item-link"
                  :class="{ active: route.path === item.to || (item.to !== '/admin' && route.path.startsWith(item.to)) }"
                  :title="isSidebarCollapsed ? item.label : undefined"
                >
                  <!-- Dashboard icon -->
                  <svg v-if="item.icon === 'dashboard'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect width="7" height="9" x="3" y="3" rx="1"/>
                    <rect width="7" height="5" x="14" y="3" rx="1"/>
                    <rect width="7" height="9" x="14" y="12" rx="1"/>
                    <rect width="7" height="5" x="3" y="16" rx="1"/>
                  </svg>

                  <!-- Listings icon -->
                  <svg v-else-if="item.icon === 'listings'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 6h16M4 12h16M4 18h16"/>
                  </svg>

                  <!-- Map icon -->
                  <svg v-else-if="item.icon === 'map'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>
                    <line x1="9" x2="9" y1="3" y2="18"/>
                    <line x1="15" x2="15" y1="6" y2="21"/>
                  </svg>

                  <!-- CPU / Parser icon -->
                  <svg v-else-if="item.icon === 'cpu'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect width="16" height="16" x="4" y="4" rx="2"/>
                    <rect width="6" height="6" x="9" y="9" rx="1"/>
                    <path d="M15 2v2M9 2v2M20 15h2M20 9h2M9 20v2M15 20v2M2 9h2M2 15h2"/>
                  </svg>

                  <!-- Globe icon -->
                  <svg v-else-if="item.icon === 'globe'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="2" x2="22" y1="12" y2="12"/>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  </svg>

                  <!-- History icon -->
                  <svg v-else-if="item.icon === 'history'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                    <path d="M3 3v5h5M12 7v5l4 2"/>
                  </svg>

                  <!-- Alert icon -->
                  <svg v-else-if="item.icon === 'alert'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>

                  <!-- Telegram / Send icon -->
                  <svg v-else-if="item.icon === 'send'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="22" y1="2" x2="11" y2="13"/>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                  </svg>

                  <!-- Users icon -->
                  <svg v-else-if="item.icon === 'users'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>

                  <!-- Shield icon -->
                  <svg v-else-if="item.icon === 'shield'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  </svg>

                  <!-- Chart icon -->
                  <svg v-else-if="item.icon === 'chart'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="20" x2="18" y2="10"/>
                    <line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6" y1="20" x2="6" y2="14"/>
                  </svg>

                  <!-- Settings icon -->
                  <svg v-else-if="item.icon === 'settings'" class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                  </svg>

                  <span v-if="!isSidebarCollapsed" class="item-label">{{ item.label }}</span>
                  <span v-if="!isSidebarCollapsed && item.badge" class="item-badge">{{ item.badge }}</span>
                </NuxtLink>
              </li>
            </ul>
          </div>
        </nav>

        <!-- Sidebar User Footer -->
        <div class="ad-sidebar-footer">
          <div class="user-profile-row" @click="showUserMenu = !showUserMenu">
            <div class="user-avatar-circle">
              {{ (adminUser?.first_name || adminUser?.username || 'A')[0].toUpperCase() }}
            </div>
            <div v-if="!isSidebarCollapsed" class="user-meta">
              <span class="user-name">{{ adminUser?.first_name || adminUser?.username || 'Administrator' }}</span>
              <span class="user-role-badge" :class="roleBadgeColor(adminUser?.role)">{{ adminUser?.role }}</span>
            </div>
          </div>

          <button v-if="!isSidebarCollapsed" class="logout-btn" @click="logout" title="Chiqish">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="logout-icon">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
          </button>
        </div>
      </aside>

      <!-- MAIN CONTENT WRAPPER -->
      <div class="ad-main-wrapper">
        <!-- TOP HEADER -->
        <header class="ad-header">
          <div class="header-left">
            <button class="mobile-menu-btn" @click="isMobileOpen = !isMobileOpen">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="3" y1="12" x2="21" y2="12"/>
                <line x1="3" y1="6" x2="21" y2="6"/>
                <line x1="3" y1="18" x2="21" y2="18"/>
              </svg>
            </button>

            <!-- Breadcrumbs -->
            <nav class="ad-breadcrumbs" aria-label="Breadcrumb">
              <NuxtLink to="/admin" class="bc-item">Joyliy Admin</NuxtLink>
              <template v-if="breadcrumbs && breadcrumbs.length">
                <span v-for="(bc, idx) in breadcrumbs" :key="idx" class="bc-crumb">
                  <span class="bc-sep">/</span>
                  <NuxtLink v-if="bc.to" :to="bc.to" class="bc-item">{{ bc.label }}</NuxtLink>
                  <span v-else class="bc-active">{{ bc.label }}</span>
                </span>
              </template>
              <template v-else-if="title">
                <span class="bc-sep">/</span>
                <span class="bc-active">{{ title }}</span>
              </template>
            </nav>
          </div>

          <!-- Header Right & Actions -->
          <div class="header-right">
            <!-- Command K Quick Search Trigger -->
            <button class="command-trigger-btn" @click="isCommandKOpen = true" title="Qidiruv (⌘K)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="cmd-icon">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <span class="cmd-text">Tezkor buyruq...</span>
              <kbd class="cmd-kbd">⌘K</kbd>
            </button>

            <!-- System Health Status -->
            <div class="system-status-indicator" title="Tizim holati: Faol">
              <span class="status-dot pulse-dot" />
              <span class="status-label">Online</span>
            </div>

            <!-- Quick Action: Fast Scan -->
            <button
              class="quick-action-btn scan-btn"
              @click="triggerQuickScan"
              :disabled="isQuickScanning"
              title="Avtomatik skanerlashni ishga tushirish"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon" :class="{ 'spin-icon': isQuickScanning }">
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
              </svg>
              <span class="btn-text">Skanerlash</span>
            </button>

            <!-- Quick Action: Add Listing -->
            <NuxtLink to="/admin/listings?action=new" class="quick-action-btn primary-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span class="btn-text">E‘lon qo‘shish</span>
            </NuxtLink>

            <!-- Theme Toggle -->
            <button class="icon-action-btn" @click="toggleTheme" :title="adminTheme === 'light' ? 'Tungi rejim' : 'Kunduzgi rejim'">
              <svg v-if="adminTheme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
            </button>

            <!-- External Site Link -->
            <a href="/" target="_blank" class="icon-action-btn" title="Joyliy.uz saytiga o‘tish">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
              </svg>
            </a>
          </div>
        </header>

        <!-- PAGE CONTENT CONTAINER -->
        <main class="ad-content-container">
          <slot />
        </main>
      </div>
    </div>

    <!-- COMMAND K MODAL -->
    <div v-if="isCommandKOpen" class="cmd-modal-overlay" @click.self="isCommandKOpen = false">
      <div class="cmd-modal-card">
        <div class="cmd-search-input-row">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="cmd-input-icon">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Sahifa yoki amalni qidirish..."
            class="cmd-search-field"
            autofocus
          />
          <button class="cmd-esc-btn" @click="isCommandKOpen = false">ESC</button>
        </div>

        <div class="cmd-results-list">
          <div
            v-for="(item, idx) in filteredCommandLinks"
            :key="idx"
            class="cmd-item-row"
            @click="handleCommandSelect(item)"
          >
            <div class="cmd-item-info">
              <span class="cmd-item-label">{{ item.label }}</span>
              <span class="cmd-item-cat">{{ item.category }}</span>
            </div>
            <span class="cmd-item-arrow">→</span>
          </div>
          <div v-if="filteredCommandLinks.length === 0" class="cmd-empty-state">
            Hech narsa topilmadi
          </div>
        </div>
      </div>
    </div>

    <!-- TOASTS -->
    <div class="ad-toasts-container">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="ad-toast-card"
        :class="`toast-${t.type}`"
        @click="removeToast(t.id)"
      >
        <span class="toast-dot" />
        <span class="toast-msg">{{ t.message }}</span>
        <button class="toast-close" @click.stop="removeToast(t.id)">×</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ad-shell {
  display: flex;
  min-height: 100vh;
  background-color: var(--ad-bg);
  color: var(--ad-text-main);
  transition: all 0.2s ease;
}

/* Sidebar */
.ad-sidebar {
  width: 250px;
  background: var(--ad-surface);
  border-right: 1px solid var(--ad-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 40;
  transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.ad-shell.is-collapsed .ad-sidebar {
  width: 70px;
}

.ad-sidebar-brand {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--ad-border);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--ad-text-main);
}

.brand-logo-mark {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #2878c8 0%, #1e5ba0 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(40, 120, 200, 0.25);
}

.brand-icon {
  width: 20px;
  height: 20px;
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--ad-text-main);
}

.brand-uz {
  color: var(--ad-primary);
}

.brand-badge {
  font-size: 10px;
  font-weight: 700;
  background: var(--ad-primary-light);
  color: var(--ad-primary);
  padding: 1px 5px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  width: fit-content;
}

.sidebar-toggle-btn {
  background: none;
  border: 1px solid var(--ad-border);
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--ad-text-muted);
  transition: all 0.15s;
}

.sidebar-toggle-btn:hover {
  background: var(--ad-border-subtle);
  color: var(--ad-text-main);
}

.toggle-icon {
  width: 16px;
  height: 16px;
}

.ad-sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--ad-text-light);
  letter-spacing: 0.6px;
  padding: 0 10px 6px 10px;
}

.section-divider {
  height: 1px;
  background: var(--ad-border);
  margin: 6px 4px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.nav-item-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: var(--ad-radius-md);
  color: var(--ad-text-muted);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  transition: all 0.15s ease;
  position: relative;
}

.nav-item-link:hover {
  background: var(--ad-border-subtle);
  color: var(--ad-text-main);
}

.nav-item-link.active {
  background: var(--ad-primary-light);
  color: var(--ad-primary);
  font-weight: 600;
}

.item-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.item-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-badge {
  font-size: 10px;
  font-weight: 600;
  background: var(--ad-primary);
  color: #fff;
  padding: 2px 6px;
  border-radius: 10px;
}

.ad-sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--ad-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-profile-row {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex: 1;
  overflow: hidden;
}

.user-avatar-circle {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--ad-border);
  color: var(--ad-text-main);
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--ad-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-badge {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 1px 6px;
  border-radius: 4px;
  width: fit-content;
  margin-top: 2px;
}

.badge-purple { background: var(--ad-purple-light); color: var(--ad-purple); }
.badge-blue { background: var(--ad-primary-light); color: var(--ad-primary); }
.badge-emerald { background: var(--ad-success-light); color: var(--ad-success); }
.badge-amber { background: var(--ad-warning-light); color: var(--ad-warning); }
.badge-gray { background: var(--ad-border-subtle); color: var(--ad-text-muted); }

.logout-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--ad-text-muted);
  padding: 6px;
  border-radius: 6px;
  transition: all 0.15s;
}

.logout-btn:hover {
  background: var(--ad-danger-light);
  color: var(--ad-danger);
}

.logout-icon {
  width: 18px;
  height: 18px;
}

/* Main Layout */
.ad-main-wrapper {
  flex: 1;
  margin-left: 250px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.ad-shell.is-collapsed .ad-main-wrapper {
  margin-left: 70px;
}

/* Header */
.ad-header {
  height: 64px;
  background: var(--ad-surface);
  border-bottom: 1px solid var(--ad-border);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 30;
  backdrop-filter: blur(8px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  color: var(--ad-text-main);
  cursor: pointer;
  padding: 6px;
}

.ad-breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
}

.bc-item {
  color: var(--ad-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.bc-item:hover {
  color: var(--ad-primary);
}

.bc-sep {
  color: var(--ad-text-light);
  font-size: 12px;
}

.bc-active {
  font-weight: 600;
  color: var(--ad-text-main);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.command-trigger-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--ad-border-subtle);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  padding: 6px 12px;
  color: var(--ad-text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.command-trigger-btn:hover {
  border-color: var(--ad-primary);
  color: var(--ad-text-main);
}

.cmd-icon {
  width: 15px;
  height: 15px;
}

.cmd-kbd {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 11px;
  font-family: var(--ad-font-mono);
  color: var(--ad-text-muted);
}

.system-status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--ad-success);
  background: var(--ad-success-light);
  padding: 4px 10px;
  border-radius: 20px;
}

.status-dot {
  width: 7px;
  height: 7px;
  background: var(--ad-success);
  border-radius: 50%;
}

.pulse-dot {
  animation: pulse-glow 2s infinite ease-in-out;
}

@keyframes pulse-glow {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
}

.scan-btn {
  background: var(--ad-border-subtle);
  color: var(--ad-text-main);
  border: 1px solid var(--ad-border);
}

.scan-btn:hover {
  background: var(--ad-border);
}

.primary-btn {
  background: var(--ad-primary);
  color: #fff;
}

.primary-btn:hover {
  background: var(--ad-primary-hover);
}

.btn-icon {
  width: 15px;
  height: 15px;
}

.spin-icon {
  animation: spin 1s infinite linear;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.icon-action-btn {
  width: 36px;
  height: 36px;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ad-text-muted);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s;
}

.icon-action-btn:hover {
  background: var(--ad-border-subtle);
  color: var(--ad-text-main);
}

.icon-action-btn svg {
  width: 18px;
  height: 18px;
}

/* Content Container */
.ad-content-container {
  flex: 1;
  padding: 24px;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}

/* Command Modal */
.cmd-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
}

.cmd-modal-card {
  width: 580px;
  max-width: 90vw;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  box-shadow: var(--ad-shadow-lg);
  overflow: hidden;
}

.cmd-search-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--ad-border);
}

.cmd-input-icon {
  width: 20px;
  height: 20px;
  color: var(--ad-text-muted);
}

.cmd-search-field {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: var(--ad-text-main);
  font-family: inherit;
}

.cmd-esc-btn {
  background: var(--ad-border-subtle);
  border: 1px solid var(--ad-border);
  border-radius: 4px;
  font-size: 11px;
  padding: 2px 6px;
  color: var(--ad-text-muted);
  cursor: pointer;
}

.cmd-results-list {
  max-height: 340px;
  overflow-y: auto;
  padding: 8px;
}

.cmd-item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: var(--ad-radius-md);
  cursor: pointer;
  transition: background 0.15s;
}

.cmd-item-row:hover {
  background: var(--ad-primary-light);
}

.cmd-item-info {
  display: flex;
  flex-direction: column;
}

.cmd-item-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--ad-text-main);
}

.cmd-item-cat {
  font-size: 11px;
  color: var(--ad-text-muted);
}

.cmd-item-arrow {
  color: var(--ad-text-muted);
}

.cmd-empty-state {
  padding: 24px;
  text-align: center;
  color: var(--ad-text-muted);
  font-size: 13.5px;
}

/* Toasts */
.ad-toasts-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 110;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.ad-toast-card {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  box-shadow: var(--ad-shadow-lg);
  font-size: 13.5px;
  color: var(--ad-text-main);
  min-width: 280px;
  max-width: 420px;
  animation: toast-in 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes toast-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.toast-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.toast-success .toast-dot { background: var(--ad-success); }
.toast-error .toast-dot { background: var(--ad-danger); }
.toast-info .toast-dot { background: var(--ad-primary); }
.toast-warning .toast-dot { background: var(--ad-warning); }

.toast-msg {
  flex: 1;
}

.toast-close {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--ad-text-muted);
}

/* Responsive */
@media (max-width: 992px) {
  .mobile-menu-btn {
    display: block;
  }
  .ad-sidebar {
    transform: translateX(-100%);
  }
  .ad-shell.mobile-open .ad-sidebar {
    transform: translateX(0);
  }
  .ad-main-wrapper,
  .ad-shell.is-collapsed .ad-main-wrapper {
    margin-left: 0;
  }
  .ad-mobile-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.5);
    z-index: 35;
  }
  .command-trigger-btn .cmd-text,
  .command-trigger-btn .cmd-kbd {
    display: none;
  }
  .quick-action-btn .btn-text {
    display: none;
  }
}
</style>
