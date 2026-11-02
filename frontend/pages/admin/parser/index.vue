<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminShell from '~/components/admin/AdminShell.vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Parser Boshqaruvi — Joyliy Admin',
})

const { authFetch, showToast } = useAdminAuth()

const isLoading = ref(true)
const isTriggering = ref(false)
const parserData = ref<any>(null)

const triggerSource = ref('all')
const triggerForce = ref(true)

const schedules = ref(['08:00', '14:00', '20:00'])
const newScheduleTime = ref('')

const loadParserStatus = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/admin/parser/status')
    if (res && res.success) {
      parserData.value = res
      if (res.schedules) {
        schedules.value = res.schedules
      }
    }
  } catch (err: any) {
    showToast('Parser holatini yuklashda xatolik', 'error')
  } finally {
    isLoading.value = false
  }
}

const triggerRun = async () => {
  isTriggering.value = true
  showToast('Skanerlash vazifasi ishga tushirilmoqda...', 'info')
  try {
    const res = await authFetch('/api/admin/parser/run', {
      method: 'POST',
      body: {
        source: triggerSource.value,
        force: triggerForce.value,
      },
    })
    if (res && res.success) {
      showToast('Skanerlash muvaffaqiyatli boshlandi / yakunlandi!', 'success')
      await loadParserStatus()
    } else {
      showToast(res?.message || 'Skanerlash boshlanmadi', 'warning')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Xatolik yuz berdi', 'error')
  } finally {
    isTriggering.value = false
  }
}

const togglePause = async () => {
  const willPause = !parserData.value?.is_paused
  try {
    const res = await authFetch('/api/admin/parser/pause', {
      method: 'POST',
      body: { paused: willPause },
    })
    if (res && res.success) {
      showToast(res.message, 'info')
      await loadParserStatus()
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Amal bajarilmadi', 'error')
  }
}

const saveSchedules = async () => {
  try {
    const res = await authFetch('/api/admin/parser/schedules', {
      method: 'POST',
      body: { schedules: schedules.value },
    })
    if (res && res.success) {
      showToast('Jadval muvaffaqiyatli saqlandi!', 'success')
    }
  } catch (err: any) {
    showToast(err?.data?.detail || 'Jadvalni saqlashda xatolik', 'error')
  }
}

const addSchedule = () => {
  if (newScheduleTime.value && !schedules.value.includes(newScheduleTime.value)) {
    schedules.value.push(newScheduleTime.value)
    schedules.value.sort()
    newScheduleTime.value = ''
    saveSchedules()
  }
}

const removeSchedule = (idx: number) => {
  schedules.value.splice(idx, 1)
  saveSchedules()
}

onMounted(() => {
  loadParserStatus()
})

const formatDate = (dateStr?: string) => {
  if (!dateStr) return 'Mavjud emas'
  try {
    return new Date(dateStr).toLocaleString('uz-UZ', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <AdminShell
    title="Parser boshqaruvi"
    :breadcrumbs="[{ label: 'Avtomatizatsiya' }, { label: 'Parser' }]"
  >
    <div class="parser-page">
      <div class="page-title-row">
        <div>
          <h1 class="page-title">Avtomatik Parser Boshqaruv Markazi</h1>
          <p class="page-sub">Kunlik 08:00, 14:00, 20:00 jadvalli skanerlash, manbalarni tekshirish va dublikatlarni bloklash</p>
        </div>
        <div class="title-actions">
          <button class="rf-btn" @click="loadParserStatus" :disabled="isLoading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="i-15" :class="{ 'spin-i': isLoading }">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            Yangilash
          </button>
        </div>
      </div>

      <!-- Live Status & Instant Trigger Card -->
      <div class="p-card status-hero-card">
        <div class="status-col">
          <div class="status-top">
            <span class="status-dot" :class="parserData?.is_running ? 'dot-active' : (parserData?.is_paused ? 'dot-paused' : 'dot-idle')" />
            <span class="status-headline">
              {{ parserData?.is_running ? '🟢 Skanerlash jarayoni davom etmoqda' : (parserData?.is_paused ? '⏸️ Parser to‘xtatib turilgan (Pauza)' : '🟢 Kutish rejimida (Aktiv)') }}
            </span>
          </div>
          <p class="status-sub">
            Vaqt mintaqasi: <strong>Asia/Tashkent</strong> • Keyingi rejalashtirilgan skan: <strong>{{ parserData?.next_scheduled_scan || '08:00' }}</strong>
          </p>

          <div class="hero-meta-row">
            <div class="hm-item">
              <span class="hm-k">Oxirgi skan:</span>
              <span class="hm-v">{{ formatDate(parserData?.last_run?.created_at) }}</span>
            </div>
            <div class="hm-item">
              <span class="hm-k">Topilgan yangi e‘lonlar:</span>
              <span class="hm-v text-emerald">+{{ parserData?.last_run?.new_listings || 0 }} ta</span>
            </div>
            <div class="hm-item">
              <span class="hm-k">Dublikatlar ushlandi:</span>
              <span class="hm-v">{{ parserData?.last_run?.duplicates || 0 }} ta</span>
            </div>
          </div>
        </div>

        <div class="trigger-col">
          <div class="trigger-box">
            <div class="trigger-opts">
              <select v-model="triggerSource" class="trig-select">
                <option value="all">Barcha manbalar</option>
                <option value="olx">Faqat OLX.uz</option>
              </select>
              <label class="trig-checkbox">
                <input v-model="triggerForce" type="checkbox" />
                <span>Majburiy (Force)</span>
              </label>
            </div>

            <div class="trig-btns">
              <button class="instant-scan-btn" @click="triggerRun" :disabled="isTriggering">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="i-16" :class="{ 'spin-i': isTriggering }">
                  <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                </svg>
                {{ isTriggering ? 'Skanerlanmoqda...' : 'Hoziroq skanerlash' }}
              </button>

              <button class="pause-btn" @click="togglePause">
                {{ parserData?.is_paused ? '▶️ Qayta faollashtirish' : '⏸️ Pauza qilish' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Schedule & Metrics Row -->
      <div class="parser-grid-row">
        <!-- Daily Schedules Config -->
        <div class="p-card flex-1">
          <h3 class="card-h3">Avtomatik Skanerlash Jadvallari</h3>
          <p class="card-desc">Toshkent vaqti bilan har kuni belgilangan vaqtlarda avtomatik ishga tushadi</p>

          <div class="schedules-list">
            <div v-for="(sc, sIdx) in schedules" :key="sIdx" class="schedule-chip">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="sc-clock">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span class="sc-time">{{ sc }}</span>
              <button class="sc-del" @click="removeSchedule(sIdx)" title="O‘chirish">×</button>
            </div>
          </div>

          <div class="add-schedule-row">
            <input v-model="newScheduleTime" type="time" class="time-input" />
            <button class="add-sc-btn" @click="addSchedule">+ Jadval qo‘shish</button>
          </div>
        </div>

        <!-- 30 Days Statistics -->
        <div class="p-card flex-1">
          <h3 class="card-h3">30 Kunlik Samaradorlik</h3>
          <p class="card-desc">Skanerlar ishonchliligi va dublikatdan himoya statistikasi</p>

          <div class="metrics-v-list">
            <div class="mv-item">
              <span class="mv-k">Jami skanerlashlar:</span>
              <span class="mv-v font-bold">{{ parserData?.stats_30d?.total_runs || 0 }} marta</span>
            </div>
            <div class="mv-item">
              <span class="mv-k">Muvaffaqiyatli yakunlangan:</span>
              <span class="mv-v text-emerald font-bold">{{ parserData?.stats_30d?.successful_runs || 0 }} marta</span>
            </div>
            <div class="mv-item">
              <span class="mv-k">Xatolik bilan tugagan:</span>
              <span class="mv-v text-danger font-bold">{{ parserData?.stats_30d?.failed_runs || 0 }} marta</span>
            </div>
            <div class="mv-item">
              <span class="mv-k">Dublikatlar ushlanib qolgan:</span>
              <span class="mv-v text-purple font-bold">{{ parserData?.stats_30d?.duplicates_detected || 0 }} ta</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Nav Links -->
      <div class="parser-quick-nav">
        <NuxtLink to="/admin/parser/sources" class="nav-tile">
          <div class="nt-title">🌐 Parser Manbalari</div>
          <div class="nt-desc">OLX.uz va boshqa platformalar sozlamalarini boshqarish</div>
        </NuxtLink>
        <NuxtLink to="/admin/parser/history" class="nav-tile">
          <div class="nt-title">📜 Skanerlash Tarixi</div>
          <div class="nt-desc">Barcha o‘tgan skanerlash jurnallari va natijalari</div>
        </NuxtLink>
        <NuxtLink to="/admin/parser/failed" class="nav-tile">
          <div class="nt-title">⚠️ Xatoliklar & Qayta urinish</div>
          <div class="nt-desc">Muvaffaqiyatsiz skanlarni qayta ishga tushirish</div>
        </NuxtLink>
      </div>
    </div>
  </AdminShell>
</template>

<style scoped>
.parser-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--ad-text-main);
  margin: 0;
  letter-spacing: -0.4px;
}

.page-sub {
  font-size: 13.5px;
  color: var(--ad-text-muted);
  margin-top: 2px;
}

.rf-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  padding: 7px 14px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.p-card {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 22px;
  box-shadow: var(--ad-shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-hero-card {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.status-col {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-active { background: var(--ad-success); box-shadow: 0 0 8px var(--ad-success); }
.dot-idle { background: #3b82f6; }
.dot-paused { background: var(--ad-warning); }

.status-headline {
  font-size: 16px;
  font-weight: 700;
  color: var(--ad-text-main);
}

.status-sub {
  font-size: 13px;
  color: var(--ad-text-muted);
}

.hero-meta-row {
  display: flex;
  gap: 18px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.hm-item {
  display: flex;
  flex-direction: column;
  font-size: 12.5px;
}

.hm-k {
  color: var(--ad-text-muted);
}

.hm-v {
  font-weight: 700;
  color: var(--ad-text-main);
}

.trigger-col {
  display: flex;
  align-items: center;
}

.trigger-box {
  background: var(--ad-bg);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trigger-opts {
  display: flex;
  align-items: center;
  gap: 12px;
}

.trig-select {
  height: 34px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-sm);
  background: var(--ad-surface);
  color: var(--ad-text-main);
  padding: 0 8px;
  font-size: 13px;
}

.trig-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--ad-text-muted);
  cursor: pointer;
}

.trig-btns {
  display: flex;
  gap: 8px;
}

.instant-scan-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ad-primary);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: var(--ad-radius-md);
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.instant-scan-btn:hover:not(:disabled) {
  background: var(--ad-primary-hover);
}

.pause-btn {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  padding: 8px 14px;
  border-radius: var(--ad-radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.parser-grid-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.flex-1 { flex: 1; min-width: 320px; }

.card-h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--ad-text-main);
}

.card-desc {
  font-size: 13px;
  color: var(--ad-text-muted);
}

.schedules-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.schedule-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--ad-primary-light);
  border: 1px solid var(--ad-primary);
  border-radius: var(--ad-radius-md);
  padding: 6px 12px;
  color: var(--ad-primary);
}

.sc-clock {
  width: 14px;
  height: 14px;
}

.sc-time {
  font-family: var(--ad-font-mono);
  font-weight: 700;
  font-size: 14px;
}

.sc-del {
  background: none;
  border: none;
  color: var(--ad-primary);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.add-schedule-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.time-input {
  height: 36px;
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  background: var(--ad-bg);
  color: var(--ad-text-main);
  padding: 0 8px;
  font-size: 13px;
}

.add-sc-btn {
  height: 36px;
  background: var(--ad-border-subtle);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-md);
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.metrics-v-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mv-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid var(--ad-border-subtle);
  font-size: 13.5px;
}

.mv-k { color: var(--ad-text-muted); }
.mv-v { color: var(--ad-text-main); }
.text-emerald { color: #10b981; }
.text-danger { color: #ef4444; }
.text-purple { color: #8b5cf6; }

.parser-quick-nav {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.nav-tile {
  background: var(--ad-surface);
  border: 1px solid var(--ad-border);
  border-radius: var(--ad-radius-lg);
  padding: 18px;
  text-decoration: none;
  box-shadow: var(--ad-shadow-sm);
  transition: all 0.15s;
}

.nav-tile:hover {
  border-color: var(--ad-primary);
  transform: translateY(-2px);
}

.nt-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--ad-text-main);
}

.nt-desc {
  font-size: 12.5px;
  color: var(--ad-text-muted);
  margin-top: 4px;
}

.i-15 { width: 15px; height: 15px; }
.i-16 { width: 16px; height: 16px; }

.spin-i { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
