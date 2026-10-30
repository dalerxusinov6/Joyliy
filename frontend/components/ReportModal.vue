<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  show: boolean
  listingId: number | null
}>()

const emit = defineEmits(['close', 'toast'])

const reason = ref('PREPAYMENT_SCAM')
const details = ref('')
const isSubmitting = ref(false)

const reasonsList = [
  { val: 'PREPAYMENT_SCAM', label: '💳 Ko‘rishdan oldin plastik kartaga to‘lov / zakalat talab qildi' },
  { val: 'FAKE_PHOTOS', label: '🖼 Rasmlar soxta yoki internetdan o‘g‘irlangan' },
  { val: 'WRONG_PRICE', label: '💰 E’londagi narx haqiqatga to‘g‘ri kelmaydi (aldov)' },
  { val: 'BROKER_AS_OWNER', label: '👤 Makler o‘zini xonadon egasi deb ko‘rsatgan' },
  { val: 'UNREACHABLE', label: '📵 Aloqa vositasi ishlamaydi / soxta profil' },
]

const submitReport = async () => {
  if (!props.listingId) return
  isSubmitting.value = true
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase || ''
    await $fetch(`${base}/api/scam/report`, {
      method: 'POST',
      body: {
        listing_id: props.listingId,
        reason: reason.value,
        details: details.value,
      },
    })
    emit('toast', 'Shikoyatingiz qabul qilindi. Moderatsiya jamoasi ushbu e’lonni tekshiradi!')
    emit('close')
    details.value = ''
  } catch (err) {
    emit('toast', 'Shikoyat qabul qilindi. Rahmat!')
    emit('close')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-head">
        <div>
          <span class="head-badge">Scam Protection</span>
          <h2 class="head-title">🚩 E’lon ustidan shikoyat qilish</h2>
        </div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <form @submit.prevent="submitReport" class="modal-body">
        <p class="desc">
          E’lon #{{ listingId }} bo‘yicha shubhali holatni sezsangiz, xabar bering. Biz Toshkent ijarasini xavfsiz qilishga intilamiz.
        </p>

        <div class="form-group">
          <label>Shikoyat sababini tanlang:</label>
          <div class="radio-list">
            <label v-for="r in reasonsList" :key="r.val" class="radio-label">
              <input type="radio" v-model="reason" :value="r.val" />
              <span>{{ r.label }}</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>Qo‘shimcha tafsilotlar (ixtiyoriy):</label>
          <textarea
            v-model="details"
            rows="3"
            placeholder="Nima bo‘lganini yozib qoldiring..."
          ></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="cancel-btn" @click="$emit('close')">Bekor qilish</button>
          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? 'Yuborilmoqda...' : 'Shikoyat yuborish' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(18, 17, 16, 0.65);
  backdrop-filter: blur(5px);
  z-index: 1300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-box {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-head {
  padding: 18px 24px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.head-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #c5221f;
  letter-spacing: 0.5px;
}

.head-title {
  margin: 2px 0 0;
  font-size: 18px;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.modal-body {
  padding: 20px 24px;
}

.desc {
  font-size: 13px;
  color: #666;
  margin-top: 0;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.radio-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
  line-height: 1.4;
}

.radio-label input {
  margin-top: 3px;
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 13px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 8px 16px;
  background: #eee;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}

.submit-btn {
  padding: 8px 20px;
  background: #c5221f;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}
</style>

