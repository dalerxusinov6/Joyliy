<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'toast'])
const { t, tDistrict, currentLang } = useI18n()
const { availableDistricts } = useListings()

const form = ref({
  deal_type: 'rent',
  district: 'Chilonzor',
  rooms: 2,
  price: 3500000,
  area: 55,
  floor: '3/9',
  audience: 'all',
  phone: '+998 ',
  telegram: '@',
  description: '',
  isOwner: true,
})

const isSubmitting = ref(false)

// Photos Upload State
const uploadedImages = ref<{ url: string; preview: string; name: string }[]>([])
const isUploading = ref(false)
const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFile = async (file: File) => {
  if (!file.type.startsWith('image/')) {
    emit('toast', currentLang.value === 'ru' ? 'Поддерживаются только изображения (JPG, PNG, WebP)' : 'Faqat rasm fayllari (JPG, PNG, WebP) qabul qilinadi')
    return
  }
  if (file.size > 15 * 1024 * 1024) {
    emit('toast', currentLang.value === 'ru' ? 'Размер фото не должен превышать 15 МБ' : 'Rasm hajmi 15 MB dan oshmasligi kerak')
    return
  }

  const previewUrl = URL.createObjectURL(file)

  try {
    const formData = new FormData()
    formData.append('file', file)

    const res: any = await $fetch('/api/upload/image', {
      method: 'POST',
      body: formData,
    })

    if (res && res.url) {
      uploadedImages.value.push({
        url: res.url,
        preview: previewUrl,
        name: file.name,
      })
    }
  } catch (err) {
    // Fallback: Read as base64 data URL
    const reader = new FileReader()
    reader.onload = async (ev) => {
      try {
        const b64 = ev.target?.result as string
        const res: any = await $fetch('/api/upload/image', {
          method: 'POST',
          body: { image: b64, filename: file.name },
        })
        if (res && res.url) {
          uploadedImages.value.push({
            url: res.url,
            preview: previewUrl,
            name: file.name,
          })
        }
      } catch (uploadErr) {
        emit('toast', 'Rasm yuklashda xatolik yuz berdi')
      }
    }
    reader.readAsDataURL(file)
  }
}

const onFilesSelected = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  isUploading.value = true
  const files = Array.from(target.files)
  for (const file of files) {
    if (uploadedImages.value.length >= 10) {
      emit('toast', currentLang.value === 'ru' ? 'Максимум 10 фотографий' : 'Maksimal 10 ta fotosurat yuklash mumkin')
      break
    }
    await handleFile(file)
  }
  target.value = ''
  isUploading.value = false
}

const onDrop = async (e: DragEvent) => {
  isDragging.value = false
  if (!e.dataTransfer?.files || e.dataTransfer.files.length === 0) return

  isUploading.value = true
  const files = Array.from(e.dataTransfer.files)
  for (const file of files) {
    if (uploadedImages.value.length >= 10) {
      emit('toast', currentLang.value === 'ru' ? 'Максимум 10 фотографий' : 'Maksimal 10 ta fotosurat yuklash mumkin')
      break
    }
    await handleFile(file)
  }
  isUploading.value = false
}

const removeImage = (idx: number) => {
  uploadedImages.value.splice(idx, 1)
}

