<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
const { t } = useI18n()
</script>

<template>
  <footer class="monograph-footer">
    <div class="wrap">
      <!-- Top Masthead of Footer -->
      <div class="footer-top-bar">
        <div class="footer-brand">
          <span class="footer-brand-title">JOYLIY</span>
          <span class="footer-brand-sub">Toshkent Arxitektura va Ijara Monografiyasi</span>
        </div>
        <div class="footer-edition">
          <span>Nashr № 01 · 2026</span>
        </div>
      </div>

      <!-- Main Columns Grid -->
      <div class="footer-columns-grid">
        <!-- Col 1: About / Statement -->
        <div class="footer-col about-col">
          <h4 class="col-heading">Toshkent Ijarasi</h4>
          <p class="col-desc">
            Joyliy — mulk egalari va ijarachilarni to‘g‘ridan-to‘g‘ri bog‘lovchi mustaqil arxitektura va turar-joy maydoni. Ortiqcha komissiyalarsiz va shaffof shartlar bilan yangi uyingizni kashf eting.
          </p>
          <div class="footer-badges">
            <span class="f-badge">0% Vositachilik</span>
            <span class="f-badge">Shaffof narxlar</span>
          </div>
        </div>

        <!-- Col 2: Directory -->
        <div class="footer-col">
          <h4 class="col-heading">01 / Katalog</h4>
          <a href="#katalog" class="footer-link">Barcha xonadonlar</a>
          <a href="#katalog" class="footer-link">Maklersiz uylar</a>
          <a href="#katalog" class="footer-link">Oxirgi 3 kunlik</a>
          <a href="#katalog" class="footer-link">Sheriklik va talabalar</a>
        </div>

        <!-- Col 3: Districts -->
        <div class="footer-col">
          <h4 class="col-heading">02 / Koordinatalar</h4>
          <a href="#katalog" class="footer-link">Chilonzor tumani</a>
          <a href="#katalog" class="footer-link">Yunusobod tumani</a>
          <a href="#katalog" class="footer-link">Mirzo Ulug‘bek tumani</a>
          <a href="#katalog" class="footer-link">Mirobod tumani</a>
          <a href="#katalog" class="footer-link">Yakkasaroy tumani</a>
        </div>

        <!-- Col 4: Telegram & Contacts -->
        <div class="footer-col">
          <h4 class="col-heading">03 / Aloqa va Bot</h4>
          <a href="https://t.me/joyliy_bot" target="_blank" rel="noopener" class="footer-link special">
            🤖 Telegram Bot: @joyliy_bot
          </a>
          <a href="https://t.me/joyliy_uz" target="_blank" rel="noopener" class="footer-link special">
            📢 Telegram Kanal: @joyliy_uz
          </a>
          <a href="mailto:salom@joyliy.uz" class="footer-link">
            ✉️ salom@joyliy.uz
          </a>
          <span class="city-location">Toshkent, O‘zbekiston</span>
        </div>
      </div>

      <!-- Bottom Legal Line -->
      <div class="footer-bottom-line">
        <div class="legal-left">
          © 2026 Joyliy. Barcha huquqlar himoyalangan.
        </div>
        <div class="legal-right">
          E’lonlar ochiq manbalar va mulk egalari tomonidan taqdim etiladi.
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.monograph-footer {
  background: var(--surf);
  border-top: 1px solid var(--sand);
  padding: 56px 0 32px;
  margin-top: 60px;
}

.footer-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--sand);
  margin-bottom: 40px;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-brand {
  display: flex;
  align-items: baseline;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-brand-title {
  font-family: var(--font-serif);
  font-size: 24px;
  letter-spacing: 0.15em;
  font-weight: 600;
  color: var(--ink);
}

.footer-brand-sub {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
}

.footer-edition {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.1em;
  color: var(--terracotta);
}

.footer-columns-grid {
  display: grid;
  gap: 36px;
  grid-template-columns: 1fr;
  margin-bottom: 48px;
}

.col-heading {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink);
  margin: 0 0 16px;
}

.col-desc {
  font-size: 14px;
  line-height: 1.65;
  color: var(--muted);
  margin: 0 0 18px;
}

.footer-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.f-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  padding: 3px 8px;
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  color: var(--muted);
  background: var(--ivory);
}

.footer-link {
  display: block;
  font-size: 13.5px;
  color: var(--muted);
  padding: 5px 0;
  transition: color 0.18s ease;
}

.footer-link:hover {
  color: var(--terracotta);
}

.footer-link.special {
  color: var(--ink);
  font-weight: 600;
}

.city-location {
  display: block;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted);
  margin-top: 8px;
}

.footer-bottom-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 24px;
  border-top: 1px solid var(--sand);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted);
  flex-wrap: wrap;
  gap: 12px;
}

@media (min-width: 768px) {
  .footer-columns-grid {
    grid-template-columns: 1.5fr 1fr 1fr 1.2fr;
  }
}
</style>
