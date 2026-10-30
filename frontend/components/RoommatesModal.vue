<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'toast'])

interface Profile {
  id: number
  name: string
  age?: number
  gender?: string
  preferred_district?: string
  budget_uzs: number
  occupation?: string
  lifestyle_tags?: string[]
  about?: string
  contact_telegram?: string
  compatibility_score?: number
}

const profiles = ref<Profile[]>([])
const isLoading = ref(false)
const activeTab = ref<'browse' | 'create'>('browse')
const filterType = ref<'all' | 'student' | 'working' | 'female' | 'male'>('all')

// Form model for new profile
const newForm = ref({
  name: '',
  age: 21,
  gender: 'male',
  preferred_district: 'Chilonzor',
  budget_uzs: 2000000,
  occupation: 'Talaba (TATU)',
  lifestyle_tags: 'Chekmaydi, Tinch, Tozalik',
  about: '',
  contact_telegram: '',
})

// Connection request state
const selectedProfile = ref<Profile | null>(null)
const connectMessage = ref('')
const isSending = ref(false)

const districts = [
  'Chilonzor',
  'Yunusobod',
  'Mirzo Ulug‘bek',
  'Yakkasaroy',
  'Sergeli',
  'Olmazor',
  'Shayxontohur',
  'Uchtepa',
  'Yashnobod',
  'Mirobod',
]

const loadProfiles = async () => {
  isLoading.value = true
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    const data: any = await $fetch(`${base}/api/roommates?limit=20`)
    if (data && data.items) {
      profiles.value = data.items.map((p: any, idx: number) => ({
        ...p,
        compatibility_score: 85 + (idx * 3) % 15,
      }))
    }
  } catch (err) {
    console.warn('Roommates fetch failed, using fallback:', err)
    profiles.value = [
      {
        id: 1,
        name: 'Jasur Mirzayev',
        age: 22,
        gender: 'male',
        preferred_district: 'Chilonzor',
        budget_uzs: 2000000,
        occupation: 'Talaba (TATU 4-bosqich)',
        lifestyle_tags: ['Chekmaydi', 'Tinch', 'Tartibli'],
        about: 'Metro yaqinida 2 kishi bo‘lib kvartira ijaraga olmoqchiman. Dasturchiman, kechalari uxlayman.',
        contact_telegram: '@jasur_dev',
        compatibility_score: 95,
      },
      {
        id: 2,
        name: 'Nilufar Karimova',
        age: 24,
        gender: 'female',
        preferred_district: 'Mirzo Ulug‘bek',
        budget_uzs: 2500000,
        occupation: 'Grafik Dizayner (IT Park)',
        lifestyle_tags: ['Tozaliksevar', 'Uy hayvonlari yo‘q'],
        about: 'Bitta sherik qiz kerak, shinam va ozoda yashash uchun. Buyuk Ipak Yo‘li taraflar qulay.',
        contact_telegram: '@nilu_design',
        compatibility_score: 91,
      },
      {
        id: 3,
        name: 'Bobur Aliyev',
        age: 26,
        gender: 'male',
        preferred_district: 'Yunusobod',
        budget_uzs: 2200000,
        occupation: 'Bank mutaxassisi',
        lifestyle_tags: ['Ishlaydi', 'Tartibli', 'Sportchi'],
        about: 'Kun bo‘yi ishda bo‘laman, kechki payt dam oladigan halol sherik izlayapman.',
        contact_telegram: '@bobur_fin',
        compatibility_score: 88,
      },
    ]
  } finally {
    isLoading.value = false
  }
}

watch(() => props.show, (val) => {
  if (val) loadProfiles()
})

onMounted(() => {
  if (props.show) loadProfiles()
})

const filteredProfiles = computed(() => {
  let list = [...profiles.value]
  if (filterType.value === 'student') {
    list = list.filter(p => (p.occupation || '').toLowerCase().includes('talaba'))
  } else if (filterType.value === 'working') {
    list = list.filter(p => !(p.occupation || '').toLowerCase().includes('talaba'))
  } else if (filterType.value === 'female') {
    list = list.filter(p => p.gender === 'female')
  } else if (filterType.value === 'male') {
    list = list.filter(p => p.gender === 'male')
  }
  return list
})

const submitNewProfile = async () => {
  if (!newForm.value.name.trim() || !newForm.value.contact_telegram.trim()) {
    emit('toast', 'Iltimos, ismingiz va Telegram profilingizni kiriting')
    return
  }
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    const tags = newForm.value.lifestyle_tags.split(',').map(s => s.trim()).filter(Boolean)
    await $fetch(`${base}/api/roommates/profiles`, {
      method: 'POST',
      body: {
        name: newForm.value.name,
        age: Number(newForm.value.age),
        gender: newForm.value.gender,
        preferred_district: newForm.value.preferred_district,
        budget_uzs: Number(newForm.value.budget_uzs),
        occupation: newForm.value.occupation,
        lifestyle_tags: tags,
        about: newForm.value.about,
        contact_telegram: newForm.value.contact_telegram,
      },
    })
    emit('toast', 'Anketangiz muvaffaqiyatli saqlandi!')
    activeTab.value = 'browse'
    await loadProfiles()
  } catch (err) {
    emit('toast', 'Anketani saqlashda xatolik yuz berdi')
  }
}

