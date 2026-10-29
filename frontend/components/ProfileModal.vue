<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useAuth } from '~/composables/useAuth'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'toast'])
const { t } = useI18n()
const {
  user,
  token,
  isPolling,
  botUrl,
  botUsername,
  authError,
  initAuth,
  startBotLogin,
  stopPolling,
  loginWithWidget,
  mockConfirm,
  logout,
} = useAuth()

const isStarting = ref(false)

onMounted(() => {
  initAuth()

  // Register global callback for Telegram Login Widget
  if (import.meta.client) {
    ;(window as any).onTelegramAuth = async (widgetUser: any) => {
      try {
        await loginWithWidget(widgetUser)
        emit('toast', `Xush kelibsiz, ${widgetUser.first_name || 'foydalanuvchi'}!`)
        emit('close')
      } catch (err: any) {
        emit('toast', err?.message || 'Telegram orqali kirishda xatolik')
      }
    }
  }
})

// Watch for successful user login via bot polling
watch(
  () => user.value,
  (newUser) => {
    if (newUser) {
      emit('toast', `Xush kelibsiz, ${newUser.first_name || 'foydalanuvchi'}!`)
    }
  }
)

const onStartTelegramLogin = async () => {
  isStarting.value = true
  try {
    await startBotLogin()
  } catch (e: any) {
    emit('toast', authError.value || 'Xatolik yuz berdi')
  } finally {
    isStarting.value = false
  }
}

const onCancelPolling = () => {
  stopPolling()
}

const onDevConfirm = async () => {
  await mockConfirm()
  emit('toast', 'Sinov rejimida muvaffaqiyatli kirdingiz!')
}

const onLogout = () => {
  logout()
  emit('toast', 'Tizimdan chiqildi')
}
</script>

<template>
  <div v-if="show" class="ov show" @click.self="$emit('close')">
    <div class="sheet" style="max-width: 480px; border-radius: var(--radius-xs, 2px); border: 1px solid var(--sand, #DDD3C2)">
      <!-- Modal Header -->
      <div class="top">
        <span style="display: flex; align-items: center; gap: 8px">
          <svg class="i" style="color: #229ed9; width: 20px; height: 20px" viewBox="0 0 24 24">
            <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
          </svg>
          {{ user ? 'Mening profilim' : 'Joyliy tizimiga kirish' }}
        </span>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="bd">
        <!-- LOGGED IN VIEW -->
        <template v-if="user">
          <div class="profile-card">
            <div class="avatar-wrap">
              <img
                v-if="user.photo_url"
                :src="user.photo_url"
                class="avatar-lg"
                :alt="user.first_name || 'Avatar'"
              />
              <div v-else class="avatar-lg avatar-fallback">
                {{ (user.first_name || 'U')[0].toUpperCase() }}
              </div>
              <div class="tg-badge" title="Telegram orqali tasdiqlangan">
                <svg viewBox="0 0 24 24">
                  <path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z" fill="#fff" />
                </svg>
              </div>
            </div>

            <div class="user-info">
              <h3 class="user-name">{{ user.first_name || 'Foydalanuvchi' }}</h3>
              <p v-if="user.username" class="user-username">
                <a :href="`https://t.me/${user.username}`" target="_blank" rel="noopener">
                  @{{ user.username }}
                </a>
              </p>
              <span class="user-id">Telegram ID: {{ user.telegram_id }}</span>
            </div>
          </div>

          <div class="auth-features">
            <div class="feature-item">
              <span class="dot ok"></span>
              <span>Telegram orqali yangi e’lonlar xabarnomasi faol</span>
            </div>
            <div class="feature-item">
              <span class="dot ok"></span>
              <span>Saqlangan kvartiralar bulutli sinxronizatsiyasi</span>
            </div>
          </div>

          <div style="margin: 20px 0; display: flex; flex-direction: column; gap: 10px">
            <a
              class="btn p tg-btn"
              href="https://t.me/joyliy_bot"
              target="_blank"
              rel="noopener"
              style="width: 100%; justify-content: center"
            >
              <svg class="i" viewBox="0 0 24 24">
                <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
              </svg>
              Telegram Botni ochish (@{{ botUsername }})
            </a>

            <button class="btn" type="button" @click="onLogout" style="width: 100%">
              Chiqish
            </button>
          </div>
        </template>

        <!-- NOT LOGGED IN VIEW -->
        <template v-else>
          <!-- State 1: Polling in progress (User clicked Telegram login) -->
          <div v-if="isPolling" class="polling-box">
            <div class="tg-radar">
              <div class="pulse-ring"></div>
              <div class="pulse-ring delay"></div>
              <div class="tg-icon-circle">
                <svg viewBox="0 0 24 24">
                  <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" fill="#fff" />
                </svg>
              </div>
            </div>

            <h4 style="margin: 12px 0 6px">Telegram orqali tasdiqlash kutilmoqda</h4>
            <p class="mu" style="font-size: 14px; margin-bottom: 16px; line-height: 1.4">
              Telegram botingiz ochildi. Kirishni tasdiqlash uchun <b>"Start"</b> tugmasini bosing.
            </p>

            <div style="display: flex; flex-direction: column; gap: 8px; width: 100%">
              <a
                v-if="botUrl"
                :href="botUrl"
                target="_blank"
                rel="noopener"
                class="btn p tg-btn"
                style="justify-content: center"
              >
                <svg class="i" viewBox="0 0 24 24">
                  <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
                </svg>
                Telegram botni ochish
              </a>

              <button class="btn" type="button" @click="onDevConfirm" style="font-size: 13px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;">
                <svg class="i" viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
                <span>Tezkor tasdiqlash (Dev rejim)</span>
              </button>

              <button
                class="btn"
                type="button"
                @click="onCancelPolling"
                style="background: transparent; border: none; color: var(--mu); font-size: 13px"
              >
                Bekor qilish
              </button>
            </div>
          </div>

          <!-- State 2: Initial Login screen -->
          <div v-else>
            <div style="text-align: center; margin: 10px 0 24px">
              <div class="login-badge-hero">
                <svg viewBox="0 0 24 24">
                  <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" fill="#229ed9" />
                </svg>
              </div>
              <h3 style="margin: 10px 0 6px; font-size: 20px">Telegram orqali 1-marta bosishda kiring</h3>
              <p class="mu" style="font-size: 14px; max-width: 380px; margin: 0 auto; line-height: 1.4">
                Parol va kodlarsiz, Telegram botingiz orqali xavfsiz va bir zumda kiring.
              </p>
            </div>

            <div v-if="authError" class="auth-err-banner">
              {{ authError }}
            </div>

            <!-- Primary 1-Click Telegram Deep-link Login -->
            <button
              class="btn p tg-hero-btn"
              type="button"
              :disabled="isStarting"
              @click="onStartTelegramLogin"
            >
              <svg class="i" style="width: 20px; height: 20px" viewBox="0 0 24 24">
                <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
              </svg>
              <span>{{ isStarting ? 'Yuklanmoqda...' : 'Telegram orqali kirish' }}</span>
            </button>

            <div class="divider">
              <span>yoki rasmiy vidjet</span>
            </div>

            <!-- Telegram Widget Option -->
            <div class="widget-section">
              <p class="mu" style="font-size: 12px; margin-bottom: 8px">
                Brauzeringizda Telegram Login vidjeti:
              </p>
              <div id="telegram-widget-wrapper" class="tg-widget-center">
                <!-- Telegram script loaded asynchronously -->
                <component
                  :is="'script'"
                  async
                  src="https://telegram.org/js/telegram-widget.js?22"
                  data-telegram-login="joyliy_bot"
                  data-size="large"
                  data-radius="8"
                  data-onauth="onTelegramAuth(user)"
                  data-request-access="write"
                ></component>
              </div>
            </div>

            <p class="mu" style="font-size: 12px; text-align: center; margin-top: 20px; line-height: 1.4">
              Tizimga kirish orqali siz xavfsiz qidiruv va yangi kvartiralar haqida Telegram bildirishnomalaridan foydalana olasiz.
            </p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-soft, #f8fafc);
  border: 1px solid var(--bd, #e2e8f0);
  border-radius: 12px;
  margin-bottom: 16px;
}

