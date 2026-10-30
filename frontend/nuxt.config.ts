// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: false },

  app: {
    head: {
      title: 'Joyliy — Toshkentda maklersiz ijara',
      htmlAttrs: {
        lang: 'uz',
      },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        {
          name: 'description',
          content: 'Toshkentda egasidan maklersiz ijara kvartiralar qidiruv platformasi.',
        },
        { name: 'theme-color', content: '#BC684B' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'%3E%3Crect width='24' height='24' rx='5.5' fill='%23BC684B'/%3E%3Cpath d='M4.5 10.5L12 4.25L19.5 10.5V18.5C19.5 19.3284 18.8284 20 18 20H6C5.17157 20 4.5 19.3284 4.5 18.5V10.5Z' stroke='%23FFFFFF' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ccircle cx='12' cy='13' r='1.6' fill='%23FFFFFF'/%3E%3C/svg%3E" },
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'alternate icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'shortcut icon', href: '/favicon.ico' },
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
        { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: '',
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  nitro: {
    routeRules: {
      '/api/**': {
        proxy: 'http://localhost:8000/api/**',
      },
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '',
      yandexMapsApiKey: process.env.YANDEX_MAPS_API_KEY || '',
    },
  },
})

