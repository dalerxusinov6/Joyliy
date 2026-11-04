export interface Neighborhood {
  id: string
  name_uz: string
  name_ru?: string
  center_lat: number
  center_lon: number
  overall_score: number
  scores: Record<string, number>
  description_uz: string
  highlights_uz: string[]
  price_tier: string
  avg_rent_1room_uzs: number
  avg_rent_2room_uzs: number
  avg_rent_3room_uzs: number
}

export function useNeighborhoods() {
  const items = useState<Neighborhood[]>('neighborhoods', () => [])
  const loaded = useState<boolean>('neighborhoods_loaded', () => false)

  const load = async () => {
    if (loaded.value) return
    try {
      const base = (useRuntimeConfig().public.apiBase as string) || ''
      const res: any = await $fetch(`${base}/api/neighborhoods`)
      items.value = res?.districts || []
      loaded.value = true
    } catch (e) {
      console.warn('neighborhoods fetch failed', e)
    }
  }

  const byName = (name: string): Neighborhood | undefined => {
    const n = name === 'Yangi Hayot' ? 'Yangihayot' : name
    return items.value.find((d) => d.id === n || d.name_uz === n)
  }

  return { items, load, byName }
}