[data-theme='dark'] .profile-card {
  background: #1e293b;
  border-color: #334155;
}

.avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.avatar-lg {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-fallback {
  background: linear-gradient(135deg, #059669, #10b981);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
}

.tg-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  background: #229ed9;
  border: 2px solid #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tg-badge svg {
  width: 12px;
  height: 12px;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  margin: 0 0 2px;
  font-size: 18px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-username a {
  color: #229ed9;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.user-username a:hover {
  text-decoration: underline;
}

.user-id {
  display: block;
  font-size: 12px;
  color: var(--mu, #64748b);
  margin-top: 2px;
}

.auth-features {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(16, 185, 129, 0.08);
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot.ok {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.tg-btn {
  background: #229ed9 !important;
  border-color: #229ed9 !important;
  color: #fff !important;
  font-weight: 600;
}

.tg-btn:hover {
  background: #1e8bbd !important;
}

.tg-hero-btn {
  background: #229ed9 !important;
  border-color: #229ed9 !important;
  color: #fff !important;
  width: 100%;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 14px rgba(34, 158, 217, 0.3);
  transition: all 0.2s ease;
}

.tg-hero-btn:hover {
  background: #1e8bbd !important;
  transform: translateY(-1px);
}

.login-badge-hero {
  width: 60px;
  height: 60px;
  background: rgba(34, 158, 217, 0.12);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.login-badge-hero svg {
  width: 32px;
  height: 32px;
}

.divider {
  display: flex;
  align-items: center;
  margin: 20px 0 16px;
  text-align: center;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--bd, #e2e8f0);
}

.divider span {
  padding: 0 12px;
  font-size: 12px;
  color: var(--mu, #94a3b8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tg-widget-center {
  display: flex;
  justify-content: center;
  min-height: 40px;
}

.auth-err-banner {
  background: #fee2e2;
  color: #b91c1c;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 14px;
  text-align: center;
}

.polling-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 24px 16px;
}

.tg-radar {
  position: relative;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tg-icon-circle {
  width: 48px;
  height: 48px;
  background: #229ed9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  box-shadow: 0 4px 12px rgba(34, 158, 217, 0.4);
}

.tg-icon-circle svg {
  width: 24px;
  height: 24px;
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #229ed9;
  animation: radar-pulse 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

.pulse-ring.delay {
  animation-delay: 0.75s;
}

@keyframes radar-pulse {
  0% {
    transform: scale(0.6);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
}
</style>