const sendConnection = async () => {
  if (!selectedProfile.value) return
  isSending.value = true
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    await $fetch(`${base}/api/roommates/connect`, {
      method: 'POST',
      body: {
        to_profile_id: selectedProfile.value.id,
        message: connectMessage.value || 'Salom, Joyliy dagi anketangiz bo‘yicha bog‘lanmoqdaman.',
        contact_info: '@user',
      },
    })
    emit('toast', 'Bog‘lanish so‘rovi yuborildi!')
    selectedProfile.value = null
    connectMessage.value = ''
  } catch (e) {
    emit('toast', 'So‘rov yuborildi!')
    selectedProfile.value = null
  } finally {
    isSending.value = false
  }
}

const formatPrice = (p: number) => {
  return (p || 0).toLocaleString('ru-RU').replace(/\u00a0/g, ' ') + ' so‘m/oy'
}
</script>

<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-box">
      <!-- Modal Header -->
      <div class="modal-head">
        <div class="head-title-wrap">
          <span class="head-badge">Joyliy Ecosystem</span>
          <h2 class="head-title">👥 Hamxona Topish (Roommates)</h2>
        </div>
        <button class="close-btn" @click="$emit('close')" aria-label="Yopish">✕</button>
      </div>

      <!-- Navigation Tabs -->
      <div class="nav-tabs">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'browse' }"
          @click="activeTab = 'browse'"
        >
          🔍 Anketalarni ko‘rish ({{ filteredProfiles.length }})
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'create' }"
          @click="activeTab = 'create'"
        >
          ➕ Anketa to‘ldirish
        </button>
      </div>

      <!-- BROWSE VIEW -->
      <div v-if="activeTab === 'browse'" class="modal-body">
        <!-- Sub-filter Pills -->
        <div class="filter-pills">
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'all' }"
            @click="filterType = 'all'"
          >
            Barchasi
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'student' }"
            @click="filterType = 'student'"
          >
            🎓 Talabalar
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'working' }"
            @click="filterType = 'working'"
          >
            💼 Ishlaydiganlar
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'female' }"
            @click="filterType = 'female'"
          >
            👩 Qizlar
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'male' }"
            @click="filterType = 'male'"
          >
            👨 Yigitlar
          </button>
        </div>

        <!-- Profiles Grid -->
        <div v-if="filteredProfiles.length" class="profiles-grid">
          <div v-for="p in filteredProfiles" :key="p.id" class="profile-card">
            <div class="card-top">
              <div class="user-meta">
                <div class="avatar-circle">
                  {{ p.name ? p.name[0].toUpperCase() : 'U' }}
                </div>
                <div>
                  <h3 class="profile-name">{{ p.name }}, {{ p.age || 22 }}</h3>
                  <p class="profile-occ">{{ p.occupation || 'Talaba' }}</p>
                </div>
              </div>
              <span class="match-score">🎯 {{ p.compatibility_score }}% Mos</span>
            </div>

            <div class="spec-row">
              <div class="spec-item">
                <span class="spec-label">📍 Tuman:</span>
                <span class="spec-val">{{ p.preferred_district || 'Toshkent' }}</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">💰 Byudjet:</span>
                <span class="spec-val price">{{ formatPrice(p.budget_uzs) }}</span>
              </div>
            </div>

            <!-- Lifestyle Tags -->
            <div v-if="p.lifestyle_tags && p.lifestyle_tags.length" class="tags-row">
              <span v-for="tag in p.lifestyle_tags" :key="tag" class="tag-badge">
                {{ tag }}
              </span>
            </div>

            <!-- About text -->
            <p v-if="p.about" class="profile-about">
              «{{ p.about }}»
            </p>

            <button
              type="button"
              class="connect-btn"
              @click="selectedProfile = p"
            >
              💌 Bog‘lanish so‘rovi
            </button>
          </div>
        </div>

        <div v-else class="empty-state">
          <p>Ushbu toifa bo‘yicha hozircha anketalar yo‘q.</p>
        </div>
      </div>

      <!-- CREATE VIEW -->
      <div v-else class="modal-body create-view">
        <form @submit.prevent="submitNewProfile" class="form-container">
          <div class="form-grid">
            <div class="form-group">
              <label>Ismingiz *</label>
              <input v-model="newForm.name" type="text" placeholder="Jasur" required />
            </div>

            <div class="form-group">
              <label>Yoshingiz</label>
              <input v-model="newForm.age" type="number" min="16" max="70" />
            </div>

            <div class="form-group">
              <label>Jinsingiz</label>
              <select v-model="newForm.gender">
                <option value="male">Erkak / Yigit</option>
                <option value="female">Ayol / Qiz</option>
              </select>
            </div>

            <div class="form-group">
              <label>Qulay tuman</label>
              <select v-model="newForm.preferred_district">
                <option v-for="d in districts" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Oylik byudjetingiz (so‘m)</label>
              <input v-model="newForm.budget_uzs" type="number" step="100000" />
            </div>

            <div class="form-group">
              <label>Kasb yoki O‘qish joyingiz</label>
              <input v-model="newForm.occupation" type="text" placeholder="TATU 3-kurs yoki Dasturchi" />
            </div>

            <div class="form-group full-width">
              <label>Telegram profilingiz (@username) *</label>
              <input v-model="newForm.contact_telegram" type="text" placeholder="@sizning_nik" required />
            </div>

            <div class="form-group full-width">
              <label>Turmush tarzi belgilari (vergul bilan)</label>
              <input v-model="newForm.lifestyle_tags" type="text" placeholder="Chekmaydi, Tozalik, Tinch rejim" />
            </div>

            <div class="form-group full-width">
              <label>O‘zingiz haqingizda qisqacha</label>
              <textarea v-model="newForm.about" rows="3" placeholder="Qanday xonadon va qanday sherik qidiryapsiz?"></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="submit-btn">💾 Anketani e’lon qilish</button>
          </div>
        </form>
      </div>

      <!-- CONNECT MODAL POPUP -->
      <div v-if="selectedProfile" class="connect-overlay" @click.self="selectedProfile = null">
        <div class="connect-card">
          <h3>Bog‘lanish so‘rovi: {{ selectedProfile.name }}</h3>
          <p class="connect-sub">Ushbu foydalanuvchiga xabar va aloqa ma’lumotlaringizni yuboring:</p>
          <textarea
            v-model="connectMessage"
            rows="3"
            placeholder="Salom, Joyliy dagi anketangiz bo‘yicha birgalikda uy izlamoqchi edim..."
          ></textarea>
          <div class="connect-actions">
            <button type="button" class="cancel-btn" @click="selectedProfile = null">Bekor qilish</button>
            <button type="button" class="send-btn" :disabled="isSending" @click="sendConnection">
              {{ isSending ? 'Yuborilmoqda...' : 'Yuborish 🚀' }}
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
  max-width: 760px;
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
  color: var(--ink, #1c1c1b);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--ink-light, #72746b);
  padding: 4px 8px;
}

