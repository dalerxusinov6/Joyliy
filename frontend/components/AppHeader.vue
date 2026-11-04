<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useAuth } from '~/composables/useAuth'
import { useListings } from '~/composables/useListings'

const emit = defineEmits([
  'openFavorites',
  'openProfile',
  'openNew',
  'filterMaklersiz',
  'openMap',
  'openRoommates',
  'openCompare',
  'openNeighborhoods',
])
const { currentLang, setLang, t } = useI18n()
const { count: favCount } = useFavorites()
const { user, initAuth } = useAuth()
const { compareList, filterDealType, filterPropertyType, aiSearchActive, resetAiMatch } = useListings()

const isDark = ref(false)
const compact = ref(false)
const onScroll = () => { compact.value = window.scrollY > 40 }

onMounted(() => {
  initAuth()
  const saved = localStorage.getItem('joyliy_theme')
  isDark.value = saved === 'dark'
  document.documentElement.dataset.theme = isDark.value ? 'dark' : 'light'
  if (!saved) localStorage.setItem('joyliy_theme', 'light')
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))

const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.dataset.theme = theme
  localStorage.setItem('joyliy_theme', theme)
}

const goDeal = async (deal: 'rent' | 'sale') => {
  if (aiSearchActive.value) await resetAiMatch()
  filterDealType.value = deal
  filterPropertyType.value = ''
  if (route.path !== '/') await navigateTo('/#katalog')
  else document.getElementById('katalog')?.scrollIntoView({ behavior: 'smooth' })
}
const route = useRoute()
</script>

<template>
  <nav class="hdr" :class="{ compact }" aria-label="Asosiy navigatsiya">
    <div class="wrap">
      <div class="cap">
        <NuxtLink to="/" class="logo" aria-label="Joyliy — bosh sahifa">
          <svg viewBox="0 0 40 40" aria-hidden="true"><rect class="lm-bg" x="1" y="1" width="38" height="38" rx="19" /><path class="lm-l" d="M12 29V17l8-6 8 6v12" fill="none" stroke-width="1.6" /><path class="lm-d" d="M16.5 29v-6.5a3.5 3.5 0 0 1 7 0V29" /></svg>
          <b>Joyliy</b><i>.UZ</i>
        </NuxtLink>

        <div class="links">
          <NuxtLink to="/" class="lnk" exact-active-class="on">{{ t('home') }}</NuxtLink>
          <button type="button" class="lnk" @click="goDeal('sale')">Sotuv</button>
          <button type="button" class="lnk" @click="goDeal('rent')">Ijara</button>
          <button type="button" class="lnk" @click="emit('openMap')">{{ t('map') }}</button>
          <button type="button" class="lnk" @click="emit('openRoommates')">{{ t('roommates_tab') }}</button>
        </div>

        <div class="right">
          <div class="lang hide-m" role="group" aria-label="Til">
            <button v-for="lg in ['uz', 'ru', 'en']" :key="lg" type="button" :aria-pressed="currentLang === lg" @click="setLang(lg as any)">{{ lg.toUpperCase() }}</button>
          </div>
          <button type="button" class="ib" :aria-label="isDark ? t('theme_light') : t('theme_dark')" @click="toggleTheme">
            <svg v-if="isDark" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5" /></svg>
            <svg v-else viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" /></svg>
          </button>
          <button type="button" class="ib hide-m" :aria-label="t('compare')" @click="emit('openCompare')">
            <svg viewBox="0 0 24 24"><path d="M7 4v16M17 4v16M3 8h8M13 16h8" /></svg>
            <span v-if="compareList.length" class="dot">{{ compareList.length }}</span>
          </button>
          <button type="button" class="ib hide-m" :aria-label="t('saved')" @click="emit('openFavorites')">
            <svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" /></svg>
            <span v-if="favCount" class="dot">{{ favCount }}</span>
          </button>
          <button type="button" class="ib hide-m" :aria-label="user ? user.first_name : t('profile')" @click="emit('openProfile')">
            <img v-if="user && user.photo_url" :src="user.photo_url" class="ava" alt="" />
            <span v-else-if="user && user.first_name" class="ini">{{ user.first_name[0].toUpperCase() }}</span>
            <svg v-else viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" /></svg>
          </button>
          <button type="button" class="cta" @click="emit('openNew')">
            <span class="long">{{ t('post_ad') }}</span><span class="short">+ {{ t('post_ad_short') }}</span>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.hdr { position: fixed; top: calc(14px + env(safe-area-inset-top, 0px)); left: 0; right: 0; z-index: var(--z-header); transition: top .3s; }
