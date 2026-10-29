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
    emit('toast', 'Iltimos, barcha maydonlarni to‘ldiring.')
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
      <!-- Top Bar -->
      <div class="top post-ad-header">
        <div class="header-text">
          <span class="post-title">E’lon berish (Uy egalari uchun)</span>
          <span class="post-subtitle">Vositachilarsiz bevosita ijarachilarga yetkazing</span>
        </div>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form class="bd post-ad-body" @submit.prevent="onSubmit">
        <!-- Trust Banner -->
        <div class="post-trust-banner">
          <svg class="i banner-icon" viewBox="0 0 24 24">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          <div class="banner-text">
            <b>100% Maklersiz kafolati:</b> Joyliy faqat uy egalarining e’lonlarini qabul qiladi. E’lon joylash to‘liq bepul.
          </div>
        </div>

        <!-- Row 1: District & Rooms -->
        <div class="form-row">
          <div class="fi">
            <label for="pad_district">Tuman</label>
            <select id="pad_district" v-model="form.district">
              <option v-for="d in availableDistricts" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <div class="fi">
            <label for="pad_rooms">Xonalar soni</label>
            <select id="pad_rooms" v-model.number="form.rooms">
              <option :value="1">1 xona</option>
              <option :value="2">2 xona</option>
              <option :value="3">3 xona</option>
              <option :value="4">4+ xona</option>
            </select>
          </div>
        </div>

        <!-- Row 2: Price & Area -->
        <div class="form-row">
          <div class="fi">
            <label for="pad_price">Oylik ijara narxi (so‘m)</label>
            <input id="pad_price" v-model.number="form.price" type="number" step="100000" placeholder="Masalan: 4000000" required />
          </div>

          <div class="fi">
            <label for="pad_area">Maydon (m²)</label>
            <input id="pad_area" v-model.number="form.area" type="number" placeholder="55" required />
          </div>
        </div>

        <!-- Row 3: Floor & Target Audience -->
        <div class="form-row">
          <div class="fi">
            <label for="pad_floor">Qavat (masalan: 3/9)</label>
            <input id="pad_floor" v-model="form.floor" placeholder="4/9" />
          </div>

          <div class="fi">
            <label for="pad_aud">Kimlar uchun mo‘ljallangan?</label>
            <select id="pad_aud" v-model="form.audience">
              <option value="all">🌐 Farqi yo‘q (Barchaga)</option>
              <option value="family">👨‍👩‍👧 Faqat oila uchun</option>
              <option value="female">👩 Qizlar / Talabalar</option>
              <option value="male">👨 Yigitlar / Talabalar</option>
            </select>
          </div>
        </div>

        <!-- Row 4: Contacts -->
        <div class="form-row">
          <div class="fi">
            <label for="pad_phone">Telefon raqam</label>
            <input id="pad_phone" v-model="form.phone" type="tel" placeholder="+998 90 123 45 67" required />
          </div>

          <div class="fi">
            <label for="pad_telegram">Telegram username</label>
            <input id="pad_telegram" v-model="form.telegram" placeholder="@username" />
          </div>
        </div>

        <!-- Description -->
        <div class="fi">
          <label for="pad_desc">Tavsif va shartlar</label>
          <textarea
            id="pad_desc"
            v-model="form.description"
            rows="3"
            placeholder="Kvartira ta’miri, mavjud texnikalar, depozit yoki boshqa shartlar..."
          ></textarea>
        </div>

        <!-- Confirmation Checkbox -->
        <label class="owner-consent-chk">
          <input type="checkbox" v-model="form.isOwner" required />
          <span class="consent-text">
            <b>Men ushbu mulk egasiman</b> va vositachi (makler/rieltor) emasman. Soxta ma’lumot berilsa e’lon o‘chirilishiga roziman.
          </span>
        </label>

        <!-- Submit Actions -->
        <div class="post-actions">
          <button class="btn" type="button" @click="$emit('close')">Bekor qilish</button>
          <button class="btn p" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Yuborilmoqda...' : 'E’lonni joylashtirish' }}
          </button>
        </div>

        <!-- Telegram Bot Alternative Hint -->
        <div class="bot-alt-hint">
          E’loningizni fotosuratlar bilan birga to‘g‘ridan-to‘g‘ri <a href="https://t.me/joyliy_bot" target="_blank" rel="noopener">@joyliy_bot</a> orqali ham tez va oson yuborishingiz mumkin.
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.post-ad-sheet {
  max-width: 620px;
}

.post-ad-header {
  padding: 18px 24px;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.post-title {
  font-size: 17px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.post-subtitle {
  font-size: 12px;
  color: var(--tx-muted);
}

.post-ad-body {
  padding: 24px;
}

.post-trust-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--mint-subtle);
  border: 1px solid rgba(23, 77, 58, 0.15);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  margin-bottom: 20px;
}

.banner-icon {
  width: 22px;
  height: 22px;
  color: var(--ac);
  flex: none;
}

.banner-text {
  font-size: 13px;
  color: var(--ac-dark);
  line-height: 1.45;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.owner-consent-chk {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 16px;
  background: var(--surf);
  border: 1px solid var(--bd);
  border-radius: var(--radius-md);
  margin-top: 10px;
  cursor: pointer;
}

.owner-consent-chk input {
  width: 18px;
  height: 18px;
  accent-color: var(--ac);
  margin-top: 2px;
  flex: none;
}

.consent-text {
  font-size: 13px;
  color: var(--tx);
  line-height: 1.45;
}

.post-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.post-actions .btn {
  flex: 1;
}

.post-actions .btn.p {
  flex: 2;
  background: var(--ac);
  color: #FFFFFF;
}

.bot-alt-hint {
  text-align: center;
  font-size: 12px;
  color: var(--tx-muted);
  margin-top: 16px;
  line-height: 1.5;
}

.bot-alt-hint a {
  color: var(--ac);
  font-weight: 700;
  text-decoration: underline;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
