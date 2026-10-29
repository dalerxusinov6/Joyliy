<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
const { t } = useI18n()
</script>

<template>
  <footer>
    <div class="wrap fg">
      <div>
        <div class="logo" style="margin-bottom: 8px">
          <b>
            <svg class="i" style="stroke: #fff" viewBox="0 0 24 24">
              <circle cx="8" cy="15" r="4" fill="none" stroke="currentColor" stroke-width="2" />
              <path d="m11 12 9-9M16 7l3 3" fill="none" stroke="currentColor" stroke-width="2" />
            </svg>
          </b>
          Joyliy
        </div>
        Toshkentda egasidan to‘g‘ridan-to‘g‘ri maklersiz ijara platformasi.
      </div>
      <div>
        <h4>Platforma</h4>
        <a href="#natija">{{ t('find_apartment') }}</a>
        <a href="#qanday">{{ t('how_it_works') }}</a>
        <a href="#natija">{{ t('no_agent_rentals') }}</a>
      </div>
      <div>
        <h4>Yordam</h4>
        <a href="#">Xavfsizlik qoidalari</a>
        <a href="#">Maklersiz mezonlari</a>
        <a href="#">Shikoyat qilish</a>
      </div>
      <div>
        <h4>Aloqa</h4>
        <a href="mailto:salom@joyliy.uz">salom@joyliy.uz</a>
        <a href="https://t.me/joyliy_bot" target="_blank" rel="noopener">Telegram: @joyliy_bot</a>
        <a href="#">Toshkent, O‘zbekiston</a>
      </div>
    </div>
    <div class="wrap" style="margin-top: 20px">© 2026 Joyliy — Barcha huquqlar himoyalangan.</div>
  </footer>
</template>

