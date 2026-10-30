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
      'Shartnomani albatta soliq portalida ro‘yxatdan o‘tkazing',
      'Uyga kirishdan oldin zalog va buyumlar dalolatnomasini tuzing',
    ],
  },
])

const quickQuestions = [
  '📄 Ijara shartnomasini soliqda qanday ro‘yxatdan o‘tkazamiz?',
  '💵 Zalog (depozit) qachon qaytariladi?',
  '💡 Kommunal to‘lovlarni kim to‘lashi kerak?',
  '🛡 Firibgarlardan qanday saqlanish mumkin?',
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
      text: 'O‘zbekiston qonunchiligiga ko‘ra (FK 535-modda), ijara shartnomasi yozma tuzilishi va ijara.soliq.uz tizimida hisobga qo‘yilishi shart. Zalog depoziti esa mol-mulk shikastlanmagan taqdirda to‘liq qaytarilishi lozim.',
      practical_tips: ['Egasining pasporti va kadastr hujjatini shaxsan tekshiring.'],
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="assistant-container">
    <!-- Floating Trigger Button -->
    <button
      type="button"
      class="assistant-trigger"
      :class="{ 'is-active': isOpen }"
      @click="isOpen = !isOpen"
      title="Joyliy AI Maslahatchi"
    >
      <span class="trigger-icon">💬</span>
      <span class="trigger-text">AI Maslahatchi</span>
      <span class="online-indicator"></span>
    </button>

    <!-- Chat Drawer Panel -->
    <div v-if="isOpen" class="chat-drawer">
      <!-- Drawer Header -->
      <div class="chat-head">
        <div class="head-info">
          <div class="ai-avatar">🤖</div>
          <div>
            <h3 class="head-title">Joyliy AI Maslahatchi</h3>
            <span class="head-status">Toshkent Ijara Huquqi & Maslahat</span>
          </div>
        </div>
        <button class="close-chat-btn" @click="isOpen = false">✕</button>
      </div>

      <!-- Quick prompts -->
      <div class="quick-prompts">
        <button
          v-for="q in quickQuestions"
          :key="q"
          type="button"
          class="prompt-chip"
          @click="sendQuestion(q)"
        >
          {{ q }}
        </button>
      </div>

      <!-- Messages Body -->
      <div class="chat-body">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="msg-bubble-wrap"
          :class="msg.sender"
        >
          <div class="msg-bubble">
            <p class="msg-text">{{ msg.text }}</p>

            <!-- Legal references -->
            <div v-if="msg.legal_references && msg.legal_references.length" class="legal-box">
              <span class="legal-title">📚 Qonuniy asoslar:</span>
              <ul>
                <li v-for="ref in msg.legal_references" :key="ref">{{ ref }}</li>
              </ul>
            </div>

            <!-- Practical Tips -->
            <div v-if="msg.practical_tips && msg.practical_tips.length" class="tips-box">
              <span class="tips-title">💡 Amaliy tavsiya:</span>
              <ul>
                <li v-for="tip in msg.practical_tips" :key="tip">{{ tip }}</li>
              </ul>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="typing-indicator">
          <span>AI javob tayyorlamoqda...</span>
        </div>
      </div>

      <!-- Chat Input -->
      <div class="chat-foot">
        <form @submit.prevent="sendQuestion()" class="chat-form">
          <input
            v-model="inputQuery"
            type="text"
            placeholder="Ijara, soliq yoki shartnoma haqida so‘rang..."
            class="chat-input"
          />
          <button type="submit" class="chat-send" :disabled="!inputQuery.trim() || isLoading">
            ➤
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.assistant-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1100;
}

@media (max-width: 640px) {
  .assistant-container {
    bottom: calc(72px + env(safe-area-inset-bottom, 0px));
    right: 14px;
  }
}

.assistant-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: var(--radius-full, 9999px);
  background: var(--terracotta, #C85A32);
  color: #ffffff;
  border: none;
  font-size: 13.5px;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(200, 90, 50, 0.35);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

.assistant-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(200, 90, 50, 0.45);
}

.trigger-icon {
  font-size: 16px;
}

.online-indicator {
  width: 8px;
  height: 8px;
  background: #2ecc71;
  border-radius: 50%;
  border: 1.5px solid var(--terracotta, #C85A32);
}

.chat-drawer {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 380px;
  max-width: calc(100vw - 32px);
  height: 520px;
  max-height: calc(100vh - 120px);
  background: var(--surf, #ffffff);
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 16px;
  box-shadow: 0 20px 45px rgba(0,0,0,0.22);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.2s ease-out;
}

@media (max-width: 640px) {
  .chat-drawer {
    position: fixed;
    inset: auto 12px calc(76px + env(safe-area-inset-bottom, 0px)) 12px;
    width: auto;
    max-width: none;
    height: 72vh;
    max-height: 580px;
    border-radius: 20px;
    box-shadow: 0 -8px 36px rgba(0, 0, 0, 0.28);
  }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-head {
  padding: 14px 18px;
  background: var(--sand-light, #f8f6f2);
  border-bottom: 1px solid var(--sand, #ebe5db);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.head-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-avatar {
  width: 34px;
  height: 34px;
  background: #BC684B;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.head-title {
  margin: 0;
  font-size: 14.5px;
  font-weight: 700;
  color: var(--ink, #1c1c1b);
}

.head-status {
  font-size: 11px;
  color: #72746b;
}

.close-chat-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #72746b;
}

.quick-prompts {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 8px 12px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}

.prompt-chip {
  padding: 4px 10px;
  border-radius: 14px;
  border: 1px solid #eee;
  background: #fafafa;
  font-size: 11.5px;
  cursor: pointer;
  color: #555;
  transition: all 0.15s;
}

.prompt-chip:hover {
  background: #f0f0f0;
  color: #BC684B;
}

.chat-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.msg-bubble-wrap {
  display: flex;
}

.msg-bubble-wrap.user {
  justify-content: flex-end;
}

.msg-bubble-wrap.ai {
  justify-content: flex-start;
}

.msg-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.45;
}

.user .msg-bubble {
  background: #BC684B;
  color: #ffffff;
  border-bottom-right-radius: 2px;
}

.ai .msg-bubble {
  background: #f4f2ee;
  color: #222;
  border-bottom-left-radius: 2px;
}

.msg-text {
  margin: 0;
}

.legal-box, .tips-box {
  margin-top: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 11.5px;
}

.legal-box {
  background: #eef4f9;
  border-left: 3px solid #2b78e4;
}

.tips-box {
  background: #fff9e6;
  border-left: 3px solid #fbbc04;
}

.legal-title, .tips-title {
  font-weight: 700;
  display: block;
  margin-bottom: 3px;
}

.legal-box ul, .tips-box ul {
  margin: 0;
  padding-left: 16px;
}

.typing-indicator {
  font-size: 11.5px;
  font-style: italic;
  color: #888;
}

.chat-foot {
  padding: 10px 14px;
  border-top: 1px solid var(--sand, #ebe5db);
  background: #ffffff;
}

.chat-form {
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-family: inherit;
  font-size: 13px;
  outline: none;
}

.chat-send {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #BC684B;
  color: #ffffff;
  border: none;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

