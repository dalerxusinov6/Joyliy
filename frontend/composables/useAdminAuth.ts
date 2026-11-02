import { ref, computed } from 'vue'

export interface AdminUser {
  id: number
  username: string
  role: 'super_admin' | 'admin' | 'editor' | 'analyst' | 'viewer'
  email?: string
  first_name?: string
  last_login_at?: string
  photo_url?: string
}

export interface AdminToast {
  id: number
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
}

const adminUser = ref<AdminUser | null>(null)
const adminToken = ref<string | null>(null)
const isLoading = ref<boolean>(false)
const authError = ref<string | null>(null)
const adminTheme = ref<'light' | 'dark'>('light')
const toasts = ref<AdminToast[]>([])

let toastIdCounter = 0

export function useAdminAuth() {
  const router = useRouter()
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || ''

  const isAuthenticated = computed(() => !!adminUser.value)

  const showToast = (message: string, type: AdminToast['type'] = 'info', duration = 3500) => {
    const id = ++toastIdCounter
    toasts.value.push({ id, message, type })
    if (import.meta.client) {
      setTimeout(() => {
        toasts.value = toasts.value.filter((t) => t.id !== id)
      }, duration)
    }
  }

  const removeToast = (id: number) => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  const toggleTheme = () => {
    adminTheme.value = adminTheme.value === 'light' ? 'dark' : 'light'
    if (import.meta.client) {
      localStorage.setItem('joyliy_admin_theme', adminTheme.value)
      document.documentElement.setAttribute('data-admin-theme', adminTheme.value)
    }
  }

  const initTheme = () => {
    if (import.meta.client) {
      const saved = localStorage.getItem('joyliy_admin_theme')
      if (saved === 'dark' || saved === 'light') {
        adminTheme.value = saved
      } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        adminTheme.value = 'dark'
      }
      document.documentElement.setAttribute('data-admin-theme', adminTheme.value)
    }
  }

  const initAuth = async () => {
    if (!import.meta.client) return
    initTheme()
    try {
      const storedToken = localStorage.getItem('joyliy_admin_token')
      const storedUser = localStorage.getItem('joyliy_admin_user')

      if (storedToken) {
        adminToken.value = storedToken
      }
      if (storedUser) {
        try {
          adminUser.value = JSON.parse(storedUser)
        } catch {
          // invalid json
        }
      }

      // Verify with backend
      await checkAuth()
    } catch (e) {
      console.warn('Admin init auth check error:', e)
    }
  }

  const checkAuth = async (): Promise<boolean> => {
    try {
      const headers: Record<string, string> = {}
      if (adminToken.value) {
        headers['Authorization'] = `Bearer ${adminToken.value}`
      }

      const res: any = await $fetch(`${apiBase}/api/admin/auth/me`, {
        headers,
        credentials: 'include',
      })

      if (res && res.authenticated && res.user) {
        adminUser.value = res.user
        if (import.meta.client) {
          localStorage.setItem('joyliy_admin_user', JSON.stringify(res.user))
        }
        return true
      }
      adminUser.value = null
      return false
    } catch (e: any) {
      adminUser.value = null
      return false
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    isLoading.value = true
    authError.value = null
    try {
      const res: any = await $fetch(`${apiBase}/api/admin/auth/login`, {
        method: 'POST',
        body: { username, password },
        credentials: 'include',
      })

      if (res && res.success && res.token) {
        adminToken.value = res.token
        adminUser.value = res.user
        if (import.meta.client) {
          localStorage.setItem('joyliy_admin_token', res.token)
          localStorage.setItem('joyliy_admin_user', JSON.stringify(res.user))
        }
        showToast(`Xush kelibsiz, ${res.user.first_name || res.user.username}!`, 'success')
        await router.push('/admin')
        return true
      }
      authError.value = res?.message || 'Login yoki parol noto‘g‘ri'
      return false
    } catch (e: any) {
      authError.value = e?.data?.detail || e?.data?.message || 'Kirishda xatolik yuz berdi'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await $fetch(`${apiBase}/api/admin/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
    } catch {
      // Ignore network errors on logout
    }
    adminUser.value = null
    adminToken.value = null
    if (import.meta.client) {
      localStorage.removeItem('joyliy_admin_token')
      localStorage.removeItem('joyliy_admin_user')
    }
    showToast('Tizimdan chiqildi', 'info')
    await router.push('/admin/login')
  }

  const hasRole = (allowedRoles: string[]): boolean => {
    if (!adminUser.value) return false
    if (adminUser.value.role === 'super_admin') return true
    return allowedRoles.includes(adminUser.value.role)
  }

  const authFetch = async <T = any>(endpoint: string, options: any = {}): Promise<T> => {
    const headers = options.headers || {}
    if (adminToken.value) {
      headers['Authorization'] = `Bearer ${adminToken.value}`
    }
    options.headers = headers
    options.credentials = 'include'

    try {
      const fullUrl = endpoint.startsWith('http') ? endpoint : `${apiBase}${endpoint}`
      return await $fetch<T>(fullUrl, options)
    } catch (e: any) {
      if (e?.response?.status === 401 || e?.status === 401) {
        adminUser.value = null
        adminToken.value = null
        if (import.meta.client) {
          localStorage.removeItem('joyliy_admin_token')
          localStorage.removeItem('joyliy_admin_user')
        }
        router.push('/admin/login')
      }
      throw e
    }
  }

  return {
    adminUser,
    adminToken,
    isAuthenticated,
    isLoading,
    authError,
    adminTheme,
    toasts,
    showToast,
    removeToast,
    toggleTheme,
    initTheme,
    initAuth,
    checkAuth,
    login,
    logout,
    hasRole,
    authFetch,
  }
}