.hdr .wrap { display: flex; }
.cap { flex: 1; min-width: 0; display: flex; align-items: center; gap: 6px; border-radius: 999px; padding: 6px; background: var(--glass); backdrop-filter: blur(18px) saturate(1.2); -webkit-backdrop-filter: blur(18px) saturate(1.2); border: 1px solid var(--glass-line); box-shadow: var(--sh-floating); transition: background .3s; }
.hdr.compact { top: calc(8px + env(safe-area-inset-top, 0px)); }
.hdr.compact .cap { background: var(--glass-strong); }
.logo { display: flex; align-items: center; gap: 10px; padding: 4px 12px 4px 6px; text-decoration: none; color: var(--tx); }
.logo svg { width: 32px; height: 32px; }
.lm-bg { fill: var(--accent-black); } .lm-l { stroke: var(--bg); } .lm-d { fill: var(--brand-sand); }
.logo b { font: 800 20px/1 var(--font-sans); letter-spacing: -.04em; }
.logo i { font: 500 10px var(--font-sans); color: var(--tx-muted); font-style: normal; letter-spacing: .1em; align-self: flex-end; margin-bottom: 3px; }
.links { display: flex; gap: 2px; margin: 0 auto; }
.lnk { padding: 10px 14px; border-radius: 999px; text-decoration: none; font: 500 14px var(--font-sans); color: var(--tx); background: transparent; border: 0; cursor: pointer; }
.lnk:hover, .lnk.on { background: var(--surface); }
.right { margin-left: auto; display: flex; align-items: center; gap: 2px; }
.lang { display: flex; background: color-mix(in srgb, var(--tx) 6%, transparent); border-radius: 999px; padding: 3px; margin-right: 4px; }
.lang button { border: 0; background: transparent; padding: 6px 9px; border-radius: 999px; font: 600 11px var(--font-sans); letter-spacing: .06em; cursor: pointer; color: var(--tx-muted); }
.lang button[aria-pressed="true"] { background: var(--surface); color: var(--tx); }
.ib { width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center; border: 0; background: transparent; cursor: pointer; position: relative; color: var(--tx); flex: none; }
.ib:hover { background: color-mix(in srgb, var(--tx) 7%, transparent); }
.ib svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.ava { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
.ini { width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center; background: var(--surface-subtle); font: 700 13px var(--font-sans); }
.dot { position: absolute; top: 5px; right: 5px; min-width: 16px; height: 16px; border-radius: 8px; background: var(--blue-primary); color: var(--on-ink); font: 700 10px/16px var(--font-sans); text-align: center; padding: 0 4px; }
.cta { margin-left: 6px; border: 0; border-radius: 999px; padding: 12px 22px; background: var(--accent-black); color: var(--on-ink); font: 600 14px var(--font-sans); cursor: pointer; white-space: nowrap; transition: background .2s; }
.cta:hover { background: var(--blue-primary); }
.cta .short { display: none; }
@media (max-width: 1180px) { .links { display: none; } }
@media (max-width: 767px) {
  .hide-m { display: none; }
  .logo i { display: none; }
  .cta { padding: 10px 14px; font-size: 13px; }
  .cta .long { display: none; }
  .cta .short { display: inline; }
}
</style>
