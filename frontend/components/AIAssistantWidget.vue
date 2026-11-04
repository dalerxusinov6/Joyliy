<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useAssistant } from '~/composables/useAssistant'
import AssistantChat from '~/components/AssistantChat.vue'

const props = withDefaults(defineProps<{ show?: boolean }>(), { show: false })
const emit = defineEmits(['close', 'select', 'showAll'])

const { t } = useI18n()
const { prefill, send } = useAssistant()

const isOpen = ref(false)
const tipHidden = ref(true)

watch(
  () => props.show,
  (val) => {
    isOpen.value = val
    if (val && prefill.value) {
      const q = prefill.value
      prefill.value = ''
      setTimeout(() => send(q), 80)
    }
  },
  { immediate: true },
)

watch(isOpen, async (o) => {
  if (!import.meta.client) return
  document.body.classList.toggle('chat-open', o)
  if (o && window.matchMedia('(min-width: 768px)').matches) {
    await nextTick()
    setTimeout(() => (document.querySelector('#as-panel input') as HTMLInputElement | null)?.focus({ preventScroll: true }), 260)
  }
})

const open = () => { isOpen.value = true }
const close = () => { isOpen.value = false; emit('close') }

onMounted(() => {
  try { tipHidden.value = localStorage.getItem('joyliy_tip') === '1' } catch { tipHidden.value = false }
})
const hideTip = () => { tipHidden.value = true; try { localStorage.setItem('joyliy_tip', '1') } catch {} }
const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape' && isOpen.value) close() }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => { window.removeEventListener('keydown', onKey); if (import.meta.client) document.body.classList.remove('chat-open') })
</script>

<template>
  <div class="as-wrap" :class="{ hidden: isOpen }">
    <div v-if="!tipHidden && !isOpen" class="as-tip p-glass">
      <span>Ijara shartnomasi, zalog yoki uy qidirish bo‘yicha savolingiz bormi?</span>
      <button type="button" aria-label="Yopish" @click="hideTip">×</button>
    </div>
    <button type="button" class="as-btn" :aria-expanded="isOpen" aria-controls="as-panel" :aria-label="t('ai_assistant')" @click="open">
      <span class="orb" aria-hidden="true"></span>
      <span class="t">Joyliy AI<small>Maslahatchi · onlayn</small></span>
    </button>
  </div>

  <Transition name="scrim">
    <div v-if="isOpen" class="as-scrim" aria-hidden="true" @click="close"></div>
  </Transition>

  <Transition name="as">
    <div v-if="isOpen" id="as-panel" class="as p-glass" role="dialog" aria-label="Joyliy AI maslahatchi">
      <div class="hd">
        <span class="orb sm" aria-hidden="true"></span>
        <div><b>Joyliy AI</b><span>{{ t('bot_subtitle') }}</span></div>
        <button type="button" class="x" :aria-label="t('close')" @click="close">
          <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" /></svg>
        </button>
      </div>
      <AssistantChat @select="close" @showAll="(q: string) => { close(); emit('showAll', q) }" />
    </div>
  </Transition>
</template>

<style scoped>
.as-wrap { position: fixed; right: calc(20px + env(safe-area-inset-right, 0px)); bottom: calc(20px + env(safe-area-inset-bottom, 0px)); z-index: var(--z-chatbot); display: grid; justify-items: end; gap: 10px; }
.as-wrap.hidden { display: none; }
.as-tip { max-width: 260px; padding: 12px 14px 12px 16px; border-radius: 18px 18px 6px 18px; font: 600 13px/1.4 var(--font-sans); color: var(--tx); display: flex; gap: 10px; align-items: flex-start; animation: rise .5s .8s both; }
.as-tip button { border: 0; background: none; cursor: pointer; color: var(--tx-muted); padding: 0; line-height: 1; font-size: 16px; }
.as-btn { height: 64px; border-radius: 999px; border: 0; cursor: pointer; display: flex; align-items: center; gap: 12px; padding: 0 24px 0 10px; background: var(--accent-black); color: var(--on-ink); box-shadow: 0 20px 44px -14px rgba(38, 37, 33, .75); font: 700 15px var(--font-sans); }
.t { text-align: left; line-height: 1.2; }
.t small { display: block; font-size: 11px; font-weight: 500; opacity: .75; }
.orb { width: 44px; height: 44px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #FBF8F2, #D5C8B5 45%, #514437); flex: none; position: relative; animation: breathe 4s ease-in-out infinite; }
.orb::after { content: ""; position: absolute; inset: -6px; border-radius: 50%; border: 1px solid rgba(213, 200, 181, .7); animation: ring 2.6s ease-out infinite; }
.orb.sm { width: 34px; height: 34px; }
.as { position: fixed; right: calc(20px + env(safe-area-inset-right, 0px)); bottom: calc(20px + env(safe-area-inset-bottom, 0px)); z-index: var(--z-chat-fullscreen); width: 410px; height: min(640px, calc(100svh - 40px)); border-radius: 28px; overflow: hidden; display: flex; flex-direction: column; }
.hd { display: flex; gap: 12px; align-items: center; padding: 14px 14px 12px 16px; border-bottom: 1px solid var(--bd); flex: none; }
.hd b { display: block; font-weight: 700; }
.hd span:not(.orb) { font-size: 12px; color: var(--tx-muted); }
.x { margin-left: auto; width: 40px; height: 40px; border-radius: 50%; border: 0; background: transparent; cursor: pointer; display: grid; place-items: center; color: var(--tx); }
.x:hover { background: var(--surface-subtle); }
.x svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; }
.as > :deep(.chat) { flex: 1; min-height: 0; }
.as.p-glass { background: color-mix(in srgb, var(--bg) 97%, transparent); }
.as-scrim { position: fixed; inset: 0; z-index: calc(var(--z-chat-fullscreen) - 1); background: rgba(20, 19, 17, .38); backdrop-filter: blur(10px) saturate(1.1); -webkit-backdrop-filter: blur(10px) saturate(1.1); }
.scrim-enter-active, .scrim-leave-active { transition: opacity .25s; }
.scrim-enter-from, .scrim-leave-to { opacity: 0; }
.as-enter-active, .as-leave-active { transition: opacity .2s, transform .25s; }
.as-enter-from, .as-leave-to { opacity: 0; transform: translateY(16px); }
@keyframes rise { from { transform: translateY(16px); } to { transform: none; } }
@keyframes breathe { 50% { transform: scale(.93); } }
@keyframes ring { from { transform: scale(.85); opacity: 1; } to { transform: scale(1.35); opacity: 0; } }
@media (max-width: 1023px) { .as-wrap { bottom: calc(var(--mobile-nav-height) + var(--mobile-nav-bottom) + 20px + env(safe-area-inset-bottom, 0px)); right: 16px; } .as-btn { height: 56px; padding: 0 16px 0 8px; font-size: 14px; } .orb { width: 40px; height: 40px; } .t small { display: none; } }
@media (max-width: 767px) {
  .as-btn { width: 56px; padding: 0; justify-content: center; } .t { display: none; } .as-tip { display: none; }
  .as { left: 0; right: 0; bottom: 0; width: auto; height: min(84dvh, 680px); border-radius: 24px 24px 0 0; padding-bottom: env(safe-area-inset-bottom, 0px); }
}
@media (prefers-reduced-motion: reduce) { .orb, .orb::after, .as-tip { animation: none; } }
</style>
