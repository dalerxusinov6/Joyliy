<script setup lang="ts">
import type { ListingItem } from '~/composables/useListings'
import { useListings } from '~/composables/useListings'
import ListingDetail from '~/components/ListingDetail.vue'

defineProps<{ listing: ListingItem | null }>()
const emit = defineEmits(['close', 'toast'])
const { selectedListing } = useListings()
</script>

<template>
  <ListingDetail
    v-if="listing"
    :key="listing.id"
    :listing="listing"
    @close="emit('close')"
    @toast="(m: string) => emit('toast', m)"
    @select="(l: ListingItem) => (selectedListing = l)"
  />
</template>
