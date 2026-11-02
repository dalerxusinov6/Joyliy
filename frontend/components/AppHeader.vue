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
  'openNeighborhoods'
])
const { currentLang, setLang, t } = useI18n()
const { count: favCount } = useFavorites()
const { user, initAuth } = useAuth()
const { compareList } = useListings()

const isDark = ref(false)

onMounted(() => {
  initAuth()
  const saved = localStorage.getItem('joyliy_theme')
  if (saved === 'dark') {
    isDark.value = true
    document.documentElement.dataset.theme = 'dark'
  } else {
    isDark.value = false
    document.documentElement.dataset.theme = 'light'
    if (!saved) {
      localStorage.setItem('joyliy_theme', 'light')
    }
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
  <header class="iconly-header">
    <div class="wrap hd">
      <!-- Left: Logo & Wordmark -->
      <NuxtLink to="/" class="brand-link" aria-label="Joyliy.uz bosh sahifasi">
        <div class="brand-logo-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="logo-icon">
            <path d="M3 10.5 12 3l9 7.5V20a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 20v-9.5z" />
            <circle cx="12" cy="13" r="2.2" fill="currentColor" />
          </svg>
        </div>
        <div class="brand-identity">
          <span class="brand-name">Joyliy<span class="brand-tld">.uz</span></span>
        </div>
      </NuxtLink>

      <!-- Center: Clean Floating Pill Navigation (Hidden on mobile/tablet, desktop only) -->
      <nav class="d iconly-nav" aria-label="Asosiy navigatsiya">
        <a href="#katalog" class="nav-item">Bosh sahifa</a>
        <a href="#katalog" class="nav-item" @click.prevent="$emit('filterMaklersiz')">Maklersiz</a>
        <a href="#xarita" class="nav-item" @click.prevent="$emit('openMap')">Xarita</a>
        <a href="#hamxona" class="nav-item" @click.prevent="$emit('openRoommates')">Hamxona</a>
        <a href="#taqqoslash" class="nav-item" @click.prevent="$emit('openCompare')">
          Taqqoslash
          <span v-if="compareList.length" class="badge-mini">{{ compareList.length }}</span>
        </a>
      </nav>

      <span class="sp"></span>

      <!-- Right: Responsive Controls & Dark CTA Pill -->
      <div class="header-right">
        <!-- Language Switcher Pill -->
        <div class="lang-pill" role="group" aria-label="Tilni tanlash">
          <button
            type="button"
            class="lang-choice"
            :class="{ active: currentLang === 'uz' }"
            @click="onLangChange('uz')"
          >
            UZ
          </button>
          <button
            type="button"
            class="lang-choice"
            :class="{ active: currentLang === 'ru' }"
            @click="onLangChange('ru')"
          >
            RU
          </button>
        </div>

        <!-- Theme Toggle -->
        <button
          class="ib theme-btn"
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
            <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
          </svg>
          <span v-if="favCount > 0" class="fav-count">{{ favCount }}</span>
        </button>

        <!-- Profile (Desktop only) -->
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

        <!-- Iconly Black Capsule CTA Button -->
        <button class="btn btn-dark cta-post" @click="$emit('openNew')" title="E’lon berish">
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
.iconly-header {
  position: sticky;
  top: 0;
  z-index: var(--z-header, 100);
  background: rgba(243, 244, 245, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-subtle);
  transition: all 0.25s ease;
}

:root[data-theme="dark"] .iconly-header {
  background: rgba(14, 18, 23, 0.88);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

@media (min-width: 640px) {
  .brand-link {
    gap: 10px;
  }
}

.brand-logo-mark {
  width: 32px;
  height: 32px;
  background: var(--blue-gradient);
  color: #ffffff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(40, 120, 200, 0.3);
  transition: all 0.2s var(--ease);
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .brand-logo-mark {
    width: 36px;
    height: 36px;
    border-radius: 12px;
  }
}

.brand-link:hover .brand-logo-mark {
  transform: scale(1.05);
  box-shadow: 0 6px 18px rgba(40, 120, 200, 0.4);
}

.logo-icon {
  width: 17px;
  height: 17px;
  color: #ffffff;
}

@media (min-width: 768px) {
  .logo-icon {
    width: 20px;
    height: 20px;
  }
}

.brand-identity {
  display: flex;
  align-items: center;
}

.brand-name {
  font-family: var(--font-sans);
  font-size: clamp(16px, 4.4vw, 20px);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  line-height: 1;
  white-space: nowrap;
}

.brand-tld {
  color: var(--blue-primary);
  font-weight: 700;
}

/* Center Desktop Nav */
.iconly-nav {
  display: none;
  align-items: center;
  gap: 6px;
  margin-left: 24px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 4px 6px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

:root[data-theme="dark"] .iconly-nav {
  background: rgba(22, 27, 34, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
}

.nav-item {
  color: var(--text-secondary);
  font-size: 13.5px;
  font-weight: 600;
  padding: 7px 14px;
  border-radius: var(--radius-full);
  transition: all 0.18s var(--ease);
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.nav-item:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.8);
}

:root[data-theme="dark"] .nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

/* Header Right Controls */
.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

@media (min-width: 375px) {
  .header-right {
    gap: 8px;
  }
}

@media (min-width: 768px) {
  .header-right {
    gap: 10px;
  }
}

.desktop-only {
  display: none !important;
}

@media (min-width: 1024px) {
  .desktop-only {
    display: inline-flex !important;
  }
}

/* Language Pill Switcher */
.lang-pill {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  padding: 2px;
  height: 34px;
}

@media (min-width: 768px) {
  .lang-pill {
    padding: 3px;
    height: 36px;
  }
}

:root[data-theme="dark"] .lang-pill {
  background: rgba(22, 27, 34, 0.8);
}

.lang-choice {
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  padding: 3px 7px;
  border-radius: var(--radius-full);
  transition: all 0.18s ease;
  min-height: 28px;
}

@media (min-width: 768px) {
  .lang-choice {
    font-size: 11.5px;
    padding: 4px 10px;
  }
}

.lang-choice.active {
  background: #17191D;
  color: #FFFFFF;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

:root[data-theme="dark"] .lang-choice.active {
  background: var(--blue-primary);
  color: #FFFFFF;
}

.theme-btn {
  min-width: 36px;
  min-height: 36px;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  background: var(--surface);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s var(--ease);
}

@media (min-width: 768px) {
  .theme-btn {
    min-width: 38px;
    min-height: 38px;
    width: 38px;
    height: 38px;
  }
}

.theme-btn:hover {
  border-color: var(--blue-primary);
  color: var(--blue-primary);
}

.badge-mini {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--blue-primary);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  width: 17px;
  height: 17px;
  border-radius: 50%;
}

.saved-btn {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  background: var(--surface);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.fav-count {
  position: absolute;
  top: -3px;
  right: -3px;
  background: #EF4444;
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
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  background: var(--surface);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s var(--ease);
}

.profile-btn:hover {
  border-color: var(--blue-primary);
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.user-initial {
  font-family: var(--font-sans);
  font-weight: 700;
  color: var(--blue-primary);
  font-size: 14px;
}

.cta-post {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 36px;
  padding: 0 12px;
  font-size: 12.5px;
  font-weight: 700;
  border-radius: var(--radius-full);
  white-space: nowrap;
  background: #17191D;
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 12px rgba(23, 25, 29, 0.15);
  transition: all 0.18s var(--ease);
}

@media (min-width: 375px) {
  .cta-post {
    padding: 0 14px;
    font-size: 13px;
    height: 38px;
  }
}

:root[data-theme="dark"] .cta-post {
  background: var(--blue-primary);
}

.cta-post:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(23, 25, 29, 0.22);
}

.cta-post:active {
  transform: scale(0.97);
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
    height: 42px;
    padding: 0 20px;
    font-size: 13.5px;
  }
  .cta-text-full {
    display: inline;
  }
  .cta-text-short {
    display: none;
  }
}

@media (min-width: 1024px) {
  .iconly-nav {
    display: inline-flex;
  }
}
</style>
