<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'E‘lonlar Boshqaruvi — Joyliy Admin',
})

const route = useRoute()
const router = useRouter()
const { authFetch, showToast, hasRole } = useAdminAuth()

// Filters and Pagination State
const search = ref('')
const district = ref('')
const dealType = ref('')
const rooms = ref('')
const source = ref('')
const status = ref('')
const telegramStatus = ref('')
const sortBy = ref('newest')
const page = ref(1)
const limit = ref(25)

// Data State
const isLoading = ref(true)
const listings = ref<any[]>([])
const pagination = ref({
  total: 0,
  page: 1,
  limit: 25,
  total_pages: 1,
})

// Bulk Selection
const selectedIds = ref<number[]>([])

// Create / Edit Modal State
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingItem = ref<any>(null)
const isSubmitting = ref(false)

// Delete Confirm Modal
const showDeleteConfirm = ref(false)
const deletingId = ref<number | null>(null)

// Form model
const formModel = ref({
  title: '',
  price: 500,
  currency: 'USD',
  deal_type: 'rent',
  rooms: 2,
  area_m2: 65,
  floor: 4,
  total_floors: 9,
  district: 'Chilonzor',
  address: '',
  description: '',
  contact_phone: '+998901234567',
  images: ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'],
  property_type: 'apartment',
  status: 'active',
})

const districtsList = [
  'Chilonzor', 'Yunusobod', 'Mirzo Ulug‘bek', 'Yakkasaroy', 'Mirobod',
  'Shayxontohur', 'Olmazor', 'Uchtepa', 'Yashnobod', 'Sergeli', 'Bektemir', 'Yangihayot'
]

const loadListings = async () => {
  isLoading.value = true
  try {
    const params: Record<string, any> = {
      page: page.value,
      limit: limit.value,
      sort: sortBy.value,
    }
    if (search.value.trim()) params.search = search.value.trim()
    if (district.value) params.district = district.value
    if (dealType.value) params.deal_type = dealType.value
    if (rooms.value) params.rooms = rooms.value
    if (source.value) params.source = source.value
    if (status.value) params.status = status.value
    if (telegramStatus.value) params.telegram_status = telegramStatus.value

    const queryStr = new URLSearchParams(params).toString()
    const res = await authFetch(`/api/admin/listings?${queryStr}`)
    if (res && res.success) {
      listings.value = res.items || []
      pagination.value = res.pagination || { total: 0, page: 1, limit: limit.value, total_pages: 1 }
    }
  } catch (err: any) {
    showToast('E‘lonlarni yuklashda xatolik yuz berdi', 'error')
  } finally {
    isLoading.value = false
  }
}

// Watchers for immediate filtering
let searchTimeout: any = null
watch(search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadListings()
  }, 350)
})

watch([district, dealType, rooms, source, status, telegramStatus, sortBy, limit], () => {
  page.value = 1
  loadListings()
})

watch(page, () => {
  loadListings()
})

onMounted(() => {
  if (route.query.action === 'new') {
    showCreateModal.value = true
  }
  loadListings()
})

// Bulk actions
const toggleSelectAll = () => {
  if (selectedIds.value.length === listings.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = listings.value.map((l) => l.id)
  }
}

const toggleSelectOne = (id: number) => {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((i) => i !== id)
  } else {
    selectedIds.value.push(id)
  }
}

