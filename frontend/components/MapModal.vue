<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useListings, type ListingItem } from '~/composables/useListings'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'select'])
const { t } = useI18n()
const { listings, filterAudience } = useListings()

const mapContainer = ref<HTMLElement | null>(null)
const isLoadingMap = ref(true)
const mapError = ref<string | null>(null)
const selectedItem = ref<ListingItem | null>(null)
const selectedDistrict = ref<string>('')
const ownerOnly = ref(false)

let ymapsInstance: any = null
let mapObject: any = null
let clustererObject: any = null

// Accurate geographical coordinates for all Tashkent districts
const DISTRICT_COORDS: Record<string, [number, number]> = {
  Chilonzor: [41.2721, 69.2045],
  Yunusobod: [41.3644, 69.2882],
  'Mirzo Ulug‘bek': [41.3283, 69.3346],
  Yakkasaroy: [41.2825, 69.2514],
  Mirobod: [41.2917, 69.2789],
  Shayxontohur: [41.3211, 69.2389],
  Olmazor: [41.3496, 69.2215],
  Uchtepa: [41.2934, 69.1762],
  Sergeli: [41.2228, 69.2201],
  Yashnobod: [41.2942, 69.3289],
  Bektemir: [41.2115, 69.3368],
  'Yangi Hayot': [41.1965, 69.1895],
}

const formatMillion = (price: number) => {
  if (!price) return '0'
  return (price / 1_000_000).toFixed(1) + 'M'
}

const formatPriceFull = (price: number) => {
  return (price || 0).toLocaleString('ru-RU').replace(/\u00a0/g, ' ') + ' so‘m'
}

// Calculate deterministic, natural GPS coordinates within the district
const getListingCoordinates = (item: ListingItem): [number, number] => {
  const base = DISTRICT_COORDS[item.district] || [41.311081, 69.240562]
  const seed = Number(item.id) || 1
  // Spread listings along surrounding streets
  const latOffset = (((seed * 17) % 31) - 15) * 0.0013
  const lonOffset = (((seed * 23) % 31) - 15) * 0.0017
  return [base[0] + latOffset, base[1] + lonOffset]
}

// Dynamically load Yandex Maps API v2.1
const loadYandexMapsSdk = (): Promise<any> => {
  if (typeof window === 'undefined') return Promise.reject(new Error('SSR not supported'))
  if ((window as any).ymaps && (window as any).ymaps.Map) {
    return (window as any).ymaps.ready()
  }

  const config = useRuntimeConfig()
  const apiKey = (config.public as any).yandexMapsApiKey || ''
  const scriptUrl = apiKey
    ? `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=uz_UZ`
    : 'https://api-maps.yandex.ru/2.1/?lang=uz_UZ'

  return new Promise((resolve, reject) => {
    const existing = document.getElementById('yandex-maps-sdk')
    if (existing) {
      if ((window as any).ymaps) {
        (window as any).ymaps.ready(resolve)
      } else {
        existing.addEventListener('load', () => (window as any).ymaps.ready(resolve))
        existing.addEventListener('error', reject)
      }
      return
    }

    const script = document.createElement('script')
    script.id = 'yandex-maps-sdk'
    script.src = scriptUrl
    script.type = 'text/javascript'
    script.async = true
    script.onload = () => {
      if ((window as any).ymaps) {
        (window as any).ymaps.ready(resolve)
      } else {
        reject(new Error('Ymaps not defined on load'))
      }
    }
    script.onerror = (e) => reject(e)
    document.head.appendChild(script)
  })
}

const initMap = async () => {
  isLoadingMap.value = true
  mapError.value = null
  selectedItem.value = null

  try {
    await loadYandexMapsSdk()
    ymapsInstance = (window as any).ymaps

    await nextTick()
    const container = document.getElementById('yandex-map-container')
    if (!container) return

    if (mapObject) {
      mapObject.destroy()
      mapObject = null
    }

    // Initialize Tashkent Map
    mapObject = new ymapsInstance.Map(
      'yandex-map-container',
      {
        center: [41.311081, 69.240562], // Amir Temur Square / Center of Tashkent
        zoom: 12,
        controls: ['zoomControl', 'fullscreenControl', 'geolocationControl', 'typeSelector'],
      },
      {
        searchControlProvider: 'yandex#search',
        suppressMapOpenBlock: true,
      }
    )

    renderPlacemarks()
    isLoadingMap.value = false
  } catch (err: any) {
    console.error('Yandex Maps initialization failed:', err)
    mapError.value = 'Xaritani yuklashda xatolik yuz berdi. Internet aloqasini tekshiring.'
    isLoadingMap.value = false
  }
}

