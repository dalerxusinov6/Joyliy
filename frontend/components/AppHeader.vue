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

const onLangChange = (e: Event) => {
  const target = e.target as HTMLSelectElement
  setLang(target.value.toLowerCase() as any)
}
</script>

<template>
  <header>
    <div class="wrap hd">
      <!-- Brand Logo -->
      <NuxtLink to="/" class="logo">
        <div class="logo-icon-box">
          <svg viewBox="0 0 24 24" class="logo-svg" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <!-- House arch combined with key symbol -->
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

      <!-- Desktop Navigation -->
      <nav class="d">
        <a href="#natija">{{ t('find_apartment') }}</a>
        <a href="#natija" @click="$emit('filterMaklersiz')">
          <span class="nav-pill-badge">100%</span>
          {{ t('no_agent_rentals') }}
        </a>
        <a href="#qanday">{{ t('how_it_works') }}</a>
        <a href="#nega">Nega Joyliy?</a>
      </nav>

      <span class="sp"></span>

      <!-- Right Header Actions -->
      <div class="header-actions">
        <!-- Language selector -->
        <div class="lang-selector-wrap opt">
          <select class="lang" :value="currentLang.toUpperCase()" @change="onLangChange" aria-label="Til">
            <option value="UZ">UZ</option>
            <option value="RU">RU</option>
            <option value="EN">EN</option>
          </select>
        </div>

        <!-- Theme toggle -->
        <button class="ib opt" @click="toggleTheme" :aria-label="isDark ? 'Yorug‘ rejim' : 'Qorong‘i rejim'">
          <!-- Sun icon when dark -->
          <svg v-if="isDark" class="i" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
          </svg>
          <!-- Moon icon when light -->
          <svg v-else class="i" viewBox="0 0 24 24">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        </button>

        <!-- Saved favorites -->
        <button class="ib fav-btn" @click="$emit('openFavorites')" :aria-label="t('saved')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
          </svg>
          <span v-if="favCount > 0" class="badge">{{ favCount }}</span>
        </button>

        <!-- Post ad CTA Button -->
        <button class="btn p post-btn opt" @click="$emit('openNew')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M12 5v14M5 12h14" />
          </svg>
          <span>{{ t('post_ad') }}</span>
        </button>

        <!-- User Profile Pill -->
        <button
          class="profile-pill"
          @click="$emit('openProfile')"
          :aria-label="t('profile')"
          :title="user ? user.first_name : t('profile')"
        >
          <img v-if="user && user.photo_url" :src="user.photo_url" class="avatar-header" alt="Avatar" />
          <span v-else-if="user && user.first_name" class="avatar-initial-header">
            {{ user.first_name[0].toUpperCase() }}
          </span>
          <div v-else class="avatar-guest">
            <svg class="i" viewBox="0 0 24 24">
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21a8 8 0 0 1 16 0" />
            </svg>
          </div>
          <span v-if="user" class="profile-name opt">{{ user.first_name }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.logo-wordmark {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.logo-title {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--tx);
}

.logo-sub {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--ac);
  margin-top: 1px;
}

.logo-svg {
  width: 20px;
  height: 20px;
}

.nav-pill-badge {
  background: var(--mint);
  color: var(--ac-dark);
  font-size: 10px;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: var(--radius-full);
  margin-right: 4px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.post-btn {
  background: var(--ac) !important;
  color: #FFFFFF !important;
  border-color: var(--ac) !important;
  font-weight: 700;
  padding: 0 18px;
  border-radius: var(--radius-md);
  box-shadow: 0 4px 14px rgba(23, 77, 58, 0.22);
}

.post-btn:hover {
  background: var(--ac-hover) !important;
  transform: translateY(-1px);
}

.profile-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 3px 6px 3px 3px;
  border-radius: var(--radius-full);
  background: var(--card);
  border: 1px solid var(--bd);
  transition: all 0.2s var(--ease-smooth);
}

.profile-pill:hover {
  border-color: var(--bd-hover);
  background: var(--surf-muted);
}

.avatar-header,
.avatar-initial-header,
.avatar-guest {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  object-fit: cover;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-header {
  border: 1.5px solid var(--ac);
}

.avatar-initial-header {
  background: var(--ac);
  color: var(--mint);
  font-weight: 700;
  font-size: 14px;
}

.avatar-guest {
  background: var(--surf-muted);
  color: var(--tx-muted);
}

.avatar-guest svg {
  width: 18px;
  height: 18px;
}

.profile-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--tx);
  padding-right: 6px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (min-width: 1024px) {
  .post-btn {
    display: inline-flex !important;
  }
}
</style>
