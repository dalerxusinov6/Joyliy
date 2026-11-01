"""Free AI / LLM Integration Service with Qwen and Multi-Tier Free Model Support.

Connects to free model providers in priority order:
1. Qwen 2.5 Free Suite:
   - OpenRouter Free Tier (qwen/qwen-2.5-72b-instruct:free, qwen/qwen-2.5-7b-instruct:free, qwen/qwen-2.5-coder-32b-instruct:free)
   - SiliconFlow Free Tier (Qwen/Qwen2.5-7B-Instruct via SILICONFLOW_API_KEY)
   - Alibaba DashScope Free Tier (qwen-plus / qwen-turbo via DASHSCOPE_API_KEY)
   - Groq Cloud Free Tier (qwen-2.5-32b via GROQ_API_KEY)
   - Hugging Face Free Serverless (Qwen/Qwen2.5-7B-Instruct via HF_TOKEN)
2. Google Gemini Free Tier (Gemini 2.0 Flash / 1.5 Flash via GEMINI_API_KEY or GOOGLE_API_KEY)
3. Groq Cloud Free Tier (Llama 3.3 70B via GROQ_API_KEY)
4. Pollinations AI Public Endpoint (polite zero-key free gateway)
5. Grounded Qwen-Aligned Uzbekistan Real Estate Knowledge & Heuristic Reasoning Engine (instant, 100% reliable)
"""

from __future__ import annotations