const renderPlacemarks = () => {
  if (!mapObject || !ymapsInstance) return

  if (clustererObject) {
    mapObject.geoObjects.remove(clustererObject)
  }

  // Create clusterer for neat grouping when zoomed out
  clustererObject = new ymapsInstance.Clusterer({
    preset: 'islands#invertedDarkGreenClusterIcons',
    groupByCoordinates: false,
    clusterDisableClickZoom: false,
    clusterHideIconOnBalloonOpen: false,
    geoObjectHideIconOnBalloonOpen: false,
  })

  let filtered = [...listings.value]
  if (selectedDistrict.value) {
    filtered = filtered.filter((x) => x.district === selectedDistrict.value)
  }
  if (ownerOnly.value) {
    filtered = filtered.filter((x) => x.is_owner)
  }
  if (filterAudience.value && filterAudience.value !== 'all') {
    filtered = filtered.filter((x) => x.target_audience === filterAudience.value)
  }

  const placemarks: any[] = []

  filtered.forEach((item) => {
    const coords = getListingCoordinates(item)
    const isOwner = item.is_owner
    const priceText = formatMillion(item.price_uzs)

    const placemark = new ymapsInstance.Placemark(
      coords,
      {
        iconCaption: priceText,
        hintContent: `${item.title} — ${formatPriceFull(item.price_uzs)}`,
        balloonContentHeader: `<div style="font-size:15px;font-weight:700;color:#059669;">${formatPriceFull(item.price_uzs)}</div>`,
        balloonContentBody: `
          <div style="font-family:Inter,sans-serif;max-width:260px;">
            <div style="font-weight:600;font-size:13px;line-height:1.3;margin-bottom:6px;">${item.title}</div>
            <div style="font-size:12px;color:#64748b;margin-bottom:8px;">
              ${item.rooms} xona · ${item.area} m² · ${item.district}
            </div>
            ${item.image_urls && item.image_urls.length ? `<img src="${item.image_urls[0]}" style="width:100%;height:130px;object-fit:cover;border-radius:6px;margin-bottom:8px;" />` : ''}
          </div>
        `,
        balloonContentFooter: `
          <div style="text-align:right;">
            <button id="balloon-view-btn-${item.id}" style="background:#059669;color:#fff;border:none;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:12px;">
              Batafsil ko‘rish ➔
            </button>
          </div>
        `,
      },
      {
        preset: isOwner ? 'islands#darkGreenMoneyIcon' : 'islands#blueMoneyIcon',
        openBalloonOnClick: true,
      }
    )

    // Handle pin click: set active selected preview card
    placemark.events.add('click', () => {
      selectedItem.value = item
    })

    // Handle balloon open to hook up details button
    placemark.events.add('balloonopen', () => {
      setTimeout(() => {
        const btn = document.getElementById(`balloon-view-btn-${item.id}`)
        if (btn) {
          btn.onclick = () => {
            emit('select', item)
          }
        }
      }, 50)
    })

    placemarks.push(placemark)
  })

  clustererObject.add(placemarks)
  mapObject.geoObjects.add(clustererObject)
}

const onDistrictClick = (district: string) => {
  if (selectedDistrict.value === district) {
    selectedDistrict.value = ''
    if (mapObject) {
      mapObject.setCenter([41.311081, 69.240562], 12, { duration: 400 })
    }
  } else {
    selectedDistrict.value = district
    const coords = DISTRICT_COORDS[district]
    if (coords && mapObject) {
      mapObject.setCenter(coords, 14, { duration: 400 })
    }
  }
  renderPlacemarks()
}

const toggleOwnerOnly = () => {
  ownerOnly.value = !ownerOnly.value
  renderPlacemarks()
}

watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      setTimeout(() => {
        initMap()
      }, 50)
    } else {
      if (mapObject) {
        mapObject.destroy()
        mapObject = null
      }
    }
  }
)

watch(
  () => listings.value,
  () => {
    if (mapObject) {
      renderPlacemarks()
    }
  }
)

watch(filterAudience, () => {
  if (mapObject) {
    renderPlacemarks()
  }
})

onBeforeUnmount(() => {
  if (mapObject) {
    mapObject.destroy()
    mapObject = null
  }
})
</script>

