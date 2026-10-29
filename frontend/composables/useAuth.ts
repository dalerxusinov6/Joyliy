import { ref } from 'vue'

export interface AuthUser {
  id: number
  telegram_id: number
  first_name?: string
  username?: string
  photo_url?: string
  is_admin?: boolean
}

export function useAuth() {
  const user = useState<AuthUser | null>('user', () => null)
  const token = useState<string | null>('auth_token', () => null)
  const isPolling = ref(false)
  const activeSessionId = ref<string | null>(null)
  const botUrl = ref<string | null>(null)
  const botUsername = ref<string>('joyliy_bot')
  const authError = ref<string | null>(null)

  let pollIntervalTimer: any = null

  // Initialize auth from localStorage
  const initAuth = async () => {
    if (!import.meta.client) return
    try {
      const storedToken = localStorage.getItem('joyliy_token')
      const storedUser = localStorage.getItem('joyliy_user')
      if (storedToken && storedUser) {
        token.value = storedToken
        user.value = JSON.parse(storedUser)

        // Validate token against backend
        const config = useRuntimeConfig()
        const apiBase = config.public.apiBase || ''
        try {
          const res: any = await $fetch(`${apiBase}/api/auth/me`, {
            headers: { Authorization: `Bearer ${storedToken}` },
          })
          if (res && res.id) {
            user.value = res
            localStorage.setItem('joyliy_user', JSON.stringify(res))
          }
        } catch (e: any) {
          if (e?.response?.status === 401) {
            logout()
          }
        }
      }
    } catch (e) {
      console.error('Error initializing auth:', e)
    }
  }

  // Start deep-link session via Joyliy Telegram bot
  const startBotLogin = async () => {
    authError.value = null
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase || ''

    try {
      const data: any = await $fetch(`${apiBase}/api/auth/telegram/session`, {
        method: 'POST',
      })

      activeSessionId.value = data.session_id
      botUrl.value = data.bot_url
      botUsername.value = data.bot_username || 'joyliy_bot'
      isPolling.value = true

      // Open Telegram link in a new tab/window
      if (typeof window !== 'undefined' && data.bot_url) {
        window.open(data.bot_url, '_blank')
      }

      // Start polling
      startPolling(data.session_id)
      return data
    } catch (err: any) {
      authError.value = 'Telegram bot sessiyasini yaratishda xatolik yuz berdi'
      throw err
    }
  }

  // Poll for authentication status
  const startPolling = (sessionId: string) => {
    stopPolling()
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase || ''

    let attempts = 0
    const maxAttempts = 120 // 3 minutes maximum

    pollIntervalTimer = setInterval(async () => {
      attempts++
      if (attempts > maxAttempts) {
        stopPolling()
        authError.value = 'Kirish vaqti tugadi. Qaytadan urinib ko‘ring.'
        return
      }

      try {
        const res: any = await $fetch(`${apiBase}/api/auth/telegram/check?session_id=${sessionId}`)
        if (res.status === 'AUTHENTICATED' && res.user && res.token) {
          stopPolling()
          token.value = res.token
          user.value = res.user
          if (import.meta.client) {
            localStorage.setItem('joyliy_token', res.token)
            localStorage.setItem('joyliy_user', JSON.stringify(res.user))
          }
        } else if (res.status === 'EXPIRED') {
          stopPolling()
          authError.value = 'Kirish sessiyasi muddati tugadi.'
        }
      } catch (e) {
        // Continue polling despite temporary network hiccups
      }
    }, 1500)
  }

  const stopPolling = () => {
    if (pollIntervalTimer) {
      clearInterval(pollIntervalTimer)
      pollIntervalTimer = null
    }
    isPolling.value = false
  }

  // Official Telegram Web Login widget callback
  const loginWithWidget = async (widgetData: any) => {
    authError.value = null
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase || ''

    try {
      const res: any = await $fetch(`${apiBase}/api/auth/telegram/widget`, {
        method: 'POST',
        body: widgetData,
      })

      if (res.status === 'AUTHENTICATED' && res.user && res.token) {
        token.value = res.token
        user.value = res.user
        if (import.meta.client) {
          localStorage.setItem('joyliy_token', res.token)
          localStorage.setItem('joyliy_user', JSON.stringify(res.user))
        }
        return res.user
      }
    } catch (e: any) {
      authError.value = e?.data?.detail || 'Telegram vidjeti orqali kirishda xatolik'
      throw e
    }
  }

  // Mock confirm for fast local testing
  const mockConfirm = async () => {
    if (!activeSessionId.value) return
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase || ''

    const res: any = await $fetch(`${apiBase}/api/auth/telegram/mock_confirm`, {
      method: 'POST',
      body: {
        session_id: activeSessionId.value,
        telegram_id: 5079685694,
        first_name: 'Foydalanuvchi',
        username: 'joyliy_user',
      },
    })
    if (res.status === 'AUTHENTICATED') {
      stopPolling()
      token.value = res.token
      user.value = res.user
      if (import.meta.client) {
        localStorage.setItem('joyliy_token', res.token)
        localStorage.setItem('joyliy_user', JSON.stringify(res.user))
      }
    }
  }

  const logout = () => {
    stopPolling()
    user.value = null
    token.value = null
    if (import.meta.client) {
      localStorage.removeItem('joyliy_token')
      localStorage.removeItem('joyliy_user')
    }
  }

  return {
    user,
    token,
    isPolling,
    activeSessionId,
    botUrl,
    botUsername,
    authError,
    initAuth,
    startBotLogin,
    stopPolling,
    loginWithWidget,
    mockConfirm,
    logout,
  }
}