const handleBulkAction = async (action: 'archive' | 'restore' | 'delete') => {
  if (!selectedIds.value.length) return
  if (action === 'delete' && !confirm(`${selectedIds.value.length} ta e‘lonni o‘chirishni tasdiqlaysizmi?`)) {
    return
  }
  try {
    const res = await authFetch('/api/admin/listings/bulk', {
      method: 'POST',
      body: {
        action,
        listing_ids: selectedIds.value,
      },
    })
    if (res && res.success) {
      showToast(res.message || 'Amal muvaffaqiyatli bajarildi', 'success')
      selectedIds.value = []
      await loadListings()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Xatolik yuz berdi', 'error')
  }
}

// Publish to Telegram
const publishToTelegram = async (id: number) => {
  try {
    showToast('Telegramga yuborilmoqda...', 'info')
    const res = await authFetch(`/api/admin/telegram/publish/${id}`, {
      method: 'POST',
    })
    if (res && res.success) {
      showToast('E‘lon Telegram kanalga muvaffaqiyatli post qilindi!', 'success')
      await loadListings()
    } else {
      showToast(res?.message || 'Yuborish amalga oshmadi', 'warning')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Telegramga yuborishda xatolik', 'error')
  }
}

// Open Edit modal
const openEditModal = (item: any) => {
  editingItem.value = item
  formModel.value = {
    title: item.title,
    price: item.price,
    currency: item.currency || 'USD',
    deal_type: item.deal_type || 'rent',
    rooms: item.rooms || 1,
    area_m2: item.area_m2 || 50,
    floor: item.floor || 1,
    total_floors: item.total_floors || 9,
    district: item.district || 'Chilonzor',
    address: item.address || '',
    description: item.description || '',
    contact_phone: item.contact_phone || '',
    images: item.images && item.images.length ? item.images : ['/placeholder.png'],
    property_type: item.property_type || 'apartment',
    status: item.status || 'active',
  }
  showEditModal.value = true
}

// Save Edit
const saveListingEdit = async () => {
  if (!editingItem.value) return
  isSubmitting.value = true
  try {
    const res = await authFetch(`/api/admin/listings/${editingItem.value.id}`, {
      method: 'PUT',
      body: formModel.value,
    })
    if (res && res.success) {
      showToast('E‘lon muvaffaqiyatli tahrirlandi!', 'success')
      showEditModal.value = false
      await loadListings()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Saqlashda xatolik yuz berdi', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Create Manual Listing
const handleCreateListing = async () => {
  isSubmitting.value = true
  try {
    const res = await authFetch('/api/admin/listings', {
      method: 'POST',
      body: formModel.value,
    })
    if (res && res.success) {
      showToast('Yangi e‘lon muvaffaqiyatli yaratildi!', 'success')
      showCreateModal.value = false
      await loadListings()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Yaratishda xatolik yuz berdi', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Delete Single
const confirmDeleteSingle = (id: number) => {
  deletingId.value = id
  showDeleteConfirm.value = true
}

const executeDelete = async () => {
  if (!deletingId.value) return
  try {
    const res = await authFetch(`/api/admin/listings/${deletingId.value}`, {
      method: 'DELETE',
    })
    if (res && res.success) {
      showToast('E‘lon butunlay o‘chirildi', 'success')
      showDeleteConfirm.value = false
      deletingId.value = null
      await loadListings()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'O‘chirishda xatolik', 'error')
  }
}

const formatPrice = (price: number = 0, currency: string = 'USD') => {
  const sym = currency === 'USD' ? '$' : 'so‘m'
  return `${new Intl.NumberFormat('uz-UZ').format(price)} ${sym}`
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <AdminShell title="E‘lonlar bazasi">
    <div class="listings-page">
      <!-- Title & Actions Bar -->
      <div class="page-header-row">
        <div>
          <h1 class="page-title">E‘lonlar Boshqaruvi</h1>
          <p class="page-sub">Joyliy platformasidagi barcha aktiv, arxivlangan va yangi topilgan kvartiralar</p>
        </div>

        <div class="header-btns">
          <button class="primary-btn" @click="showCreateModal = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-i">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Yangi e‘lon qo‘shish
          </button>
        </div>
      </div>

      <!-- Filters Toolbar Card -->
      <div class="filters-card">
        <!-- Search Row -->
        <div class="search-bar-row">
          <div class="search-input-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-i">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              v-model="search"
              type="text"
              placeholder="Sarlavha, manzil, ID yoki URL bo‘yicha qidirish..."
              class="search-input"
            />
            <button v-if="search" class="clear-search-btn" @click="search = ''">×</button>
          </div>
        </div>

        <!-- Filter Selects Grid -->
        <div class="filter-selects-grid">
          <!-- District -->
          <div class="filter-group">
            <label class="fg-label">Tuman</label>
            <select v-model="district" class="fg-select">
              <option value="">Barcha tumanlar</option>
              <option v-for="d in districtsList" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <!-- Deal Type (Rent / Sale) -->
          <div class="filter-group">
            <label class="fg-label">Bitim turi</label>
            <select v-model="dealType" class="fg-select">
              <option value="">Barchasi</option>
              <option value="rent">🔑 Ijara (Rent)</option>
              <option value="sale">🏷️ Sotuv (Sale)</option>
            </select>
          </div>

          <!-- Room Count -->
          <div class="filter-group">
            <label class="fg-label">Xonalar</label>
            <select v-model="rooms" class="fg-select">
              <option value="">Ixtiyoriy</option>
              <option value="1">1 xona</option>
              <option value="2">2 xona</option>
              <option value="3">3 xona</option>
              <option value="4">4+ xona</option>
            </select>
          </div>

          <!-- Source -->
          <div class="filter-group">
            <label class="fg-label">Manba</label>
            <select v-model="source" class="fg-select">
              <option value="">Barcha manbalar</option>
              <option value="olx">OLX.uz</option>
              <option value="manual">Qo‘lda kiritilgan</option>
              <option value="telegram">Telegram</option>
            </select>
          </div>

          <!-- Status -->
          <div class="filter-group">
            <label class="fg-label">Holati</label>
            <select v-model="status" class="fg-select">
              <option value="">Barchasi</option>
              <option value="active">🟢 Faol</option>
              <option value="archived">⚪ Arxivlangan</option>
              <option value="pending">🟡 Kutilmoqda</option>
            </select>
          </div>

          <!-- Telegram Status -->
          <div class="filter-group">
            <label class="fg-label">Telegram nashr</label>
            <select v-model="telegramStatus" class="fg-select">
              <option value="">Barchasi</option>
              <option value="published">✅ Nashr qilingan</option>
              <option value="pending">⏳ Kutilmoqda</option>
              <option value="failed">❌ Xatolik</option>
            </select>
          </div>

          <!-- Sort -->
          <div class="filter-group">
            <label class="fg-label">Saralash</label>
            <select v-model="sortBy" class="fg-select">
              <option value="newest">Eng yangi</option>
              <option value="oldest">Eng eski</option>
              <option value="price_asc">Arzonroq</option>
              <option value="price_desc">Qimmatroq</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Bulk Actions Bar -->
      <div v-if="selectedIds.length > 0" class="bulk-actions-bar">
        <span class="bulk-count"><strong>{{ selectedIds.length }}</strong> ta e‘lon tanlandi</span>
        <div class="bulk-btns">
          <button class="bulk-btn" @click="handleBulkAction('archive')">Arxivlash</button>
          <button class="bulk-btn" @click="handleBulkAction('restore')">Faollashtirish</button>
          <button class="bulk-btn danger" @click="handleBulkAction('delete')">O‘chirish</button>
        </div>
      </div>

      <!-- Listings Table Card -->
      <div class="table-card">
        <div class="table-responsive">
          <table class="ad-table">
            <thead>
              <tr>
                <th class="th-cb">
                  <input
                    type="checkbox"
                    :checked="listings.length > 0 && selectedIds.length === listings.length"
                    @change="toggleSelectAll"
                  />
                </th>
                <th>Rasm</th>
                <th>E‘lon sarlavhasi</th>
                <th>Narx</th>
                <th>Turi</th>
                <th>Tuman / Manzil</th>
                <th>Manba</th>
                <th>Status</th>
                <th>Telegram</th>
                <th>Sana</th>
                <th class="text-right">Amallar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in listings" :key="item.id" :class="{ 'row-selected': selectedIds.includes(item.id) }">
                <td class="td-cb">
                  <input
                    type="checkbox"
                    :checked="selectedIds.includes(item.id)"
                    @change="toggleSelectOne(item.id)"
                  />
                </td>
                <td>
                  <img
                    :src="item.image_url || '/placeholder.png'"
                    class="listing-thumb"
                    alt="Rasm"
                    loading="lazy"
                    onerror="this.src='/placeholder.png'"
                  />
                </td>
                <td>
                  <div class="listing-info-col">
                    <NuxtLink :to="`/admin/listings/${item.id}`" class="listing-title">
                      {{ item.title }}
                    </NuxtLink>
                    <span class="listing-specs">
                      {{ item.rooms }} xona • {{ item.area_m2 || '-' }} m² • {{ item.floor || '-' }}/{{ item.total_floors || '-' }}-qavat
                    </span>
                  </div>
                </td>
                <td class="font-mono font-bold text-nowrap">
                  {{ formatPrice(item.price, item.currency) }}
                </td>
                <td>
                  <span class="deal-badge" :class="item.deal_type === 'sale' ? 'badge-sale' : 'badge-rent'">
                    {{ item.deal_type === 'sale' ? 'Sotuv' : 'Ijara' }}
                  </span>
                </td>
                <td>
                  <div class="loc-col">
                    <span class="district-pill">{{ item.district }}</span>
                    <span v-if="item.neighborhood" class="sub-neighborhood">{{ item.neighborhood }}</span>
                  </div>
                </td>
                <td>
                  <span class="source-badge">{{ item.source }}</span>
                </td>
                <td>
                  <span class="status-pill" :class="item.status === 'active' ? 'st-active' : 'st-archived'">
                    {{ item.status === 'active' ? 'Faol' : 'Arxiv' }}
                  </span>
                </td>
                <td>
                  <span class="tg-pill" :class="item.telegram_status === 'published' ? 'tg-yes' : 'tg-no'">
                    {{ item.telegram_status === 'published' ? '✓ Post' : 'Navbat' }}
                  </span>
                </td>
                <td class="text-xs text-muted text-nowrap">
                  {{ formatDate(item.created_at) }}
                </td>
                <td class="text-right text-nowrap">
                  <div class="row-actions">
                    <!-- Dossier Link -->
                    <NuxtLink :to="`/admin/listings/${item.id}`" class="act-btn" title="Batafsil">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    </NuxtLink>

                    <!-- Quick Edit -->
                    <button class="act-btn" @click="openEditModal(item)" title="Tahrirlash">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>

                    <!-- Publish to TG -->
                    <button class="act-btn tg-btn" @click="publishToTelegram(item.id)" title="Telegramga chiqarish">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="22" y1="2" x2="11" y2="13"/>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                      </svg>
                    </button>

                    <!-- Delete -->
                    <button class="act-btn del-btn" @click="confirmDeleteSingle(item.id)" title="O‘chirish">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="!listings.length && !isLoading">
                <td colspan="11" class="empty-state-cell">
                  <div class="empty-box">
                    <p>Hech qanday e‘lon topilmadi</p>
                    <button class="bulk-btn" @click="search = ''; district = ''; dealType = ''; rooms = '';">
                      Filtrlarni tozalash
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Controls -->
        <div class="pagination-footer">
          <div class="pagination-info">
            Jami <strong>{{ pagination.total }}</strong> ta e‘lon (Sahifa {{ pagination.page }} / {{ pagination.total_pages }})
          </div>

          <div class="pagination-controls">
            <div class="page-size-selector">
              <span>Sahifada:</span>
              <select v-model="limit" class="page-size-select">
                <option :value="10">10</option>
                <option :value="25">25</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>

            <div class="page-nav-btns">
              <button
                class="page-nav-btn"
                :disabled="page <= 1"
                @click="page = 1"
                title="Birinchi sahifa"
              >
                «
              </button>
              <button
                class="page-nav-btn"
                :disabled="page <= 1"
                @click="page--"
                title="Oldingi"
              >
                ‹
              </button>
              <span class="current-page-num">{{ page }}</span>
              <button
                class="page-nav-btn"
                :disabled="page >= pagination.total_pages"
                @click="page++"
                title="Keyingi"
              >
                ›
              </button>
              <button
                class="page-nav-btn"
                :disabled="page >= pagination.total_pages"
                @click="page = pagination.total_pages"
                title="Oxirgi sahifa"
              >
                »
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- CREATE / EDIT MODAL -->
      <div v-if="showCreateModal || showEditModal" class="ad-modal-backdrop" @click.self="showCreateModal = false; showEditModal = false;">
        <div class="ad-modal-card">
          <div class="ad-modal-header">
            <h3 class="modal-h3">{{ showCreateModal ? 'Yangi E‘lon Qo‘shish' : 'E‘lonni Tahrirlash' }}</h3>
            <button class="modal-close-x" @click="showCreateModal = false; showEditModal = false;">×</button>
          </div>

          <form @submit.prevent="showCreateModal ? handleCreateListing() : saveListingEdit()" class="ad-modal-form">
            <div class="form-grid-2">
              <div class="f-field span-2">
                <label>Sarlavha</label>
                <input v-model="formModel.title" type="text" required class="f-input" />
              </div>

              <div class="f-field">
                <label>Narx</label>
                <input v-model.number="formModel.price" type="number" required class="f-input" />
              </div>

              <div class="f-field">
                <label>Valyuta</label>
                <select v-model="formModel.currency" class="f-input">
                  <option value="USD">USD ($)</option>
                  <option value="UZS">UZS (so‘m)</option>
                </select>
              </div>

              <div class="f-field">
                <label>Bitim turi</label>
                <select v-model="formModel.deal_type" class="f-input">
                  <option value="rent">Ijara (Rent)</option>
                  <option value="sale">Sotuv (Sale)</option>
                </select>
              </div>

              <div class="f-field">
                <label>Xonalar soni</label>
                <input v-model.number="formModel.rooms" type="number" min="1" max="10" required class="f-input" />
              </div>

              <div class="f-field">
                <label>Maydoni (m²)</label>
                <input v-model.number="formModel.area_m2" type="number" class="f-input" />
              </div>

              <div class="f-field">
                <label>Qavat / Jami qavat</label>
                <div class="flex-row gap-2">
                  <input v-model.number="formModel.floor" type="number" placeholder="Qavat" class="f-input" />
                  <input v-model.number="formModel.total_floors" type="number" placeholder="Jami" class="f-input" />
                </div>
              </div>

              <div class="f-field">
                <label>Tuman</label>
                <select v-model="formModel.district" class="f-input" required>
                  <option v-for="d in districtsList" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>

              <div class="f-field">
                <label>Aloqa telefoni</label>
                <input v-model="formModel.contact_phone" type="text" placeholder="+998..." class="f-input" />
              </div>

              <div class="f-field span-2">
                <label>To‘liq manzil</label>
                <input v-model="formModel.address" type="text" placeholder="Ko‘cha, uy..." class="f-input" />
              </div>

              <div class="f-field span-2">
                <label>Batafsil tavsif</label>
                <textarea v-model="formModel.description" rows="3" class="f-textarea"></textarea>
              </div>
            </div>

            <div class="modal-footer-btns">
              <button type="button" class="btn-cancel" @click="showCreateModal = false; showEditModal = false;">Bekor qilish</button>
              <button type="submit" class="btn-save" :disabled="isSubmitting">
                {{ isSubmitting ? 'Saqlanmoqda...' : 'Saqlash' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- DELETE CONFIRM MODAL -->
      <div v-if="showDeleteConfirm" class="ad-modal-backdrop" @click.self="showDeleteConfirm = false">
        <div class="ad-modal-card small-modal">
          <div class="ad-modal-header">
            <h3 class="modal-h3 text-danger">E‘lonni o‘chirish</h3>
            <button class="modal-close-x" @click="showDeleteConfirm = false">×</button>
          </div>
          <div class="ad-modal-body">
            <p>Haqiqatan ham ushbu e‘lonni butunlay o‘chirib tashlamoqchimisiz? Ushbu amal qaytarib bo‘lmaydi.</p>
          </div>
          <div class="modal-footer-btns">
            <button class="btn-cancel" @click="showDeleteConfirm = false">Bekor qilish</button>
            <button class="btn-delete" @click="executeDelete">Ha, o‘chirilsin</button>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.listings-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--ad-text-main);
  margin: 0;
  letter-spacing: -0.4px;
}

.page-sub {
  font-size: 13.5px;
  color: var(--ad-text-muted);
  margin-top: 2px;
}

.primary-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: var(--ad-radius-md);
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.primary-btn:hover {
  background: var(--ad-primary-hover);
}

.btn-i {
  width: 16px;
  height: 16px;
}

/* Filters Card */
.filters-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: var(--ad-shadow-sm);
}

.search-input-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-i {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: var(--ad-text-light);
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 36px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  background: var(--ad-bg);
  color: var(--ad-text-main);
  font-size: 13.5px;
  outline: none;
  transition: all 0.15s;
}

.search-input:focus {
  background: var(--ad-surface);
  border-color: var(--ad-primary);
}

.clear-search-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  font-size: 18px;
  color: var(--ad-text-muted);
  cursor: pointer;
}

.filter-selects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.fg-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--ad-text-muted);
  text-transform: uppercase;
}

.fg-select {
  height: 34px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-sm);
  background: var(--ad-bg);
  color: var(--ad-text-main);
  padding: 0 8px;
  font-size: 12.5px;
  outline: none;
}

.fg-select:focus {
  border-color: var(--ad-primary);
}

/* Bulk Bar */
.bulk-actions-bar {
  background: var(--ad-primary-light);
  border: 1px solid var(--ad-primary);
  border-radius: var(--ad-radius-md);
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.bulk-count {
  font-size: 13.5px;
  color: var(--ad-primary);
}

.bulk-btns {
  display: flex;
  gap: 8px;
}

.bulk-btn {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-sm);
  padding: 5px 12px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}

.bulk-btn.danger {
  color: var(--ad-danger);
  border-color: var(--ad-danger);
}

/* Table Card */
.table-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  box-shadow: var(--ad-shadow-sm);
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.ad-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.ad-table th {
  padding: 12px 14px;
  background: var(--ad-bg);
  color: var(--ad-text-muted);
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  border-bottom: 1px solid var(--ad-border);
}

.ad-table td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--ad-border-subtle);
  vertical-align: middle;
}

.row-selected {
  background: var(--ad-primary-light);
}

.listing-thumb {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  background: var(--ad-border);
}

.listing-info-col {
  display: flex;
  flex-direction: column;
  max-width: 260px;
}

.listing-title {
  font-weight: 600;
  color: var(--ad-text-main);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.listing-title:hover {
  color: var(--ad-primary);
}

.listing-specs {
  font-size: 11.5px;
  color: var(--ad-text-muted);
}

.deal-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
}

.badge-rent { background: var(--ad-primary-light); color: var(--ad-primary); }
.badge-sale { background: var(--ad-purple-light); color: var(--ad-purple); }

.district-pill {
  font-size: 12px;
  font-weight: 500;
  color: var(--ad-text-main);
}

.sub-neighborhood {
  font-size: 10.5px;
  color: var(--ad-text-muted);
}

.source-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--ad-text-muted);
  text-transform: uppercase;
}

