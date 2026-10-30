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

  // Intelligent Ecosystem Fields
  coordinates_lat?: number
  coordinates_lon?: number
  metro_station?: string
  metro_distance_m?: number
  fair_price_category?: string // 'BELOW_MARKET' | 'FAIR_PRICE' | 'ABOVE_MARKET'
  estimated_market_price?: number
  price_diff_percent?: number
  scam_risk_score?: number
  scam_risk_level?: string // 'LOW' | 'MEDIUM' | 'HIGH'
  scam_risk_reasons?: string[]
  is_furnished?: boolean
  renovation_type?: string
  match_percentage?: number
  match_pros?: string[]
  match_cons?: string[]
}

export function useListings() {
  const listings = useState<ListingItem[]>('listings', () => [])
  const isLoading = useState<boolean>('listings_loading', () => false)
  const selectedListing = useState<ListingItem | null>('selected_listing', () => null)

  // AI Match Search state
  const aiSearchQuery = useState<string>('ai_search_query', () => '')
  const isAiSearching = useState<boolean>('is_ai_searching', () => false)
  const aiSearchActive = useState<boolean>('ai_search_active', () => false)
  const aiParsedCriteria = useState<any>('ai_parsed_criteria', () => null)

  // Comparison state
  const compareList = useState<ListingItem[]>('compare_list', () => [])

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
            metro_name: item.metro_station || item.district || 'Metro',
            metro_minutes: Math.max(3, Math.round((item.metro_distance_m || 500) / 75)),
            days_ago: daysAgo,
            is_shared_room: item.rooms === 0,
            amenities: ['mebel', 'kond', 'kir', 'net'],
            disclaimer: item.disclaimer || 'Egasidan ekanligi mustaqil tasdiqlanmagan.',
            source_attribution: item.source_attribution || 'Tashqi manba (OLX Uzbekistan)',

            // Ecosystem properties
            coordinates_lat: item.coordinates_lat,
            coordinates_lon: item.coordinates_lon,
            metro_station: item.metro_station,
            metro_distance_m: item.metro_distance_m,
            fair_price_category: item.fair_price_category,
            estimated_market_price: item.estimated_market_price,
            price_diff_percent: item.price_diff_percent,
            scam_risk_score: item.scam_risk_score,
            scam_risk_level: item.scam_risk_level,
            scam_risk_reasons: item.scam_risk_reasons,
            is_furnished: item.is_furnished,
            renovation_type: item.renovation_type,
          }
        })
      }
    } catch (err) {
      console.warn('API fetch fallback, loading default listings:', err)
    } finally {
      isLoading.value = false
    }
  }

  // AI Match Natural Language Query Execution
  const runAiMatch = async (query: string) => {
    if (!query || !query.trim()) {
      aiSearchActive.value = false
      aiParsedCriteria.value = null
      await fetchListings()
      return
    }

    isAiSearching.value = true
    aiSearchActive.value = true
    aiSearchQuery.value = query

    try {
      const config = useRuntimeConfig()
      const base = config.public.apiBase || ''
      const res: any = await $fetch(`${base}/api/ai/match`, {
        method: 'POST',
        body: { query: query.trim(), limit: 40 },
      })

      if (res && res.matches) {
        aiParsedCriteria.value = res.parsed_criteria
        listings.value = res.matches.map((m: any) => {
          const item = m.listing
          const isOwner =
            item.classification?.label === 'LIKELY_OWNER' ||
            item.title.toLowerCase().includes('maklersiz') ||
            item.title.toLowerCase().includes('egasidan')

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
            metro_name: item.metro_station || item.district || 'Metro',
            metro_minutes: Math.max(3, Math.round((item.metro_distance_m || 500) / 75)),
            days_ago: 0,
            is_shared_room: item.rooms === 0,
            amenities: ['mebel', 'kond', 'kir', 'net'],
            disclaimer: item.disclaimer || 'Egasidan ekanligi mustaqil tasdiqlanmagan.',
            source_attribution: item.source_attribution || 'Tashqi manba (OLX Uzbekistan)',

            coordinates_lat: item.coordinates_lat,
            coordinates_lon: item.coordinates_lon,
            metro_station: item.metro_station,
            metro_distance_m: item.metro_distance_m,
            fair_price_category: item.fair_price_category,
            estimated_market_price: item.estimated_market_price,
            price_diff_percent: item.price_diff_percent,
            scam_risk_score: item.scam_risk_score,
            scam_risk_level: item.scam_risk_level,
            scam_risk_reasons: item.scam_risk_reasons,
            is_furnished: item.is_furnished,
            renovation_type: item.renovation_type,

            // AI Match specifics
            match_percentage: m.match_percentage,
            match_pros: m.pros || [],
            match_cons: m.cons || [],
          }
        })
      }
    } catch (e) {
      console.error('AI match failed, falling back:', e)
    } finally {
      isAiSearching.value = false
    }
  }

  const resetAiMatch = async () => {
    aiSearchActive.value = false
    aiSearchQuery.value = ''
    aiParsedCriteria.value = null
    await fetchListings()
  }

  // Comparison methods
  const toggleCompare = (item: ListingItem) => {
    const idx = compareList.value.findIndex((x) => x.id === item.id)
    if (idx >= 0) {
      compareList.value.splice(idx, 1)
    } else {
      if (compareList.value.length >= 4) {
        compareList.value.shift()
      }
      compareList.value.push(item)
    }
  }

  const isInCompare = (id: number) => {
    return compareList.value.some((x) => x.id === id)
  }

  const clearCompare = () => {
    compareList.value = []
  }

  // Filtered listings logic
  const filteredListings = computed(() => {
    let result = [...listings.value]

    // If AI Match is active, keep match score ordering
    if (aiSearchActive.value) {
      return result
    }

    // District filter
    if (filterDistrict.value) {
      result = result.filter((item) => item.district === filterDistrict.value)
    }

    // Rooms filter
    if (filterRooms.value) {
      const r = Number(filterRooms.value)
      if (r === 4) {
        result = result.filter((item) => item.rooms >= 4)
      } else {
        result = result.filter((item) => item.rooms === r)
      }
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
    if (filterCategory.value === 'fair_cheap') result = result.filter((item) => item.fair_price_category === 'BELOW_MARKET')

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

    // AI Match & Comparison
    aiSearchQuery,
    isAiSearching,
    aiSearchActive,
    aiParsedCriteria,
    runAiMatch,
    resetAiMatch,
    compareList,
    toggleCompare,
    isInCompare,
    clearCompare,
  }
}
