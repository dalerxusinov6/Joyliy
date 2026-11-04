<script setup lang="ts">
import { useAssistant } from '~/composables/useAssistant'
import { useListings } from '~/composables/useListings'
import { useI18n } from '~/composables/useI18n'

const emit = defineEmits(['select', 'showAll'])
const { t, tDistrict } = useI18n()
const { messages, isLoading, quick, init, send } = useAssistant()
const { listings, selectedListing } = useListings()

const input = ref('')
const box = ref<HTMLElement | null>(null)

const scroll = async () => {
  await nextTick()
  if (box.value) box.value.scrollTop = box.value.scrollHeight
}
watch([messages, isLoading], scroll, { deep: true })
onMounted(() => { init(); scroll() })

const submit = () => {
  const q = input.value.trim()
  if (!q) return
  input.value = ''
  send(q)
}

const clean = (s: string) => (s || '').replace(/\*\*/g, '').replace(/^#{1,6}\s*/gm, '').replace(/^\s*[-*]\s+/gm, '• ')
const money = (v: number) => (v >= 1e9 ? `${(v / 1e9).toLocaleString('ru-RU', { maximumFractionDigits: 2 })} mlrd` : `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln`)

const openListing = (id: number) => {
  const l = listings.value.find((x) => x.id === id)
  if (l) { selectedListing.value = l; emit('select', l) }
}
</script>

<template>
  <div class="chat">
    <div ref="box" class="msgs" aria-live="polite">
      <div v-for="m in messages" :key="m.id" class="m" :class="m.sender === 'user' ? 'u' : 'b'">
        <template v-if="m.sender === 'user'">{{ m.text }}</template>
        <template v-else>
          <span class="txt">{{ clean(m.text) }}</span>
          <div v-if="m.legal_references && m.legal_references.length" class="box legal">
            <b>{{ t('legal_basis') }}</b>
            <ul><li v-for="r in m.legal_references" :key="r">{{ r }}</li></ul>
          </div>
          <div v-if="m.practical_tips && m.practical_tips.length" class="box tip">
            <b>{{ t('practical_tip') }}</b>
            <ul><li v-for="r in m.practical_tips" :key="r">{{ r }}</li></ul>
          </div>
          <button v-for="l in m.listings || []" :key="l.id" type="button" class="mini" @click="openListing(l.id)">
            <span class="th"><img v-if="l.image" :src="l.image" alt="" loading="lazy" referrerpolicy="no-referrer" /></span>
            <span class="mt"><b>{{ l.rooms }} xonali · {{ tDistrict(l.district) }}</b><small>{{ money(l.price_uzs) }} so‘m<template v-if="l.match"> · {{ l.match }}% mos</template></small></span>
          </button>
          <button v-if="m.more_query" type="button" class="link" @click="emit('showAll', m.more_query)">Barcha natijalarni ko‘rish →</button>
        </template>
      </div>
      <div v-if="isLoading" class="m b"><span class="typing"><i></i><i></i><i></i></span></div>
    </div>
    <div class="qs">
      <button v-for="q in quick" :key="q" type="button" @click="send(q)">{{ q }}</button>
    </div>
    <form @submit.prevent="submit">
      <label class="sr" for="chat-in">{{ t('send_message') }}</label>
      <input id="chat-in" v-model="input" autocomplete="off" :placeholder="t('chat_placeholder')" />
      <button class="send" type="submit" :aria-label="t('send_message')" :disabled="isLoading">
        <svg viewBox="0 0 24 24"><path d="M4 12l16-8-6 16-2.5-6.5z" /></svg>
      </button>
    </form>
  </div>
</template>

<style scoped>
.chat { display: flex; flex-direction: column; min-height: 0; height: 100%; }
.sr { position: absolute; left: -9999px; }
.msgs { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; overscroll-behavior: contain; min-height: 0; }
.m { max-width: 90%; padding: 11px 14px; border-radius: 18px; font-size: 14px; line-height: 1.55; white-space: pre-line; }
.m.b { background: var(--surface); color: var(--tx); border-bottom-left-radius: 6px; }
.m.u { background: var(--accent-black); color: var(--on-ink); align-self: flex-end; border-bottom-right-radius: 6px; }
.box { white-space: normal; margin-top: 10px; padding: 10px 12px; border-radius: 12px; font-size: 13px; }
.box.legal { background: var(--surface-subtle); }
.box.tip { background: var(--ok-bg); }
.box b { display: block; font: 700 11px var(--font-sans); letter-spacing: .1em; text-transform: uppercase; margin-bottom: 4px; color: var(--tx-muted); }
.box ul { margin: 0; padding-left: 18px; }
.mini { display: grid; grid-template-columns: 56px 1fr; gap: 12px; align-items: center; width: 100%; margin-top: 8px; padding: 6px; border-radius: 14px; border: 0; background: var(--bg); color: var(--tx); text-align: left; cursor: pointer; white-space: normal; }
.mini:hover { background: var(--surface-subtle); }
.th { width: 56px; height: 44px; border-radius: 10px; overflow: hidden; background: var(--surface-subtle); display: block; }
.th img { width: 100%; height: 100%; object-fit: cover; display: block; }
.mt { display: grid; gap: 2px; min-width: 0; }
.mt b { font-size: 13px; font-weight: 700; }
.mt small { font-size: 12px; color: var(--tx-muted); }
.link { background: none; border: 0; padding: 8px 0 0; font: 700 13px var(--font-sans); color: var(--blue-primary); cursor: pointer; }
.typing { display: inline-flex; gap: 4px; }
.typing i { width: 6px; height: 6px; border-radius: 50%; background: var(--tx-muted); animation: tp 1s infinite; }
.typing i:nth-child(2) { animation-delay: .15s; }
.typing i:nth-child(3) { animation-delay: .3s; }
@keyframes tp { 50% { transform: translateY(-4px); opacity: .4; } }
.qs { display: flex; gap: 6px; overflow-x: auto; padding: 0 16px 10px; scrollbar-width: none; flex: none; }
.qs button { flex: none; border: 1px solid var(--brand-sand); background: transparent; border-radius: 999px; padding: 7px 12px; font: 700 12px var(--font-sans); cursor: pointer; color: var(--tx); }
form { display: flex; gap: 8px; padding: 12px; border-top: 1px solid var(--bd); flex: none; }
input { flex: 1; min-width: 0; border: 1px solid var(--brand-sand); background: var(--surface); border-radius: 999px; padding: 12px 16px; font: 400 16px var(--font-sans); color: var(--tx); }
input:focus { outline: none; border-color: var(--blue-primary); }
.send { width: 46px; border: 0; border-radius: 50%; background: var(--accent-black); color: var(--on-ink); cursor: pointer; display: grid; place-items: center; flex: none; }
.send:disabled { opacity: .5; }
.send svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
@media (prefers-reduced-motion: reduce) { .typing i { animation: none; } }
</style>
