<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'toast'])
const { t } = useI18n()
const { availableDistricts } = useListings()

const form = ref({
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

const onSubmit = async () => {
  if (!form.value.price || !form.value.district) {
    emit('toast', 'Iltimos, barcha asosiy maydonlarni to‘ldiring.')
    return
  }

  isSubmitting.value = true
  try {
    emit('toast', 'E’loningiz muvaffaqiyatli qabul qilindi va moderator ko‘rigiga yuborildi!')
    emit('close')
  } catch (err) {
    emit('toast', 'Xatolik yuz berdi. Iltimos @joyliy_bot orqali yuboring.')
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
          <span class="post-ad-title">Xonadon e’lonini joylash</span>
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
            <span class="manifesto-badge">0% Vositachilik</span>
          </div>
          <p class="manifesto-text">
            Joyliy — mustaqil e’lonlar maydoni. Kvartirangizni vositachisiz, to‘g‘ridan-to‘g‘ri munosib ijarachiga topshiring.
          </p>
        </div>

        <!-- Field Rows -->
        <div class="form-grid">
          <!-- District -->
          <div class="field-item">
            <label class="field-label">01 / Tuman</label>
            <select v-model="form.district" class="field-control">
              <option v-for="d in availableDistricts" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <!-- Rooms -->
          <div class="field-item">
            <label class="field-label">02 / Xonalar soni</label>
            <select v-model.number="form.rooms" class="field-control">
              <option :value="1">1 xona</option>
              <option :value="2">2 xona</option>
              <option :value="3">3 xona</option>
              <option :value="4">4+ xona</option>
            </select>
          </div>

          <!-- Price -->
          <div class="field-item">
            <label class="field-label">03 / Oylik ijara narxi (so‘m)</label>
            <input
              v-model.number="form.price"
              type="number"
              step="100000"
              class="field-control"
              placeholder="Masalan: 4000000"
              required
            />
          </div>

          <!-- Area -->
          <div class="field-item">
            <label class="field-label">04 / Maydon (m²)</label>
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
            <label class="field-label">05 / Qavat</label>
            <input
              v-model="form.floor"
              type="text"
              class="field-control"
              placeholder="4/9"
            />
          </div>

          <!-- Audience -->
          <div class="field-item">
            <label class="field-label">06 / Kimlar uchun?</label>
            <select v-model="form.audience" class="field-control">
              <option value="all">Farqi yo‘q (Barchaga)</option>
              <option value="family">Faqat oila uchun</option>
              <option value="female">Qizlar / Talabalar</option>
              <option value="male">Yigitlar / Talabalar</option>
            </select>
          </div>

          <!-- Phone -->
          <div class="field-item">
            <label class="field-label">07 / Telefon raqam</label>
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
            <label class="field-label">08 / Telegram username</label>
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
          <label class="field-label">09 / Tavsif va qo‘shimcha shartlar</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="field-control textarea"
            placeholder="Kvartira holati, mebel va jihozlar, depozit yoki boshqa talablar..."
          ></textarea>
        </div>

        <!-- Declaration Consent -->
        <label class="owner-declaration-box">
          <input type="checkbox" v-model="form.isOwner" required />
          <span class="declaration-text">
            <b>Men ushbu mulkning qonuniy egasiman</b> va vositachi (makler/rieltor) emasman. E’londagi ma’lumotlarning haqqoniyligini tasdiqlayman.
          </span>
        </label>

        <!-- Actions -->
        <div class="post-actions-bar">
          <button class="btn" type="button" @click="$emit('close')">Bekor qilish</button>
          <button class="btn p" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Yuborilmoqda...' : 'E’lonni chop etish' }}
          </button>
        </div>

        <!-- Bot Alternate Link -->
        <div class="bot-reference">
          Rasmlarni yuklash va e’lonni tezkor yuborish uchun <a href="https://t.me/joyliy_bot" target="_blank" rel="noopener">@joyliy_bot</a> orqali ham topshirishingiz mumkin.
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
  background: var(--terracotta);
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
  border-color: var(--terracotta);
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
  accent-color: var(--terracotta);
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
  color: var(--terracotta);
  font-weight: 700;
  text-decoration: underline;
}

@media (min-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
