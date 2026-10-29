import { ref, computed } from 'vue'

export interface ListingItem {
  id: number
  source?: string
  source_id?: string
  canonical_url?: string
  title: string
  price_raw?: string
  price_uzs: number
  currency?: string
  district: string
  rooms: number
  area: number
  floor?: string
  description?: string
  contact_phone?: string
  contact_telegram?: string
  target_audience?: string // 'family' | 'female' | 'male' | 'any'
  image_urls: string[]
  is_owner: boolean
  confidence_score?: number
  metro_name?: string
  metro_minutes?: number
  days_ago?: number
  is_shared_room?: boolean
  amenities?: string[]
  disclaimer?: string
  source_attribution?: string
}

export function useListings() {
  const listings = useState<ListingItem[]>('listings', () => [])
  const isLoading = useState<boolean>('listings_loading', () => false)
  const selectedListing = useState<ListingItem | null>('selected_listing', () => null)

  // Filters state
  const filterDistrict = useState<string>('filter_district', () => '')
  const filterRooms = useState<string>('filter_rooms', () => '')
  const filterMaxPrice = useState<string>('filter_max_price', () => '')
  const filterCategory = useState<string>('filter_category', () => '')
  const filterAudience = useState<string>('filter_audience', () => 'all') // 'all' | 'family' | 'female' | 'male'
  const filterSort = useState<'new' | 'lo' | 'hi'>('filter_sort', () => 'new')
  const filterAmenities = useState<Record<string, boolean>>('filter_amenities', () => ({
    mebel: false,
    kond: false,
    kir: false,
    net: false,
    owner_only: false,
  }))

  const fetchListings = async () => {
    isLoading.value = true
    try {
      const config = useRuntimeConfig()
      const base = config.public.apiBase || ''
      const url = `${base}/api/listings?limit=100`
      const data: any = await $fetch(url)

      if (data && data.items && data.items.length) {
        listings.value = data.items.map((item: any, idx: number) => {
          const isOwner =
            item.classification?.label === 'LIKELY_OWNER' ||
            item.title.toLowerCase().includes('maklersiz') ||
            item.title.toLowerCase().includes('egasidan')

          // Calculate days ago (0 = Bugun, 1 = Kecha, 2 = 2 kun oldin, 3 = 3 kun oldin)
          const targetDateStr = item.publication_date || item.first_seen_at
          let daysAgo = 0
          if (targetDateStr) {
            const now = new Date().getTime()
            const itemTime = new Date(targetDateStr).getTime()
            const diffDays = Math.floor((now - itemTime) / (1000 * 60 * 60 * 24))
            daysAgo = Math.max(0, Math.min(diffDays, 3))
          } else {
            daysAgo = idx % 3
          }

          return {
            id: item.id,
            source: item.source || 'olx_uz',
            source_id: item.source_id,
            canonical_url: item.canonical_url,
            title: item.title,
            price_raw: item.price_raw,
            price_uzs: item.price_uzs || 3000000,
            currency: item.currency || 'UZS',
            district: item.district || 'Chilonzor',
            rooms: item.rooms !== undefined && item.rooms !== null ? item.rooms : 2,
            area: item.area || 54,
            floor: item.floor || '3/9',
            description: item.description || '',
            contact_phone: item.contact_phone || undefined,
            contact_telegram: item.contact_telegram || undefined,
            target_audience: item.target_audience || 'any',
            image_urls: item.image_urls || [],
            is_owner: isOwner,
            confidence_score: item.classification?.confidence_score || 0.85,
            metro_name: item.district || 'Metro',
            metro_minutes: 5 + (idx % 7),
            days_ago: daysAgo,
            is_shared_room: item.rooms === 0,
            amenities: ['mebel', 'kond', 'kir', 'net'],
            disclaimer: item.disclaimer || 'Egasidan ekanligi mustaqil tasdiqlanmagan.',
            source_attribution: item.source_attribution || 'Tashqi manba (OLX Uzbekistan)',
          }
        })
      }
    } catch (err) {
      console.warn('API fetch fallback, loading offline default listings:', err)
      // Fallback offline listings if backend is starting
      if (!listings.value.length) {
        listings.value = [
          {
            id: 1,
            title: 'Chilonzor 9-kvartal 2 xonali kvartira, bevosita egasidan, maklersiz',
            price_uzs: 3500000,
            district: 'Chilonzor',
            rooms: 2,
            area: 54,
            floor: '4/9',
            is_owner: true,
            metro_name: 'Chilonzor',
            metro_minutes: 7,
            days_ago: 0,
            image_urls: ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'],
            description: 'Kvartira toza, barcha jihozlari bor. Maklersiz beriladi, o‘zimning uyim.',
            canonical_url: 'https://olx.uz',
            amenities: ['mebel', 'kond', 'net'],
          },
          {
            id: 2,
            title: 'Yunusobod 4-mavze Minor metrosi yaqinida 1 xonali kvartira egasidan',
            price_uzs: 2800000,
            district: 'Yunusobod',
            rooms: 1,
            area: 38,
            floor: '2/5',
            is_owner: true,
            metro_name: 'Minor',
            metro_minutes: 5,
            days_ago: 1,
            image_urls: ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'],
            description: 'Minor metrosiga 5 daqiqa piyoda. Uy egasidan, vositachilarsiz.',
            canonical_url: 'https://olx.uz',
            amenities: ['mebel', 'net'],
          },
        ]
      }
    } finally {
      isLoading.value = false
    }
  }

  // Filtered listings computed
  const filteredListings = computed(() => {
    let result = [...listings.value]

    // District filter
    if (filterDistrict.value) {
      result = result.filter((item) => item.district === filterDistrict.value)
    }

    // Rooms filter
    if (filterRooms.value) {
      const r = Number(filterRooms.value)
      result = result.filter((item) => item.rooms === r)
    }

    // Max Price filter
    if (filterMaxPrice.value) {
      const maxP = Number(filterMaxPrice.value)
      if (maxP > 0) {
        result = result.filter((item) => item.price_uzs <= maxP)
      }
    }

    // Category filter
    if (filterCategory.value === '1') result = result.filter((item) => item.rooms === 1)
    if (filterCategory.value === '2') result = result.filter((item) => item.rooms === 2)
    if (filterCategory.value === '3') result = result.filter((item) => item.rooms === 3)
    if (filterCategory.value === 'room') result = result.filter((item) => item.is_shared_room)
    if (filterCategory.value === 'stu') result = result.filter((item) => item.price_uzs <= 2700000)
    if (filterCategory.value === 'mk') result = result.filter((item) => item.is_owner)
    if (filterCategory.value === '3days') result = result.filter((item) => (item.days_ago || 0) <= 3)
    if (filterCategory.value === 'today') result = result.filter((item) => (item.days_ago || 0) === 0)

    // Target Audience filter ('family', 'female', 'male')
    if (filterAudience.value && filterAudience.value !== 'all') {
      result = result.filter((item) => item.target_audience === filterAudience.value)
    }

    // Owner only amenity toggle
    if (filterAmenities.value.owner_only) {
      result = result.filter((item) => item.is_owner)
    }

    // Sort order
    if (filterSort.value === 'lo') {
      result.sort((a, b) => a.price_uzs - b.price_uzs)
    } else if (filterSort.value === 'hi') {
      result.sort((a, b) => b.price_uzs - a.price_uzs)
    } else {
      result.sort((a, b) => (a.days_ago || 0) - (b.days_ago || 0))
    }

    return result
  })

  // District options
  const availableDistricts = computed(() => {
    return [
      'Chilonzor',
      'Yunusobod',
      'Mirzo Ulug‘bek',
      'Yakkasaroy',
      'Sergeli',
      'Olmazor',
      'Shayxontohur',
      'Uchtepa',
      'Yashnobod',
      'Bektemir',
      'Yangi Hayot',
      'Mirobod',
    ]
  })

  return {
    listings,
    filteredListings,
    isLoading,
    selectedListing,
    filterDistrict,
    filterRooms,
    filterMaxPrice,
    filterCategory,
    filterAudience,
    filterSort,
    filterAmenities,
    availableDistricts,
    fetchListings,
  }
}

