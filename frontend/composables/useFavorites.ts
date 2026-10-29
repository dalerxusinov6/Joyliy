import { ref, computed } from 'vue'

export function useFavorites() {
  const favorites = useState<number[]>('favorites', () => [])

  const initFavorites = () => {
    if (import.meta.client) {
      try {
        const stored = localStorage.getItem('joyliy_favs')
        if (stored) {
          favorites.value = JSON.parse(stored)
        }
      } catch (e) {
        console.error('Failed to load favorites', e)
      }
    }
  }

  const toggleFavorite = (id: number): boolean => {
    const idx = favorites.value.indexOf(id)
    let isAdded = false
    if (idx > -1) {
      favorites.value.splice(idx, 1)
      isAdded = false
    } else {
      favorites.value.push(id)
      isAdded = true
    }
    if (import.meta.client) {
      localStorage.setItem('joyliy_favs', JSON.stringify(favorites.value))
    }
    return isAdded
  }

  const isFavorite = (id: number): boolean => {
    return favorites.value.includes(id)
  }

  const count = computed(() => favorites.value.length)

  return {
    favorites,
    initFavorites,
    toggleFavorite,
    isFavorite,
    count,
  }
}

