<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

const { t, tDistrict } = useI18n()
const { filterCategory, filterDealType, filterDistrict, filterPropertyType, aiSearchActive, resetAiMatch } = useListings()
const route = useRoute()

const go = async (fn: () => void) => {
  if (aiSearchActive.value) await resetAiMatch()
  fn()
  if (route.path !== '/') await navigateTo('/#katalog')
  else document.getElementById('katalog')?.scrollIntoView({ behavior: 'smooth' })
}
const cat = (key: string, deal: 'rent' | 'sale' = 'rent') => go(() => { filterDealType.value = deal; filterCategory.value = key; filterPropertyType.value = ''; filterDistrict.value = '' })
const dist = (d: string) => go(() => { filterDistrict.value = d; filterCategory.value = '' })
const districts = ['Chilonzor', 'Yunusobod', 'Mirzo Ulug‘bek', 'Mirobod', 'Yakkasaroy', 'Yashnobod']
</script>

<template>
  <footer class="ft">
    <div class="wrap">
      <div class="grid">
        <div class="brand">
          <NuxtLink to="/" class="logo" aria-label="Joyliy">
            <svg viewBox="0 0 40 40" aria-hidden="true"><rect class="a" x="1" y="1" width="38" height="38" rx="19" /><path class="b" d="M12 29V17l8-6 8 6v12" fill="none" stroke-width="1.6" /><path class="c" d="M16.5 29v-6.5a3.5 3.5 0 0 1 7 0V29" /></svg>
            <b>Joyliy</b>
          </NuxtLink>
          <p>{{ t('footer_about_desc') }}</p>
        </div>
        <div>
          <h4>{{ t('footer_catalog') }}</h4>
          <ul>
            <li><button type="button" @click="cat('')">{{ t('footer_all_apts') }}</button></li>
            <li><button type="button" @click="cat('mk')">{{ t('footer_no_agent') }}</button></li>
            <li><button type="button" @click="cat('fair_cheap')">{{ t('footer_cheap') }}</button></li>
            <li><button type="button" @click="cat('3days')">{{ t('footer_new') }}</button></li>
            <li><button type="button" @click="cat('room')">{{ t('footer_roommates') }}</button></li>
          </ul>
        </div>
        <div>
          <h4>{{ t('footer_districts') }}</h4>
          <ul>
            <li v-for="d in districts" :key="d"><button type="button" @click="dist(d)">{{ tDistrict(d) }}</button></li>
          </ul>
        </div>
        <div>
          <h4>{{ t('footer_contacts') }}</h4>
          <ul>
            <li><a href="https://t.me/joyliy_bot" target="_blank" rel="noopener">Telegram bot · @joyliy_bot</a></li>
            <li><a href="https://t.me/joyliy_uz" target="_blank" rel="noopener">Kanal · @joyliy_uz</a></li>
            <li><a href="mailto:salom@joyliy.uz">salom@joyliy.uz</a></li>
            <li>{{ t('footer_city') }}</li>
          </ul>
        </div>
      </div>
      <div class="fine"><span>{{ t('footer_rights') }}</span><span>{{ t('footer_disclaimer') }}</span></div>
    </div>
  </footer>
</template>

<style scoped>
.ft { padding-block: 72px 40px; color: var(--tx-muted); font-size: 14px; background: transparent; border: 0; }
.grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 32px; border-top: 1px solid var(--brand-sand); padding-top: 40px; }
.brand { display: grid; gap: 14px; align-content: start; }
.brand p { margin: 0; max-width: 38ch; }
.logo { display: flex; align-items: center; gap: 10px; text-decoration: none; color: var(--tx); }
.logo svg { width: 32px; height: 32px; }
.a { fill: var(--accent-black); } .b { stroke: var(--bg); } .c { fill: var(--brand-sand); }
.logo b { font: 800 20px/1 var(--font-sans); letter-spacing: -.04em; }
h4 { margin: 0 0 14px; font: 600 11px var(--font-sans); letter-spacing: .16em; text-transform: uppercase; color: var(--tx); }
ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
a, button { text-decoration: none; background: none; border: 0; padding: 0; cursor: pointer; color: inherit; text-align: left; font: inherit; }
a:hover, button:hover { color: var(--tx); }
.fine { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-top: 40px; font-size: 12px; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 480px) { .grid { grid-template-columns: 1fr; } }
</style>
