<script setup lang="ts">
import ModalShell from '~/components/ModalShell.vue'
import RoommatesPanel from '~/components/RoommatesPanel.vue'
import { useI18n } from '~/composables/useI18n'

defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'toast'])
const { t } = useI18n()
</script>

<template>
  <ModalShell :show="show" wide :title="t('roommates_tab')" @close="emit('close')">
    <RoommatesPanel @toast="(m: string) => emit('toast', m)" />
  </ModalShell>
</template>
