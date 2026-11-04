<script setup lang="ts">
const props = defineProps<{ show: boolean; title: string; wide?: boolean; drawer?: boolean }>()
const emit = defineEmits(['close'])

const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape' && props.show) emit('close') }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <Transition name="ms">
    <div v-if="show" class="scrim" :class="{ drawer }" @click.self="emit('close')">
      <section class="panel" :class="{ wide, drawer }" role="dialog" aria-modal="true" :aria-label="title">
        <header class="hd">
          <h3>{{ title }}</h3>
          <button type="button" class="x" aria-label="Yopish" @click="emit('close')">
            <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </header>
        <div class="bd"><slot /></div>
        <footer v-if="$slots.footer" class="ft"><slot name="footer" /></footer>
      </section>
    </div>
  </Transition>
</template>

<style scoped>
.scrim { position: fixed; inset: 0; z-index: var(--z-modal); background: rgba(20, 19, 17, .5); backdrop-filter: blur(3px); display: grid; place-items: center; padding: 16px; }
.scrim.drawer { place-items: stretch end; padding: 0; background: rgba(20, 19, 17, .4); }
.panel { background: var(--bg); color: var(--tx); border-radius: 28px; width: min(720px, 100%); max-height: calc(100svh - 32px); display: flex; flex-direction: column; overflow: hidden; box-shadow: var(--sh-modal); }
.panel.wide { width: min(980px, 100%); }
.panel.drawer { width: min(440px, 100%); max-height: none; height: 100%; border-radius: 0; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
.hd { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 18px 22px; border-bottom: 1px solid var(--bd); flex: none; }
.hd h3 { margin: 0; font: 600 22px/1.2 var(--font-sans); letter-spacing: -.02em; }
.x { width: 40px; height: 40px; border-radius: 50%; border: 0; background: transparent; cursor: pointer; display: grid; place-items: center; color: var(--tx); }
.x:hover { background: var(--surface-subtle); }
.x svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; }
.bd { overflow-y: auto; padding: 22px; display: grid; gap: 16px; align-content: start; flex: 1; min-height: 0; overscroll-behavior: contain; }
.ft { display: flex; justify-content: flex-end; gap: 8px; padding: 14px 22px; border-top: 1px solid var(--bd); flex-wrap: wrap; flex: none; }
.ms-enter-active, .ms-leave-active { transition: opacity .2s; }
.ms-enter-active .panel, .ms-leave-active .panel { transition: transform .25s cubic-bezier(.2, .7, .2, 1); }
.ms-enter-from, .ms-leave-to { opacity: 0; }
.ms-enter-from .panel { transform: translateY(18px); }
.ms-enter-from .panel.drawer { transform: translateX(30px); }
@media (max-width: 767px) {
  .scrim:not(.drawer) { place-items: end stretch; padding: 0; }
  .panel:not(.drawer) { width: 100%; border-radius: 24px 24px 0 0; max-height: 92svh; padding-bottom: env(safe-area-inset-bottom, 0px); }
}
@media (prefers-reduced-motion: reduce) { .ms-enter-active, .ms-leave-active, .ms-enter-active .panel, .ms-leave-active .panel { transition: none; } }
</style>
