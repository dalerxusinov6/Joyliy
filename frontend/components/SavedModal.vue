<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useFavorites } from '~/composables/useFavorites'
import { useListings, type ListingItem } from '~/composables/useListings'
import ListingCard from '~/components/ListingCard.vue'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'select'])
const { t } = useI18n()
const { favorites } = useFavorites()
const { listings } = useListings()

const savedListings = computed(() => {
  return listings.value.filter((l) => favorites.value.includes(l.id))
})
</script>

<template>
  <div v-if="show" class="ov show" @click.self="$emit('close')">
    <div class="sheet" style="max-width: 800px">
      <div class="top">
        <span>{{ t('saved') }} ({{ savedListings.length }})</span>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="bd">
        <div v-if="savedListings.length" class="grid" style="grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))">
          <ListingCard
            v-for="item in savedListings"
            :key="item.id"
            :listing="item"
            @select="$emit('select', item)"
          />
        </div>
        <div v-else class="empty">
          <svg class="i" style="width: 48px; height: 48px; margin-bottom: 8px; color: var(--mu)" viewBox="0 0 24 24">
            <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
          </svg>
          <p>{{ t('no_saved') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

