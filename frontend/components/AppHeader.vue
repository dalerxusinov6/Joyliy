<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useAuth } from '~/composables/useAuth'

const emit = defineEmits(['openFavorites', 'openProfile', 'openNew', 'filterMaklersiz'])
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
      <NuxtLink to="/" class="logo">
        <b>
          <svg class="i" style="stroke: #fff" viewBox="0 0 24 24">
            <circle cx="8" cy="15" r="4" fill="none" stroke="currentColor" stroke-width="2" />
            <path d="m11 12 9-9M16 7l3 3" fill="none" stroke="currentColor" stroke-width="2" />
          </svg>
        </b>
        Joyliy
      </NuxtLink>

      <nav class="d">
        <a href="#natija">{{ t('find_apartment') }}</a>
        <a href="#natija" @click="$emit('filterMaklersiz')">{{ t('no_agent_rentals') }}</a>
        <a href="#qanday">{{ t('how_it_works') }}</a>
      </nav>

      <span class="sp"></span>

      <!-- Language selector -->
      <select class="lang opt" :value="currentLang.toUpperCase()" @change="onLangChange" aria-label="Til">
        <option value="UZ">UZ</option>
        <option value="RU">RU</option>
        <option value="EN">EN</option>
      </select>

      <!-- Theme toggle -->
      <button class="ib opt" @click="toggleTheme" aria-label="Mavzu">
        <svg class="i" viewBox="0 0 24 24">
          <path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z" />
        </svg>
      </button>

      <!-- Saved favorites -->
      <button class="ib" @click="$emit('openFavorites')" aria-label="Saqlanganlar">
        <svg class="i" viewBox="0 0 24 24">
          <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
        </svg>
        <span v-if="favCount > 0" class="badge">{{ favCount }}</span>
      </button>

      <!-- Post ad -->
      <button class="btn p opt" style="display: none" id="pubTop" @click="$emit('openNew')">
        <svg class="i" viewBox="0 0 24 24">
          <path d="M12 5v14M5 12h14" />
        </svg>
        <span>{{ t('post_ad') }}</span>
      </button>

      <!-- Profile button -->
      <button
        class="ib profile-btn"
        @click="$emit('openProfile')"
        :aria-label="t('profile')"
        :title="user ? user.first_name : t('profile')"
      >
        <img v-if="user && user.photo_url" :src="user.photo_url" class="avatar-header" alt="Avatar" />
        <span v-else-if="user && user.first_name" class="avatar-initial-header">
          {{ user.first_name[0].toUpperCase() }}
        </span>
        <svg v-else class="i" viewBox="0 0 24 24">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 21a8 8 0 0 1 16 0" />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.avatar-header {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid #229ed9;
}

.avatar-initial-header {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #229ed9;
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (min-width: 1024px) {
  #pubTop {
    display: inline-flex !important;
  }
}
</style>

