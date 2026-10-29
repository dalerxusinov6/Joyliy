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
        <div class="brand-logo-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="logo-icon">
            <path d="M3 10.5 12 3l9 7.5V20a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 20v-9.5z" />
            <circle cx="12" cy="13" r="2" fill="currentColor" />
          </svg>
        </div>
        <div class="brand-identity">
          <span class="brand-name">Joyliy</span>
        </div>
      </NuxtLink>

      <!-- Center: Clean Navigation -->
      <nav class="d editorial-nav">
        <a href="#katalog" class="nav-item">Katalog</a>
        <a href="#katalog" class="nav-item" @click.prevent="$emit('filterMaklersiz')">Maklersiz</a>
        <a href="#xarita" class="nav-item" @click.prevent="$emit('openMap')">Xarita</a>
        <a href="#falsafa" class="nav-item">Falsafa</a>
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

        <!-- Saved Listings (Visible on tablet/desktop, mobile has bottom bar) -->
        <button
          class="ib saved-btn desktop-only"
          @click="$emit('openFavorites')"
          :aria-label="t('saved')"
          title="Saqlangan uylar"
        >
          <svg class="i" viewBox="0 0 24 24">
            <path d="m19 21-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          <span v-if="favCount > 0" class="fav-count">{{ favCount }}</span>
        </button>

        <!-- Profile (Visible on tablet/desktop, mobile has bottom bar) -->
        <button
          class="profile-btn desktop-only"
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
        <button class="btn p cta-post" @click="$emit('openNew')" title="E’lon joylash">
          <svg class="cta-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span class="cta-text-full">E’lon berish</span>
          <span class="cta-text-short">E’lon</span>
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
  gap: 10px;
}

.brand-logo-mark {
  width: 32px;
  height: 32px;
  background: var(--ink);
  color: #ffffff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  width: 18px;
  height: 18px;
}

.brand-identity {
  display: flex;
  align-items: center;
}

.brand-name {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--ink);
  line-height: 1;
}

.editorial-nav {
  display: none;
  gap: 28px;
  margin-left: 36px;
}

.nav-item {
  color: var(--ink);
  font-size: 14px;
  font-weight: 600;
  position: relative;
  padding: 6px 0;
  transition: color 0.18s;
}

.nav-item:hover {
  color: var(--terracotta);
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
  gap: 8px;
}

@media (min-width: 768px) {
  .header-right {
    gap: 12px;
  }
}

.desktop-only {
  display: none !important;
}

@media (min-width: 768px) {
  .desktop-only {
    display: inline-flex !important;
  }
}

.lang-group {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
  font-size: 12px;
  border: 1px solid var(--sand);
  padding: 0 8px;
  height: 36px;
  border-radius: 8px;
  background: var(--surf);
}

.theme-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--sand);
  background: var(--surf);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ink);
  transition: all 0.18s var(--ease);
}

.theme-btn:hover {
  border-color: var(--ink);
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
  width: 38px;
  height: 38px;
  border-radius: 8px;
  border: 1px solid var(--sand);
  background: var(--surf);
  display: flex;
  align-items: center;
  justify-content: center;
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
  width: 38px;
  height: 38px;
  border-radius: 8px;
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
  border-radius: 8px;
}

.user-initial {
  font-family: var(--font-sans);
  font-weight: 700;
  color: var(--terracotta);
  font-size: 15px;
}

.cta-post {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 36px;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 700;
  border-radius: 8px;
  white-space: nowrap;
  background: var(--terracotta);
  color: #ffffff;
  border: none;
  transition: all 0.18s var(--ease);
}

.cta-post:hover {
  background: var(--terracotta-hover);
}

.cta-plus {
  width: 13px;
  height: 13px;
  flex-shrink: 0;
}

.cta-text-full {
  display: none;
}

.cta-text-short {
  display: inline;
}

@media (min-width: 768px) {
  .cta-post {
    height: 40px;
    padding: 0 18px;
    font-size: 13.5px;
    border-radius: 10px;
  }
  .cta-text-full {
    display: inline;
  }
  .cta-text-short {
    display: none;
  }
}

@media (min-width: 1024px) {
  .editorial-nav {
    display: flex;
  }
}
</style>
