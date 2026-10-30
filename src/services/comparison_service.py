"""Shortlist Battle: Side-by-Side Apartment Comparison, Matrix Scoring, and AI Winner Selection."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing
from src.services.price_intelligence_service import price_intelligence_service
from src.services.scam_detector_service import scam_detector_service

logger = logging.getLogger(__name__)


class ComparisonService:
    """Evaluates 2 to 5 apartments side-by-side, computes metric differences, and chooses the best overall value."""

    async def compare_listings(
        self, session: AsyncSession, listing_ids: List[int]
    ) -> Dict[str, Any]:
        """Generate structured comparison table and select top recommendation."""
        if not listing_ids:
            return {"error": "Kamida 2 ta kvartira tanlanishi kerak", "items": []}

        stmt = select(Listing).where(Listing.id.in_(listing_ids[:5]))
        listings = (await session.execute(stmt)).scalars().all()

        if len(listings) < 2:
            return {
                "error": "Taqqoslash uchun kamida 2 ta mavjud kvartira kerak",
                "items": [self._format_card(l) for l in listings],
            }

        detailed_items = []
        winner_id = None
        best_composite_score = -1.0

        for l in listings:
            # 1. Price intelligence
            price_eval = await price_intelligence_service.evaluate_listing_price(session, l)
            # 2. Scam risk evaluation
            risk_eval = await scam_detector_service.analyze_listing_risk(session, l)

            # Price per square meter
            price_per_sqm = int(l.price_uzs / l.area) if (l.price_uzs and l.area and l.area > 5) else 0

            # Composite Value Score (0 - 100)
            score = 60.0

            # Cheaper relative to market is better
            diff_pct = price_eval.get("diff_percent", 0.0)
            if diff_pct < 0:
                score += min(20.0, abs(diff_pct) * 1.5)  # Below market bonus
            else:
                score -= min(20.0, diff_pct * 1.2)

            # Owner status bonus
            if l.classification and l.classification.label == "LIKELY_OWNER":
                score += 15.0
            elif l.classification and l.classification.label == "LIKELY_AGENT":
                score -= 10.0

            # Metro proximity bonus
            if l.metro_distance_m:
                if l.metro_distance_m <= 800:
                    score += 10.0
                elif l.metro_distance_m <= 1500:
                    score += 5.0

            # Low scam risk bonus
            r_score = risk_eval.get("risk_score", 10)
            if r_score <= 20:
                score += 10.0
            elif r_score >= 50:
                score -= 20.0

            if score > best_composite_score:
                best_composite_score = score
                winner_id = l.id

            detailed_items.append({
                "id": l.id,
                "title": l.title,
                "canonical_url": l.canonical_url,
                "price_uzs": l.price_uzs,
                "price_formatted": f"{l.price_uzs:,} so‘m" if l.price_uzs else "Kelishilgan",
                "district": l.district or "Noma’lum",
                "rooms": l.rooms or 1,
                "area": l.area or 0,
                "price_per_sqm_uzs": price_per_sqm,
                "floor": l.floor or "—",
                "is_owner": bool(l.classification and l.classification.label == "LIKELY_OWNER"),
                "owner_label": "Egasidan (Maklersiz)" if (l.classification and l.classification.label == "LIKELY_OWNER") else "Agentlik / Tekshirilmoqda",
                "metro_station": l.metro_station or "—",
                "metro_distance_m": l.metro_distance_m,
                "fair_price_category": price_eval.get("category"),
                "fair_price_label": price_eval.get("category_label"),
                "price_diff_percent": price_eval.get("diff_percent"),
                "scam_risk_level": risk_eval.get("risk_level"),
                "scam_risk_label": risk_eval.get("risk_level_label"),
                "image_url": l.image_urls[0] if (l.image_urls and len(l.image_urls) > 0) else None,
                "composite_score": round(score, 1),
                "is_winner": False,
            })

        # Set winner badge and AI summary
        winner_item = None
        for item in detailed_items:
            if item["id"] == winner_id:
                item["is_winner"] = True
                winner_item = item

        summary = self._generate_ai_summary(winner_item, len(detailed_items))

        return {
            "total_compared": len(detailed_items),
            "winner_listing_id": winner_id,
            "ai_comparison_summary": summary,
            "items": detailed_items,
        }

    def _format_card(self, l: Listing) -> Dict[str, Any]:
        return {
            "id": l.id,
            "title": l.title,
            "price_uzs": l.price_uzs,
            "district": l.district,
            "rooms": l.rooms,
            "area": l.area,
        }

    def _generate_ai_summary(self, winner: Optional[Dict[str, Any]], count: int) -> str:
        if not winner:
            return "Kvartiralar ko‘rsatkichlari bo‘yicha deyarli teng."

        pros_txt = []
        if winner.get("is_owner"):
            pros_txt.append("maklersiz egasidan bo‘lgani")
        if (winner.get("price_diff_percent") or 0) < 0:
            pros_txt.append(f"bozor narxidan {abs(winner['price_diff_percent'])}% arzonligi")
        if winner.get("metro_distance_m") and winner["metro_distance_m"] <= 1000:
            pros_txt.append(f"metroga yaqinligi ({winner['metro_distance_m']}m)")

        reasons = ", ".join(pros_txt) if pros_txt else "eng yaxshi narx va sharoit mutanosibligi"
        return (
            f"Taqqoslangan {count} ta variant orasida #{winner['id']} ({winner['district']}, {winner['rooms']} xona) "
            f"eng maqbul tanlov deb topildi: {reasons} hisobiga g‘olib bo‘ldi."
        )


comparison_service = ComparisonService()
