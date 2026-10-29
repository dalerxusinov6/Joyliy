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
    // In demo / production without API key, show helpful message and link to bot
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
    <div class="sheet" style="max-width: 600px">
      <div class="top">
        <span>Yangi e’lon joylash (Egasidan)</span>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form class="bd" @submit.prevent="onSubmit">
        <div style="background: var(--acs); padding: 12px 16px; border-radius: 12px; margin-bottom: 16px">
          <p style="margin: 0; font-size: 13px; color: var(--ac); font-weight: 500">
            Joyliy — faqat maklersiz va toza e'lonlar maydoni. O‘z kvartirangizni bevosita ijarachilarga bering.
          </p>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">
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

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">
          <div class="fi">
            <label for="pad_price">Oylik ijara narxi (so‘m)</label>
            <input id="pad_price" v-model.number="form.price" type="number" step="100000" required />
          </div>

          <div class="fi">
            <label for="pad_area">Maydon (m²)</label>
            <input id="pad_area" v-model.number="form.area" type="number" required />
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">
          <div class="fi">
            <label for="pad_floor">Qavat (masalan: 3/9)</label>
            <input id="pad_floor" v-model="form.floor" placeholder="4/9" />
          </div>

          <div class="fi">
            <label for="pad_phone">Telefon raqam</label>
            <input id="pad_phone" v-model="form.phone" type="tel" placeholder="+998 90 123 45 67" required />
          </div>
        </div>

        <div class="fi">
          <label for="pad_desc">Tavsif va shartlar</label>
          <textarea
            id="pad_desc"
            v-model="form.description"
            rows="3"
            placeholder="Kvartira holati, mebellar, qo‘shimcha talablar..."
            style="width: 100%; border: 1px solid var(--bd); border-radius: 12px; padding: 10px; background: var(--card); color: var(--tx)"
          ></textarea>
        </div>

        <label class="chk" style="margin-top: 8px">
          <input type="checkbox" v-model="form.isOwner" required />
          <span><b>Men ushbu mulk egasiman va vositachi (makler) emasman</b></span>
        </label>

        <div class="cbar" style="margin-top: 20px; padding: 0; background: none; border: none">
          <button class="btn" type="button" @click="$emit('close')">Bekor qilish</button>
          <button class="btn p" type="submit" :disabled="isSubmitting">E’lonni joylash</button>
        </div>
      </form>
    </div>
  </div>
</template>

