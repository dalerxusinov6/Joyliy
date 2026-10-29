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
      ],
      link: [
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
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
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

