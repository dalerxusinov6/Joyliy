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
    <div class="sheet saved-sheet">
      <!-- Header -->
      <div class="top saved-header">
        <div class="header-left">
          <span class="saved-title">Saqlangan uylar ({{ savedListings.length }})</span>
        </div>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <div class="bd saved-body">
        <div v-if="savedListings.length" class="grid saved-grid">
          <ListingCard
            v-for="item in savedListings"
            :key="item.id"
            :listing="item"
            @select="$emit('select', item)"
          />
        </div>

        <!-- Empty Monograph State -->
        <div v-else class="saved-empty-box">
          <span class="numeral-accent">00</span>
          <h3 class="empty-title">Kolleksiya hali bo‘sh</h3>
          <p class="empty-desc">
            O‘zingizga ma’qul kelgan xonadonlarni belgilab qo‘ying va keyinroq solishtirish uchun shu yerda saqlang.
          </p>
          <button class="btn p" type="button" @click="$emit('close')">
            Katalogga qaytish
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.saved-sheet {
  max-width: 880px;
}

.saved-header {
  padding: 18px 24px;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.saved-title {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
}

.saved-body {
  padding: 24px;
}

.saved-grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.saved-empty-box {
  text-align: center;
  padding: 64px 20px;
  border: 1px dashed var(--sand);
  border-radius: var(--radius-xs);
  background: var(--surf);
}

.empty-title {
  font-family: var(--font-serif);
  font-size: 22px;
  margin: 12px 0 8px;
}

.empty-desc {
  font-size: 14.5px;
  color: var(--muted);
  max-width: 440px;
  margin: 0 auto 24px;
  line-height: 1.6;
}
</style>