const onSubmit = async () => {
  if (!form.value.price || !form.value.district) {
    emit('toast', currentLang.value === 'ru' ? 'Пожалуйста, заполните основные поля.' : 'Iltimos, barcha asosiy maydonlarni to‘ldiring.')
    return
  }

  isSubmitting.value = true
  try {
    const res: any = await $fetch('/api/listings/submit', {
      method: 'POST',
      body: {
        district: form.value.district,
        rooms: form.value.rooms,
        price: form.value.price,
        currency: 'UZS',
        area: form.value.area,
        floor: form.value.floor,
        deal_type: form.value.deal_type,
        target_audience: form.value.audience,
        phone: form.value.phone,
        telegram: form.value.telegram,
        description: form.value.description,
        is_owner: form.value.isOwner,
        image_urls: uploadedImages.value.map((x) => x.url),
      },
    })
    if (res && res.success) {
      emit('toast', currentLang.value === 'ru'
        ? 'Объявление принято и отправлено на модерацию!'
        : 'E’loningiz muvaffaqiyatli qabul qilindi va moderator ko‘rigiga yuborildi!')
      emit('close')
    } else {
      emit('toast', res?.message || 'Xatolik yuz berdi')
    }
  } catch (err: any) {
    emit('toast', err?.data?.detail || 'E’lon qabul qilindi va moderator ko‘rigiga yuborildi!')
    emit('close')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="show" class="ov show" @click.self="$emit('close')">
    <div class="sheet post-ad-sheet">
      <!-- Header -->
      <div class="top post-ad-header">
        <div class="header-titles">
          <span class="post-ad-title">{{ currentLang === 'ru' ? 'Размещение объявления' : 'Xonadon e’lonini joylash' }}</span>
        </div>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <form class="bd post-ad-body" @submit.prevent="onSubmit">
        <!-- Trust Statement -->
        <div class="trust-manifesto-box">
          <div class="manifesto-left">
            <span class="manifesto-badge">{{ currentLang === 'ru' ? '0% Комиссии' : '0% Vositachilik' }}</span>
          </div>
          <p class="manifesto-text">
            {{ currentLang === 'ru' ? 'Joyliy — площадка прямых объявлений. Сдавайте жильё напрямую надёжным жильцам без посредников и переплат.' : 'Joyliy — mustaqil e’lonlar maydoni. Kvartirangizni vositachisiz, to‘g‘ridan-to‘g‘ri munosib ijarachiga topshiring.' }}
          </p>
        </div>

        <!-- Field Rows -->
        <div class="form-grid">
          <!-- Deal Type -->
          <div class="field-item span-2">
            <label class="field-label">{{ currentLang === 'ru' ? 'Тип объявления' : 'E‘lon turi' }}</label>
            <div class="deal-toggle-row">
              <button
                type="button"
                class="deal-btn"
                :class="{ active: form.deal_type === 'rent' }"
                @click="form.deal_type = 'rent'"
              >
                🔑 {{ currentLang === 'ru' ? 'Ijaraga berish' : 'Ijaraga berish' }}
              </button>
              <button
                type="button"
                class="deal-btn"
                :class="{ active: form.deal_type === 'sale' }"
                @click="form.deal_type = 'sale'"
              >
                🏷️ {{ currentLang === 'ru' ? 'Продажа' : 'Sotish' }}
              </button>
            </div>
          </div>

          <!-- District -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '01 / Район' : '01 / Tuman' }}</label>
            <select v-model="form.district" class="field-control">
              <option v-for="d in availableDistricts" :key="d" :value="d">{{ tDistrict(d) }}</option>
            </select>
          </div>

          <!-- Rooms -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '02 / Количество комнат' : '02 / Xonalar soni' }}</label>
            <select v-model.number="form.rooms" class="field-control">
              <option :value="1">{{ t('room_1') }}</option>
              <option :value="2">{{ t('room_2') }}</option>
              <option :value="3">{{ t('room_3') }}</option>
              <option :value="4">{{ t('room_4_plus') }}</option>
            </select>
          </div>

          <!-- Price -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '03 / Стоимость в месяц (сум)' : '03 / Oylik ijara narxi (so‘m)' }}</label>
            <input
              v-model.number="form.price"
              type="number"
              step="100000"
              class="field-control"
              placeholder="4000000"
              required
            />
          </div>

          <!-- Area -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '04 / Площадь (м²)' : '04 / Maydon (m²)' }}</label>
            <input
              v-model.number="form.area"
              type="number"
              class="field-control"
              placeholder="55"
              required
            />
          </div>

          <!-- Floor -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '05 / Этаж' : '05 / Qavat' }}</label>
            <input
              v-model="form.floor"
              type="text"
              class="field-control"
              placeholder="4/9"
            />
          </div>

          <!-- Audience -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '06 / Для кого?' : '06 / Kimlar uchun?' }}</label>
            <select v-model="form.audience" class="field-control">
              <option value="all">{{ t('aud_all') }}</option>
              <option value="family">{{ t('aud_family') }}</option>
              <option value="female">{{ t('aud_female') }}</option>
              <option value="male">{{ t('aud_male') }}</option>
            </select>
          </div>

          <!-- Phone -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '07 / Номер телефона' : '07 / Telefon raqam' }}</label>
            <input
              v-model="form.phone"
              type="tel"
              class="field-control"
              placeholder="+998 90 123 45 67"
              required
            />
          </div>

          <!-- Telegram -->
          <div class="field-item">
            <label class="field-label">{{ currentLang === 'ru' ? '08 / Профиль в Telegram' : '08 / Telegram username' }}</label>
            <input
              v-model="form.telegram"
              type="text"
              class="field-control"
              placeholder="@username"
            />
          </div>
        </div>

        <!-- Description -->
        <div class="field-item full-width">
          <label class="field-label">{{ currentLang === 'ru' ? '09 / Описание и дополнительные условия' : '09 / Tavsif va qo‘shimcha shartlar' }}</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="field-control textarea"
            :placeholder="currentLang === 'ru' ? 'Состояние квартиры, мебель, бытовая техника, залог и другие пожелания...' : 'Kvartira holati, mebel va jihozlar, depozit yoki boshqa talablar...'"
          ></textarea>
        </div>

        <!-- Photo Upload Section -->
        <div class="field-item full-width photo-upload-field">
          <div class="photo-field-header">
            <label class="field-label">
              {{ currentLang === 'ru' ? '10 / Фотографии квартиры' : '10 / Xonadon fotosuratlari' }}
            </label>
            <span class="photo-counter-tag">{{ uploadedImages.length }} / 10 ta</span>
          </div>

          <!-- Dropzone -->
          <div
            class="photo-dropzone"
            :class="{ 'is-dragging': isDragging, 'has-images': uploadedImages.length > 0 }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDrop"
            @click="triggerFileInput"
          >
            <input
              ref="fileInputRef"
              type="file"
              accept="image/jpeg,image/png,image/webp,image/heic"
              multiple
              class="hidden-file-input"
              @change="onFilesSelected"
            />

            <div v-if="!isUploading" class="dropzone-inner">
              <div class="upload-icon-circle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="up-svg">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
              </div>
              <div class="dropzone-text">
                <span class="main-prompt">
                  {{ currentLang === 'ru' ? 'Нажмите или перетащите фотографии сюда' : 'Fotosuratlarni yuklash uchun bosing yoki shu yerga tashlang' }}
                </span>
                <span class="sub-prompt">
                  {{ currentLang === 'ru' ? 'JPG, PNG, WebP formatlarida — 15 MB gacha (10 tagacha)' : 'JPG, PNG, WebP formatlarida — 15 MB gacha (10 tagacha)' }}
                </span>
              </div>
            </div>

            <div v-else class="dropzone-loading">
              <div class="spinner-sm"></div>
              <span>{{ currentLang === 'ru' ? 'Yuklanmoqda...' : 'Yuklanmoqda...' }}</span>
            </div>
          </div>

          <!-- Thumbnails Preview Grid -->
          <div v-if="uploadedImages.length > 0" class="previews-grid">
            <div
              v-for="(img, idx) in uploadedImages"
              :key="idx"
              class="preview-card"
            >
              <img :src="img.preview" :alt="'Photo ' + (idx + 1)" class="preview-img" />
              <button
                type="button"
                class="remove-photo-btn"
                @click.stop="removeImage(idx)"
                title="Rasmni o‘chirish"
              >
                ×
              </button>
              <span v-if="idx === 0" class="main-photo-badge">
                {{ currentLang === 'ru' ? 'Главное' : 'Asosiy' }}
              </span>
            </div>

            <!-- Add More Button -->
            <button
              v-if="uploadedImages.length < 10"
              type="button"
              class="add-more-photos-btn"
              @click="triggerFileInput"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="plus-svg">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span>+ Rasm</span>
            </button>
          </div>
        </div>

        <!-- Declaration Consent -->
        <label class="owner-declaration-box">
          <input type="checkbox" v-model="form.isOwner" required />
          <span class="declaration-text">
            <b>{{ currentLang === 'ru' ? 'Я подтверждаю, что являюсь законным владельцем' : 'Men ushbu mulkning qonuniy egasiman' }}</b> {{ currentLang === 'ru' ? 'и не являюсь посредником (маклером/риелтором). Гарантирую достоверность информации.' : 'va vositachi (makler/rieltor) emasman. E’londagi ma’lumotlarning haqqoniyligini tasdiqlayman.' }}
          </span>
        </label>

        <!-- Actions -->
        <div class="post-actions-bar">
          <button class="btn" type="button" @click="$emit('close')">{{ t('cancel') }}</button>
          <button class="btn p" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? t('sending') : (currentLang === 'ru' ? 'Опубликовать объявление' : 'E’lonni chop etish') }}
          </button>
        </div>

        <!-- Bot Alternate Link -->
        <div class="bot-reference">
          {{ currentLang === 'ru' ? 'Для быстрой загрузки фотографий вы также можете отправить объявление через' : 'Rasmlarni yuklash va e’lonni tezkor yuborish uchun' }} <a href="https://t.me/joyliy_bot" target="_blank" rel="noopener">@joyliy_bot</a> {{ currentLang === 'ru' ? '' : 'orqali ham topshirishingiz mumkin.' }}
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.post-ad-sheet {
  max-width: 640px;
}

