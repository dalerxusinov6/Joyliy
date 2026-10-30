"""AI Virtual Apartment Assistant: Real Estate Consultation, Lease Advice, and Listing Evaluation."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing
from src.services.price_intelligence_service import price_intelligence_service
from src.services.scam_detector_service import scam_detector_service
from src.services.free_llm_service import free_llm_service

logger = logging.getLogger(__name__)


KNOWLEDGE_BASE_UZ = {
    "shartnoma": (
        "O‘zbekistonda ijara shartnomasini tuzish va ijara.soliq.uz orqali ro‘yxatdan o‘tkazish majburiydir. "
        "Shartnomada ijara narxi, to‘lov sanasi, depozit (zalog) miqdori va kommunal to‘lovlar kimning zimmasidaligi aniq ko‘rsatilishi kerak."
    ),
    "zalog": (
        "Zalog (garov puli) odatda 1 oylik to‘lov miqdorida olinadi. Uni to‘lashdan oldin shartnomaga yozdiring: "
        "«Ijara muddati tugab, xonadon topshirilgach, zalog to‘liq qaytariladi». Shuningdek, ko‘chib kirayotganda "
        "uydagi barcha kamchiliklarni fotosuratga olib, dalolatnoma qiling."
    ),
    "kommunal": (
        "Toshkentda odatda sovuq suv, issiq suv, gaz va elektr energiyasi hisoblagich (schetchik) bo‘yicha to‘lanadi. "
        "Isitish (otoplenie) va uy boshqaruvi (kvartplata/JEU) xarajatlarini aksariyat hollarda uy egasi to‘laydi. "
        "Buni oldindan kelishib oling."
    ),
    "savollar": (
        "Uy egasi bilan uchrashganda quyidagi 5 ta asosiy savolni bering:\n"
        "1. Kvartira kadastr hujjati va egalik huquqi kimning nomida?\n"
        "2. Qo‘shnilar kimlar va uyda tinchlik qoidalari qanday?\n"
        "3. Kommunal to‘lovlardan qarzdorlik yo‘qmi (kvitansiyalarni tekshiring)?\n"
        "4. Narx qancha muddatga o‘zgarmasdan kafolatlanadi?\n"
        "5. Zalog puli qanday shartlarda qaytariladi?"
    ),
}


class AIAssistantService:
    """Conversational real estate consultant providing grounded advice for Tashkent rentals."""

    async def get_response(
        self,
        session: AsyncSession,
        user_message: str,
        listing_id: Optional[int] = None,
        language: str = "uz",
    ) -> Dict[str, Any]:
        """Generate intelligent, verified real estate response."""
        msg_lower = user_message.lower()

        # If a specific listing is being consulted
        if listing_id:
            return await self._evaluate_specific_listing(session, listing_id, user_message, language)

        # 1. Try real free LLM generation with grounded Uzbekistan knowledge context
        llm_response = None
        if len(user_message.strip()) > 5:
            ctx_items = [f"{k.upper()}: {v}" for k, v in KNOWLEDGE_BASE_UZ.items()]
            ctx_str = "\n\n".join(ctx_items)
            try:
                llm_response = await free_llm_service.generate_response(
                    user_message=user_message,
                    context=ctx_str,
                )
            except Exception as e:
                logger.warning("LLM service call failed, using rule-based response: %s", e)

        if llm_response and len(llm_response.strip()) > 20:
            text = llm_response.strip()
            quick_topics = [
                "Ijara shartnomasi (soliq)",
                "Zalog (depozit) qaytarish",
                "Kommunal to‘lovlar",
                "Uy egasiga savollar",
            ]
        # 2. General rental advice fallback logic
        elif any(w in msg_lower for w in ["shartnoma", "договор", "contract", "soliq", "registratsiya", "propiska"]):
            text = (
                "📄 **Ijara shartnomasi va qonuniy masalalar:**\n\n"
                f"{KNOWLEDGE_BASE_UZ['shartnoma']}\n\n"
                "💡 *Maslahat:* Hech qachon shartnomasiz oldindan 2-3 oylik to‘lov bermang. "
                "Eganing pasporti va kadastr hujjatini shaxsan ko‘rib solishtiring."
            )
            quick_topics = ["Zalog puli qanday qaytariladi?", "Kommunal to‘lovlar tartibi", "Uy egasiga beriladigan savollar"]

        elif any(w in msg_lower for w in ["zalog", "залог", "deposit", "depozit", "garov"]):
            text = (
                "💰 **Depozit (Zalog) xavfsizligi:**\n\n"
                f"{KNOWLEDGE_BASE_UZ['zalog']}\n\n"
                "⚠️ *Ehtiyot bo‘ling:* Uyni shaxsan ko‘rmasdan yoki kalitni olmasdan turib bank kartasiga zalog tashlamang!"
            )
            quick_topics = ["Ijara shartnomasi", "Uy egasiga beriladigan savollar", "Bozor narxini tekshirish"]

        elif any(w in msg_lower for w in ["kommunal", "коммуналка", "svet", "gaz", "suv", "utilities", "schetchik"]):
            text = (
                "⚡️ **Kommunal to‘lovlar bo‘yicha tartib:**\n\n"
                f"{KNOWLEDGE_BASE_UZ['kommunal']}\n\n"
                "💡 Ko‘chib kirgan birinchi kuni hisoblagich (schetchik) ko‘rsatkichlarini rasmga olib uy egasiga yuboring."
            )
            quick_topics = ["Ijara shartnomasi", "Zalog qoidalari", "Eng qulay tumanlar"]

        elif any(w in msg_lower for w in ["savol", "savollar", "вопрос", "что спросить", "questions", "nima so‘rash"]):
            text = (
                "🗣 **Uy egasi bilan uchrashganda so‘raladigan muhim savollar:**\n\n"
                f"{KNOWLEDGE_BASE_UZ['savollar']}"
            )
            quick_topics = ["Shartnoma tuzish", "Firibgarlikdan saqlanish", "Chilonzorda ijara narxlari"]

        elif any(w in msg_lower for w in ["makler", "maklersiz", "rieltor", "komissiya", "риелтор"]):
            text = (
                "🤝 **Maklersiz ijara va komissiya:**\n\n"
                "Joyliy platformasi aynan **maklersiz, bevosita uy egalarining** e‘lonlarini avtomatlashtirilgan tahlil orqali ajratib beradi.\n\n"
                "Oddiy agentliklar birinchi oy to‘lovidan 50% komissiya oladi. Egasidan to‘g‘ridan-to‘g‘ri olsangiz, "
                "bu mablag‘ (masalan, 2-3 million so‘m) to‘liq cho‘ntagingizda qoladi."
            )
            quick_topics = ["Egasidan uylarni topish", "AI Qidiruv", "Taqqoslash"]

        else:
            text = (
                "Assalomu alaykum! Men Joyliy AI — Toshkentdagi ijara bo‘yicha shaxsiy virtual yordamchingizman.\n\n"
                "Men sizga quyidagi masalalarda yordam bera olaman:\n"
                "• Aniq bir kvartiraning narxi adolatli yoki yo‘qligini baholash\n"
                "• Ijara shartnomasi va zalog (depozit) xavfsizligi\n"
                "• Kommunal to‘lovlar va uy egasi bilan kelishuvlar\n"
                "• Firibgarlar tuzog‘iga tushib qolmaslik choralari\n\n"
                "Savolingizni yozing yoki pastdagi mavzulardan birini tanlang!"
            )
            quick_topics = ["Kvartira narxini tekshirish", "Ijara shartnomasi qoidalari", "Uy egasiga nimalar deyish kerak?"]

        return {
            "response": text,
            "reply": text,
            "quick_topics": quick_topics,
            "practical_tips": quick_topics,
            "legal_references": [
                "O‘zbekiston Respublikasi Fuqarolik kodeksi 535-modda",
                "ijara.soliq.uz davlat soliq xizmati elektron hisobi"
            ],
            "listing_evaluated": None,
        }

    async def _evaluate_specific_listing(
        self, session: AsyncSession, listing_id: int, user_message: str, language: str
    ) -> Dict[str, Any]:
        """Perform dedicated AI valuation and audit for an individual listing."""
        stmt = select(Listing).where(Listing.id == listing_id)
        listing = (await session.execute(stmt)).scalars().first()

        if not listing:
            return {
                "response": f"Kechirasiz, #{listing_id}-raqamli kvartira topilmadi.",
                "quick_topics": ["Boshqa kvartiralarni ko‘rish", "AI Qidiruv"],
                "listing_evaluated": None,
            }

        price_eval = await price_intelligence_service.evaluate_listing_price(session, listing)
        risk_eval = await scam_detector_service.analyze_listing_risk(session, listing)

        price_str = f"{listing.price_uzs:,} so‘m" if listing.price_uzs else "Kelishilgan"
        is_owner = bool(listing.classification and listing.classification.label == "LIKELY_OWNER")

        owner_txt = "✅ **Egasidan (Maklersiz)**" if is_owner else "⚠️ **Vositachi / Tekshiruvda**"
        price_status = price_eval.get("category_label", "Bozorbop")
        diff_p = price_eval.get("diff_percent", 0.0)

        risk_level = risk_eval.get("risk_level_label", "Xavfsiz")
        risk_reasons = "\n• ".join(risk_eval.get("reasons", []))

        verdict = (
            f"🏠 **#{listing.id} — «{listing.title}» tahlili:**\n\n"
            f"📍 **Hudud:** {listing.district or 'Toshkent'}\n"
            f"💰 **Narxi:** {price_str} ({price_status}, {diff_p:+}%\n"
            f"🔑 **Muallif:** {owner_txt}\n"
            f"🛡 **Xavfsizlik darajasi:** {risk_level}\n\n"
            f"📊 **Bozor tahlili:**\n"
            f"{price_eval.get('explanation')}\n\n"
            f"🔍 **Xavf ko‘rsatkichlari:**\n"
            f"• {risk_reasons}\n\n"
            f"💡 **Tavsiya:** Kvartirani shaxsan borib ko‘ring, uy egasining kadastr hujjatini tekshiring va ijara shartnomasini rasmiylashtiring."
        )

        custom_llm_advice = None
        if len(user_message.strip()) > 6 and not any(k in user_message.lower() for k in ["tahlil", "baholash", "evaluate"]):
            listing_dict = {
                "id": listing.id,
                "title": listing.title,
                "price_uzs": listing.price_uzs,
                "district": listing.district,
                "area": listing.area,
                "rooms": listing.rooms,
                "is_owner": is_owner,
                "description": listing.description,
            }
            try:
                custom_llm_advice = await free_llm_service.evaluate_listing(listing_dict, user_message)
            except Exception as e:
                logger.debug("Listing LLM evaluation fallback: %s", e)

        final_response = f"{custom_llm_advice}\n\n---\n{verdict}" if custom_llm_advice and len(custom_llm_advice.strip()) > 20 else verdict

        return {
            "response": final_response,
            "quick_topics": ["Egasi bilan uchrashuvda nima so‘rash kerak?", "Shartnoma tuzish", "Boshqa kvartiralar bilan solishtirish"],
            "listing_evaluated": {
                "id": listing.id,
                "title": listing.title,
                "price_uzs": listing.price_uzs,
                "district": listing.district,
                "fair_price_category": price_eval.get("category"),
                "scam_risk_level": risk_eval.get("risk_level"),
            },
        }


assistant_service = AIAssistantService()
