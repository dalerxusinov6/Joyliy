<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'

interface ChatMessage {
  id: string
  sender: 'user' | 'ai'
  text: string
  legal_references?: string[]
  practical_tips?: string[]
}

const isOpen = ref(false)
const inputQuery = ref('')
const isLoading = ref(false)

const messages = ref<ChatMessage[]>([
  {
    id: '1',
    sender: 'ai',
    text: 'Assalomu alaykum! Men Joyliy AI – O‘zbekiston ijara bozori bo‘yicha virtual yordamchingizman. Ijara shartnomasi, soliq (ijara.soliq.uz), zalog yoki firibgarlikdan saqlanish bo‘yicha savolingiz bormi?',
    practical_tips: [
      'Shartnomani albatta ijara.soliq.uz portalida ro‘yxatdan o‘tkazing',
      'Uyga ko‘chib kirishdan oldin zalog va buyumlar ro‘yxatini tuzing',
    ],
  },
])

const quickQuestions = [
  { text: 'Shartnomani soliqda qanday ro‘yxatdan o‘tkazish mumkin?', icon: 'file' },
  { text: 'Zalog (depozit) qachon qaytarilishi kerak?', icon: 'money' },
  { text: 'Kommunal to‘lovlarni kim to‘lashi shart?', icon: 'bulb' },
  { text: 'Firibgarlardan qanday himoyalanamiz?', icon: 'shield' },
]

// Toggle global body class to suppress bottom navigation & lock background scroll on mobile
watch(isOpen, (opened) => {
  if (typeof document !== 'undefined') {
    if (opened) {
      document.body.classList.add('chat-open')
    } else {
      document.body.classList.remove('chat-open')
    }
  }
})

onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.body.classList.remove('chat-open')
  }
})

