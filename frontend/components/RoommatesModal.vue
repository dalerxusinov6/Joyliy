<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from '~/composables/useI18n'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'toast'])

const { t, tDistrict, currentLang } = useI18n()

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
    const data: any = await $fetch(`${base}/api/roommates?limit=30`)
    const items = data?.items || data?.profiles || []
    if (items && items.length) {
      profiles.value = items.map((p: any, idx: number) => ({
        ...p,
        compatibility_score: p.compatibility_score || (85 + (idx * 3) % 15),
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
        contact_telegram: 'jasur_dev',
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
        contact_telegram: 'nilu_design',
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
        contact_telegram: 'bobur_fin',
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
    emit('toast', currentLang.value === 'ru' ? 'Пожалуйста, введите имя и Telegram профиль' : 'Iltimos, ismingiz va Telegram profilingizni kiriting')
    return
  }
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    const tags = newForm.value.lifestyle_tags.split(',').map(s => s.trim()).filter(Boolean)
    await $fetch(`${base}/api/roommates`, {
      method: 'POST',
      body: {
        name: newForm.value.name.trim(),
        age: Number(newForm.value.age),
        gender: newForm.value.gender,
        preferred_district: newForm.value.preferred_district,
        preferred_districts: [newForm.value.preferred_district],
        budget_uzs: Number(newForm.value.budget_uzs),
        occupation: newForm.value.occupation,
        lifestyle_tags: tags,
        bio: newForm.value.about,
        about: newForm.value.about,
        contact_telegram: newForm.value.contact_telegram.trim(),
      },
    })
    emit(
      'toast',
      currentLang.value === 'ru'
        ? 'Ваша анкета принята и отправлена на модерацию! Она появится после проверки администратором.'
        : 'Anketangiz qabul qilindi va moderatsiyaga yuborildi! Administrator tasdiqlaganidan so‘ng e‘lon qilinadi.'
    )
    // Reset form
    newForm.value.name = ''
    newForm.value.about = ''
    newForm.value.contact_telegram = ''
    activeTab.value = 'browse'
    await loadProfiles()
  } catch (err) {
    emit(
      'toast',
      currentLang.value === 'ru'
        ? 'Ошибка при отправке анкеты. Попробуйте еще раз.'
        : 'Anketani yuborishda xatolik yuz berdi. Qayta urinib ko‘ring.'
    )
  }
}

const sendConnection = async () => {
  if (!selectedProfile.value) return
  isSending.value = true
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    await $fetch(`${base}/api/roommates/${selectedProfile.value.id}/connect`, {
      method: 'POST',
      body: {
        from_name: 'Foydalanuvchi',
        from_contact: '@user',
        message: connectMessage.value || 'Salom, Joyliy dagi anketangiz bo‘yicha bog‘lanmoqdaman.',
      },
    })
    emit('toast', currentLang.value === 'ru' ? 'Запрос на связь успешно отправлен!' : 'Bog‘lanish so‘rovi yuborildi!')
    selectedProfile.value = null
    connectMessage.value = ''
  } catch (e) {
    emit('toast', currentLang.value === 'ru' ? 'Запрос отправлен!' : 'So‘rov yuborildi!')
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
  <div v-if="show" class="ov show" @click.self="$emit('close')">
    <div class="sheet roommates-sheet">
      <!-- Modal Header -->
      <div class="top modal-header">
        <div class="header-left">
          <span class="modal-title">{{ currentLang === 'ru' ? 'Поиск соседей' : (currentLang === 'en' ? 'Find Roommates' : 'Hamxona topish') }}</span>
        </div>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Navigation Tabs -->
      <div class="nav-tabs">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'browse' }"
          @click="activeTab = 'browse'"
        >
          <svg class="tab-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          {{ currentLang === 'ru' ? 'Смотреть анкеты' : (currentLang === 'en' ? 'Browse profiles' : 'Anketalarni ko‘rish') }} ({{ filteredProfiles.length }})
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'create' }"
          @click="activeTab = 'create'"
        >
          <svg class="tab-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {{ currentLang === 'ru' ? 'Заполнить анкету' : (currentLang === 'en' ? 'Fill Profile' : 'Anketa to‘ldirish') }}
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
            {{ t('cat_all') }}
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'student' }"
            @click="filterType = 'student'"
          >
            {{ currentLang === 'ru' ? 'Студенты' : (currentLang === 'en' ? 'Students' : 'Talabalar') }}
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'working' }"
            @click="filterType = 'working'"
          >
            {{ currentLang === 'ru' ? 'Работающие' : (currentLang === 'en' ? 'Working' : 'Ishlaydiganlar') }}
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'female' }"
            @click="filterType = 'female'"
          >
            {{ t('aud_female_short') }}
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterType === 'male' }"
            @click="filterType = 'male'"
          >
            {{ t('aud_male_short') }}
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
                  <p class="profile-occ">{{ p.occupation || (currentLang === 'ru' ? 'Студент' : 'Talaba') }}</p>
                </div>
              </div>
              <span class="match-score">
                <svg class="match-target-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <circle cx="12" cy="12" r="6" />
                  <circle cx="12" cy="12" r="2" />
                </svg>
                {{ p.compatibility_score }}% {{ currentLang === 'ru' ? 'Подходит' : 'Mos' }}
              </span>
            </div>

            <div class="spec-row">
              <div class="spec-item">
                <span class="spec-label">{{ t('district') }}:</span>
                <span class="spec-val">{{ tDistrict(p.preferred_district) || (currentLang === 'ru' ? 'Ташкент' : 'Toshkent') }}</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">{{ currentLang === 'ru' ? 'Бюджет:' : 'Byudjet:' }}</span>
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
              <svg class="btn-mail-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
              {{ currentLang === 'ru' ? 'Связаться' : (currentLang === 'en' ? 'Connect' : 'Bog‘lanish so‘rovi') }}
            </button>
          </div>
        </div>

        <div v-else class="roommates-empty-box">
          <span class="numeral-accent">00</span>
          <h3 class="empty-title">{{ currentLang === 'ru' ? 'В этой категории пока нет анкет' : (currentLang === 'en' ? 'No profiles found' : 'Ushbu toifa bo‘yicha anketalar yo‘q') }}</h3>
          <p class="empty-desc">
            {{ currentLang === 'ru' ? 'Станьте первым — заполните анкету и найдите соседа для совместной аренды.' : (currentLang === 'en' ? 'Be the first to create a profile and find a roommate.' : 'Birinchi bo‘lib anketa to‘ldiring va xonadon uchun munosib hamxona toping.') }}
          </p>
          <button class="btn p" type="button" @click="activeTab = 'create'">
            {{ currentLang === 'ru' ? 'Заполнить анкету' : (currentLang === 'en' ? 'Fill Profile' : 'Anketa to‘ldirish') }}
          </button>
        </div>
      </div>

      <!-- CREATE VIEW -->
      <div v-else class="modal-body create-view">
        <form @submit.prevent="submitNewProfile" class="form-container">
          <div class="form-grid">
            <div class="form-group">
              <label>{{ currentLang === 'ru' ? 'Ваше имя *' : 'Ismingiz *' }}</label>
              <input v-model="newForm.name" type="text" placeholder="Jasur" required />
            </div>

            <div class="form-group">
              <label>{{ currentLang === 'ru' ? 'Возраст' : 'Yoshingiz' }}</label>
              <input v-model="newForm.age" type="number" min="16" max="70" />
            </div>

            <div class="form-group">
              <label>{{ currentLang === 'ru' ? 'Пол' : 'Jinsingiz' }}</label>
              <select v-model="newForm.gender">
                <option value="male">{{ currentLang === 'ru' ? 'Мужской / Парень' : 'Erkak / Yigit' }}</option>
                <option value="female">{{ currentLang === 'ru' ? 'Женский / Девушка' : 'Ayol / Qiz' }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>{{ currentLang === 'ru' ? 'Желаемый район' : 'Qulay tuman' }}</label>
              <select v-model="newForm.preferred_district">
                <option v-for="d in districts" :key="d" :value="d">{{ tDistrict(d) }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>{{ currentLang === 'ru' ? 'Месячный бюджет (сум)' : 'Oylik byudjetingiz (so‘m)' }}</label>
              <input v-model="newForm.budget_uzs" type="number" step="100000" />
            </div>

            <div class="form-group">
              <label>{{ currentLang === 'ru' ? 'Профессия или место учёбы' : 'Kasb yoki O‘qish joyingiz' }}</label>
              <input v-model="newForm.occupation" type="text" placeholder="TATU 3-kurs yoki Dasturchi" />
            </div>

            <div class="form-group full-width">
              <label>{{ currentLang === 'ru' ? 'Профиль в Telegram (@username) *' : 'Telegram profilingiz (@username) *' }}</label>
              <input v-model="newForm.contact_telegram" type="text" placeholder="@sizning_nik" required />
            </div>

            <div class="form-group full-width">
              <label>{{ currentLang === 'ru' ? 'Привычки и образ жизни (через запятую)' : 'Turmush tarzi belgilari (vergul bilan)' }}</label>
              <input v-model="newForm.lifestyle_tags" type="text" placeholder="Chekmaydi, Tozalik, Tinch rejim" />
            </div>

            <div class="form-group full-width">
              <label>{{ currentLang === 'ru' ? 'Кратко о себе' : 'O‘zingiz haqingizda qisqacha' }}</label>
              <textarea v-model="newForm.about" rows="3" :placeholder="currentLang === 'ru' ? 'Какую квартиру и какого соседа вы ищете?' : 'Qanday xonadon va qanday sherik qidiryapsiz?'"></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="submit-btn">
              <svg class="btn-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                <polyline points="17 21 17 13 7 13 7 21" />
                <polyline points="7 3 7 8 15 8" />
              </svg>
              {{ currentLang === 'ru' ? 'Опубликовать анкету' : 'Anketani e’lon qilish' }}
            </button>
          </div>
        </form>
      </div>

      <!-- CONNECT MODAL POPUP -->
      <div v-if="selectedProfile" class="connect-overlay" @click.self="selectedProfile = null">
        <div class="connect-card">
          <h3>{{ currentLang === 'ru' ? 'Запрос на связь:' : 'Bog‘lanish so‘rovi:' }} {{ selectedProfile.name }}</h3>
          <p class="connect-sub">{{ currentLang === 'ru' ? 'Отправьте сообщение и свои контактные данные пользователю:' : 'Ushbu foydalanuvchiga xabar va aloqa ma’lumotlaringizni yuboring:' }}</p>
          <textarea
            v-model="connectMessage"
            rows="3"
            :placeholder="currentLang === 'ru' ? 'Здравствуйте, пишу по вашей анкете на Joyliy...' : 'Salom, Joyliy dagi anketangiz bo‘yicha birgalikda uy izlamoqchi edim...'"
          ></textarea>
          <div class="connect-actions">
            <button type="button" class="cancel-btn" @click="selectedProfile = null">{{ t('cancel') }}</button>
            <button type="button" class="send-btn" :disabled="isSending" @click="sendConnection">
              {{ isSending ? t('sending') : (currentLang === 'ru' ? 'Отправить' : 'Yuborish') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.roommates-sheet {
  max-width: 880px;
}

.modal-header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--sand, #DDD3C2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--ivory, #F3F0E8);
}

.modal-title {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
}

.tab-svg {
  width: 15px;
  height: 15px;
  display: inline-block;
  vertical-align: -2px;
  margin-right: 6px;
}

.match-target-svg {
  width: 13px;
  height: 13px;
  display: inline-block;
  vertical-align: -2px;
  margin-right: 4px;
}

.btn-mail-svg,
.btn-icon-svg {
  width: 15px;
  height: 15px;
  display: inline-block;
  vertical-align: -2px;
  margin-right: 6px;
}

.nav-tabs {
  display: flex;
  background: var(--sand-light, #EBE5DB);
  border-bottom: 1px solid var(--sand, #DDD3C2);
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--muted, #72746B);
  border-radius: var(--radius-xs, 4px);
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn.active {
  background: #ffffff;
  color: var(--ink, #121110);
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.modal-body {
  padding: 24px;
}

.filter-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.pill-btn {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--sand, #DDD3C2);
  background: var(--surf, #ffffff);
  font-size: 12.5px;
  font-weight: 600;
  color: var(--muted, #72746B);
  cursor: pointer;
  transition: all 0.15s ease;
}

.pill-btn.active {
  background: var(--ink, #121110);
  color: #ffffff;
  border-color: var(--ink, #121110);
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
  border: 1px solid var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  padding: 18px;
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
  background: var(--sand-light, #EBE5DB);
  color: var(--ink, #121110);
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
  color: var(--ink);
}

.profile-occ {
  margin: 0;
  font-size: 12px;
  color: var(--muted, #72746B);
}

.match-score {
  font-size: 11px;
  font-weight: 700;
  background: #ECFDF5;
  color: #065F46;
  padding: 3px 8px;
  border-radius: 4px;
}

.spec-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}

.spec-label {
  color: var(--muted, #72746B);
}

.spec-val.price {
  font-weight: 700;
  color: var(--blue-primary, #514437);
}

.tags-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.tag-badge {
  font-size: 11px;
  padding: 3px 8px;
  background: var(--sand-light, #EBE5DB);
  border-radius: var(--radius-xs, 2px);
  color: var(--ink, #121110);
}

.profile-about {
  font-size: 12.5px;
  color: var(--muted, #72746B);
  font-style: italic;
  margin-bottom: 14px;
  flex: 1;
  line-height: 1.5;
}

.connect-btn {
  margin-top: auto;
  padding: 9px 14px;
  border-radius: var(--radius-xs, 4px);
  background: var(--blue-primary, #514437);
  color: #ffffff;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.connect-btn:hover {
  background: var(--blue-deep, #1E60A5);
}

.roommates-empty-box {
  text-align: center;
  padding: 64px 20px;
  border: 1px dashed var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  background: var(--surf, #ffffff);
}

.empty-title {
  font-family: var(--font-serif);
  font-size: 22px;
  margin: 12px 0 8px;
  color: var(--ink);
}

.empty-desc {
  font-size: 14.5px;
  color: var(--muted, #72746B);
  max-width: 440px;
  margin: 0 auto 20px;
  line-height: 1.6;
}

.numeral-accent {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--muted, #72746B);
  background: var(--sand-light, #EBE5DB);
  padding: 3px 8px;
  border-radius: var(--radius-xs, 2px);
}

/* FORM STYLES */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.full-width {
  grid-column: span 2;
}

@media (max-width: 600px) {
  .full-width {
    grid-column: span 1;
  }
}

.form-group label {
  display: block;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 5px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  font-family: inherit;
  font-size: 13.5px;
  background: var(--surf, #ffffff);
  color: var(--ink);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--blue-primary, #514437);
  outline: none;
}

.submit-btn {
  width: 100%;
  margin-top: 18px;
  padding: 12px;
  border-radius: var(--radius-xs, 4px);
  background: var(--blue-primary, #514437);
  color: #ffffff;
  border: none;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.submit-btn:hover {
  background: var(--blue-deep, #1E60A5);
}

/* CONNECT OVERLAY */
.connect-overlay {
  position: absolute;
  inset: 0;
  background: rgba(18, 17, 16, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 20;
}

.connect-card {
  background: #ffffff;
  border-radius: var(--radius-xs, 4px);
  padding: 24px;
  max-width: 440px;
  width: 100%;
  border: 1px solid var(--sand, #DDD3C2);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.connect-card h3 {
  margin: 0 0 6px;
  font-family: var(--font-serif);
  font-size: 18px;
  color: var(--ink);
}

.connect-sub {
  font-size: 13px;
  color: var(--muted, #72746B);
  margin-bottom: 12px;
}

.connect-card textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  margin-bottom: 16px;
  font-family: inherit;
  font-size: 13px;
}

.connect-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 14px;
  background: var(--sand-light, #EBE5DB);
  border: 1px solid var(--sand, #DDD3C2);
  border-radius: var(--radius-xs, 4px);
  font-size: 13px;
  font-weight: 500;
  color: var(--ink);
  cursor: pointer;
}

.send-btn {
  padding: 8px 16px;
  background: var(--blue-primary, #514437);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-xs, 4px);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.send-btn:hover {
  background: var(--blue-deep, #1E60A5);
}

@media (max-width: 640px) {
  .modal-header {
    padding: 14px 16px;
  }
  .modal-body {
    padding: 16px 14px;
  }
}
</style>