<template>
  <div v-if="show" class="ov show" @click.self="$emit('close')">
    <div class="sheet yandex-map-sheet">
      <!-- Modal Top Bar -->
      <div class="top">
        <div style="display: flex; align-items: center; gap: 8px">
          <!-- Yandex Maps Branded Icon -->
          <svg style="width: 22px; height: 22px" viewBox="0 0 24 24">
            <path
              d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"
              fill="#e11d48"
            />
          </svg>
          <span style="font-weight: 700; font-size: 17px">Toshkent Ijaralari — Yandex Xarita</span>
          <span class="count-pill">{{ listings.length }} ta e’lon</span>
        </div>

        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- District Filter Bar -->
      <div class="map-filter-bar">
        <button
          class="district-pill"
          :class="{ on: !selectedDistrict }"
          @click="onDistrictClick('')"
        >
          Barcha tumanlar
        </button>

        <button
          v-for="(coords, dName) in DISTRICT_COORDS"
          :key="dName"
          class="district-pill"
          :class="{ on: selectedDistrict === dName }"
          @click="onDistrictClick(dName)"
        >
          {{ dName }}
        </button>

        <button
          class="owner-toggle-pill"
          :class="{ active: ownerOnly }"
          @click="toggleOwnerOnly"
        >
          <svg class="i" style="width: 14px; height: 14px" viewBox="0 0 24 24">
            <path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z" />
          </svg>
          Maklersiz
        </button>
      </div>

      <!-- Map Body -->
      <div class="map-body-wrapper">
        <!-- Loading Spinner -->
        <div v-if="isLoadingMap" class="map-loader">
          <div class="spinner"></div>
          <p style="margin-top: 12px; font-weight: 600; font-size: 14px">
            Yandex Xarita yuklanmoqda...
          </p>
        </div>

        <!-- Error State -->
        <div v-if="mapError" class="map-error-state">
          <p style="color: #e11d48; font-weight: 600">{{ mapError }}</p>
          <button class="btn p" @click="initMap" style="margin-top: 10px">
            Qayta yuklash
          </button>
        </div>

        <!-- Actual Yandex Map Container -->
        <div id="yandex-map-container" class="yandex-map-container"></div>

        <!-- Floating Selected Apartment Card -->
        <transition name="slide-up">
          <div v-if="selectedItem" class="selected-apartment-card">
            <div class="card-thumb">
              <img
                v-if="selectedItem.image_urls && selectedItem.image_urls.length"
                :src="selectedItem.image_urls[0]"
                :alt="selectedItem.title"
              />
              <div v-else class="thumb-placeholder">Uy</div>
            </div>

            <div class="card-info">
              <div class="card-price">
                {{ formatPriceFull(selectedItem.price_uzs) }}
                <span v-if="selectedItem.is_owner" class="badge-maklersiz">Maklersiz</span>
              </div>
              <div class="card-title">{{ selectedItem.title }}</div>
              <div class="card-meta">
                {{ selectedItem.rooms }} xona · {{ selectedItem.area }} m² · {{ selectedItem.district }}
              </div>
            </div>

            <div class="card-actions">
              <button class="btn p action-btn" @click="$emit('select', selectedItem)">
                Batafsil
              </button>
              <button class="ib close-btn" @click="selectedItem = null">
                <svg class="i" viewBox="0 0 24 24">
                  <path d="M18 6 6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.yandex-map-sheet {
  max-width: 980px !important;
  width: 94vw !important;
  height: 88vh !important;
  display: flex !important;
  flex-direction: column !important;
  padding: 0 !important;
  overflow: hidden !important;
  border-radius: 16px !important;
}

.top {
  padding: 14px 20px;
  border-bottom: 1px solid var(--bd, #e2e8f0);
}

.count-pill {
  font-size: 12px;
  background: var(--bg-soft, #f1f5f9);
  color: var(--mu, #64748b);
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.map-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--bg, #fff);
  overflow-x: auto;
  white-space: nowrap;
  border-bottom: 1px solid var(--bd, #e2e8f0);
  scrollbar-width: thin;
}

.district-pill {
  background: var(--bg-soft, #f8fafc);
  border: 1px solid var(--bd, #e2e8f0);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--fg, #1e293b);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.district-pill:hover {
  background: var(--bd, #e2e8f0);
}

.district-pill.on {
  background: var(--ac, #174D3A);
  color: #fff;
  border-color: var(--ac, #174D3A);
}

.owner-toggle-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  background: var(--mint-subtle, #e8f8f0);
  border: 1px solid var(--mint, #b9f2d0);
  color: var(--ac, #174D3A);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
}

.owner-toggle-pill.active {
  background: var(--ac, #174D3A);
  color: #fff;
  border-color: var(--ac, #174D3A);
}

.map-body-wrapper {
  position: relative;
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.yandex-map-container {
  width: 100%;
  height: 100%;
  background: #e5e3df;
}

.map-loader,
.map-error-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 10;
}

.spinner {
  width: 38px;
  height: 38px;
  border: 3px solid #e2e8f0;
  border-top-color: #059669;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Floating Selected Apartment Card */
.selected-apartment-card {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  max-width: 500px;
  margin: 0 auto;
  background: var(--bg, #fff);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 20;
  border: 1px solid var(--bd, #e2e8f0);
}

[data-theme='dark'] .selected-apartment-card {
  background: #1e293b;
  border-color: #334155;
}

.card-thumb {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #64748b;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-price {
  font-size: 15px;
  font-weight: 700;
  color: var(--ac, #174D3A);
  display: flex;
  align-items: center;
  gap: 6px;
}

.badge-maklersiz {
  font-size: 10px;
  background: var(--mint, #b9f2d0);
  color: var(--ac-dark, #103b2e);
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 2px 0;
}

.card-meta {
  font-size: 12px;
  color: var(--mu, #64748b);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn {
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
}

.close-btn {
  padding: 6px;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>