.status-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
}

.st-active { background: var(--ad-success-light); color: var(--ad-success); }
.st-archived { background: var(--ad-border-subtle); color: var(--ad-text-muted); }

.tg-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
}

.tg-yes { background: var(--ad-purple-light); color: var(--ad-purple); }
.tg-no { background: var(--ad-border-subtle); color: var(--ad-text-muted); }

.row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

.act-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--ad-border);
  background: var(--ad-surface);
  color: var(--ad-text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
}

.act-btn:hover {
  background: var(--ad-primary-light);
  color: var(--ad-primary);
  border-color: var(--ad-primary);
}

.act-btn.tg-btn:hover {
  background: var(--ad-purple-light);
  color: var(--ad-purple);
  border-color: var(--ad-purple);
}

.act-btn.del-btn:hover {
  background: var(--ad-danger-light);
  color: var(--ad-danger);
  border-color: var(--ad-danger);
}

.act-btn svg {
  width: 14px;
  height: 14px;
}

/* Pagination */
.pagination-footer {
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--ad-border);
}

.pagination-info {
  font-size: 13px;
  color: var(--ad-text-muted);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--ad-text-muted);
}

.page-size-select {
  height: 30px;
  border: 1px solid var(--ad-border);
  border-radius: 4px;
  background: var(--ad-bg);
  color: var(--ad-text-main);
  font-size: 12px;
  padding: 0 4px;
}

