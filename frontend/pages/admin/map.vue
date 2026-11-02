<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Xarita Ko‘rinishi — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const mapContainer = ref<HTMLElement | null>(null)
const isLoading = ref(true)
const listings = ref<any[]>([])
const selectedItem = ref<any | null>(null)
const selectedDistrict = ref('')
const selectedDealType = ref('')

let ymapsInstance: any = null
let mapObject: any = null
let clustererObject: any = null

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
  Yangihayot: [41.1965, 69.1895],
}

const getCoordinates = (item: any): [number, number] => {
  if (item.latitude && item.longitude) {
    return [item.latitude, item.longitude]
  }
  const base = DISTRICT_COORDS[item.district] || [41.311081, 69.240562]
  const seed = Number(item.id) || 1
  const latOffset = (((seed * 17) % 31) - 15) * 0.0013
  const lonOffset = (((seed * 23) % 31) - 15) * 0.0017
  return [base[0] + latOffset, base[1] + lonOffset]
}

const loadYandexMaps = (): Promise<any> => {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') return reject('No window')
    if ((window as any).ymaps) {
      ;(window as any).ymaps.ready(() => resolve((window as any).ymaps))
      return
    }

    const script = document.createElement('script')
    script.src = 'https://api-maps.yandex.ru/2.1/?lang=uz_UZ&apikey='
    script.type = 'text/javascript'
    script.onload = () => {
      ;(window as any).ymaps.ready(() => resolve((window as any).ymaps))
    }
    script.onerror = () => reject('Yandex Maps API yuklanmadi')
    document.head.appendChild(script)
  })
}

const initMap = async () => {
  if (!mapContainer.value) return
  try {
    ymapsInstance = await loadYandexMaps()
    mapObject = new ymapsInstance.Map(mapContainer.value, {
      center: [41.311081, 69.240562],
      zoom: 12,
      controls: ['zoomControl', 'fullscreenControl'],
    })

    clustererObject = new ymapsInstance.Clusterer({
      preset: 'islands#invertedBlueClusterIcons',
      groupByCoordinates: false,
      clusterDisableClickZoom: false,
      clusterHideIconOnBalloonOpen: false,
    })

    mapObject.geoObjects.add(clustererObject)
    renderPlacemarks()
  } catch (err) {
    console.error('Yandex Map init error:', err)
  }
}

const renderPlacemarks = () => {
  if (!clustererObject || !ymapsInstance) return
  clustererObject.removeAll()

  const placemarks: any[] = []

  let filtered = listings.value
  if (selectedDistrict.value) {
    filtered = filtered.filter((i) => i.district === selectedDistrict.value)
  }
  if (selectedDealType.value) {
    filtered = filtered.filter((i) => i.deal_type === selectedDealType.value)
  }

  for (const item of filtered) {
    const coords = getCoordinates(item)
    const sym = item.currency === 'USD' ? '$' : 'so‘m'
    const priceText = `${item.price} ${sym}`

    const pm = new ymapsInstance.Placemark(
      coords,
      {
        iconCaption: priceText,
        balloonContent: item.title,
      },
      {
        preset: item.deal_type === 'sale' ? 'islands#violetDotIconWithCaption' : 'islands#blueDotIconWithCaption',
      }
    )

    pm.events.add('click', () => {
      selectedItem.value = item
    })

    placemarks.push(pm)
  }

  clustererObject.add(placemarks)

  if (selectedDistrict.value && DISTRICT_COORDS[selectedDistrict.value]) {
    mapObject.setCenter(DISTRICT_COORDS[selectedDistrict.value], 14, { duration: 400 })
  }
}

