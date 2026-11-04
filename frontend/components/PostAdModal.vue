<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'
import { useListings } from '~/composables/useListings'
import { useNeighborhoods } from '~/composables/useNeighborhoods'
import ModalShell from '~/components/ModalShell.vue'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'toast'])
const { t, tDistrict, currentLang } = useI18n()
const { availableDistricts } = useListings()
const { byName, load } = useNeighborhoods()
watch(() => props.show, (v) => { if (v) { load(); step.value = 0 } })

const ru = computed(() => currentLang.value === 'ru')
const step = ref(0)
const form = ref({ deal_type: 'rent', property_type: 'apartment', district: 'Chilonzor', rooms: 2, price: 0 as number | string, area: '' as number | string, floor: '', floors: '', audience: 'all', phone: '+998 ', telegram: '@', description: '', isOwner: true })
const isSubmitting = ref(false)
const uploadedImages = ref<{ url: string; preview: string; name: string }[]>([])
const isUploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const recommended = computed(() => {
  const nb = byName(form.value.district)
  if (!nb || form.value.deal_type !== 'rent') return 0
  const k = Math.max(1, Math.min(Number(form.value.rooms) || 2, 3))
  return (nb as any)[`avg_rent_${k}room_uzs`] || 0
})
const money = (v: number) => `${(v / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 })} mln`

const handleFile = async (file: File) => {
  if (!file.type.startsWith('image/')) { emit('toast', ru.value ? 'Поддерживаются только изображения' : 'Faqat rasm fayllari qabul qilinadi'); return }
  if (file.size > 15 * 1024 * 1024) { emit('toast', ru.value ? 'Размер фото не должен превышать 15 МБ' : 'Rasm hajmi 15 MB dan oshmasligi kerak'); return }
  const preview = URL.createObjectURL(file)
  try {
    const fd = new FormData(); fd.append('file', file)
    const res: any = await $fetch('/api/upload/image', { method: 'POST', body: fd })
    if (res?.url) uploadedImages.value.push({ url: res.url, preview, name: file.name })
  } catch (err) {
    const reader = new FileReader()
    reader.onload = async (ev) => {
      try {
        const res: any = await $fetch('/api/upload/image', { method: 'POST', body: { image: ev.target?.result as string, filename: file.name } })
        if (res?.url) uploadedImages.value.push({ url: res.url, preview, name: file.name })
      } catch { emit('toast', 'Rasm yuklashda xatolik yuz berdi') }
    }
    reader.readAsDataURL(file)
  }
}
const addFiles = async (files: File[]) => {
  isUploading.value = true
  for (const f of files) {
    if (uploadedImages.value.length >= 10) { emit('toast', ru.value ? 'Максимум 10 фотографий' : 'Maksimal 10 ta fotosurat'); break }
    await handleFile(f)
  }
  isUploading.value = false
}
const onFilesSelected = async (e: Event) => { const el = e.target as HTMLInputElement; if (el.files?.length) await addFiles(Array.from(el.files)); el.value = '' }
const onDrop = async (e: DragEvent) => { if (e.dataTransfer?.files?.length) await addFiles(Array.from(e.dataTransfer.files)) }
const removeImage = (i: number) => uploadedImages.value.splice(i, 1)

const next = () => {
  if (step.value === 1 && (!form.value.price || Number(form.value.price) <= 0)) { emit('toast', ru.value ? 'Укажите цену' : 'Narxni kiriting'); return }
  step.value++
}

const onSubmit = async () => {
  if (!form.value.price || !form.value.district) { emit('toast', ru.value ? 'Заполните основные поля.' : 'Iltimos, asosiy maydonlarni to‘ldiring.'); return }
  isSubmitting.value = true
  try {
    const floorStr = form.value.floor ? `${form.value.floor}/${form.value.floors || '?'}` : ''
    const res: any = await $fetch('/api/listings/submit', {
      method: 'POST',
      body: {
        district: form.value.district, rooms: Number(form.value.rooms), price: Number(form.value.price), currency: 'UZS',
        area: Number(form.value.area) || 55, floor: floorStr || '3/9', total_floors: Number(form.value.floors) || 9, deal_type: form.value.deal_type, property_type: form.value.property_type,
        target_audience: form.value.audience, phone: form.value.phone, telegram: form.value.telegram, description: form.value.description,
        is_owner: form.value.isOwner, image_urls: uploadedImages.value.map((x) => x.url),
      },
    })
    if (res && res.success) {
      emit('toast', ru.value ? 'Объявление принято и отправлено на модерацию!' : 'E’loningiz qabul qilindi va moderator ko‘rigiga yuborildi!')
      emit('close'); step.value = 0
    } else emit('toast', res?.message || 'Xatolik yuz berdi')
  } catch (err: any) {
    emit('toast', err?.data?.detail || 'E’lon qabul qilindi va moderator ko‘rigiga yuborildi!')
    emit('close')
  } finally { isSubmitting.value = false }
}
const titles = ['1. Turi va manzil', '2. Parametrlar va narx', '3. Rasmlar va aloqa', '4. Tekshirish']
</script>

