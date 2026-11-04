<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useAuth } from '~/composables/useAuth'
import ModalShell from '~/components/ModalShell.vue'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'toast'])
const { t, currentLang } = useI18n()
const { user, isPolling, botUrl, botUsername, authError, initAuth, startBotLogin, stopPolling, loginWithWidget, mockConfirm, logout } = useAuth()

const isStarting = ref(false)
const ru = computed(() => currentLang.value === 'ru')

onMounted(() => {
  initAuth()
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

watch(() => user.value, (u) => { if (u) emit('toast', `Xush kelibsiz, ${u.first_name || 'foydalanuvchi'}!`) })

const onStart = async () => {
  isStarting.value = true
  try { await startBotLogin() } catch (e: any) { emit('toast', authError.value || 'Xatolik yuz berdi') } finally { isStarting.value = false }
}
const onDevConfirm = async () => { await mockConfirm(); emit('toast', 'Sinov rejimida muvaffaqiyatli kirdingiz!') }
const onLogout = () => { logout(); emit('toast', 'Tizimdan chiqildi') }
</script>

<template>
  <ModalShell :show="show" drawer :title="user ? (ru ? 'Мой профиль' : 'Mening profilim') : (ru ? 'Вход в Joyliy' : 'Joyliy tizimiga kirish')" @close="emit('close')">
    <template v-if="user">
      <div class="card">
        <img v-if="user.photo_url" :src="user.photo_url" class="ava" :alt="user.first_name || 'Avatar'" />
        <span v-else class="ava">{{ (user.first_name || 'U')[0].toUpperCase() }}</span>
        <div>
          <b>{{ user.first_name || (ru ? 'Пользователь' : 'Foydalanuvchi') }}</b>
          <a v-if="user.username" :href="`https://t.me/${user.username}`" target="_blank" rel="noopener">@{{ user.username }}</a>
          <small>Telegram ID: {{ user.telegram_id }}</small>
        </div>
      </div>
      <div class="okbox">{{ ru ? 'Уведомления о новых квартирах в Telegram активны' : 'Telegram orqali yangi e’lonlar xabarnomasi faol' }}</div>
      <a class="pbtn dark full" href="https://t.me/joyliy_bot" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" class="p-ic"><path d="M21 4L3 11l6 2 2 6 3-4 5 4z" /><path d="M9 13l9-7" /></svg>{{ ru ? 'Открыть Telegram-бот' : 'Telegram botni ochish' }} (@{{ botUsername }})
      </a>
      <button type="button" class="pbtn line full" @click="onLogout">{{ ru ? 'Выйти' : 'Chiqish' }}</button>
    </template>
    <template v-else-if="isPolling">
      <div class="wait">
        <span class="pulse"></span>
        <b>{{ ru ? 'Ожидание подтверждения в Telegram' : 'Telegram orqali tasdiqlash kutilmoqda' }}</b>
        <p class="p-muted">{{ ru ? 'Бот открыт. Нажмите "Start" для подтверждения входа.' : 'Bot ochildi. Kirishni tasdiqlash uchun “Start” tugmasini bosing.' }}</p>
      </div>
      <a v-if="botUrl" :href="botUrl" target="_blank" rel="noopener" class="pbtn dark full">{{ ru ? 'Открыть Telegram-бот' : 'Telegram botni ochish' }}</a>
      <button type="button" class="pbtn line full" @click="onDevConfirm">{{ ru ? 'Подтвердить (тестовый режим)' : 'Tasdiqlash (sinov rejimi)' }}</button>
      <button type="button" class="pbtn line full" @click="stopPolling">{{ t('cancel') }}</button>
    </template>
    <template v-else>
      <div class="wait">
        <b>{{ ru ? 'Войдите через Telegram' : 'Telegram orqali kiring' }}</b>
        <p class="p-muted">{{ ru ? 'Сохранённые квартиры и уведомления о новых объявлениях работают через Telegram-бот.' : 'Saqlangan uylar va yangi e’lon xabarnomalari Telegram bot orqali ishlaydi.' }}</p>
      </div>
      <button type="button" class="pbtn dark full" :disabled="isStarting" @click="onStart">
        <svg viewBox="0 0 24 24" class="p-ic"><path d="M21 4L3 11l6 2 2 6 3-4 5 4z" /><path d="M9 13l9-7" /></svg>{{ ru ? 'Войти через Telegram' : 'Telegram orqali kirish' }}
      </button>
    </template>
  </ModalShell>
</template>

<style scoped>
.card { display: flex; gap: 14px; align-items: center; padding: 16px; border-radius: 20px; background: var(--surface); }
.ava { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; background: var(--surface-subtle); display: grid; place-items: center; font: 700 20px var(--font-sans); flex: none; }
.card b { display: block; font-size: 16px; }
.card a { color: var(--blue-primary); font-size: 14px; text-decoration: none; }
.card small { display: block; color: var(--tx-muted); font-size: 12px; }
.wait { display: grid; gap: 8px; justify-items: start; }
.wait b { font: 600 20px var(--font-sans); }
.pulse { width: 14px; height: 14px; border-radius: 50%; background: var(--ok); box-shadow: 0 0 0 0 rgba(79, 107, 74, .5); animation: pl 2s infinite; }
@keyframes pl { 70% { box-shadow: 0 0 0 12px rgba(79, 107, 74, 0); } 100% { box-shadow: 0 0 0 0 rgba(79, 107, 74, 0); } }
@media (prefers-reduced-motion: reduce) { .pulse { animation: none; } }
</style>
