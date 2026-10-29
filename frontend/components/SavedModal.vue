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
        <div class="header-text">
          <span class="saved-title">{{ t('saved') }}</span>
          <span class="saved-count-pill">{{ savedListings.length }} ta e’lon</span>
        </div>
        <button class="ib" @click="$emit('close')" :aria-label="t('close')">
          <svg class="i" viewBox="0 0 24 24">
            <path d="M18 6 6 18M6 6l12 12" />
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

        <!-- Empty State -->
        <div v-else class="empty saved-empty">
          <div class="empty-icon-box">
            <svg class="i empty-heart-icon" viewBox="0 0 24 24">
              <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" />
            </svg>
          </div>
          <h3>{{ t('no_saved') }}</h3>
          <p class="empty-sub">
            O‘zingizga yoqqan kvartiralarni yurakcha belgisini bosib saqlab qo‘ying va keyinroq oson solishtiring.
          </p>
          <button class="btn p" type="button" @click="$emit('close')">
            E’lonlarni ko‘rish
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

.header-text {
  display: flex;
  align-items: center;
  gap: 10px;
}

.saved-title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.saved-count-pill {
  background: var(--mint-subtle);
  color: var(--ac);
  border: 1px solid rgba(23, 77, 58, 0.15);
  font-size: 12px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.saved-body {
  padding: 24px;
}

.saved-grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.saved-empty {
  padding: 56px 24px;
  max-width: 440px;
  margin: 20px auto;
  border-radius: var(--radius-xl);
}

.empty-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--surf-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.empty-heart-icon {
  width: 28px;
  height: 28px;
  color: var(--tx-muted);
}

.saved-empty h3 {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 700;
}

.empty-sub {
  font-size: 14px;
  color: var(--tx-muted);
  line-height: 1.55;
  margin: 0 0 20px;
}
</style>
