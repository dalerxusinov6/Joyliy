<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Tizim Sozlamalari — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const activeTab = ref<'general' | 'parser' | 'telegram' | 'database' | 'security'>('general')
const isLoading = ref(true)
const isSaving = ref(false)

const settingsForm = ref<any>({
  general: {
    app_name: 'Joyliy.uz',
    website_url: 'https://joyliy.uz',
    default_currency: 'USD',
    timezone: 'Asia/Tashkent',
  },
  parser: {
    schedules: ['08:00', '14:00', '20:00'],
    request_delay_ms: 1000,
    max_retries: 3,
    auto_publish_telegram: true,
  },
  telegram: {
    channel_username: '@joyliy_uz',
    bot_username: '@joyliy_bot',
    rate_limit_per_min: 20,
  },
  database: {
    pool_size: 10,
    max_overflow: 20,
    dialect: 'PostgreSQL / SQLite',
  },
  security: {
    jwt_expire_minutes: 1440,
    enforce_https: true,
    require_ip_whitelisting: false,
  },
})

const loadSettings = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/settings')
    if (res && res.settings) {
      settingsForm.value = { ...settingsForm.value, ...res.settings }
    }
  } catch (err) {
    showToast('Sozlamalarni yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

const saveSettings = async () => {
  isSaving.value = true
  try {
    const res = await authFetch('/api/admin/settings', {
      method: 'POST',
      body: settingsForm.value,
    })
    if (res && res.success) {
      showToast('Sozlamalar muvaffaqiyatli yangilandi!', 'success')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Saqlashda xatolik', 'error')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<template>
  <AdminShell
    title="Tizim sozlamalari"
    :breadcrumbs="[
      { label: 'Tizim' },
      { label: 'Sozlamalar' }
    ]"
  >
    <div class="settings-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">Tizim Sozlamalari</h1>
          <p class="page-sub">Joyliy platformasining asosiy parametrlari, integratsiyalar va xavfsizlik sozlamalari</p>
        </div>

        <button class="save-settings-btn" @click="saveSettings" :disabled="isSaving">
          {{ isSaving ? 'Saqlanmoqda...' : 'O‘zgarishlarni saqlash' }}
        </button>
      </div>

      <!-- Settings Tabs Header -->
      <div class="settings-tabs-row">
        <button
          v-for="tab in [
            { id: 'general', label: 'Umumiy' },
            { id: 'parser', label: 'Parser & Skraping' },
            { id: 'telegram', label: 'Telegram Bot & Kanal' },
            { id: 'database', label: 'Ma‘lumotlar bazasi' },
            { id: 'security', label: 'Xavfsizlik & RBAC' }
          ]"
          :key="tab.id"
          class="settings-tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id as any"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Contents -->
      <div class="settings-card">
        <!-- GENERAL TAB -->
        <div v-if="activeTab === 'general'" class="settings-tab-pane">
          <h3 class="pane-h3">Asosiy Platforma Parametrlari</h3>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Platforma nomi</label>
              <span class="f-desc">Sayt va e‘lonlar sarlavhasida aks etuvchi nom</span>
            </div>
            <input v-model="settingsForm.general.app_name" type="text" class="field-input" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Sayt asosiy URL manzili</label>
              <span class="f-desc">Kanal xabarlari va havolalar uchun rasmiy domen</span>
            </div>
            <input v-model="settingsForm.general.website_url" type="url" class="field-input" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Standart valyuta</label>
              <span class="f-desc">Kvartira narxlari konvertatsiyasi uchun asosiy birlik</span>
            </div>
            <select v-model="settingsForm.general.default_currency" class="field-input">
              <option value="USD">USD ($ - AQSH Dollari)</option>
              <option value="UZS">UZS (so‘m - O‘zbekiston so‘mi)</option>
            </select>
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Vaqt mintaqasi</label>
              <span class="f-desc">Skanerlash jadvallari va audit hisobotlari uchun standart zona</span>
            </div>
            <input v-model="settingsForm.general.timezone" type="text" readonly class="field-input readonly" />
          </div>
        </div>

        <!-- PARSER TAB -->
        <div v-else-if="activeTab === 'parser'" class="settings-tab-pane">
          <h3 class="pane-h3">Parser va Skraping Sozlamalari</h3>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">So‘rovlar orasidagi tanaffus (ms)</label>
              <span class="f-desc">Bloklanishning oldini olish uchun so‘rovlar oraliq vaqti</span>
            </div>
            <input v-model.number="settingsForm.parser.request_delay_ms" type="number" class="field-input" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Maksimal qayta urinishlar soni</label>
              <span class="f-desc">Tarmoq uzilishi vaqtida qayta urinishlar limiti</span>
            </div>
            <input v-model.number="settingsForm.parser.max_retries" type="number" class="field-input" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Yangi e‘lonlarni darhol Telegramga chiqarish</label>
              <span class="f-desc">Skan paytida topilgan toza e‘lonlarni kutmasdan kanalga post qilish</span>
            </div>
            <label class="switch-toggle">
              <input v-model="settingsForm.parser.auto_publish_telegram" type="checkbox" />
              <span class="switch-slider" />
            </label>
          </div>
        </div>

        <!-- TELEGRAM TAB -->
        <div v-else-if="activeTab === 'telegram'" class="settings-tab-pane">
          <h3 class="pane-h3">Telegram Integratsiya Parametrlari</h3>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Rasmiy Telegram Kanal</label>
              <span class="f-desc">E‘lonlar post qilinadigan asosiy kanal</span>
            </div>
            <input v-model="settingsForm.telegram.channel_username" type="text" class="field-input" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Rasmiy Bot Username</label>
              <span class="f-desc">Foydalanuvchilar login va filtrlash boti</span>
            </div>
            <input v-model="settingsForm.telegram.bot_username" type="text" class="field-input" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Telegram API Rate Limit</label>
              <span class="f-desc">Daqiqasiga yuboriladigan maksimal postlar</span>
            </div>
            <input v-model.number="settingsForm.telegram.rate_limit_per_min" type="number" class="field-input" />
          </div>
        </div>

        <!-- DATABASE TAB -->
        <div v-else-if="activeTab === 'database'" class="settings-tab-pane">
          <h3 class="pane-h3">Ma‘lumotlar Bazasi va Pool</h3>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">DB Dialect & Holat</label>
              <span class="f-desc">SQLAlchemy 2.0 ulanish turi</span>
            </div>
            <input :value="settingsForm.database.dialect" type="text" readonly class="field-input readonly" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Ulanishlar hovuzi (Pool Size)</label>
              <span class="f-desc">Bir vaqtning o‘zida ochiq ulanishlar soni</span>
            </div>
            <input v-model.number="settingsForm.database.pool_size" type="number" class="field-input" />
          </div>
        </div>

        <!-- SECURITY TAB -->
        <div v-else-if="activeTab === 'security'" class="settings-tab-pane">
          <h3 class="pane-h3">Xavfsizlik va Sessiyalar</h3>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">Admin Sessiya Muddati (daqiqalarda)</label>
              <span class="f-desc">JWT token muddati (standart: 1440 daqiqa = 24 soat)</span>
            </div>
            <input v-model.number="settingsForm.security.jwt_expire_minutes" type="number" class="field-input" />
          </div>

          <div class="field-row">
            <div class="field-meta">
              <label class="f-label">HTTPS majburiy qilish</label>
              <span class="f-desc">Barcha HTTP so‘rovlarni avtomatik SSL ga yo‘naltirish</span>
            </div>
            <label class="switch-toggle">
              <input v-model="settingsForm.security.enforce_https" type="checkbox" />
              <span class="switch-slider" />
            </label>
          </div>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.settings-page { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 22px; font-weight: 800; color: var(--ad-text-main); margin: 0; }
.page-sub { font-size: 13.5px; color: var(--ad-text-muted); margin-top: 2px; }

.save-settings-btn {
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: var(--ad-radius-md);
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
}
.save-settings-btn:hover:not(:disabled) {
  background: var(--ad-primary-hover);
}

.settings-tabs-row {
  display: flex;
  gap: 6px;
  border-bottom: 1px solid var(--ad-border);
  padding-bottom: 2px;
  overflow-x: auto;
}

.settings-tab-btn {
  background: none;
  border: none;
  padding: 10px 16px;
  border-radius: var(--ad-radius-md) var(--ad-radius-md) 0 0;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ad-text-muted);
  cursor: pointer;
  transition: all 0.15s;
  border-bottom: 2px solid transparent;
}

.settings-tab-btn:hover {
  color: var(--ad-text-main);
}

.settings-tab-btn.active {
  color: var(--ad-primary);
  border-bottom-color: var(--ad-primary);
  background: var(--ad-primary-light);
}

.settings-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 24px;
  box-shadow: var(--ad-shadow-sm);
}

.settings-tab-pane {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pane-h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--ad-text-main);
  padding-bottom: 12px;
  border-bottom: 1px solid var(--ad-border-subtle);
}

.field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  padding: 10px 0;
  border-bottom: 1px solid var(--ad-border-subtle);
}

.field-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
  max-width: 480px;
}

.f-label {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ad-text-main);
}

.f-desc {
  font-size: 12px;
  color: var(--ad-text-muted);
}

.field-input {
  width: 280px;
  height: 38px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  background: var(--ad-bg);
  color: var(--ad-text-main);
  padding: 0 12px;
  font-size: 13.5px;
  outline: none;
}

.field-input.readonly {
  opacity: 0.7;
  cursor: not-allowed;
}

.field-input:focus:not(.readonly) {
  border-color: var(--ad-primary);
  background: var(--ad-surface);
}

/* Switch Toggle */
.switch-toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: var(--ad-border);
  border-radius: 24px;
  transition: 0.2s;
}

.switch-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.2s;
}

.switch-toggle input:checked + .switch-slider {
  background-color: var(--ad-primary);
}

.switch-toggle input:checked + .switch-slider:before {
  transform: translateX(20px);
}
</style>

