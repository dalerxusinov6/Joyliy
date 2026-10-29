<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
const { t } = useI18n()
</script>

<template>
  <footer class="app-footer">
    <div class="wrap fg footer-grid">
      <!-- Brand Column -->
      <div class="footer-brand-col">
        <NuxtLink to="/" class="logo footer-logo">
          <div class="logo-icon-box">
            <svg viewBox="0 0 24 24" class="logo-svg" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 10.5 12 3l9 7.5v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <circle cx="12" cy="13" r="2.5" />
              <path d="M12 15.5v3.5M14 17.5h-2" />
            </svg>
          </div>
          <div class="logo-wordmark">
            <span class="logo-title">Joyliy</span>
            <span class="logo-sub">Toshkent</span>
          </div>
        </NuxtLink>
        <p class="brand-desc">
          Toshkent shahrida kvartira egalari va ijarachilarni to‘g‘ridan-to‘g‘ri bog‘lovchi platforma. Ortiqcha maklerlik to‘lovlarsiz va shaffof shartlar bilan orzuingizdagi uyni toping.
        </p>
        <div class="brand-stats">
          <span class="stat-pill">⚡️ 100% Maklersiz</span>
          <span class="stat-pill">📍 Toshkent bo‘ylab</span>
        </div>
      </div>

      <!-- Column 1: Platform -->
      <div>
        <h4>Platforma</h4>
        <a href="#natija">{{ t('find_apartment') }}</a>
        <a href="#natija">{{ t('no_agent_rentals') }}</a>
        <a href="#qanday">{{ t('how_it_works') }}</a>
        <a href="#nega">Nega Joyliy?</a>
        <a href="#owner">Uy egalari uchun</a>
      </div>

      <!-- Column 2: Audience Categories -->
      <div>
        <h4>Kategoriyalar</h4>
        <a href="#natija">👨‍👩‍👧 Oila uchun ijara</a>
        <a href="#natija">👩 Qizlar va ayollar uchun</a>
        <a href="#natija">👨 Yigitlar va talabalar uchun</a>
        <a href="#natija">🚇 Metro yaqinidagi uylar</a>
        <a href="#natija">🛋 Mebelli xonadonlar</a>
      </div>

      <!-- Column 3: Contact & Telegram -->
      <div>
        <h4>Aloqa va Bot</h4>
        <a href="https://t.me/joyliy_bot" target="_blank" rel="noopener">
          🤖 Telegram Bot: @joyliy_bot
        </a>
        <a href="https://t.me/joyliy_uz" target="_blank" rel="noopener">
          📢 Telegram Kanal: @joyliy_uz
        </a>
        <a href="mailto:salom@joyliy.uz">
          ✉️ salom@joyliy.uz
        </a>
        <div class="address-text">
          Toshkent shahri, O‘zbekiston
        </div>
      </div>
    </div>

    <!-- Sub Footer -->
    <div class="wrap sub-footer">
      <div class="sub-footer-text">
        © 2026 Joyliy. Barcha huquqlar himoyalangan.
      </div>
      <div class="sub-footer-disclaimer">
        E’lonlar ommaviy manbalar va uy egalari tomonidan joylashtiriladi.
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: var(--surf);
  border-top: 1px solid var(--bd);
  padding: 56px 0 28px;
  margin-top: 56px;
}

.footer-grid {
  gap: 36px;
}

.footer-brand-col {
  display: flex;
  flex-direction: column;
}

.footer-logo {
  margin-bottom: 14px;
}

.brand-desc {
  font-size: 14px;
  line-height: 1.65;
  color: var(--tx-muted);
  margin: 0 0 16px;
  max-width: 340px;
}

.brand-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stat-pill {
  font-size: 11px;
  font-weight: 700;
  background: var(--mint-subtle);
  color: var(--ac);
  border: 1px solid rgba(23, 77, 58, 0.15);
  padding: 3px 10px;
  border-radius: var(--radius-full);
}

.address-text {
  font-size: 13px;
  color: var(--tx-muted);
  margin-top: 8px;
}

.sub-footer {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--bd);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: var(--tx-muted);
}

.sub-footer-disclaimer {
  font-size: 12px;
  opacity: 0.8;
}

@media (max-width: 767px) {
  .sub-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