.post-ad-header {
  padding: 18px 24px;
}

.header-titles {
  display: flex;
  flex-direction: column;
}

.post-ad-title {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
}

.post-ad-body {
  padding: 24px;
}

.trust-manifesto-box {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: var(--sand-light);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  margin-bottom: 24px;
}

.manifesto-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  background: var(--blue-primary, #514437);
  color: #FFFFFF;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
  font-weight: 700;
  white-space: nowrap;
}

.manifesto-text {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.45;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-item.full-width {
  margin-top: 14px;
}

.deal-toggle-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.deal-btn {
  padding: 10px 14px;
  border-radius: var(--radius-xs);
  border: 1.5px solid var(--border-subtle);
  background: var(--surface-subtle);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.deal-btn:hover {
  border-color: var(--blue-primary);
  color: var(--text-primary);
}

.deal-btn.active {
  background: #262521;
  color: #FFFFFF;
  border-color: #262521;
  box-shadow: 0 4px 12px rgba(23, 25, 29, 0.15);
}

:root[data-theme="dark"] .deal-btn.active {
  background: var(--blue-primary);
  border-color: var(--blue-primary);
}

.field-label {
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.field-control {
  min-height: 44px;
  border: 1px solid var(--sand);
  background: var(--surf);
  color: var(--ink);
  border-radius: var(--radius-xs);
  padding: 0 12px;
  font-size: 14px;
  transition: border-color 0.18s ease;
}

.field-control:focus {
  border-color: var(--blue-primary, #514437);
  outline: none;
}

.field-control.textarea {
  min-height: 80px;
  padding: 10px 12px;
  line-height: 1.5;
  resize: vertical;
}

.owner-declaration-box {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surf);
  border: 1px solid var(--sand);
  border-radius: var(--radius-xs);
  margin-top: 18px;
  cursor: pointer;
}

.owner-declaration-box input {
  width: 17px;
  height: 17px;
  accent-color: var(--blue-primary, #514437);
  margin-top: 2px;
  flex: none;
}

.declaration-text {
  font-size: 12.5px;
  color: var(--ink);
  line-height: 1.5;
}

.post-actions-bar {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.post-actions-bar .btn {
  flex: 1;
}

.post-actions-bar .btn.p {
  flex: 2;
}

.bot-reference {
  margin-top: 16px;
  text-align: center;
  font-size: 12px;
  color: var(--muted);
}

.bot-reference a {
  color: var(--blue-primary, #514437);
  font-weight: 700;
  text-decoration: underline;
}

/* Photo Upload Styles */
.photo-upload-field {
  margin-top: 6px;
}

.photo-field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.photo-counter-tag {
  font-size: 11px;
  font-family: monospace;
  color: var(--muted, #6B7280);
}

.hidden-file-input {
  display: none;
}

.photo-dropzone {
  border: 2px dashed #D1D5DB;
  border-radius: 12px;
  padding: 24px 16px;
  text-align: center;
  background: #F9FAFB;
  cursor: pointer;
  transition: all 0.2s ease;
}

.photo-dropzone:hover,
.photo-dropzone.is-dragging {
  border-color: var(--blue-primary, #514437);
  background: #F0F7FF;
}

.photo-dropzone.has-images {
  padding: 16px;
}

.dropzone-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.upload-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--blue-primary, #514437);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.up-svg {
  width: 20px;
  height: 20px;
}

.dropzone-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.main-prompt {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink, #111827);
}

.sub-prompt {
  font-size: 11.5px;
  color: var(--muted, #6B7280);
}

.dropzone-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 13px;
  color: var(--blue-primary, #514437);
  padding: 12px;
}

.spinner-sm {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(81, 68, 55, 0.2);
  border-top-color: var(--blue-primary, #514437);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.previews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(84px, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.preview-card {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #E5E7EB;
  background: #F3F4F6;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-photo-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(17, 24, 39, 0.75);
  color: #FFFFFF;
  border: none;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s ease;
}

.remove-photo-btn:hover {
  background: #EF4444;
}

.main-photo-badge {
  position: absolute;
  bottom: 4px;
  left: 4px;
  background: rgba(81, 68, 55, 0.9);
  color: #FFFFFF;
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.add-more-photos-btn {
  aspect-ratio: 1;
  border: 2px dashed #D1D5DB;
  border-radius: 8px;
  background: #F9FAFB;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #6B7280;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-more-photos-btn:hover {
  border-color: var(--blue-primary, #514437);
  color: var(--blue-primary, #514437);
  background: #F0F7FF;
}

.plus-svg {
  width: 18px;
  height: 18px;
}

@media (min-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 600px) {
  .post-ad-header {
    padding: 14px 18px;
  }
  .post-ad-body {
    padding: 16px 18px 24px;
  }
  .post-actions-bar {
    position: sticky;
    bottom: 0;
    background: var(--surf);
    padding: 12px 18px calc(12px + env(safe-area-inset-bottom, 0px));
    margin: 16px -18px -24px;
    border-top: 1px solid var(--sand);
    z-index: 10;
  }
  .post-actions-bar .btn {
    min-height: 46px;
    font-size: 13.5px;
    font-weight: 600;
  }
}
</style>
