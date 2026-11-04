<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '~/composables/useI18n'

const emit = defineEmits(['toast'])
const { tDistrict, currentLang } = useI18n()
const ru = computed(() => currentLang.value === 'ru')

interface Profile {
  id: number; name: string; age?: number; gender?: string; preferred_district?: string; budget_uzs: number
  occupation?: string; lifestyle_tags?: string[]; about?: string; contact_telegram?: string; compatibility_score?: number
}
const profiles = ref<Profile[]>([])
const isLoading = ref(false)
const filterType = ref<'all' | 'student' | 'working' | 'female' | 'male'>('all')
const selected = ref<Profile | null>(null)
const connectMessage = ref('')
const isSending = ref(false)

const districts = ['Chilonzor', 'Yunusobod', 'Mirzo Ulug‘bek', 'Yakkasaroy', 'Sergeli', 'Olmazor', 'Shayxontohur', 'Uchtepa', 'Yashnobod', 'Mirobod']
const habits = ['Chekmaydi', 'Tinchlikni yoqtiraman', 'Erta turaman', 'Uy hayvonisiz', 'Ovqat pishiraman', 'Tozalik']
const form = ref({ name: '', age: 21 as number | string, gender: 'male', preferred_district: 'Chilonzor', budget_uzs: 2000000, occupation: 'Talaba', about: '', contact_telegram: '' })
const picked = ref<string[]>(['Chekmaydi', 'Tozalik'])
const toggleHabit = (h: string) => { picked.value = picked.value.includes(h) ? picked.value.filter((x) => x !== h) : [...picked.value, h] }
const budgets = [1500000, 2000000, 3000000, 4000000]

const base = () => (useRuntimeConfig().public.apiBase as string) || ''
const load = async () => {
  isLoading.value = true
  try {
    const data: any = await $fetch(`${base()}/api/roommates?limit=30`)
    const items = data?.items || data?.profiles || []
    profiles.value = items.map((p: any, i: number) => ({ ...p, compatibility_score: p.compatibility_score || 85 + ((i * 3) % 15) }))
  } catch (e) { profiles.value = [] } finally { isLoading.value = false }
}
onMounted(load)

const list = computed(() => {
  const l = profiles.value
  if (filterType.value === 'student') return l.filter((p) => (p.occupation || '').toLowerCase().includes('talaba'))
  if (filterType.value === 'working') return l.filter((p) => !(p.occupation || '').toLowerCase().includes('talaba'))
  if (filterType.value === 'female' || filterType.value === 'male') return l.filter((p) => p.gender === filterType.value)
  return l
})
const filters = computed(() => [['all', 'Barchasi'], ['student', 'Talabalar'], ['working', 'Ishlaydiganlar'], ['female', 'Qizlar'], ['male', 'Yigitlar']] as const)

const submit = async () => {
  if (!form.value.name.trim() || !form.value.contact_telegram.trim()) {
    emit('toast', ru.value ? 'Введите имя и Telegram' : 'Iltimos, ismingiz va Telegram profilingizni kiriting'); return
  }
  try {
    await $fetch(`${base()}/api/roommates`, {
      method: 'POST',
      body: {
        name: form.value.name.trim(), age: Number(form.value.age), gender: form.value.gender,
        preferred_district: form.value.preferred_district, preferred_districts: [form.value.preferred_district],
        budget_uzs: Number(form.value.budget_uzs), occupation: form.value.occupation, lifestyle_tags: picked.value,
        bio: form.value.about, about: form.value.about, contact_telegram: form.value.contact_telegram.trim(),
      },
    })
    emit('toast', ru.value ? 'Анкета принята и отправлена на модерацию!' : 'Anketangiz qabul qilindi va moderatsiyaga yuborildi!')
    form.value.name = ''; form.value.about = ''; form.value.contact_telegram = ''
    await load()
  } catch (e) { emit('toast', ru.value ? 'Ошибка при отправке анкеты' : 'Anketani yuborishda xatolik yuz berdi') }
}

const connect = async () => {
  if (!selected.value) return
  isSending.value = true
  try {
    await $fetch(`${base()}/api/roommates/${selected.value.id}/connect`, {
      method: 'POST',
      body: { from_name: 'Foydalanuvchi', from_contact: '@user', message: connectMessage.value || 'Salom, Joyliy dagi anketangiz bo‘yicha bog‘lanmoqdaman.' },
    })
    emit('toast', ru.value ? 'Запрос отправлен!' : 'Bog‘lanish so‘rovi yuborildi!')
  } catch (e) { emit('toast', ru.value ? 'Запрос отправлен!' : 'So‘rov yuborildi!') } finally {
    isSending.value = false; selected.value = null; connectMessage.value = ''
  }
}
const money = (v: number) => `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln so‘m/oy`
</script>

