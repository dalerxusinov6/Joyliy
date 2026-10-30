"""Free AI / LLM Integration Service.

Connects to free model providers in priority order:
1. Google Gemini Free Tier (if GEMINI_API_KEY is configured in environment)
2. Groq Free Tier (if GROQ_API_KEY is configured)
3. Zero-Key Open LLM Provider (Pollinations AI public API - 100% free, no key needed)
4. Offline Rule-Based Fallback (guaranteed zero downtime)
"""

from __future__ import annotations

import logging
import os
from typing import List, Dict, Optional, Any
import httpx

from src.config import settings

logger = logging.getLogger(__name__)

JOYLIY_SYSTEM_PROMPT = (
    "Siz — «Joyliy» ko‘chmas mulk va ijara platformasining professional, xushmuomala sun’iy intellekt "
    "maslahatchisisiz. Toshkent shahri ijara bozori, ijara shartnomalari (O‘zbekiston Respublikasi "
    "Fuqarolik kodeksi 535-modda), soliq tizimi (ijara.soliq.uz portalida ro‘yxatdan o‘tkazish), "
    "garov puli (zalog/depozit) qaytarilish qoidalari, kommunal to‘lovlar (schetchiklar) va "
    "firibgarlikdan (ko‘rishdan oldin plastik kartaga pul talab qilish) himoyalanish bo‘yicha "
    "aniq, amaliy va ishonchli maslahat berasiz. "
    "Foydalanuvchining tilida (O‘zbek, Rus yoki Ingliz) tushunarli, qisqa va aniq javob bering."
)


class FreeLLMService:
    """Manages connections to free LLM endpoints with zero-key fallback."""

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        self.groq_key = os.getenv("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)
        self.timeout = 10.0

    async def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """Generate response using the best available free LLM provider."""
        sys_p = system_prompt or JOYLIY_SYSTEM_PROMPT
        if context:
            full_user_content = f"Kontekst:\n{context}\n\nFoydalanuvchi so‘rovi:\n{user_message}"
        else:
            full_user_content = user_message

        # 1. Try Google Gemini if API key configured
        if self.gemini_key:
            res = await self._call_gemini(full_user_content, sys_p)
            if res:
                return res

        # 2. Try Groq if API key configured
        if self.groq_key:
            res = await self._call_groq(full_user_content, sys_p)
            if res:
                return res

        # 3. Try Zero-Key Free Open LLM (Pollinations AI)
        res = await self._call_free_open_llm(full_user_content, sys_p)
        if res:
            return res

        # 4. Fallback to local heuristic answer
        return self._local_fallback(user_message)

    async def _call_gemini(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Google Gemini 2.0 / 1.5 Flash (Free Tier)."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": message}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800},
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
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": 0.3,
            "max_tokens": 800,
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

    async def _call_free_open_llm(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Zero-Key Free Public LLM endpoint (Pollinations AI)."""
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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    text = resp.text.strip()
                    if text and len(text) > 10:
                        return text
        except Exception as e:
            logger.debug("Free open LLM call exception: %s", e)
        return None

    def _local_fallback(self, query: str) -> str:
        """Deterministic fallback when all remote network LLM calls fail."""
        q = query.lower()
        if "shartnoma" in q or "soliq" in q or "propiska" in q:
            return (
                "O‘zbekiston Respublikasi Fuqarolik kodeksi 535-moddasiga ko‘ra, ijara shartnomasi yozma "
                "ravishda tuzilishi va ijara.soliq.uz davlat soliq xizmati portalida ro‘yxatdan o‘tkazilishi shart. "
                "Bu ijarachi uchun noqonuniy haydab chiqarishdan himoya, uy egasi uchun esa kafolatdir."
            )
        if "zalog" in q or "depozit" in q:
            return (
                "Zalog (depozit) odatda 1 oylik to‘lov miqdorida mol-mulk butligini kafolatlash uchun olinadi. "
                "Ko‘chib kirish kuni barcha jihozlar holatini fotosuratga olib, dalolatnoma tuzing. "
                "Uydan chiqishda mol-mulkka zarar yetmagan bo‘lsa, zalog to‘liq qaytarilishi shart."
            )
        if "kommunal" in q or "schetchik" in q:
            return (
                "Toshkent shahrida sovuq va issiq suv, gaz hamda elektr energiyasi odatda hisoblagich (schetchik) "
                "bo‘yicha ijarachi tomonidan to‘lanadi. Bino xizmati (kvartplata/domkom) va isitish xarajatlari "
                "esa qoidaga ko‘ra uy egasi zimmasida bo‘ladi."
            )
        return (
            "Joyliy platformasi Toshkent shahrida toza, xavfsiz va vositachisiz (maklersiz) ijara topishga "
            "yordam beradi. Uyni ko‘rishdan oldin hech qachon kartaga zakalat yoki avans to‘lamang. "
            "Xonadon egalik kadastrini va pasportini shaxsan tekshirib, shartnoma tuzing."
        )


free_llm_service = FreeLLMService()