const sendQuestion = async (textToSend?: string) => {
  const query = (textToSend || inputQuery.value).trim()
  if (!query || isLoading.value) return

  messages.value.push({
    id: Date.now().toString(),
    sender: 'user',
    text: query,
  })

  inputQuery.value = ''
  isLoading.value = true

  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    const res: any = await $fetch(`${base}/api/assistant/chat`, {
      method: 'POST',
      body: { message: query },
    })

    messages.value.push({
      id: (Date.now() + 1).toString(),
      sender: 'ai',
      text: res.reply || 'Savolingiz qabul qilindi.',
      legal_references: res.legal_references || [],
      practical_tips: res.practical_tips || [],
    })
  } catch (err) {
    messages.value.push({
      id: (Date.now() + 1).toString(),
      sender: 'ai',
      text: 'O‘zbekiston FK 535-moddasiga ko‘ra, ijara shartnomasi yozma tuzilishi va ijara.soliq.uz tizimida hisobga qo‘yilishi shart. Zalog depoziti mol-mulk shikastlanmagan taqdirda to‘liq qaytariladi.',
      practical_tips: ['Mulkdorning pasporti va kadastr hujjatini shaxsan tekshiring.'],
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="iconly-assistant-wrapper">
    <!-- Floating Trigger Capsule Button (Strictly positioned ABOVE bottom nav) -->
    <button
      v-show="!isOpen"
      type="button"
      class="iconly-assistant-trigger"
      @click="isOpen = true"
      title="Joyliy AI Maslahatchi"
      aria-label="AI Maslahatchi chatini ochish"
    >
      <div class="trigger-spark-circle">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="sparkle-svg">
          <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
        </svg>
      </div>
      <span class="trigger-text">AI Maslahatchi</span>
      <span class="online-dot"></span>
    </button>

    <!-- Chat Drawer Panel (Dedicated Fullscreen on Mobile, Floating Drawer on Desktop) -->
    <Transition name="fade-slide">
      <div v-if="isOpen" class="iconly-chat-drawer">
        <!-- Drawer Header -->
        <div class="chat-header-bar">
          <div class="header-bot-info">
            <div class="bot-avatar-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="bot-svg">
                <rect width="18" height="12" x="3" y="6" rx="2" />
                <path d="M12 2v4M9 12h.01M15 12h.01M10 16h4" />
              </svg>
            </div>
            <div>
              <h3 class="bot-name">Joyliy AI Maslahatchi</h3>
              <span class="bot-subtitle">Groq Qwen AI · Toshkent Ijara Huquqi</span>
            </div>
          </div>
          <button class="btn-close-drawer" @click="isOpen = false" aria-label="Yopish">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="drawer-close-svg">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <!-- Quick Suggestions Strip -->
        <div class="quick-prompts-strip">
          <button
            v-for="q in quickQuestions"
            :key="q.text"
            type="button"
            class="prompt-pill-btn"
            @click="sendQuestion(q.text)"
          >
            <svg v-if="q.icon === 'file'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="pill-svg">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <svg v-else-if="q.icon === 'money'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="pill-svg">
              <rect width="20" height="12" x="2" y="6" rx="2" />
              <circle cx="12" cy="12" r="2" />
              <path d="M6 12h.01M18 12h.01" />
            </svg>
            <svg v-else-if="q.icon === 'bulb'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="pill-svg">
              <path d="M12 2a6 6 0 0 0-6 6c0 2.5 1.5 4.5 3 6v2h6v-2c1.5-1.5 3-3.5 3-6a6 6 0 0 0-6-6Z" />
              <path d="M9 22h6" />
            </svg>
            <svg v-else-if="q.icon === 'shield'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="pill-svg">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <span>{{ q.text }}</span>
          </button>
        </div>

        <!-- Messages Body -->
        <div class="chat-messages-scroll">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="message-row"
            :class="msg.sender"
          >
            <div class="message-bubble">
              <p class="bubble-text">{{ msg.text }}</p>

              <!-- Legal references -->
              <div v-if="msg.legal_references && msg.legal_references.length" class="legal-references-box">
                <span class="box-tag">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="box-svg">
                    <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                    <path d="M6 6h10M6 10h10" />
                  </svg>
                  <span>Qonuniy asos:</span>
                </span>
                <ul class="box-list">
                  <li v-for="ref in msg.legal_references" :key="ref">{{ ref }}</li>
                </ul>
              </div>

              <!-- Practical Tips -->
              <div v-if="msg.practical_tips && msg.practical_tips.length" class="practical-tips-box">
                <span class="box-tag">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="box-svg">
                    <path d="M12 2a6 6 0 0 0-6 6c0 2.5 1.5 4.5 3 6v2h6v-2c1.5-1.5 3-3.5 3-6a6 6 0 0 0-6-6Z" />
                    <path d="M9 22h6" />
                  </svg>
                  <span>Amaliy tavsiya:</span>
                </span>
                <ul class="box-list">
                  <li v-for="tip in msg.practical_tips" :key="tip">{{ tip }}</li>
                </ul>
              </div>
            </div>
          </div>

          <div v-if="isLoading" class="typing-pill">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-label">AI tahlil qilmoqda...</span>
          </div>
        </div>

        <!-- Chat Input Footer -->
        <div class="chat-footer-bar">
          <form @submit.prevent="sendQuestion()" class="input-form">
            <input
              v-model="inputQuery"
              type="text"
              placeholder="Ijara yoki shartnoma bo‘yicha so‘rang..."
              class="chat-text-input"
            />
            <button
              type="submit"
              class="btn-send-message"
              :disabled="!inputQuery.trim() || isLoading"
              aria-label="Xabar yuborish"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="send-arr">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Centralized Independent Positioning System */
.iconly-assistant-wrapper {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: var(--z-chatbot, 1100);
  pointer-events: none;
}

@media (max-width: 1023px) {
  .iconly-assistant-wrapper {
    /* Guaranteed minimum gap of 20px above the bottom navigation */
    bottom: calc(
      var(--mobile-nav-height, 64px) +
      var(--mobile-nav-bottom, 12px) +
      var(--chatbot-gap, 20px) +
      env(safe-area-inset-bottom, 0px)
    );
    right: 16px;
  }
}

/* Floating Trigger Capsule */
.iconly-assistant-trigger {
  pointer-events: auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 48px;
  height: var(--chatbot-size, 52px);
  padding: 0 18px 0 12px;
  border-radius: var(--radius-full);
  background: var(--blue-gradient);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.35);
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 10px 28px rgba(40, 120, 200, 0.38);
  cursor: pointer;
  transition: all 0.22s var(--ease);
}

@media (max-width: 374px) {
  .iconly-assistant-trigger {
    padding: 0 12px 0 10px;
    font-size: 12px;
    gap: 6px;
    height: 46px;
  }
}

.iconly-assistant-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 34px rgba(40, 120, 200, 0.48);
}

.iconly-assistant-trigger:active {
  transform: scale(0.96);
}

.trigger-spark-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.24);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sparkle-svg {
  width: 16px;
  height: 16px;
}

.online-dot {
  width: 7px;
  height: 7px;
  background: #10B981;
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.85);
}

/* Chat Drawer Panel */
.iconly-chat-drawer {
  pointer-events: auto;
  position: absolute;
  bottom: 0;
  right: 0;
  width: 400px;
  max-width: calc(100vw - 32px);
  height: 560px;
  max-height: calc(100vh - 120px);
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-card);
  box-shadow: 0 20px 56px rgba(23, 25, 29, 0.18), 0 4px 16px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: var(--z-modal, 1200);
}

:root[data-theme="dark"] .iconly-chat-drawer {
  background: rgba(22, 27, 34, 0.96);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 56px rgba(0, 0, 0, 0.45);
}