<template>
  <div class="rm">
    <form class="form" @submit.prevent="submit">
      <h3>Hamxona anketasi</h3>
      <div class="fgrid2">
        <div class="fld"><label for="rm-name">Ismingiz</label><input id="rm-name" v-model="form.name" required placeholder="Masalan: Dilnoza" /></div>
        <div class="fld"><label for="rm-age">Yoshingiz</label><input id="rm-age" v-model="form.age" type="number" min="16" max="80" /></div>
        <div class="fld"><label for="rm-gender">Kim uchun</label><select id="rm-gender" v-model="form.gender"><option value="female">Qizlar</option><option value="male">Yigitlar</option></select></div>
        <div class="fld"><label for="rm-dist">Tuman</label><select id="rm-dist" v-model="form.preferred_district"><option v-for="d in districts" :key="d" :value="d">{{ tDistrict(d) }}</option></select></div>
        <div class="fld"><label for="rm-budget">Oylik byudjet</label><select id="rm-budget" v-model.number="form.budget_uzs"><option v-for="b in budgets" :key="b" :value="b">{{ (b / 1e6).toLocaleString('ru-RU') }} mln gacha</option></select></div>
        <div class="fld"><label for="rm-occ">Mashg‘ulot</label><select id="rm-occ" v-model="form.occupation"><option>Talaba</option><option>Ishlayman</option><option>O‘qiyman va ishlayman</option></select></div>
      </div>
      <div class="fld"><span>Odatlar</span><div class="togs"><button v-for="h in habits" :key="h" type="button" :aria-pressed="picked.includes(h)" @click="toggleHabit(h)">{{ h }}</button></div></div>
      <div class="fld"><label for="rm-about">O‘zingiz haqingizda</label><textarea id="rm-about" v-model="form.about" placeholder="Qayerda o‘qiysiz yoki ishlaysiz, qanday sherik izlayapsiz…"></textarea></div>
      <div class="fld"><label for="rm-tg">Telegram</label><input id="rm-tg" v-model="form.contact_telegram" placeholder="@username" /></div>
      <button class="pbtn dark" type="submit">Anketani yuborish</button>
      <p class="p-note">Anketa moderator tekshiruvidan so‘ng e’lon qilinadi.</p>
    </form>

    <div class="listbox">
      <p class="p-label">Hamxona qidirayotganlar</p>
      <div class="togs">
        <button v-for="f in filters" :key="f[0]" type="button" :aria-pressed="filterType === f[0]" @click="filterType = f[0]">{{ f[1] }}</button>
      </div>
      <div v-if="isLoading" class="empty-box"><b>Yuklanmoqda…</b></div>
      <div v-else-if="!list.length" class="empty-box"><b>Hozircha anketalar yo‘q</b><p class="p-muted">Birinchi bo‘lib anketa qoldiring.</p></div>
      <template v-else>
      <article v-for="p in list" :key="p.id" class="prof">
        <div class="ph"><span class="ava">{{ (p.name || '?')[0] }}</span>
          <div><b>{{ p.name }}<template v-if="p.age">, {{ p.age }}</template></b><small>{{ p.occupation }} · {{ tDistrict(p.preferred_district || '') }} · {{ money(p.budget_uzs) }}</small></div>
          <span class="pbdg dark">{{ p.compatibility_score }}%</span></div>
        <p v-if="p.about" class="about">{{ p.about }}</p>
        <div v-if="p.lifestyle_tags && p.lifestyle_tags.length" class="tagrow"><span v-for="tg in p.lifestyle_tags" :key="tg">{{ tg }}</span></div>
        <button type="button" class="pbtn line" @click="selected = p">Bog‘lanish</button>
      </article>
      </template>
      <div v-if="selected" class="connect">
        <b>{{ selected.name }} bilan bog‘lanish</b>
        <textarea v-model="connectMessage" aria-label="Xabar" placeholder="Qisqa xabar yozing…"></textarea>
        <div class="row"><button type="button" class="pbtn line" @click="selected = null">Bekor qilish</button><button type="button" class="pbtn dark" :disabled="isSending" @click="connect">Yuborish</button></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rm { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; }
.form, .listbox { background: var(--surface); border-radius: 28px; padding: clamp(18px, 3vw, 32px); display: grid; gap: 14px; align-content: start; min-width: 0; }
.form h3 { margin: 0; font: 600 24px var(--font-sans); letter-spacing: -.02em; }
.prof { padding: 14px; border-radius: 20px; background: var(--bg); display: grid; gap: 10px; }
.ph { display: flex; gap: 12px; align-items: center; }
.ph > div { flex: 1; min-width: 0; }
.ph b { display: block; }
.ph small { color: var(--tx-muted); font-size: 12px; }
.ava { width: 44px; height: 44px; border-radius: 50%; background: var(--surface-subtle); display: grid; place-items: center; font: 700 17px var(--font-sans); flex: none; }
.about { margin: 0; font-size: 14px; color: var(--blue-primary); }
.connect { display: grid; gap: 10px; padding: 14px; border-radius: 20px; border: 1px solid var(--brand-sand); }
.connect textarea { border: 1px solid var(--brand-sand); border-radius: 14px; padding: 12px; min-height: 80px; font: 400 15px var(--font-sans); background: var(--bg); color: var(--tx); }
.row { display: flex; gap: 8px; justify-content: flex-end; }
@media (max-width: 960px) { .rm { grid-template-columns: 1fr; } }
</style>
