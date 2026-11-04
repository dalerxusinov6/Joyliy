import { ref, computed } from 'vue'
import { useNeighborhoods } from '~/composables/useNeighborhoods'

const cleanText = (v: any): string =>
  String(v || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|li)>/gi, '\n')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\n{3,}/g, '\n\n')
    .trim()

const SHARED_RE = /sherik|подсел|подсл|койк|koika|sheriklik|комнату для|xona beriladi/i

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
  published_at?: string
  near_metro?: boolean
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
  deal_type?: 'rent' | 'sale'
  property_type?: string
  match_percentage?: number
  match_pros?: string[]
  match_cons?: string[]
}

export function useListings() {
  const { byName: nbByName } = useNeighborhoods()

  const listings = useState<ListingItem[]>('listings', () => [])
  const isLoading = useState<boolean>('listings_loading', () => false)
  const isLoadingMore = useState<boolean>('listings_loading_more', () => false)
  const selectedListing = useState<ListingItem | null>('selected_listing', () => null)

  // Server-side Pagination & Unlimited Discovery State
  const currentPage = useState<number>('listings_page', () => 1)
  const pageSize = useState<number>('listings_page_size', () => 24)
  const totalCount = useState<number>('listings_total_count', () => 0)
  const totalPages = useState<number>('listings_total_pages', () => 1)
  const hasNextPage = useState<boolean>('listings_has_next', () => false)
  const hasPrevPage = useState<boolean>('listings_has_prev', () => false)

  // AI Match Search state
  const aiSearchQuery = useState<string>('ai_search_query', () => '')
  const isAiSearching = useState<boolean>('is_ai_searching', () => false)
  const aiSearchActive = useState<boolean>('ai_search_active', () => false)
  const aiParsedCriteria = useState<any>('ai_parsed_criteria', () => null)

  // Comparison state
  const compareList = useState<ListingItem[]>('compare_list', () => [])

  // Filters state
  const filterDealType = useState<'rent' | 'sale'>('filter_deal_type', () => 'rent')
  const filterPropertyType = useState<string>('filter_property_type', () => '')
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

  const detectAmenities = (item: any): string[] => {
    const txt = `${item.title || ''} ${item.description || ''}`.toLowerCase()
    const out: string[] = []
    if (/мебел|mebel|jihoz/.test(txt) || item.is_furnished === true && /мебел|mebel|jihoz/.test(txt)) out.push('mebel')
    if (/кондиц|konditsioner|kondisioner/.test(txt)) out.push('kond')
    if (/стиральн|kir yuvish|стирал/.test(txt)) out.push('kir')
    if (/wi-?fi|интернет|internet/.test(txt)) out.push('net')
    return out
  }

  const mapRawItem = (item: any, idx: number): ListingItem => {
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
      description: cleanText(item.description),
      contact_phone: item.contact_phone || undefined,
      contact_telegram: item.contact_telegram || undefined,
      target_audience: item.target_audience || 'any',
      image_urls: item.image_urls || [],
      is_owner: isOwner,
      confidence_score: item.classification?.confidence_score || 0.85,
      metro_name: item.metro_station || item.district || 'Metro',
      metro_minutes: Math.max(3, Math.round((item.metro_distance_m || 500) / 75)),
      days_ago: daysAgo,
      published_at: targetDateStr || undefined,
      is_shared_room: item.rooms === 0 || SHARED_RE.test(`${item.title || ''} ${item.description || ''}`),
      near_metro: /metro|метро/i.test(`${item.title || ''} ${item.description || ''}`),
      amenities: detectAmenities(item),
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
      deal_type: item.deal_type || (item.canonical_url?.includes('prodazha') || item.title?.toLowerCase().includes('sotiladi') || item.title?.toLowerCase().includes('сотилади') || item.title?.toLowerCase().includes('продается') ? 'sale' : 'rent'),
      property_type: item.property_type,
    }
  }

  const marketDiff = (l: ListingItem): number | null => {
    if (l.price_diff_percent) return Math.round(l.price_diff_percent)
    if ((l.deal_type || 'rent') !== 'rent' || l.is_shared_room) return null
    const nb: any = nbByName(l.district)
    if (!nb) return null
    const k = Math.max(1, Math.min(l.rooms || 2, 3))
    const bench = nb[`avg_rent_${k}room_uzs`]
    if (!bench) return null
    return Math.round(((l.price_uzs - bench) / bench) * 100)
  }
  const isNewListing = (l: ListingItem) => !!l.published_at && Date.now() - new Date(l.published_at).getTime() < 3 * 864e5

  const fetchListings = async () => {
    isLoading.value = true

    try {
      const config = useRuntimeConfig()
      const base = config.public.apiBase || ''

      // Fetch all listings across entire database so client-side filters have all apartments
      const url = `${base}/api/listings?limit=2000`
      const data: any = await $fetch(url)

      if (data && data.items) {
        const mapped = data.items.map((item: any, idx: number) => mapRawItem(item, idx))
        listings.value = mapped
        totalCount.value = data.total ?? mapped.length
        totalPages.value = 1
        currentPage.value = 1
        hasNextPage.value = false
        hasPrevPage.value = false
      }
    } catch (err) {
      console.warn('API fetch fallback, loading default listings:', err)
    } finally {
      isLoading.value = false
      isLoadingMore.value = false
    }
  }

  const loadMoreListings = async () => {}
  const goToPage = async (_page: number) => {}

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

      const rawMatches = res?.matches || res?.results || []
      if (res && rawMatches.length > 0) {
        aiParsedCriteria.value = res.parsed_criteria || res.parsed_filters
        listings.value = rawMatches.map((m: any) => {
          const item = m.listing || m
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
            description: cleanText(item.description),
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
            amenities: detectAmenities(item),
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
            match_percentage: m.match_percentage ?? m.match_score ?? 85,
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

    // Deal Type Filter ('rent' | 'sale')
    if (filterDealType.value) {
      result = result.filter((item) => (item.deal_type || 'rent') === filterDealType.value)
    }

    // Property Type Filter (e.g. 'new_building', 'secondary', 'house')
    if (filterPropertyType.value) {
      result = result.filter((item) => {
        const pt = (item.property_type || '').toLowerCase()
        const t = (item.title || '').toLowerCase()
        if (filterPropertyType.value === 'new_building') {
          return pt === 'new_building' || t.includes('новостройк') || t.includes('yangi bino') || t.includes('novostroyka')
        }
        if (filterPropertyType.value === 'house') {
          return pt === 'house' || t.includes('dom') || t.includes('hovli') || t.includes('ҳовли') || t.includes('dacha') || t.includes('дача')
        }
        if (filterPropertyType.value === 'secondary') {
          return pt === 'secondary' || (!t.includes('новостройк') && !t.includes('hovli') && !t.includes('ҳовли'))
        }
        return true
      })
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
    if (filterCategory.value === 'metro') result = result.filter((item) => !!item.near_metro)
    if (filterCategory.value === '3days') result = result.filter((item) => isNewListing(item))
    if (filterCategory.value === 'today') result = result.filter((item) => (item.days_ago || 0) === 0)
    if (filterCategory.value === 'fair_cheap') result = result.filter((item) => { const d = marketDiff(item); return d !== null && d <= -10 })

    // Target Audience filter ('family', 'female', 'male') - applies for rent only
    if (filterDealType.value === 'rent' && filterAudience.value && filterAudience.value !== 'all') {
      result = result.filter((item) => item.target_audience === filterAudience.value)
    }

    for (const key of ['mebel', 'kond', 'kir', 'net'] as const) {
      if (filterAmenities.value[key]) result = result.filter((item) => (item.amenities || []).includes(key))
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
    filterDealType,
    filterPropertyType,
    filterSort,
    filterAmenities,
    availableDistricts,
    fetchListings,
    mapRawItem,
    marketDiff,
    isNewListing,

    // Server Pagination & Unlimited Discovery
    currentPage,
    pageSize,
    totalCount,
    totalPages,
    hasNextPage,
    hasPrevPage,
    isLoadingMore,
    loadMoreListings,
    goToPage,

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
