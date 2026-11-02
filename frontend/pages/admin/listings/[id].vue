<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

const route = useRoute()
const router = useRouter()
const { authFetch, showToast } = useAdminAuth()

const listingId = route.params.id

const isLoading = ref(true)
const isSaving = ref(false)
const listing = ref<any>(null)
const updateHistory = ref<any[]>([])

const editableForm = ref({
  title: '',
  price: 0,
  currency: 'USD',
  deal_type: 'rent',
  rooms: 1,
  area_m2: 0,
  floor: 1,
  total_floors: 1,
  district: '',
  neighborhood: '',
  address: '',
  description: '',
  contact_phone: '',
  contact_name: '',
  property_type: 'apartment',
  status: 'active',
})

const activeImageIdx = ref(0)

const districtsList = [
  'Chilonzor', 'Yunusobod', 'Mirzo Ulug‘bek', 'Yakkasaroy', 'Mirobod',
  'Shayxontohur', 'Olmazor', 'Uchtepa', 'Yashnobod', 'Sergeli', 'Bektemir', 'Yangihayot'
]

const loadListingDetail = async () => {
  isLoading.value = true
  try {
    const res = await authFetch(`/api/admin/listings/${listingId}`)
    if (res && res.success) {
      listing.value = res.item
      updateHistory.value = res.update_history || []

      editableForm.value = {
        title: listing.value.title || '',
        price: listing.value.price || 0,
        currency: listing.value.currency || 'USD',
        deal_type: listing.value.deal_type || 'rent',
        rooms: listing.value.rooms || 1,
        area_m2: listing.value.area_m2 || 0,
        floor: listing.value.floor || 1,
        total_floors: listing.value.total_floors || 1,
        district: listing.value.district || '',
        neighborhood: listing.value.neighborhood || '',
        address: listing.value.address || '',
        description: listing.value.description || '',
        contact_phone: listing.value.contact_phone || '',
        contact_name: listing.value.contact_name || '',
        property_type: listing.value.property_type || 'apartment',
        status: listing.value.status || 'active',
      }
    } else {
      showToast('E‘lon topilmadi', 'error')
    }
  } catch (err: any) {
    showToast('E‘lon ma‘lumotlarini yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

const saveChanges = async () => {
  isSaving.value = true
  try {
    const res = await authFetch(`/api/admin/listings/${listingId}`, {
      method: 'PUT',
      body: editableForm.value,
    })
    if (res && res.success) {
      showToast('O‘zgarishlar muvaffaqiyatli saqlandi!', 'success')
      await loadListingDetail()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Saqlashda xatolik', 'error')
  } finally {
    isSaving.value = false
  }
}

const publishToTelegram = async () => {
  try {
    showToast('Telegramga yuborilmoqda...', 'info')
    const res = await authFetch(`/api/admin/telegram/publish/${listingId}`, {
      method: 'POST',
    })
    if (res && res.success) {
      showToast('E‘lon Telegram kanalga muvaffaqiyatli post qilindi!', 'success')
      await loadListingDetail()
    } else {
      showToast(res?.message || 'Yuborish amalga oshmadi', 'warning')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Telegramga yuborishda xatolik', 'error')
  }
}

onMounted(() => {
  loadListingDetail()
})

const formatPrice = (price: number = 0, currency: string = 'USD') => {
  const sym = currency === 'USD' ? '$' : 'so‘m'
  return `${new Intl.NumberFormat('uz-UZ').format(price)} ${sym}`
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleString('uz-UZ', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <AdminShell
    :title="`E‘lon #${listingId}`"
    :breadcrumbs="[
      { label: 'E‘lonlar', to: '/admin/listings' },
      { label: `Dossier #${listingId}` }
    ]"
  >
    <div class="dossier-page">
      <div v-if="isLoading" class="loading-box">
        <div class="spinner" />
        <span>E‘lon ma‘lumotlari yuklanmoqda...</span>
      </div>

      <div v-else-if="listing" class="dossier-layout">
        <!-- Top Dossier Action Header -->
        <div class="dossier-header-bar">
          <div class="dh-left">
            <span class="dh-id-tag">ID: #{{ listing.id }}</span>
            <span class="dh-source-tag">Manba: {{ listing.source }} ({{ listing.source_id || 'ID yo‘q' }})</span>
            <span class="dh-status-tag" :class="listing.status === 'active' ? 'st-act' : 'st-arc'">
              {{ listing.status === 'active' ? '🟢 Faol' : '⚪ Arxiv' }}
            </span>
          </div>

          <div class="dh-right">
            <a
              v-if="listing.source_url"
              :href="listing.source_url"
              target="_blank"
              class="sec-btn"
              title="Asl manbaga o‘tish"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
              </svg>
              Asl manba
            </a>

            <button class="tg-publish-btn" @click="publishToTelegram">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
              Telegramga chiqarish
            </button>

            <button class="save-primary-btn" @click="saveChanges" :disabled="isSaving">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              {{ isSaving ? 'Saqlanmoqda...' : 'O‘zgarishlarni saqlash' }}
            </button>
          </div>
        </div>

        <!-- Main Dossier Grid -->
        <div class="dossier-columns-grid">
          <!-- Left Column: Gallery & Source Info -->
          <div class="dossier-left-col">
            <!-- Gallery Card -->
            <div class="dossier-card">
              <div class="gallery-main-view">
                <img
                  :src="(listing.images && listing.images[activeImageIdx]) || listing.image_url || '/placeholder.png'"
                  alt="Kvartira fotosurati"
                  class="main-gallery-img"
                  onerror="this.src='/placeholder.png'"
                />
              </div>

              <!-- Thumbnails row -->
              <div v-if="listing.images && listing.images.length > 1" class="gallery-thumbs-row">
                <img
                  v-for="(img, idx) in listing.images"
                  :key="idx"
                  :src="img"
                  class="thumb-item"
                  :class="{ active: idx === activeImageIdx }"
                  @click="activeImageIdx = idx"
                  alt="Rasm"
                  onerror="this.src='/placeholder.png'"
                />
              </div>
            </div>

            <!-- Telegram & Source Card -->
            <div class="dossier-card">
              <h4 class="card-h4">Integratsiya va Manba</h4>
              <div class="info-list">
                <div class="info-row">
                  <span class="info-k">Telegram holati:</span>
                  <span class="info-v font-bold" :class="listing.telegram_status === 'published' ? 'text-success' : 'text-muted'">
                    {{ listing.telegram_status === 'published' ? '✅ Chop etilgan' : '⏳ Navbatda' }}
                  </span>
                </div>
                <div class="info-row">
                  <span class="info-k">Telegram xabar ID:</span>
                  <span class="info-v font-mono">{{ listing.telegram_message_id || 'Mavjud emas' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-k">Telegram nashr vaqti:</span>
                  <span class="info-v">{{ formatDate(listing.telegram_published_at) }}</span>
                </div>
                <div class="info-row">
                  <span class="info-k">Topilgan vaqti:</span>
                  <span class="info-v">{{ formatDate(listing.created_at) }}</span>
                </div>
                <div class="info-row">
                  <span class="info-k">Oxirgi skanerlash:</span>
                  <span class="info-v">{{ formatDate(listing.updated_at) }}</span>
                </div>
              </div>
            </div>

            <!-- Price & Update History Timeline -->
            <div class="dossier-card">
              <h4 class="card-h4">O‘zgarishlar tarixi (Audit)</h4>
              <div v-if="updateHistory.length" class="history-timeline">
                <div v-for="(h, hIdx) in updateHistory" :key="hIdx" class="history-item">
                  <div class="history-dot" />
                  <div class="history-info">
                    <span class="history-change">
                      {{ h.change_type === 'price_change' ? '💰 Narx o‘zgardi:' : '✏️ Yangilanish:' }}
                      <strong>{{ h.old_value }}</strong> → <strong>{{ h.new_value }}</strong>
                    </span>
                    <span class="history-time">{{ formatDate(h.created_at) }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-xs text-muted py-2">
                Hozircha o‘zgarishlar tarixi mavjud emas
              </div>
            </div>
          </div>

          <!-- Right Column: Editable Specifications Form -->
          <div class="dossier-right-col">
            <div class="dossier-card">
              <h4 class="card-h4">Tahrirlash va Xususiyatlar</h4>

              <div class="specs-form-grid">
                <!-- Title -->
                <div class="form-f span-2">
                  <label>E‘lon sarlavhasi</label>
                  <input v-model="editableForm.title" type="text" class="input-text" />
                </div>

                <!-- Price & Currency -->
                <div class="form-f">
                  <label>Narx</label>
                  <input v-model.number="editableForm.price" type="number" class="input-text font-bold" />
                </div>

                <div class="form-f">
                  <label>Valyuta</label>
                  <select v-model="editableForm.currency" class="input-text">
                    <option value="USD">USD ($)</option>
                    <option value="UZS">UZS (so‘m)</option>
                  </select>
                </div>

                <!-- Deal Type & Property Type -->
                <div class="form-f">
                  <label>Bitim turi</label>
                  <select v-model="editableForm.deal_type" class="input-text">
                    <option value="rent">🔑 Ijara (Rent)</option>
                    <option value="sale">🏷️ Sotuv (Sale)</option>
                  </select>
                </div>

                <div class="form-f">
                  <label>Mulk turi</label>
                  <select v-model="editableForm.property_type" class="input-text">
                    <option value="apartment">Kvartira</option>
                    <option value="house">Hovli / Uy</option>
                    <option value="commercial">Tijorat mulki</option>
                  </select>
                </div>

                <!-- Rooms & Area -->
                <div class="form-f">
                  <label>Xonalar soni</label>
                  <input v-model.number="editableForm.rooms" type="number" class="input-text" />
                </div>

                <div class="form-f">
                  <label>Maydoni (m²)</label>
                  <input v-model.number="editableForm.area_m2" type="number" class="input-text" />
                </div>

                <!-- Floor & Total Floors -->
                <div class="form-f">
                  <label>Qavat</label>
                  <input v-model.number="editableForm.floor" type="number" class="input-text" />
                </div>

                <div class="form-f">
                  <label>Jami qavatlar</label>
                  <input v-model.number="editableForm.total_floors" type="number" class="input-text" />
                </div>

                <!-- District & Neighborhood -->
                <div class="form-f">
                  <label>Tuman</label>
                  <select v-model="editableForm.district" class="input-text">
                    <option v-for="d in districtsList" :key="d" :value="d">{{ d }}</option>
                  </select>
                </div>

                <div class="form-f">
                  <label>Mahalla / Mo‘ljal</label>
                  <input v-model="editableForm.neighborhood" type="text" class="input-text" />
                </div>

                <!-- Address -->
                <div class="form-f span-2">
                  <label>To‘liq manzil</label>
                  <input v-model="editableForm.address" type="text" class="input-text" />
                </div>

                <!-- Contact Info -->
                <div class="form-f">
                  <label>Aloqa shaxsi</label>
                  <input v-model="editableForm.contact_name" type="text" class="input-text" />
                </div>

                <div class="form-f">
                  <label>Telefon raqam</label>
                  <input v-model="editableForm.contact_phone" type="text" class="input-text" />
                </div>

                <!-- Status -->
                <div class="form-f span-2">
                  <label>E‘lon holati (Status)</label>
                  <select v-model="editableForm.status" class="input-text">
                    <option value="active">🟢 Faol (Saytda ko‘rinadi)</option>
                    <option value="archived">⚪ Arxivlangan (Saytda ko‘rinmaydi)</option>
                    <option value="pending">🟡 Kutilmoqda</option>
                  </select>
                </div>

                <!-- Description -->
                <div class="form-f span-2">
                  <label>To‘liq tavsif</label>
                  <textarea v-model="editableForm.description" rows="8" class="textarea-input"></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.dossier-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-box {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 80px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--ad-text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--ad-border);
  border-top-color: var(--ad-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.dossier-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 14px 20px;
  box-shadow: var(--ad-shadow-sm);
  flex-wrap: wrap;
  gap: 14px;
}

.dh-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.dh-id-tag {
  font-family: var(--ad-font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--ad-text-main);
  background: var(--ad-border-subtle);
  padding: 4px 8px;
  border-radius: 4px;
}

.dh-source-tag {
  font-size: 12.5px;
  color: var(--ad-text-muted);
}

.dh-status-tag {
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
}

.st-act { background: var(--ad-success-light); color: var(--ad-success); }
.st-arc { background: var(--ad-border-subtle); color: var(--ad-text-muted); }

.dh-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.sec-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-border-subtle);
  border: 1px solid var(--ad-border);
  color: var(--ad-text-main);
  padding: 7px 14px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
}

.tg-publish-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-purple-light);
  border: 1px solid var(--ad-purple);
  color: var(--ad-purple);
  padding: 7px 14px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.save-primary-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 7px 16px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.save-primary-btn:hover:not(:disabled) {
  background: var(--ad-primary-hover);
}

.btn-icon {
  width: 15px;
  height: 15px;
}

/* Columns Grid */
.dossier-columns-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 20px;
}

.dossier-left-col, .dossier-right-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dossier-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 20px;
  box-shadow: var(--ad-shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-h4 {
  font-size: 15px;
  font-weight: 700;
  color: var(--ad-text-main);
  margin: 0;
}

.gallery-main-view {
  width: 100%;
  height: 280px;
  background: var(--ad-bg);
  border-radius: var(--ad-radius-md);
  overflow: hidden;
}

.main-gallery-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.gallery-thumbs-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.thumb-item {
  width: 58px;
  height: 58px;
  border-radius: 6px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.15s;
}

.thumb-item.active {
  border-color: var(--ad-primary);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid var(--ad-border-subtle);
}

.info-k {
  color: var(--ad-text-muted);
}

.info-v {
  color: var(--ad-text-main);
}

.text-success { color: var(--ad-success); }

/* History Timeline */
.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.history-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--ad-primary);
  margin-top: 5px;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-change {
  font-size: 12.5px;
  color: var(--ad-text-main);
}

.history-time {
  font-size: 11px;
  color: var(--ad-text-light);
}

/* Specs Form */
.specs-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.span-2 {
  grid-column: span 2;
}

.form-f {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-f label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ad-text-muted);
}

.input-text, .textarea-input {
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  background: var(--ad-bg);
  color: var(--ad-text-main);
  padding: 8px 12px;
  font-size: 13.5px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.15s;
}

.input-text:focus, .textarea-input:focus {
  border-color: var(--ad-primary);
  background: var(--ad-surface);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 992px) {
  .dossier-columns-grid {
    grid-template-columns: 1fr;
  }
}
</style>
