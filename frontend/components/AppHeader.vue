<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useAuth } from '~/composables/useAuth'

const emit = defineEmits(['openFavorites', 'openProfile', 'openNew', 'filterMaklersiz', 'openMap'])
const { currentLang, setLang, t } = useI18n()
const { count: favCount } = useFavorites()
const { user, initAuth } = useAuth()

const isDark = ref(false)

onMounted(() => {
  initAuth()
  const saved = localStorage.getItem('joyliy_theme')
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.dataset.theme = 'dark'
  }
})

const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.dataset.theme = theme
  localStorage.setItem('joyliy_theme', theme)
}

const onLangChange = (lang: string) => {
  setLang(lang.toLowerCase() as any)
}
</script>

<template>
  <header class="editorial-header">
    <div class="wrap hd">
      <!-- Left: Architectural Brand Wordmark -->
      <NuxtLink to="/" class="brand-link">
        <div class="brand-badge-box">
          <span class="brand-num">№</span>
        </div>
        <div class="brand-identity">
          <span class="brand-name">JOYLIY</span>
          <span class="brand-issue">Toshkent · Maklersiz Ijara</span>
        </div>
      </NuxtLink>

      <!-- Center: Numbered Editorial Directory -->
      <nav class="d editorial-nav">
        <a href="#katalog" class="nav-item">
          <span class="nav-idx">01</span>
          <span class="nav-label">Katalog</span>
        </a>
        <a href="#katalog" class="nav-item" @click.prevent="$emit('filterMaklersiz')">
          <span class="nav-idx">02</span>
          <span class="nav-label">Maklersiz</span>
        </a>
        <a href="#xarita" class="nav-item" @click.prevent="$emit('openMap')">
          <span class="nav-idx">03</span>
          <span class="nav-label">Xarita</span>
        </a>
        <a href="#falsafa" class="nav-item">
          <span class="nav-idx">04</span>
          <span class="nav-label">Falsafa</span>
        </a>
      </nav>

      <span class="sp"></span>

      <!-- Right: Controls & CTA -->
      <div class="header-right">
        <!-- Language Switcher -->
        <div class="lang-group opt">
          <button
            type="button"
            class="lang-btn"
            :class="{ active: currentLang === 'uz' }"
            @click="onLangChange('uz')"
          >
            UZ
          </button>
          <span class="lang-slash">/</span>
          <button
            type="button"
            class="lang-btn"
            :class="{ active: currentLang === 'ru' }"
            @click="onLangChange('ru')"
          >
            RU
          </button>
        </div>

        <!-- Theme Toggle -->
        <button
          class="ib theme-btn opt"
          @click="toggleTheme"
          :aria-label="isDark ? 'Yorug‘ rejim' : 'Qorong‘i rejim'"
          title="Rejimni almashtirish"
        >
          <svg v-if="isDark" class="i" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
          </svg>
          <svg v-else class="i" viewBox="0 0 24 24">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        </button>

        <!-- Saved Listings -->
        <button
          class="ib saved-btn"
          @click="$emit('openFavorites')"
          :aria-label="t('saved')"
          title="Saqlangan uylar"
        >
          <svg class="i" viewBox="0 0 24 24">
            <path d="m19 21-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          <span v-if="favCount > 0" class="fav-count">{{ favCount }}</span>
        </button>

        <!-- Profile -->
        <button
          class="profile-btn"
          @click="$emit('openProfile')"
          :aria-label="t('profile')"
          :title="user ? user.first_name : t('profile')"
        >
          <img v-if="user && user.photo_url" :src="user.photo_url" class="user-avatar" alt="Avatar" />
          <span v-else-if="user && user.first_name" class="user-initial">
            {{ user.first_name[0].toUpperCase() }}
          </span>
          <svg v-else class="i" viewBox="0 0 24 24">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21a8 8 0 0 1 16 0" />
          </svg>
        </button>

        <!-- Terracotta CTA -->
        <button class="btn p cta-post opt" @click="$emit('openNew')">
          <span>E’lon berish</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.editorial-header {
  border-bottom: 1px solid var(--sand);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-badge-box {
  width: 32px;
  height: 32px;
  background: var(--ink);
  color: var(--ivory);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-xs);
}

.brand-num {
  font-family: var(--font-serif);
  font-style: italic;
  font-size: 15px;
}

.brand-identity {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-family: var(--font-serif);
  font-size: 21px;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--ink);
  line-height: 1;
}

.brand-issue {
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 3px;
}

.editorial-nav {
  display: none;
  gap: 28px;
  margin-left: 36px;
}

.nav-item {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  color: var(--ink);
  font-size: 13.5px;
  font-weight: 500;
  position: relative;
  padding: 6px 0;
}

.nav-idx {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--terracotta);
  font-weight: 600;
}

.nav-label {
  letter-spacing: 0.02em;
}

.nav-item::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--terracotta);
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.25s var(--ease);
}

.nav-item:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-group {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  border: 1px solid var(--sand);
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  background: var(--surf);
}

.lang-btn {
  color: var(--muted);
  font-weight: 600;
  padding: 0 2px;
  transition: color 0.15s ease;
}

.lang-btn.active {
  color: var(--terracotta);
  font-weight: 800;
}

.lang-slash {
  color: var(--sand);
}

.saved-btn {
  position: relative;
}

.fav-count {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--terracotta);
  color: #fff;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--sand);
  background: var(--surf);
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s var(--ease);
}

.profile-btn:hover {
  border-color: var(--ink);
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-xs);
}

.user-initial {
  font-family: var(--font-serif);
  font-style: italic;
  font-weight: 700;
  color: var(--terracotta);
  font-size: 16px;
}

.cta-post {
  padding: 0 18px;
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

@media (min-width: 1024px) {
  .editorial-nav {
    display: flex;
  }
}
</style>
