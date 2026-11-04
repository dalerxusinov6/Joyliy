<script setup lang="ts">
import ModalShell from '~/components/ModalShell.vue'
import DistrictMap from '~/components/DistrictMap.vue'
import { useI18n } from '~/composables/useI18n'
import { useModals } from '~/composables/useModals'

defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'select'])
const { t } = useI18n()
const { showNeighborhoods } = useModals()
const guide = () => { emit('close'); showNeighborhoods.value = true }
</script>

<template>
  <ModalShell :show="show" wide :title="t('map')" @close="emit('close')">
    <DistrictMap @select="(l: any) => { emit('close'); emit('select', l) }" @guide="guide" />
  </ModalShell>
</template>
