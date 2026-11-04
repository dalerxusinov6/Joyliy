import { useI18n } from '~/composables/useI18n'

export interface ChatListing {
  id: number
  title: string
  price_uzs: number
  district: string
  rooms: number
  area?: number
  image?: string
  match?: number
}

export interface ChatMessage {
  id: string
  sender: 'user' | 'ai'
  text: string
  legal_references?: string[]
  practical_tips?: string[]
  listings?: ChatListing[]
  more_query?: string
}

const LEGAL_RE = /shartnoma|договор|soliq|налог|zalog|залог|depozit|deposit|kommunal|коммунал|firib|мошен|aldov|makler|комисс|риелтор|savol|вопрос|contract|tax/i
const SEARCH_RE = /xona|комн|mln|млн|million|kvartira|квартир|ijara|аренд|снять|sotib|купить|qidir|ищу|kerak|нужн|chilonzor|yunusobod|mirobod|yakkasaroy|чиланзар|юнусабад|мирабад|яккасарай/i

export function useAssistant() {
  const { t, currentLang } = useI18n()
  const messages = useState<ChatMessage[]>('assistant_messages', () => [])
  const isLoading = useState<boolean>('assistant_loading', () => false)
  const prefill = useState<string>('assistant_prefill', () => '')

  const quick = computed(() => [t('q_tax'), t('q_deposit'), t('q_utilities'), t('q_fraud')])

  const init = () => {
    if (messages.value.length) return
    messages.value = [
      { id: 'welcome', sender: 'ai', text: t('assistant_welcome'), practical_tips: [t('tip_1'), t('tip_2')] },
    ]
  }

  const base = () => (useRuntimeConfig().public.apiBase as string) || ''

  const searchListings = async (query: string): Promise<ChatMessage | null> => {
    const res: any = await $fetch(`${base()}/api/ai/match`, { method: 'POST', body: { query, limit: 6 } })
    const raw = res?.matches || res?.results || []
    if (!raw.length) {
      return { id: `a${Date.now()}`, sender: 'ai', text: 'Afsuski, mos e’lon topilmadi. Byudjet yoki tumanni o‘zgartirib ko‘ring.' }
    }
    const items: ChatListing[] = raw.slice(0, 3).map((m: any) => {
      const l = m.listing || m
      return {
        id: l.id,
        title: l.title,
        price_uzs: l.price_uzs,
        district: l.district,
        rooms: l.rooms,
        area: l.area,
        image: (l.image_urls || [])[0],
        match: m.match_percentage ?? m.match_score,
      }
    })
    return {
      id: `a${Date.now()}`,
      sender: 'ai',
      text: `${raw.length} ta mos e’lon topdim. Eng mos variantlar:`,
      listings: items,
      more_query: raw.length > 3 ? query : undefined,
    }
  }

  const send = async (text: string, listingId?: number) => {
    const q = text.trim()
    if (!q || isLoading.value) return
    init()
    messages.value.push({ id: `u${Date.now()}`, sender: 'user', text: q })
    isLoading.value = true
    try {
      if (!listingId && SEARCH_RE.test(q) && !LEGAL_RE.test(q)) {
        const found = await searchListings(q)
        if (found) { messages.value.push(found); return }
      }
      const res: any = await $fetch(`${base()}/api/assistant/chat`, {
        method: 'POST',
        body: { message: q, listing_id: listingId ?? null, language: currentLang.value },
      })
      messages.value.push({
        id: `a${Date.now()}`,
        sender: 'ai',
        text: res.reply || res.response || 'Savolingiz qabul qilindi.',
        legal_references: res.legal_references || [],
        practical_tips: res.practical_tips || [],
      })
    } catch (err) {
      messages.value.push({
        id: `a${Date.now()}`,
        sender: 'ai',
        text: 'O‘zbekiston FK 535-moddasiga ko‘ra, ijara shartnomasi yozma tuzilishi va ijara.soliq.uz tizimida hisobga qo‘yilishi shart. Zalog depoziti mol-mulk shikastlanmagan taqdirda to‘liq qaytariladi.',
        practical_tips: ['Mulkdorning pasporti va kadastr hujjatini shaxsan tekshiring.'],
      })
    } finally {
      isLoading.value = false
    }
  }

  return { messages, isLoading, prefill, quick, init, send }
}