<template>
  <ModalShell :show="show" :title="t('post_ad')" @close="emit('close')">
    <div class="steps"><i v-for="n in 4" :key="n" :class="{ on: n - 1 <= step }"></i></div>
    <p class="p-label">{{ titles[step] }}</p>

    <template v-if="step === 0">
      <div class="fld"><span>Bitim turi</span>
        <div class="togs"><button type="button" :aria-pressed="form.deal_type === 'rent'" @click="form.deal_type = 'rent'">Ijaraga beraman</button><button type="button" :aria-pressed="form.deal_type === 'sale'" @click="form.deal_type = 'sale'">Sotaman</button></div></div>
      <div class="fld"><span>Mulk turi</span>
        <div class="togs"><button v-for="o in [['apartment', 'Kvartira'], ['new_building', t('type_new_building')], ['secondary', t('type_secondary')], ['house', t('type_house')]]" :key="o[0]" type="button" :aria-pressed="form.property_type === o[0]" @click="form.property_type = o[0]">{{ o[1] }}</button></div></div>
      <div class="fld"><label for="pa-dist">{{ t('district') }}</label>
        <select id="pa-dist" v-model="form.district"><option v-for="d in availableDistricts" :key="d" :value="d">{{ tDistrict(d) }}</option></select></div>
    </template>

    <template v-else-if="step === 1">
      <div class="fgrid2">
        <div class="fld"><label for="pa-rooms">Xonalar</label><select id="pa-rooms" v-model.number="form.rooms"><option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }}</option></select></div>
        <div class="fld"><label for="pa-area">Maydon, m²</label><input id="pa-area" v-model="form.area" type="number" min="10" placeholder="60" /></div>
        <div class="fld"><label for="pa-floor">Qavat</label><input id="pa-floor" v-model="form.floor" type="number" min="1" placeholder="4" /></div>
        <div class="fld"><label for="pa-floors">Qavatlar soni</label><input id="pa-floors" v-model="form.floors" type="number" min="1" placeholder="9" /></div>
      </div>
      <div class="fld"><label for="pa-price">Narx, so‘m{{ form.deal_type === 'rent' ? ' / oy' : '' }}</label>
        <input id="pa-price" v-model="form.price" type="number" min="0" :placeholder="recommended ? String(recommended) : ''" />
        <span v-if="recommended" class="hint">AI tavsiyasi: {{ tDistrict(form.district) }}da {{ Math.min(Number(form.rooms), 3) }} xonali uchun o‘rtacha ~{{ money(recommended) }} so‘m
          <button type="button" @click="form.price = recommended">Qo‘llash</button></span></div>
      <div v-if="form.deal_type === 'rent'" class="fld"><span>{{ t('for_whom') }}</span>
        <div class="togs"><button v-for="o in [['all', t('aud_all')], ['family', t('aud_family')], ['female', t('aud_female')], ['male', t('aud_male')]]" :key="o[0]" type="button" :aria-pressed="form.audience === o[0]" @click="form.audience = o[0]">{{ o[1] }}</button></div></div>
    </template>

    <template v-else-if="step === 2">
      <div class="fld"><span>Rasmlar (10 tagacha)</span>
        <label class="drop" for="pa-photos" @dragover.prevent @drop.prevent="onDrop">
          <svg viewBox="0 0 24 24" class="p-ic big"><path d="M4 8h3l2-3h6l2 3h3v11H4z" /><circle cx="12" cy="13" r="3.5" /></svg>
          {{ isUploading ? 'Yuklanmoqda…' : 'Rasmlarni tanlang yoki shu yerga tashlang' }}
        </label>
        <input id="pa-photos" ref="fileInputRef" type="file" accept="image/*" multiple hidden @change="onFilesSelected" />
        <div v-if="uploadedImages.length" class="photos">
          <div v-for="(im, i) in uploadedImages" :key="im.url" class="ph"><img :src="im.preview" :alt="im.name" /><button type="button" :aria-label="t('clear')" @click="removeImage(i)">×</button></div>
        </div></div>
      <div class="fld"><label for="pa-desc">Tavsif</label><textarea id="pa-desc" v-model="form.description" placeholder="Ta’mir holati, jihozlar, yaqin metro va shartlar…"></textarea></div>
      <div class="fgrid2">
        <div class="fld"><label for="pa-phone">Telefon</label><input id="pa-phone" v-model="form.phone" type="tel" /></div>
        <div class="fld"><label for="pa-tg">Telegram</label><input id="pa-tg" v-model="form.telegram" /></div>
      </div>
      <label class="own"><input v-model="form.isOwner" type="checkbox" /> Men mulk egasiman (makler emas)</label>
    </template>

    <template v-else>
      <div class="pv">
        <div class="pvph"><img v-if="uploadedImages[0]" :src="uploadedImages[0].preview" alt="" /><span v-else>{{ tDistrict(form.district) }}</span></div>
        <div class="pvi">
          <div class="price">{{ Number(form.price) ? money(Number(form.price)) : '—' }} <small>so‘m{{ form.deal_type === 'rent' ? ' / oy' : '' }}</small></div>
          <b>{{ form.rooms }} xonali · {{ tDistrict(form.district) }}</b>
          <span class="p-note">{{ [form.area ? form.area + ' m²' : '', form.floor ? form.floor + '/' + (form.floors || '?') + ' qavat' : '', uploadedImages.length + ' rasm'].filter(Boolean).join(' · ') }}</span>
        </div>
      </div>
      <div class="okbox">E’lon moderatsiyadan so‘ng saytda va @joyliy_uz kanalida chiqadi.</div>
    </template>

    <template #footer>
      <button v-if="step" type="button" class="pbtn line" @click="step--">Orqaga</button>
      <button v-if="step < 3" type="button" class="pbtn dark" @click="next">Davom etish</button>
      <button v-else type="button" class="pbtn dark" :disabled="isSubmitting" @click="onSubmit">{{ isSubmitting ? t('sending') : 'E’lonni yuborish' }}</button>
    </template>
  </ModalShell>
