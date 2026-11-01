<script setup lang="ts">
import { ref } from 'vue'

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
  '📄 Shartnomani soliqda qanday ro‘yxatdan o‘tkazish mumkin?',
  '💵 Zalog (depozit) qachon qaytarilishi kerak?',
  '💡 Kommunal to‘lovlarni kim to‘lashi shart?',
  '🛡 Firibgarlardan qanday himoyalanamiz?',
]

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
    <!-- Floating Trigger Capsule Button -->
    <button
      type="button"
      class="iconly-assistant-trigger"
      :class="{ 'is-active': isOpen }"
      @click="isOpen = !isOpen"
      title="Joyliy AI Maslahatchi"
    >
      <div class="trigger-spark-circle">✨</div>
      <span class="trigger-text">AI Maslahatchi</span>
      <span class="online-dot"></span>
    </button>

    <!-- Chat Drawer Panel (Frosted Glass Surface) -->
    <Transition name="fade-slide">
      <div v-if="isOpen" class="iconly-chat-drawer">
        <!-- Drawer Header -->
        <div class="chat-header-bar">
          <div class="header-bot-info">
            <div class="bot-avatar-circle">🤖</div>
            <div>
              <h3 class="bot-name">Joyliy AI Maslahatchi</h3>
              <span class="bot-subtitle">Groq Qwen AI · Toshkent Ijara Huquqi</span>
            </div>
          </div>
          <button class="btn-close-drawer" @click="isOpen = false">✕</button>
        </div>

        <!-- Quick Suggestions Strip -->
        <div class="quick-prompts-strip">
          <button
            v-for="q in quickQuestions"
            :key="q"
            type="button"
            class="prompt-pill-btn"
            @click="sendQuestion(q)"
          >
            {{ q }}
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
                <span class="box-tag">📚 Qonuniy asos:</span>
                <ul class="box-list">
                  <li v-for="ref in msg.legal_references" :key="ref">{{ ref }}</li>
                </ul>
              </div>

              <!-- Practical Tips -->
              <div v-if="msg.practical_tips && msg.practical_tips.length" class="practical-tips-box">
                <span class="box-tag">💡 Amaliy tavsiya:</span>
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
            <button type="submit" class="btn-send-message" :disabled="!inputQuery.trim() || isLoading">
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
.iconly-assistant-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1100;
}

@media (max-width: 640px) {
  .iconly-assistant-wrapper {
    bottom: calc(88px + env(safe-area-inset-bottom, 0px));
    right: 16px;
  }
}

/* Floating Trigger Capsule */
.iconly-assistant-trigger {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px 10px 12px;
  border-radius: var(--radius-full);
  background: var(--blue-gradient);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 13.5px;
  font-weight: 700;
  box-shadow: 0 10px 28px rgba(40, 120, 200, 0.35);
  cursor: pointer;
  transition: all 0.25s var(--ease);
}

.iconly-assistant-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 34px rgba(40, 120, 200, 0.45);
}

.trigger-spark-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
}

.online-dot {
  width: 7px;
  height: 7px;
  background: #10B981;
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8);
}

/* Chat Drawer Panel */
.iconly-chat-drawer {
  position: absolute;
  bottom: 64px;
  right: 0;
  width: 390px;
  max-width: calc(100vw - 32px);
  height: 540px;
  max-height: calc(100vh - 120px);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-card);
  box-shadow: 0 20px 56px rgba(23, 25, 29, 0.18), 0 4px 16px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:root[data-theme="dark"] .iconly-chat-drawer {
  background: rgba(22, 27, 34, 0.95);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 56px rgba(0, 0, 0, 0.45);
}

@media (max-width: 640px) {
  .iconly-chat-drawer {
    position: fixed;
    inset: auto 12px calc(84px + env(safe-area-inset-bottom, 0px)) 12px;
    width: auto;
    max-width: none;
    height: 72vh;
    border-radius: 24px;
  }
}

/* Header */
.chat-header-bar {
  padding: 16px 20px;
  background: rgba(240, 247, 253, 0.85);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

:root[data-theme="dark"] .chat-header-bar {
  background: rgba(26, 35, 50, 0.85);
}

.header-bot-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-avatar-circle {
  width: 38px;
  height: 38px;
  background: var(--blue-gradient);
  color: #ffffff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 4px 12px rgba(40, 120, 200, 0.25);
}

.bot-name {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.bot-subtitle {
  font-size: 11.5px;
  color: var(--text-secondary);
}

.btn-close-drawer {
  background: none;
  border: none;
  font-size: 16px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  transition: color 0.15s ease;
}

.btn-close-drawer:hover {
  color: var(--text-primary);
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
}

.quick-prompts-strip::-webkit-scrollbar {
  display: none;
}

.prompt-pill-btn {
  padding: 5px 12px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  background: var(--surface);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
  transition: all 0.15s ease;
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
  max-width: 86%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 13.5px;
  line-height: 1.5;
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
  gap: 4px;
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
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
  background: var(--surface);
}

.input-form {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-text-input {
  flex: 1;
  height: 42px;
  padding: 0 16px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  background: var(--surface-subtle);
  font-size: 13.5px;
  color: var(--text-primary);
  outline: none;
  transition: all 0.2s ease;
}

.chat-text-input:focus {
  border-color: var(--blue-primary);
  background: #FFFFFF;
}

:root[data-theme="dark"] .chat-text-input:focus {
  background: #1C222B;
}

.btn-send-message {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--blue-primary);
  color: #FFFFFF;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s ease;
}

.btn-send-message:hover:not(:disabled) {
  background: var(--blue-deep);
  transform: scale(1.05);
}

.btn-send-message:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-arr {
  width: 16px;
  height: 16px;
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.22s var(--ease);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
}
</style>