/* Dedicated Full-Screen Overlay on Mobile (No overlap, clean keyboard handling) */
@media (max-width: 767px) {
  .iconly-chat-drawer {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100dvh;
    max-height: 100dvh;
    border-radius: 0;
    border: none;
    z-index: var(--z-chat-fullscreen, 1300);
    padding-top: env(safe-area-inset-top, 0px);
    padding-bottom: env(safe-area-inset-bottom, 0px);
  }
}

/* Header */
.chat-header-bar {
  padding: 14px 18px;
  background: rgba(240, 247, 253, 0.85);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

:root[data-theme="dark"] .chat-header-bar {
  background: rgba(26, 35, 50, 0.85);
}

.header-bot-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bot-avatar-circle {
  width: 36px;
  height: 36px;
  background: var(--blue-gradient);
  color: #ffffff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  box-shadow: 0 4px 12px rgba(40, 120, 200, 0.25);
}

.bot-name {
  margin: 0;
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.bot-subtitle {
  font-size: 11px;
  color: var(--text-secondary);
}

.btn-close-drawer {
  min-width: 44px;
  min-height: 44px;
  width: 44px;
  height: 44px;
  background: none;
  border: none;
  font-size: 18px;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.15s ease;
}

.btn-close-drawer:hover {
  background: var(--surface-subtle);
  color: var(--text-primary);
}

.btn-close-drawer:active {
  transform: scale(0.92);
}

/* Quick Prompts */
.quick-prompts-strip {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 10px 14px;
  background: var(--surface-subtle);
  border-bottom: 1px solid var(--border-subtle);
  scrollbar-width: none;
  flex-shrink: 0;
  -webkit-overflow-scrolling: touch;
}

.quick-prompts-strip::-webkit-scrollbar {
  display: none;
}

.prompt-pill-btn {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  background: var(--surface);
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
  transition: all 0.15s ease;
  min-height: 32px;
}

.prompt-pill-btn:hover {
  background: var(--blue-pale);
  color: var(--blue-deep);
  border-color: rgba(40, 120, 200, 0.3);
}

/* Messages */
.chat-messages-scroll {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  -webkit-overflow-scrolling: touch;
}

.message-row {
  display: flex;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.ai {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 88%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 13.5px;
  line-height: 1.5;
  word-break: break-word;
}

.user .message-bubble {
  background: #17191D;
  color: #FFFFFF;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(23, 25, 29, 0.15);
}

:root[data-theme="dark"] .user .message-bubble {
  background: var(--blue-primary);
}

.ai .message-bubble {
  background: var(--surface-subtle);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.bubble-text {
  margin: 0;
}

.legal-references-box,
.practical-tips-box {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 12px;
}

.legal-references-box {
  background: rgba(40, 120, 200, 0.08);
  border-left: 3px solid var(--blue-primary);
}

.practical-tips-box {
  background: #FEF3C7;
  border-left: 3px solid #F59E0B;
  color: #92400E;
}

:root[data-theme="dark"] .practical-tips-box {
  background: rgba(245, 158, 11, 0.15);
  color: #FCD34D;
}

.box-tag {
  font-weight: 700;
  display: block;
  margin-bottom: 4px;
}

.box-list {
  margin: 0;
  padding-left: 18px;
}

.typing-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--surface-subtle);
  padding: 8px 14px;
  border-radius: var(--radius-full);
  align-self: flex-start;
  font-size: 12px;
  color: var(--text-secondary);
}

.typing-dot {
  width: 5px;
  height: 5px;
  background: var(--blue-primary);
  border-radius: 50%;
  animation: pulse 1.2s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* Footer Input */
.chat-footer-bar {
  padding: 12px 14px;
  border-top: 1px solid var(--border-subtle);
  background: var(--surface);
  flex-shrink: 0;
}

.input-form {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-text-input {
  flex: 1;
  min-height: 44px;
  height: 44px;
  padding: 0 16px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  background: var(--surface-subtle);
  font-size: 13.5px;
  color: var(--text-primary);
  outline: none;
  transition: all 0.2s ease;
  min-width: 0;
}

.chat-text-input:focus {
  border-color: var(--blue-primary);
  background: #FFFFFF;
}

:root[data-theme="dark"] .chat-text-input:focus {
  background: #1C222B;
}

.btn-send-message {
  min-width: 44px;
  min-height: 44px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--blue-primary);
  color: #FFFFFF;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s ease;
  flex-shrink: 0;
}

.btn-send-message:hover:not(:disabled) {
  background: var(--blue-deep);
  transform: scale(1.04);
}

.btn-send-message:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-arr {
  width: 16px;
  height: 16px;
}

.bot-svg {
  width: 20px;
  height: 20px;
}

.drawer-close-svg {
  width: 18px;
  height: 18px;
}

.pill-svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  color: var(--blue-primary);
}

.box-svg {
  width: 14px;
  height: 14px;
  display: inline-block;
  vertical-align: -2px;
  margin-right: 4px;
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.24s var(--ease);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
}
</style>