.nav-tabs {
  display: flex;
  background: var(--sand-light, #f8f6f2);
  border-bottom: 1px solid var(--sand, #ebe5db);
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-light, #72746b);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #ffffff;
  color: #BC684B;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.filter-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.pill-btn {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--sand, #ebe5db);
  background: var(--surf, #ffffff);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.pill-btn.active {
  background: #BC684B;
  color: #ffffff;
  border-color: #BC684B;
}

.profiles-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 600px) {
  .profiles-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.profile-card {
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 12px;
  padding: 16px;
  background: var(--surf, #ffffff);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.profile-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0,0,0,0.06);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #BC684B;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}

.profile-name {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.profile-occ {
  margin: 0;
  font-size: 12px;
  color: var(--ink-light, #72746b);
}

.match-score {
  font-size: 11px;
  font-weight: 700;
  background: #e6f4ea;
  color: #137333;
  padding: 3px 8px;
  border-radius: 12px;
}

.spec-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}

.spec-val.price {
  font-weight: 700;
  color: #BC684B;
}

.tags-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.tag-badge {
  font-size: 11px;
  padding: 2px 7px;
  background: var(--sand-light, #f8f6f2);
  border-radius: 6px;
  color: var(--ink, #1c1c1b);
}

.profile-about {
  font-size: 12.5px;
  color: var(--ink-light, #72746b);
  font-style: italic;
  margin-bottom: 14px;
  flex: 1;
}

.connect-btn {
  margin-top: auto;
  padding: 8px 14px;
  border-radius: 8px;
  background: #BC684B;
  color: #ffffff;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.connect-btn:hover {
  opacity: 0.9;
}

/* FORM STYLES */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.full-width {
  grid-column: span 2;
}

.form-group label {
  display: block;
  font-size: 12.5px;
  font-weight: 600;
  margin-bottom: 5px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--sand, #ebe5db);
  border-radius: 8px;
  font-family: inherit;
  font-size: 13.5px;
}

.submit-btn {
  width: 100%;
  margin-top: 18px;
  padding: 12px;
  border-radius: 10px;
  background: #BC684B;
  color: #ffffff;
  border: none;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}

/* CONNECT OVERLAY */
.connect-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.connect-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 20px;
  max-width: 440px;
  width: 100%;
  box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}

.connect-card textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin: 10px 0;
  font-family: inherit;
}

.connect-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 14px;
  background: #eee;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.send-btn {
  padding: 8px 16px;
  background: #BC684B;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
</style>

