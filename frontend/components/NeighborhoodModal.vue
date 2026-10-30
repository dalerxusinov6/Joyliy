<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useListings } from '~/composables/useListings'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'selectDistrict'])

const { filterDistrict } = useListings()

interface DistrictInfo {
  name: string
  score: number
  metro_count: number
  avg_price_uzs: number
  parks_count: number
  universities_count: number
  safety_score: number
  description: string
}

const districts = ref<DistrictInfo[]>([])
const isLoading = ref(false)

const loadDistricts = async () => {
  isLoading.value = true
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    const res: any = await $fetch(`${base}/api/neighborhoods`)
    if (res && res.districts) {
      districts.value = res.districts.map((d: any) => ({
        name: d.name,
        score: d.overall_score || 88,
        metro_count: d.metro_stations?.length || 3,
        avg_price_uzs: d.average_price_uzs || 4500000,
        parks_count: d.parks_count || 4,
        universities_count: d.universities_count || 5,
        safety_score: d.safety_rating || 90,
        description: d.description || 'Toshkentning nufuzli va qulay tumanlaridan biri.',
      }))
    }
  } catch (err) {
    // fallback
    districts.value = [
      { name: 'Mirobod', score: 94, metro_count: 4, avg_price_uzs: 6500000, parks_count: 5, universities_count: 6, safety_score: 95, description: 'Markaziy biznes va nufuzli yashash hududi, premium kafelar va elchixonalar.' },
      { name: 'Yakkasaroy', score: 91, metro_count: 3, avg_price_uzs: 5800000, parks_count: 4, universities_count: 4, safety_score: 93, description: 'Tinch, ko‘kalamzor, diplomatik hudud va milliy bog‘lar yaqini.' },
      { name: 'Chilonzor', score: 89, metro_count: 8, avg_price_uzs: 3800000, parks_count: 6, universities_count: 7, safety_score: 88, description: 'Toshkentning eng yirik va qulay transportli tumani, talabalar va oilalar uchun ideal.' },
      { name: 'Yunusobod', score: 90, metro_count: 6, avg_price_uzs: 4200000, parks_count: 5, universities_count: 5, safety_score: 90, description: 'Mega Planet, bozorlar, xiyobonlar va yashil mavzelar bilan mashhur.' },
      { name: 'Mirzo Ulug‘bek', score: 92, metro_count: 5, avg_price_uzs: 5200000, parks_count: 6, universities_count: 8, safety_score: 92, description: 'Akademik va ilmiy markaz, TTZ, Buyuk Ipak Yo‘li, ekologik toza havo.' },
      { name: 'Shayxontohur', score: 87, metro_count: 5, avg_price_uzs: 4800000, parks_count: 4, universities_count: 4, safety_score: 89, description: 'Tarixiy markaz, Chorsu, Samarqand Darvoza va qulay infratuzilma.' },
    ]
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadDistricts()
})

const chooseDistrict = (dName: string) => {
  filterDistrict.value = dName
  emit('selectDistrict', dName)
  emit('close')
  const el = document.getElementById('katalog')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const formatPrice = (p: number) => {
  return `${(p / 1000000).toFixed(1)} mln so‘m`
}
</script>

<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-box">
      <!-- Head -->
      <div class="modal-head">
        <div>
          <span class="head-badge">Neighborhood Intelligence</span>
          <h2 class="head-title">🏙 Toshkent Tumanlari Reytingi</h2>
        </div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <p class="intro-p">
          Joyliy tahliliy platformasi har bir tumanning transport, xavfsizlik, ta’lim va bozor narxlarini solishtiradi:
        </p>

        <div class="districts-grid">
          <div v-for="d in districts" :key="d.name" class="d-card">
            <div class="d-top">
              <h3 class="d-name">{{ d.name }}</h3>
              <span class="d-score">⭐ {{ d.score }}/100</span>
            </div>

            <p class="d-desc">{{ d.description }}</p>

            <div class="d-stats">
              <div class="stat-cell">
                <span class="s-label">O‘rtacha ijara</span>
                <span class="s-val price">~{{ formatPrice(d.avg_price_uzs) }}</span>
              </div>
              <div class="stat-cell">
                <span class="s-label">Metro bekatlari</span>
                <span class="s-val">🚇 {{ d.metro_count }} ta</span>
              </div>
              <div class="stat-cell">
                <span class="s-label">Xavfsizlik</span>
                <span class="s-val">🛡 {{ d.safety_score }}%</span>
              </div>
              <div class="stat-cell">
                <span class="s-label">Parklar</span>
                <span class="s-val">🌳 {{ d.parks_count }} ta</span>
              </div>
            </div>

            <button type="button" class="d-btn" @click="chooseDistrict(d.name)">
              Ushbu tumandagi uylarni ko‘rish →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(18, 17, 16, 0.65);
  backdrop-filter: blur(5px);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-box {
  background: var(--surf, #ffffff);
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 16px;
  width: 100%;
  max-width: 840px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-head {
  padding: 18px 24px;
  border-bottom: 1px solid var(--sand, #ebe5db);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.head-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #BC684B;
  letter-spacing: 0.5px;
}

.head-title {
  margin: 2px 0 0;
  font-size: 20px;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #72746b;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.intro-p {
  color: #72746b;
  font-size: 13.5px;
  margin-top: 0;
  margin-bottom: 16px;
}

.districts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.d-card {
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 12px;
  padding: 16px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
}

.d-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.d-name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.d-score {
  font-size: 12px;
  font-weight: 700;
  background: #fdf0eb;
  color: #BC684B;
  padding: 2px 8px;
  border-radius: 12px;
}

.d-desc {
  font-size: 12px;
  color: #72746b;
  margin: 0 0 12px;
  line-height: 1.4;
  flex: 1;
}

.d-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  background: #fcfbf9;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 11.5px;
}

.s-label {
  display: block;
  color: #888;
}

.s-val {
  font-weight: 700;
}

.s-val.price {
  color: #BC684B;
}

.d-btn {
  padding: 8px;
  border-radius: 8px;
  background: #f5f2ed;
  color: #1c1c1b;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.d-btn:hover {
  background: #BC684B;
  color: #ffffff;
}
</style>