import asyncio
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
    "maslahatchisisiz (Qwen 2.5 asosida). Toshkent shahri ijara bozori, ijara shartnomalari (O‘zbekiston Respublikasi "
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
    def qwen_key(self) -> Optional[str]:
        return os.getenv("QWEN_API_KEY") or os.getenv("OPENROUTER_API_KEY") or getattr(settings, "OPENROUTER_API_KEY", None)

    @property
    def siliconflow_key(self) -> Optional[str]:
        return os.getenv("SILICONFLOW_API_KEY") or os.getenv("QWEN_API_KEY")

    @property
    def dashscope_key(self) -> Optional[str]:
        return os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")

    @property
    def hf_token(self) -> Optional[str]:
        return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")

    @property
    def gemini_key(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)

    @property
    def groq_key(self) -> Optional[str]:
        return os.getenv("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)

    @property
    def openrouter_key(self) -> Optional[str]:
        return os.getenv("OPENROUTER_API_KEY") or getattr(settings, "OPENROUTER_API_KEY", None)

    async def _call_qwen_openrouter(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Qwen 2.5 models on OpenRouter Free Tier."""
        key = self.openrouter_key or (self.qwen_key if self.qwen_key and not self.qwen_key.startswith("gsk_") else None)
        if not key:
            return None
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://joyliy.onrender.com",
            "X-Title": "Joyliy PropTech Qwen",
        }
        for qwen_model in [
            "qwen/qwen-2.5-72b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
            "qwen/qwen-2.5-coder-32b-instruct:free",
        ]:
            payload = {
                "model": qwen_model,
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
                            text = choices[0]["message"]["content"].strip()
                            if text:
                                return text
            except Exception as e:
                logger.debug("OpenRouter Qwen (%s) error: %s", qwen_model, e)
        return None

    async def _call_qwen_siliconflow(self, message: str, system_prompt: str) -> Optional[str]:
        """Call SiliconFlow Free Qwen 2.5 API."""
        key = self.siliconflow_key
        if not key:
            return None
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "Qwen/Qwen2.5-7B-Instruct",
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
            logger.debug("SiliconFlow Qwen error: %s", e)
        return None

    async def _call_qwen_dashscope(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Alibaba DashScope Qwen API."""
        key = self.dashscope_key
        if not key:
            return None
        url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "qwen-plus",
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
            logger.debug("DashScope Qwen error: %s", e)
        return None

    async def _call_qwen_groq(
        self, message: str, system_prompt: str, max_tokens: int = 1800
    ) -> Optional[str]:
        """Call Groq Cloud with Qwen 27B or GPT-OSS models."""
        key = self.groq_key or self.qwen_key
        if not key:
            return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        for model in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                "temperature": 0.2,
                "max_tokens": max_tokens,
            }
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            text = choices[0]["message"]["content"].strip()
                            if text:
                                return text
            except Exception as e:
                logger.debug("Groq (%s) error: %s", model, e)
        return None

    async def _call_qwen_hf(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Hugging Face Serverless Qwen 2.5 endpoint."""
        token = self.hf_token
        if not token:
            return None
        url = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-7B-Instruct/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "max_tokens": 800,
            "temperature": 0.3,
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
            logger.debug("HF Qwen error: %s", e)
        return None

    async def _call_qwen_suite(self, message: str, system_prompt: str) -> Optional[str]:
        """Orchestrate calls across all available Qwen free model providers."""
        # 1. Primary: Groq Qwen/GPT-OSS if key is configured (ultra-fast < 1s inference)
        if (self.groq_key and str(self.groq_key).startswith("gsk_")) or (self.qwen_key and str(self.qwen_key).startswith("gsk_")):
            res = await self._call_qwen_groq(message, system_prompt)
            if res:
                return res

        # 2. OpenRouter Qwen Free (72B / 7B / Coder)
        res = await self._call_qwen_openrouter(message, system_prompt)
        if res:
            return res

        # 3. SiliconFlow Free Qwen 7B
        res = await self._call_qwen_siliconflow(message, system_prompt)
        if res:
            return res

        # 4. Alibaba DashScope Qwen
        res = await self._call_qwen_dashscope(message, system_prompt)
        if res:
            return res

        # 5. Hugging Face Serverless Qwen 7B
        res = await self._call_qwen_hf(message, system_prompt)
        if res:
            return res

        # 6. Groq fallback
        res = await self._call_qwen_groq(message, system_prompt)
        if res:
            return res

        return None

    async def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """Generate response using Qwen free models with multi-tier provider fallbacks."""
        sys_p = system_prompt or JOYLIY_SYSTEM_PROMPT
        if context:
            full_user_content = f"Kontekst:\n{context}\n\nFoydalanuvchi so‘rovi:\n{user_message}"
        else:
            full_user_content = user_message

        # 1. Qwen 2.5 Suite (Primary AI engine per user specification)
        qwen_res = await self._call_qwen_suite(full_user_content, sys_p)
        if qwen_res:
            return qwen_res

        # 2. Google Gemini Free Tier
        if self.gemini_key:
            res = await self._call_gemini(full_user_content, sys_p)
            if res:
                return res

        # 3. Groq Cloud Free Tier (Llama 3.3 70B)
        if self.groq_key:
            res = await self._call_groq(full_user_content, sys_p)
            if res:
                return res

        # 4. OpenRouter Generic Free Tier
        if self.openrouter_key:
            res = await self._call_openrouter(full_user_content, sys_p)
            if res:
                return res

        # 5. Zero-Key Free Public LLM (Pollinations AI)
        res = await self._call_free_open_llm(full_user_content, sys_p)
        if res:
            return res

        # 6. Fallback to Grounded Qwen-Aligned Reasoning Engine
        return self._local_fallback(user_message, context)

    async def extract_search_criteria(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract structured JSON search criteria from conversational query using Qwen."""
        system_prompt = (
            "You are an expert real estate search query parser for Tashkent, Uzbekistan (powered by Qwen 2.5). "
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
        response_text = await self._call_qwen_suite(query, system_prompt)
        if not response_text and self.gemini_key:
            response_text = await self._call_gemini(query, system_prompt)
        if not response_text and self.groq_key:
            response_text = await self._call_groq(query, system_prompt)
        if not response_text and self.openrouter_key:
            response_text = await self._call_openrouter(query, system_prompt)

        if response_text:
            return self._clean_and_parse_json(response_text)
        return None

    async def evaluate_listing(
        self, listing_data: Dict[str, Any], user_question: str
    ) -> str:
        """Deeply analyze and answer user questions regarding a specific apartment listing using Qwen."""
        sys_p = (
            "Siz «Joyliy» ko'chmas mulk platformasining mustaqil tahlilchisisiz (Qwen 2.5). "
            "Berilgan kvartira e'loni ma'lumotlarini chuqur tahlil qilib, foydalanuvchining "
            "savoliga xolis, professional va amaliy javob bering. Narx adolatliligi, egasidanligi "
            "yoki vositachi xavfi, e'lon matnidagi shubhali joylarni ko'rsatib bering."
        )
        district = listing_data.get("district") or "Toshkent"
        price_uzs = listing_data.get("price_uzs") or 0
        area = listing_data.get("area") or 0
        price_per_m2 = int(price_uzs / area) if (price_uzs and area and area > 10) else None

        district_benchmarks = {
            "chilonzor": 75000,
            "yunusobod": 85000,
            "mirzo ulug‘bek": 95000,
            "mirobod": 125000,
            "yakkasaroy": 110000,
            "shayxontohur": 90000,
            "olmazor": 75000,
            "uchtepa": 70000,
            "yashnobod": 80000,
            "sergeli": 65000,
            "yangihayot": 60000,
            "bektemir": 55000,
        }
        benchmark = district_benchmarks.get(district.lower().strip(), 80000)
        context = (
            f"Kvartira ma'lumotlari:\n"
            f"- Sarlavha: {listing_data.get('title')}\n"
            f"- Narxi: {price_uzs:,} so'm ({f'{price_per_m2:,} so‘m/m²' if price_per_m2 else 'maydon ko‘rsatilmagan'})\n"
            f"- Tuman bo‘yicha o‘rtacha narx standarti: ~{benchmark:,} so‘m/m²\n"
            f"- Tuman: {district}\n"
            f"- Maydoni: {listing_data.get('area')} m², {listing_data.get('rooms')} xona\n"
            f"- Egasidan: {'Ha (maklersiz, 0% komissiya)' if listing_data.get('is_owner') else 'Tekshiruvda/vositachi'}\n"
            f"- Tavsif: {listing_data.get('description', '')[:500]}\n"
        )
        return await self.generate_response(user_question, sys_p, context)

    async def rank_listings_for_query(
        self, query: str, candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deeply analyze each apartment candidate against the user's search query using Groq Qwen/LLM.
        Batches items in parallel chunks of 10 for sub-2s responses with complete, untruncated JSON.
        """
        if not candidates:
            return []

        candidates_to_rank = candidates[:20]
        batches = [candidates_to_rank[i:i + 10] for i in range(0, len(candidates_to_rank), 10)]

        tasks = [self._rank_single_batch(query, b) for b in batches]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_ranks = []
        for r in batch_results:
            if isinstance(r, list):
                all_ranks.extend(r)
            elif isinstance(r, Exception):
                logger.debug("Batch Groq rank error: %s", r)
        return all_ranks

    async def _rank_single_batch(
        self, query: str, batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank a single batch of up to 10 candidates with Groq Qwen."""
        compact_items = []
        for c in batch:
            desc = (c.get("description") or "").replace("\n", " ").strip()
            compact_items.append({
                "id": c["id"],
                "title": c.get("title", ""),
                "price_uzs": c.get("price_uzs", 0),
                "district": c.get("district", ""),
                "rooms": c.get("rooms", 0),
                "target_audience": c.get("target_audience", "any"),
                "is_owner": bool(c.get("is_owner", False)),
                "metro": c.get("metro_station") or "",
                "description": desc[:200],
            })

        system_prompt = (
            "Siz Toshkent ko‘chmas mulk bozorining professional mustaqil AI tahlilchisisiz (Groq Qwen). "
            "Foydalanuvchi tabiiy tilda kvartira qidirmoqda. Siz berilgan har bir kvartira e'lonini "
            "foydalanuvchi so'rovi talablari bilan qat'iy va xolis solishtirib chiqishingiz kerak.\n\n"
            "BAHOLASH MEZONLARI:\n"
            "1. 'match_score': 0 dan 100 gacha butun son.\n"
            "   - Agar foydalanuvchi alohida/to'liq kvartira yoki oila uchun so'ragan bo'lsa, lekin e'lon sheriklikka (yigitlar/qizlar/talabalar koika/yotoqxona/подселение) bo'lsa, match_score 20 dan oshmasin va is_relevant=false bo'lsin!\n"
            "   - Agar tuman, xonalar soni va byudjet mos kelsa: 85-99% ball bering.\n"
            "   - Agar byudjetdan biroz oshsa (+15%) yoki xonasi 1 taga farq qilsa: 65-80% ball bering.\n"
            "   - Agar umuman boshqa tuman yoki so'rov talabiga mutlaqo zid bo'lsa: 0-35% ball bering.\n"
            "2. 'pros': Aynan foydalanuvchi so'roviga nisbatan 2-3 ta aniq ustunlik (o'zbek tilida, masalan: 'Chilonzorda 2 xonali to‘liq kvartira', 'Byudjetdan 500 ming so‘m tejaysiz', 'Egasidan to‘g‘ridan-to‘g‘ri').\n"
            "3. 'cons': 1-2 ta aniq kamchilik (masalan: 'Byudjetdan 400,000 so‘m qimmat', 'Alohida kvartira emas, sheriklik joy', 'Metro masofasi ko‘rsatilmagan').\n"
            "4. 'is_relevant': boolean (true - ko‘rishga arziydigan variant; false - so‘rovga zid yoki sheriklik joy).\n\n"
            "QAT'IY QOIDA: Faqat va faqat toza JSON massiv qaytaring:\n"
            "[ {\"id\": int, \"match_score\": int, \"pros\": [str], \"cons\": [str], \"is_relevant\": bool}, ... ]\n"
            "Hech qanday qo'shimcha so'z, izoh yoki markdown yozmang."
        )

        user_content = (
            f"Foydalanuvchi qidiruv so'rovi:\n«{query}»\n\n"
            f"Tahlil qilinishi kerak bo'lgan kvartiralar ro'yxati:\n"
            f"{json.dumps(compact_items, ensure_ascii=False, indent=1)}"
        )

        response_text = None
        if self.groq_key or self.qwen_key:
            response_text = await self._call_qwen_groq(user_content, system_prompt, max_tokens=2200)
        if not response_text:
            response_text = await self._call_qwen_suite(user_content, system_prompt)
        if not response_text and self.gemini_key:
            response_text = await self._call_gemini(user_content, system_prompt)

        if response_text:
            parsed_list = self._clean_and_parse_json_list(response_text)
            if parsed_list:
                return parsed_list

        return []

    def _clean_and_parse_json_list(self, raw_text: str) -> Optional[List[Dict[str, Any]]]:
        """Safely extract JSON list from LLM response text."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            text = match.group(0)
        try:
            val = json.loads(text)
            if isinstance(val, list):
                return val
        except Exception as e:
            logger.debug("Failed to parse LLM JSON list: %s (raw: %s)", e, text[:120])
        return None

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
        """Call Groq Cloud (Qwen 27B / GPT-OSS models)."""
        return await self._call_qwen_groq(message, system_prompt)

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