const fetchMapData = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/map/listings')
    if (res && res.success) {
      listings.value = res.items || []
      renderPlacemarks()
    }
  } catch (err) {
    showToast('Xarita ma‘lumotlarini yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

watch([selectedDistrict, selectedDealType], () => {
  renderPlacemarks()
})

onMounted(async () => {
  await fetchMapData()
  await initMap()
})

onBeforeUnmount(() => {
  if (mapObject) {
    mapObject.destroy()
    mapObject = null
  }
})

const formatPrice = (price: number = 0, currency: string = 'USD') => {
  const sym = currency === 'USD' ? '$' : 'so‘m'
  return `${new Intl.NumberFormat('uz-UZ').format(price)} ${sym}`
}
</script>

<template>
  <AdminShell
    title="Xarita ko‘rinishi"
    :breadcrumbs="[
      { label: 'Asosiy' },
      { label: 'Xarita' }
    ]"
  >
    <div class="map-page">
      <!-- Toolbar -->
      <div class="map-toolbar">
        <div>
          <h1 class="page-title">Interaktiv E‘lonlar Xaritasi</h1>
          <p class="page-sub">Geolokatsiya, klasterlar va hududlar bo‘yicha taqsimot</p>
        </div>

        <div class="toolbar-filters">
          <select v-model="selectedDistrict" class="t-select">
            <option value="">Barcha tumanlar</option>
            <option v-for="(coords, dist) in DISTRICT_COORDS" :key="dist" :value="dist">{{ dist }}</option>
          </select>

          <select v-model="selectedDealType" class="t-select">
            <option value="">Barcha bitimlar</option>
            <option value="rent">🔑 Ijara (Rent)</option>
            <option value="sale">🏷️ Sotuv (Sale)</option>
          </select>

          <span class="count-badge">{{ listings.length }} ta e‘lon xaritada</span>
        </div>
      </div>

      <!-- Map & Drawer Layout -->
      <div class="map-layout-box">
        <div ref="mapContainer" class="ymap-container" />

        <!-- Selected Listing Drawer Preview -->
        <div v-if="selectedItem" class="listing-drawer-card">
          <button class="drawer-close" @click="selectedItem = null">×</button>
          <img
            :src="selectedItem.image_url || '/placeholder.png'"
            class="drawer-img"
            alt="Kvartira"
            onerror="this.src='/placeholder.png'"
          />
          <div class="drawer-content">
            <div class="drawer-price">{{ formatPrice(selectedItem.price, selectedItem.currency) }}</div>
            <div class="drawer-title">{{ selectedItem.title }}</div>
            <div class="drawer-meta">
              {{ selectedItem.rooms }} xona • {{ selectedItem.area_m2 || '-' }} m² • {{ selectedItem.district }}
            </div>
            <div class="drawer-actions">
              <NuxtLink :to="`/admin/listings/${selectedItem.id}`" class="d-view-btn">
                Batafsil Dossier →
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.map-page { display: flex; flex-direction: column; gap: 16px; }
.map-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 22px; font-weight: 800; color: var(--ad-text-main); margin: 0; }
.page-sub { font-size: 13.5px; color: var(--ad-text-muted); margin-top: 2px; }

.toolbar-filters { display: flex; align-items: center; gap: 10px; }
.t-select {
  height: 36px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  background: var(--ad-surface);
  color: var(--ad-text-main);
  padding: 0 10px;
  font-size: 13px;
  outline: none;
}
.count-badge {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--ad-primary);
  background: var(--ad-primary-light);
  padding: 6px 12px;
  border-radius: var(--ad-radius-md);
}

.map-layout-box {
  position: relative;
  height: calc(100vh - 210px);
  min-height: 500px;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  overflow: hidden;
  box-shadow: var(--ad-shadow-sm);
}

.ymap-container {
  width: 100%;
  height: 100%;
}

.listing-drawer-card {
  position: absolute;
  bottom: 24px;
  right: 24px;
  width: 320px;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  box-shadow: var(--ad-shadow-lg);
  z-index: 20;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slide-up 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.drawer-close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.6);
  color: #fff;
  border: none;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.drawer-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.drawer-content {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.drawer-price {
  font-size: 18px;
  font-weight: 800;
  color: var(--ad-primary);
  font-family: var(--ad-font-mono);
}

.drawer-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ad-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drawer-meta {
  font-size: 12px;
  color: var(--ad-text-muted);
}

.drawer-actions {
  margin-top: 8px;
}

.d-view-btn {
  display: block;
  text-align: center;
  background: var(--ad-primary);
  color: #fff;
  text-decoration: none;
  padding: 8px;
  border-radius: var(--ad-radius-md);
  font-size: 12.5px;
  font-weight: 600;
}
</style>
