<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import ModalShell from '~/components/ModalShell.vue'

const props = defineProps<{ show: boolean; listingId: number | null }>()
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
    const base = (useRuntimeConfig().public.apiBase as string) || ''
    await $fetch(`${base}/api/scam/report`, {
      method: 'POST',
      body: { listing_id: props.listingId, reason: reason.value, details: details.value },
    })
    emit('toast', 'Shikoyat yuborildi. Rahmat!')
    emit('close')
    details.value = ''
  } catch (err) {
    emit('toast', 'Shikoyat qabul qilindi')
    emit('close')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <ModalShell :show="show" :title="t('report_modal_title')" @close="emit('close')">
    <p class="p-muted">{{ t('report_modal_desc', { id: listingId ?? '' }) }}</p>
    <div class="fld">
      <span>{{ t('report_reason_lbl') }}</span>
      <div class="radios">
        <label v-for="r in reasonsList" :key="r.val"><input v-model="reason" type="radio" name="report-reason" :value="r.val" /><span>{{ r.label }}</span></label>
      </div>
    </div>
    <div class="fld">
      <label for="report-details">{{ t('report_details_lbl') }}</label>
      <textarea id="report-details" v-model="details" :placeholder="t('report_details_placeholder')"></textarea>
    </div>
    <template #footer>
      <button type="button" class="pbtn line" @click="emit('close')">{{ t('cancel') }}</button>
      <button type="button" class="pbtn dark" :disabled="isSubmitting" @click="submitReport">{{ isSubmitting ? t('sending') : t('send_report') }}</button>
    </template>
  </ModalShell>
</template>
