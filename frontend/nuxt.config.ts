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
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg', key: 'icon-svg' },
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico', key: 'icon-ico' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png', key: 'apple-touch-icon' },
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
    hooks: {
      'prerender:generate'(route) {
        if (route.fileName && route.fileName.endsWith('.html') && route.contents) {
          route.contents = route.contents.replace(
            '</head>',
            '<link rel="icon" type="image/svg+xml" href="/favicon.svg">\n<link rel="icon" type="image/x-icon" href="/favicon.ico">\n<link rel="shortcut icon" href="/favicon.ico">\n<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n</head>'
          )
        }
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

