<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
const { t } = useI18n()
</script>

<template>
  <footer class="iconly-footer">
    <div class="wrap">
      <!-- Top Masthead of Footer -->
      <div class="footer-top-bar">
        <div class="footer-brand">
          <div class="brand-logo-mark-sm">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="logo-icon-sm">
              <path d="M3 10.5 12 3l9 7.5V20a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 20v-9.5z" />
              <circle cx="12" cy="13" r="2.2" fill="currentColor" />
            </svg>
          </div>
          <span class="footer-brand-title">Joyliy<span class="brand-tld">.uz</span></span>
          <span class="footer-brand-sub">O‘zbekiston zamonaviy uy-joy ekosistemasi</span>
        </div>
        <div class="footer-edition">
          <span>Toshkent · 2026</span>
        </div>
      </div>

      <!-- Main Columns Grid -->
      <div class="footer-columns-grid">
        <!-- Col 1: About / Statement -->
        <div class="footer-col about-col">
          <h4 class="col-heading">Joyliy haqida</h4>
          <p class="col-desc">
            Joyliy — mulk egalari va ijarachilarni to‘g‘ridan-to‘g‘ri bog‘lovchi aqlli proptech platformasi. 0% vositachilik to‘lovi, sun’iy intellekt bozor tahlili va shaffof shartlar bilan orzuingizdagi uyni toping.
          </p>
          <div class="footer-badges">
            <span class="f-badge">0% Vositachilik</span>
            <span class="f-badge">Joyliy AI</span>
            <span class="f-badge">Shaffof narxlar</span>
          </div>
        </div>

        <!-- Col 2: Directory -->
        <div class="footer-col">
          <h4 class="col-heading">Katalog</h4>
          <a href="#katalog" class="footer-link">Barcha xonadonlar</a>
          <a href="#katalog" class="footer-link">Maklersiz uylar</a>
          <a href="#katalog" class="footer-link">Bozordan arzon takliflar</a>
          <a href="#katalog" class="footer-link">Yangi e’lonlar</a>
          <a href="#katalog" class="footer-link">Sheriklik va talabalar</a>
        </div>

        <!-- Col 3: Districts -->
        <div class="footer-col">
          <h4 class="col-heading">Tumanlar</h4>
          <a href="#katalog" class="footer-link">Chilonzor tumani</a>
          <a href="#katalog" class="footer-link">Yunusobod tumani</a>
          <a href="#katalog" class="footer-link">Mirzo Ulug‘bek tumani</a>
          <a href="#katalog" class="footer-link">Mirobod tumani</a>
          <a href="#katalog" class="footer-link">Yakkasaroy tumani</a>
          <a href="#katalog" class="footer-link">Yashnobod tumani</a>
        </div>

        <!-- Col 4: Telegram & Contacts -->
        <div class="footer-col">
          <h4 class="col-heading">Aloqa va Bot</h4>
          <a href="https://t.me/joyliy_bot" target="_blank" rel="noopener" class="footer-link special-link">
            <svg class="foot-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m22 2-11 11M22 2l-7 20-4-9-9-4z" />
            </svg>
            <span>Telegram Bot: @joyliy_bot</span>
          </a>
          <a href="https://t.me/joyliy_uz" target="_blank" rel="noopener" class="footer-link special-link">
            <svg class="foot-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m3 11 18-5v12L3 14v-3z" />
              <path d="M11.6 16.8a3 3 0 1 1-5.8-1.6" />
            </svg>
            <span>Telegram Kanal: @joyliy_uz</span>
          </a>
          <a href="mailto:salom@joyliy.uz" class="footer-link">
            <svg class="foot-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <polyline points="22,6 12,13 2,6" />
            </svg>
            <span>salom@joyliy.uz</span>
          </a>
          <span class="city-location">Toshkent shahri, O‘zbekiston</span>
        </div>
      </div>

      <!-- Bottom Legal Line -->
      <div class="footer-bottom-line">
        <div class="legal-left">
          © 2026 Joyliy.uz. Barcha huquqlar himoyalangan.
        </div>
        <div class="legal-right">
          E’lonlar ochiq manbalar va mulk egalari tomonidan taqdim etiladi.
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.iconly-footer {
  background: var(--surface);
  border-top: 1px solid var(--border-subtle);
  padding: 56px 0 32px;
  margin-top: 48px;
}

.footer-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 36px;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.brand-logo-mark-sm {
  width: 28px;
  height: 28px;
  background: var(--blue-gradient);
  color: #ffffff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon-sm {
  width: 16px;
  height: 16px;
}

.footer-brand-title {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.brand-tld {
  color: var(--blue-primary);
}

.footer-brand-sub {
  font-size: 13px;
  color: var(--text-secondary);
  margin-left: 6px;
}

.footer-edition {
  font-size: 12px;
  font-weight: 600;
  color: var(--blue-deep);
}

.footer-columns-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  margin-bottom: 40px;
}

@media (min-width: 640px) {
  .footer-columns-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .footer-columns-grid {
    grid-template-columns: 1.4fr 1fr 1fr 1.2fr;
    gap: 40px;
  }
}

.col-heading {
  font-family: var(--font-sans);
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.col-desc {
  font-size: 13.5px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 16px;
}

.footer-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.f-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--blue-deep);
  background: var(--blue-pale);
  padding: 3px 9px;
  border-radius: var(--radius-full);
}

.footer-link {
  display: block;
  font-size: 13.5px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  transition: color 0.15s ease;
}

.footer-link:hover {
  color: var(--blue-primary);
}

.special-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-weight: 600;
}

.special-link:hover {
  color: var(--blue-primary);
}

.foot-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: var(--blue-primary);
}

.city-location {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 14px;
}

.footer-bottom-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 24px;
  border-top: 1px solid var(--border-subtle);
  font-size: 12px;
  color: var(--text-secondary);
  flex-wrap: wrap;
  gap: 10px;
}
</style>
