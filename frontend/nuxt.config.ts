// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: false },

  app: {
    head: {
      title: 'Joyliy — Toshkentda maklersiz ijara',
      htmlAttrs: {
        lang: 'uz',
        'data-theme': 'light',
      },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        {
          name: 'description',
          content: 'Toshkentda egasidan maklersiz ijara kvartiralar qidiruv platformasi.',
        },
        { name: 'theme-color', content: '#F3F4F5' },
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
      script: [
        {
          type: 'text/javascript',
          innerHTML: `(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=114005652', 'ym');ym(114005652, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});`,
        },
      ],
      noscript: [
        {
          innerHTML: `<div><img src="https://mc.yandex.ru/watch/114005652" style="position:absolute; left:-9999px;" alt="" /></div>`,
        },
      ],
    },
  },

  css: ['~/assets/css/main.css', '~/assets/css/admin.css'],

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

