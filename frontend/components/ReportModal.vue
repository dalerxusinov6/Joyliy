<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'

const props = defineProps<{
  show: boolean
  listingId: number | null
}>()

const emit = defineEmits(['close', 'toast'])

const { t } = useI18n()

const reason = ref('PREPAYMENT_SCAM')
const details = ref('')
const isSubmitting = ref(false)

const reasonsList = computed(() => [
  { val: 'PREPAYMENT_SCAM', label: t('r_prepay') },
  { val: 'FAKE_PHOTOS', label: t('r_photos') },
  { val: 'WRONG_PRICE', label: t('r_price') },
  { val: 'BROKER_AS_OWNER', label: t('r_broker') },
  { val: 'UNREACHABLE', label: t('r_contact') },
])

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
    emit('toast', t('report_modal_title') + ': OK')
    emit('close')
    details.value = ''
  } catch (err) {
    emit('toast', 'OK')
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
          <h2 class="head-title">
            <svg class="modal-head-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
              <line x1="4" y1="22" x2="4" y2="15" />
            </svg>
            {{ t('report_modal_title') }}
          </h2>
        </div>
        <button class="close-btn" @click="$emit('close')" :aria-label="t('close')">
          <svg class="close-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="submitReport" class="modal-body">
        <p class="desc">
          {{ t('report_modal_desc', { id: listingId }) }}
        </p>

        <div class="form-group">
          <label>{{ t('report_reason_lbl') }}</label>
          <div class="radio-list">
            <label v-for="r in reasonsList" :key="r.val" class="radio-label">
              <input type="radio" v-model="reason" :value="r.val" />
              <span>{{ r.label }}</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>{{ t('report_details_lbl') }}</label>
          <textarea
            v-model="details"
            rows="3"
            :placeholder="t('report_details_placeholder')"
          ></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="cancel-btn" @click="$emit('close')">{{ t('cancel') }}</button>
          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? t('sending') : t('send_report') }}
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-head-svg {
  width: 18px;
  height: 18px;
  color: #c5221f;
  flex-shrink: 0;
}

.close-btn {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #666;
  transition: background 0.15s ease;
}

.close-btn:hover {
  background: #f0f0f0;
}

.close-svg {
  width: 18px;
  height: 18px;
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

