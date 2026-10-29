import { ref, computed } from 'vue'

export type Language = 'uz' | 'ru' | 'en'

const translations: Record<Language, Record<string, string>> = {
  uz: {
    find_apartment: 'Kvartira topish',
    no_agent_rentals: 'Maklersiz ijara',
    how_it_works: 'Qanday ishlaydi?',
    post_ad: 'E’lon berish',
    hero_title: 'Uy topish osonroq.',
    hero_sub: 'Toshkent bo‘ylab o‘zingizga mos kvartirani toping. Egasi bilan to‘g‘ridan-to‘g‘ri bog‘laning.',
    area_or_metro: 'Hudud yoki metro',
    rooms_count: 'Xonalar soni',
    price_range: 'Narx oralig‘i',
    all_areas: 'Barcha hududlar',
    any: 'Istalgan',
    any_price: 'Istalgan narx',
    filters: 'Filtrlar',
    search: 'Qidirish',
    clear: 'Tozalash',
    per_month: '/ oy',
    rooms_apartment: 'xonali kvartira',
    studio: 'Studiya',
    verified_owner: 'Tasdiqlangan egasi — Maklersiz',
    under_review: 'Tekshiruvda',
    save: 'Saqlash',
    saved: 'Saqlanganlar',
    today: 'Bugun',
    yesterday: 'Kecha',
    days_ago: 'kun oldin',
    listings_found: 'ta e’lon topildi',
    min_to_metro: 'metroga {min} daqiqa',
    featured: 'Tanlangan e’lonlar',
    recently_added: 'Yangi qo‘shilganlar',
    near_metro: 'Metro yaqinida',
    roommates: 'Xonadosh qidirayotganlar uchun',
    nothing_found: 'Hech narsa topilmadi. Filtrlarni o‘zgartirib ko‘ring.',
    no_saved: 'Hali hech narsa saqlanmagan.',
    close: 'Yopish',
    view_on_olx: 'OLX’da ko‘rish',
    call: 'Qo‘ng‘iroq qilish',
    telegram: 'Telegram',
    report: 'Shikoyat qilish',
    report_received: 'Shikoyat qabul qilindi. Rahmat!',
    save_added: 'Saqlanganlarga qo‘shildi!',
    save_removed: 'Saqlanganlardan o‘chirildi',
    map: 'Xarita',
    profile: 'Profil',
  },
  ru: {
    find_apartment: 'Найти квартиру',
    no_agent_rentals: 'Аренда без маклеров',
    how_it_works: 'Как это работает?',
    post_ad: 'Подать объявление',
    hero_title: 'Найти жильё стало проще.',
    hero_sub: 'Найдите подходящую квартиру по всему Ташкенту. Связывайтесь напрямую с владельцем.',
    area_or_metro: 'Район или метро',
    rooms_count: 'Количество комнат',
    price_range: 'Диапазон цен',
    all_areas: 'Все районы',
    any: 'Любое',
    any_price: 'Любая цена',
    filters: 'Фильтры',
    search: 'Искать',
    clear: 'Сбросить',
    per_month: '/ мес',
    rooms_apartment: '-комнатная квартира',
    studio: 'Студия',
    verified_owner: 'Проверенный владелец — Без маклера',
    under_review: 'На проверке',
    save: 'Сохранить',
    saved: 'Избранное',
    today: 'Сегодня',
    yesterday: 'Вчера',
    days_ago: 'дн. назад',
    listings_found: 'объявлений найдено',
    min_to_metro: 'до метро {min} мин',
    featured: 'Подборка объявлений',
    recently_added: 'Новые объявления',
    near_metro: 'Рядом с метро',
    roommates: 'Для совместной аренды',
    nothing_found: 'Ничего не найдено. Попробуйте изменить фильтры.',
    no_saved: 'Пока ничего не сохранено.',
    close: 'Закрыть',
    view_on_olx: 'Смотреть на OLX',
    call: 'Позвонить',
    telegram: 'Telegram',
    report: 'Пожаловаться',
    report_received: 'Жалоба принята. Спасибо!',
    save_added: 'Добавлено в избранное!',
    save_removed: 'Удалено из избранного',
    map: 'Карта',
    profile: 'Профиль',
  },
  en: {
    find_apartment: 'Find apartments',
    no_agent_rentals: 'No-agent rentals',
    how_it_works: 'How it works',
    post_ad: 'Post a listing',
    hero_title: 'Finding a home, made easier.',
    hero_sub: 'Find the right apartment across Tashkent. Contact the owner directly.',
    area_or_metro: 'District or metro',
    rooms_count: 'Number of rooms',
    price_range: 'Price range',
    all_areas: 'All districts',
    any: 'Any',
    any_price: 'Any price',
    filters: 'Filters',
    search: 'Search',
    clear: 'Clear',
    per_month: '/ mo',
    rooms_apartment: '-room apartment',
    studio: 'Studio',
    verified_owner: 'Verified owner — No agent',
    under_review: 'Under review',
    save: 'Save',
    saved: 'Saved',
    today: 'Today',
    yesterday: 'Yesterday',
    days_ago: 'days ago',
    listings_found: 'listings found',
    min_to_metro: '{min} min to metro',
    featured: 'Featured listings',
    recently_added: 'Recently added',
    near_metro: 'Near metro',
    roommates: 'For roommates',
    nothing_found: 'Nothing found. Try adjusting your filters.',
    no_saved: 'No saved listings yet.',
    close: 'Close',
    view_on_olx: 'View on OLX',
    call: 'Call',
    telegram: 'Telegram',
    report: 'Report',
    report_received: 'Report received. Thank you!',
    save_added: 'Added to favorites!',
    save_removed: 'Removed from favorites',
    map: 'Map',
    profile: 'Profile',
  },
}

export function useI18n() {
  const currentLang = useState<Language>('lang', () => 'uz')

  const setLang = (lang: Language) => {
    currentLang.value = lang
    if (import.meta.client) {
      localStorage.setItem('lang', lang)
      document.documentElement.lang = lang
    }
  }

  const t = (key: string, params: Record<string, any> = {}): string => {
    let text = translations[currentLang.value]?.[key] || translations.uz[key] || key
    for (const [k, v] of Object.entries(params)) {
      text = text.replace(`{${k}}`, String(v))
    }
    return text
  }

  return {
    currentLang,
    setLang,
    t,
  }
}