.page-nav-btns {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-nav-btn {
  width: 28px;
  height: 28px;
  border: 1px solid var(--ad-border);
  background: var(--ad-surface);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--ad-text-main);
  font-size: 13px;
}

.page-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.current-page-num {
  padding: 0 8px;
  font-weight: 700;
  font-size: 13px;
  color: var(--ad-primary);
}

/* Modal */
.ad-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.ad-modal-card {
  width: 640px;
  max-width: 95vw;
  max-height: 90vh;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  box-shadow: var(--ad-shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ad-modal-card.small-modal {
  width: 420px;
}

.ad-modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--ad-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--ad-text-main);
}

.modal-close-x {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--ad-text-muted);
  cursor: pointer;
}

.ad-modal-form {
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.span-2 {
  grid-column: span 2;
}

.f-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.f-field label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ad-text-muted);
}

.f-input, .f-textarea {
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-sm);
  background: var(--ad-bg);
  color: var(--ad-text-main);
  padding: 8px 10px;
  font-size: 13px;
  outline: none;
}

.f-input:focus, .f-textarea:focus {
  border-color: var(--ad-primary);
  background: var(--ad-surface);
}

.modal-footer-btns {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid var(--ad-border);
}

.btn-cancel {
  background: var(--ad-bg);
  border: 1px solid var(--ad-border);
  padding: 7px 14px;
  border-radius: var(--ad-radius-sm);
  font-size: 13px;
  cursor: pointer;
  color: var(--ad-text-main);
}

.btn-save {
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 7px 18px;
  border-radius: var(--ad-radius-sm);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.btn-delete {
  background: var(--ad-danger);
  color: #fff;
  border: none;
  padding: 7px 18px;
  border-radius: var(--ad-radius-sm);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.ad-modal-body {
  padding: 20px;
  font-size: 14px;
  color: var(--ad-text-main);
  line-height: 1.5;
}
</style>