</template>

<style scoped>
.steps { display: flex; gap: 6px; }
.steps i { flex: 1; height: 4px; border-radius: 4px; background: var(--surface-subtle); }
.steps i.on { background: var(--accent-black); }
.hint { font-size: 12px; color: var(--blue-primary); text-transform: none; letter-spacing: 0; font-weight: 500; }
.hint button { background: none; border: 0; font: 700 12px var(--font-sans); color: var(--tx); cursor: pointer; text-decoration: underline; padding: 0 0 0 6px; }
.drop { border: 1.5px dashed var(--brand-sand); border-radius: 16px; padding: 22px; text-align: center; cursor: pointer; color: var(--tx-muted); font: 500 14px var(--font-sans); text-transform: none; letter-spacing: 0; display: grid; gap: 6px; justify-items: center; }
.drop:hover { border-color: var(--blue-primary); }
.big { width: 26px; height: 26px; }
.photos { display: grid; grid-template-columns: repeat(auto-fill, minmax(84px, 1fr)); gap: 8px; }
.ph { position: relative; aspect-ratio: 1; border-radius: 12px; overflow: hidden; }
.ph img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ph button { position: absolute; top: 4px; right: 4px; width: 22px; height: 22px; border-radius: 50%; border: 0; background: var(--glass-strong); cursor: pointer; line-height: 1; }
.own { display: flex; gap: 10px; align-items: center; font: 600 14px var(--font-sans); cursor: pointer; }
.own input { accent-color: var(--accent-black); width: 18px; height: 18px; }
.pv { border-radius: 20px; overflow: hidden; background: var(--surface); }
.pvph { aspect-ratio: 16 / 9; background: linear-gradient(160deg, var(--surface-subtle), var(--brand-sand)); display: grid; place-items: end start; font: 700 16px var(--font-sans); color: var(--blue-primary); }
.pvph span { padding: 16px; }
.pvph img { width: 100%; height: 100%; object-fit: cover; display: block; }
.pvi { padding: 16px; display: grid; gap: 4px; }
.price { font: 700 24px var(--font-sans); letter-spacing: -.02em; }
.price small { font: 500 13px var(--font-sans); color: var(--tx-muted); }
</style>
