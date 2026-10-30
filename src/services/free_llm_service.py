"""Free AI / LLM Integration Service.

Connects to free model providers in priority order:
1. Google Gemini Free Tier (Gemini 2.0 Flash / 1.5 Flash via GEMINI_API_KEY or GOOGLE_API_KEY at aistudio.google.com)
2. Groq Cloud Free Tier (Llama 3.3 70B / Llama 3.1 8B via GROQ_API_KEY at console.groq.com)
3. OpenRouter Free Tier (Gemini / Llama free models via OPENROUTER_API_KEY at openrouter.ai)
4. Pollinations AI Public Endpoint (polite free gateway)
5. Grounded Uzbekistan Real Estate Knowledge & Heuristic Reasoning Engine (instant, 100% reliable)
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import List, Dict, Optional, Any
import httpx

from src.config import settings

logger = logging.getLogger(__name__)

JOYLIY_SYSTEM_PROMPT = (
    "Siz — «Joyliy» ko‘chmas mulk va ijara ekotizimining professional, xolis va aqlli sun’iy intellekt "
    "maslahatchisisiz. Toshkent shahri ijara bozori, ijara shartnomalari (O‘zbekiston Respublikasi "
    "Fuqarolik kodeksi 535-modda), soliq tizimi (ijara.soliq.uz portalida hisobga qo‘yish tartibi), "
    "garov puli (zalog/depozit) qaytarilish kafolatlari, kommunal to‘lovlar (hisoblagichlar taqsimoti) va "
    "firibgarlikdan (uyni ko‘rishdan oldin kartaga pul o‘tkazmaslik) himoyalanish bo‘yicha "
    "aniq, amaliy va ishonchli maslahat berasiz. "
    "Foydalanuvchi tilida (O‘zbek, Rus yoki Ingliz) ravon, qisqa va aniq javob bering."
)


class FreeLLMService:
    """Manages connections to free LLM endpoints with multi-tier fallback and structured extraction."""

    def __init__(self):
        self.timeout = 10.0

    @property
    def gemini_key(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)

    @property
    def groq_key(self) -> Optional[str]:
        return os.getenv("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)

    @property
    def openrouter_key(self) -> Optional[str]:
        return os.getenv("OPENROUTER_API_KEY") or getattr(settings, "OPENROUTER_API_KEY", None)

    async def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """Generate response using the best available free LLM provider with graceful local fallback."""
        sys_p = system_prompt or JOYLIY_SYSTEM_PROMPT
        if context:
            full_user_content = f"Kontekst:\n{context}\n\nFoydalanuvchi so‘rovi:\n{user_message}"
        else:
            full_user_content = user_message

        # 1. Google Gemini Free Tier
        if self.gemini_key:
            res = await self._call_gemini(full_user_content, sys_p)
            if res:
                return res

        # 2. Groq Cloud Free Tier
        if self.groq_key:
            res = await self._call_groq(full_user_content, sys_p)
            if res:
                return res

        # 3. OpenRouter Free Tier
        if self.openrouter_key:
            res = await self._call_openrouter(full_user_content, sys_p)
            if res:
                return res

        # 4. Zero-Key Free Public LLM (Pollinations AI)
        res = await self._call_free_open_llm(full_user_content, sys_p)
        if res:
            return res

        # 5. Fallback to grounded local reasoning engine
        return self._local_fallback(user_message, context)

    async def extract_search_criteria(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract structured JSON search criteria from conversational query using LLM."""
        system_prompt = (
            "You are an expert real estate search query parser for Tashkent, Uzbekistan. "
            "Extract user requirements into strict JSON with these keys:\n"
            "- district: string or null (one of: Chilonzor, Mirzo Ulug'bek, Yunusobod, Yakkasaroy, Mirobod, Shayxontohur, Olmazor, Uchtepa, Yashnobod, Sergeli, Yangihayot, Bektemir)\n"
            "- metro: string or null (e.g. Novza, Chilonzor, Oybek, Amir Temur, etc.)\n"
            "- rooms: integer or null (e.g. 1, 2, 3, 4)\n"
            "- max_price_uzs: integer in UZS or null (if given in USD, convert to UZS by multiplying by 12800. e.g. $400 -> 5120000; 4 mln -> 4000000)\n"
            "- min_price_uzs: integer in UZS or null\n"
            "- owner_only: boolean (true if mentions maklersiz, egasidan, bez makler, without broker)\n"
            "- target_audience: 'family' | 'female' | 'male' | 'students' | 'any'\n"
            "- is_furnished: boolean or null\n"
            "- reasoning: string in Uzbek briefly explaining what was detected.\n"
            "Return ONLY the raw JSON object, no markdown, no backticks."
        )
        response_text = None
        if self.gemini_key:
            response_text = await self._call_gemini(query, system_prompt)
        elif self.groq_key:
            response_text = await self._call_groq(query, system_prompt)
        elif self.openrouter_key:
            response_text = await self._call_openrouter(query, system_prompt)

        if response_text:
            return self._clean_and_parse_json(response_text)
        return None

    async def evaluate_listing(
        self, listing_data: Dict[str, Any], user_question: str
    ) -> str:
        """Deeply analyze and answer user questions regarding a specific apartment listing."""
        sys_p = (
            "Siz «Joyliy» ko'chmas mulk platformasining mustaqil ekspertisiz. "
            "Berilgan kvartira e'loni ma'lumotlarini chuqur tahlil qilib, foydalanuvchining "
            "savoliga xolis, professional va amaliy javob bering. Narx adolatliligi, egasidanligi "
            "yoki vositachi xavfi, e'lon matnidagi shubhali joylarni ko'rsatib bering."
        )
        context = (
            f"Kvartira ma'lumotlari:\n"
            f"- Sarlavha: {listing_data.get('title')}\n"
            f"- Narxi: {listing_data.get('price_uzs', 0):,} so'm\n"
            f"- Tuman: {listing_data.get('district')}\n"
            f"- Maydoni: {listing_data.get('area')} m², {listing_data.get('rooms')} xona\n"
            f"- Egasidan: {'Ha (maklersiz)' if listing_data.get('is_owner') else 'Tekshiruvda/vositachi'}\n"
            f"- Tavsif: {listing_data.get('description', '')[:500]}\n"
        )
        return await self.generate_response(user_question, sys_p, context)

    def _clean_and_parse_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Safely extract JSON object from LLM response text."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
        try:
            return json.loads(text)
        except Exception as e:
            logger.debug("Failed to parse LLM JSON: %s (raw text: %s)", e, text[:120])
            return None

    async def _call_gemini(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Google Gemini 2.0 / 1.5 Flash (Free Tier)."""
        key = self.gemini_key
        if not key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": message}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 900},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
        except Exception as e:
            logger.warning("Gemini free API call failed: %s", e)
        return None

    async def _call_groq(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Groq Cloud (Free Tier - Llama 3.3 70B)."""
        key = self.groq_key
        if not key:
            return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": 0.3,
            "max_tokens": 900,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0]["message"]["content"].strip()
        except Exception as e:
            logger.warning("Groq free API call failed: %s", e)
        return None

    async def _call_openrouter(self, message: str, system_prompt: str) -> Optional[str]:
        """Call OpenRouter Free Tier (gemini-2.0-flash-lite:free or meta-llama/llama-3.2-3b-instruct:free)."""
        key = self.openrouter_key
        if not key:
            return None
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://joyliy.onrender.com",
            "X-Title": "Joyliy PropTech",
        }
        payload = {
            "model": "google/gemini-2.0-flash-lite:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": 0.3,
            "max_tokens": 900,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0]["message"]["content"].strip()
        except Exception as e:
            logger.warning("OpenRouter free call failed: %s", e)
        return None

    async def _call_free_open_llm(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Zero-Key Free Public LLM endpoint (Pollinations AI with rate limit protection)."""
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "model": "openai",
            "seed": 42,
            "jsonMode": False,
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Joyliy-PropTech/1.0",
        }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    text = resp.text.strip()
                    if text and len(text) > 10 and "free limit reached" not in text.lower():
                        return text
        except Exception as e:
            logger.debug("Free open LLM call exception: %s", e)
        return None

    def _local_fallback(self, query: str, context: Optional[str] = None) -> str:
        """Deterministic, comprehensive local rental intelligence when offline or rate-limited."""
        q = query.lower()

        # Contract, taxes, registration
        if any(w in q for w in ["shartnoma", "soliq", "propiska", "qonun", "dokument", "hujjat", "договор", "налог"]):
            return (
                "📄 **Ijara shartnomasi va Soliq qoidalari (O‘zbekiston):**\n\n"
                "1. **Qonuniy asos:** O‘zbekiston Respublikasi Fuqarolik kodeksining 535-moddasiga binoan, turar joy "
                "ijarasi yozma shartnoma asosida rasmiylashtiriladi.\n"
                "2. **Davlat ro‘yxati (ijara.soliq.uz):** Shartnomani davlat soliq xizmati portalida (ijara.soliq.uz) "
                "onlayn hisobga qo‘yish shart. Bu bepul amalga oshiriladi va ijarachiga vaqtincha ro‘yxatda turish "
                "(vaqtincha propiska) huquqini beradi.\n"
                "3. **Kafolat:** Shartnomasiz yashash uy egasi istagan paytda uydan chiqarib yuborishi yoki narxni "
                "asossiz oshirishi xavfini tug‘diradi. Shartnomada ijara narxi va muddati qat’iy belgilanishi shart."
            )

        # Deposit, zalog, security
        if any(w in q for w in ["zalog", "depozit", "garov", "qaytarish", "залог", "депозит"]):
            return (
                "💰 **Zalog (Depozit) qaytarilish tartibi:**\n\n"
                "1. **Maqsadi:** Zalog odatda 1 oylik ijara miqdorida olinadi va uydagi mebel, texnika butligini "
                "hamda kommunal to‘lovlar qarzini qoplash uchun kafolat hisoblanadi.\n"
                "2. **Dalolatnoma (Akt):** Ko‘chib kirgan birinchi kuni kvartiradagi barcha jihozlar holatini "
                "fotosurat/videoga oling va kamchiliklarni (tirnalgan joylar, nosoz kranlar) aktga yozdiring.\n"
                "3. **Qaytarish:** Ijara muddati tugab, xonadon o‘z holida topshirilganda, uy egasi zalogni "
                "to‘liq qaytarishi shart. Asossiz ushlab qolish qonunga xilofdir."
            )

        # Utilities, communal
        if any(w in q for w in ["kommunal", "schetchik", "svet", "gaz", "suv", "коммунал", "счетчик"]):
            return (
                "⚡ **Kommunal to‘lovlar taqsimoti:**\n\n"
                "1. **Ijarachi to‘laydi:** Sovuq suv, issiq suv, tabiiy gaz va elektr energiyasi (barchasi hisoblagich "
                "/ schetchik ko‘rsatkichlari bo‘yicha ijarachi tomonidan sarflangan miqdorda to‘lanadi).\n"
                "2. **Uy egasi to‘laydi:** Binoga xizmat ko‘rsatish badallari (kvartplata / shirkat / domkom), "
                "markaziy isitish (otoplenie) va obodonlashtirish xarajatlari mulkdor zimmasida bo‘ladi.\n"
                "3. **Kirishdagi qoida:** Ko‘chib kirgan kuni barcha schetchiklar ko‘rsatkichlarini rasmga oling va "
                "avvalgi qarzdorliklar to‘langanligini tekshiring."
            )

        # Makler vs Owner, Commission
        if any(w in q for w in ["makler", "komissiya", "vositachi", "rieltor", "maklersiz", "риелтор", "комиссия"]):
            return (
                "🔑 **Maklersiz to‘g‘ridan-to‘g‘ri ijara maslahatlari:**\n\n"
                "1. **Joyliy afzalligi:** Joyliy platformasida barcha e’lonlar AI filtrlari yordamida tekshiriladi "
                "va faqat mulk egalaridan bo‘lgan e’lonlarga urg‘u beriladi — 0% komissiya.\n"
                "2. **Bozordagi vositachilar:** Toshkentda odatda maklerlar birinchi oylik to‘lovdan 30% dan 50% gacha "
                "bir martalik haq olishadi. Siz ularga shartnoma tuzish va kadastrni tekshirishdan oldin hech qanday to‘lov qilmang.\n"
                "3. **Hujjat tekshiruvi:** Uchrashuvda uy egasidan kadastr pasporti va shaxsini tasdiqlovchi hujjatni so‘rang."
            )

        # Scam prevention
        if any(w in q for w in ["firibgar", "aldov", "zakalat", "avans", "karta", "мошенник", "предоплата"]):
            return (
                "🛡 **Firibgarlardan himoyalanish (Qat’iy qoidalar):**\n\n"
                "1. **Oldindan pul o‘tkazmang:** Uyni o‘z ko‘zingiz bilan ko‘rmasdan, uy egasining kadastr hujjatini "
                "tekshirmasdan oldin hech qachon karta raqamiga «bron» yoki «zakalat» o‘tkazmang!\n"
                "2. **Arzon narx tuzog‘i:** Agar shahar markazida chiroyli ta’mirlangan uy juda arzon (masalan 2 mln so‘m) "
                "taklif qilinib, «odam ko‘p, kartamga avans tashlasangiz sizga saqlab turaman» deyilsa — bu 99% firibgardir.\n"
                "3. **Faqat Joyliyda tekshirilgan:** Shubhali e’lonlar ustidagi «Shikoyat qilish» tugmasi orqali xabar bering."
            )

        # Default helpful advisor
        return (
            "Salom! Men Joyliy platformasining AI ijara maslahatchisiman.\n\n"
            "Toshkentda xonadon ijarasi, qonuniy shartnoma tuzish (ijara.soliq.uz), zalogni qaytarish tartibi, "
            "kommunal to‘lovlar yoki tumanlar bo‘yicha narxlar tahlili haqida istalgan savolingizni bering. "
            "Sizga eng to‘g‘ri va xavfsiz yo‘lni ko‘rsatib beraman!"
        )


free_llm_service = FreeLLMService()


