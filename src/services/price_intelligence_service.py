"""Fair Price AI: Real Estate Price Intelligence, Market Valuation, and Price Drop Detection."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing
from src.models.ecosystem import ListingPriceHistory, SavedSearchAlert
from src.services.neighborhood_service import TASHKENT_DISTRICTS

logger = logging.getLogger(__name__)


class PriceIntelligenceService:
    """Calculates fair market valuation benchmarks and monitors price fluctuations."""

    def __init__(self):
        # District fallback median rates if sample size in DB is low
        self._district_defaults = {
            district: {
                1: info["avg_rent_1room_uzs"],
                2: info["avg_rent_2room_uzs"],
                3: info["avg_rent_3room_uzs"],
                4: int(info["avg_rent_3room_uzs"] * 1.3),
            }
            for district, info in TASHKENT_DISTRICTS.items()
        }

    async def get_district_market_stats(
        self, session: AsyncSession, district: Optional[str] = None
    ) -> Dict[str, Any]:
        """Aggregate actual active database listings to compute median and average prices."""
        conditions = [Listing.is_active == True, Listing.price_uzs > 0]
        if district:
            conditions.append(Listing.district.ilike(f"%{district.strip()}%"))

        # Query all matching prices and rooms
        stmt = select(Listing.price_uzs, Listing.rooms, Listing.area, Listing.district).where(and_(*conditions))
        rows = (await session.execute(stmt)).all()

        if not rows:
            return {
                "sample_size": 0,
                "overall_avg_uzs": 5000000,
                "room_breakdown": {},
            }

        room_groups: Dict[int, List[int]] = {}
        areas: List[float] = []
        all_prices: List[int] = []

        for p_uzs, rooms, area, dist in rows:
            all_prices.append(p_uzs)
            r_key = min(rooms or 1, 4)
            room_groups.setdefault(r_key, []).append(p_uzs)
            if area and area > 10:
                areas.append(area)

        all_prices.sort()
        n = len(all_prices)
        median_price = all_prices[n // 2] if n else 5000000
        avg_price = int(sum(all_prices) / n) if n else 5000000

        room_breakdown = {}
        for r, plist in room_groups.items():
            plist.sort()
            rn = len(plist)
            room_breakdown[r] = {
                "count": rn,
                "median_uzs": plist[rn // 2],
                "avg_uzs": int(sum(plist) / rn),
                "min_uzs": plist[0],
                "max_uzs": plist[-1],
            }

        avg_sqm_price = 0
        if areas and all_prices:
            total_area = sum(areas[:len(all_prices)])
            if total_area > 0:
                avg_sqm_price = int(sum(all_prices[:len(areas)]) / total_area)

        return {
            "sample_size": n,
            "district": district or "Toshkent (Barcha tumanlar)",
            "median_price_uzs": median_price,
            "avg_price_uzs": avg_price,
            "avg_sqm_price_uzs": avg_sqm_price,
            "room_breakdown": room_breakdown,
        }

    async def evaluate_listing_price(
        self, session: AsyncSession, listing: Listing
    ) -> Dict[str, Any]:
        """
        Evaluate listing rent against actual comparable listings.
        Returns fair price category: below_market, fair_price, above_market.
        """
        current_price = listing.price_uzs
        if not current_price or current_price <= 0:
            return {
                "category": "fair_price",
                "category_label": "Bozorbop (Fair Price)",
                "estimated_market_price": None,
                "diff_percent": 0.0,
                "diff_uzs": 0,
                "explanation": "Narx ko‘rsatilmagan yoki kelishilgan asosda.",
            }

        rooms = min(listing.rooms or 2, 4)
        district = listing.district or "Chilonzor"

        # 1. Fetch comparable listings from same district and room count
        comp_stmt = select(Listing.price_uzs).where(
            and_(
                Listing.district.ilike(f"%{district}%"),
                Listing.rooms == rooms,
                Listing.price_uzs > 0,
                Listing.is_active == True,
                Listing.id != (listing.id or 0),
            )
        )
        comp_prices = (await session.execute(comp_stmt)).scalars().all()

        if len(comp_prices) >= 3:
            comp_prices = sorted(comp_prices)
            estimated_market = comp_prices[len(comp_prices) // 2]
        else:
            # Fallback to district profile baseline
            district_map = self._district_defaults.get(district) or self._district_defaults.get("Chilonzor")
            estimated_market = district_map.get(rooms, 5000000)

        diff_uzs = current_price - estimated_market
        diff_percent = round((diff_uzs / estimated_market) * 100, 1)

        # Categorize
        if diff_percent <= -8.0:
            category = "below_market"
            category_label = "Bozor narxidan arzon (Below Market)"
            explanation = f"O‘xshash {rooms} xonali kvartiralarning o‘rtacha narxidan {abs(diff_percent)}% arzonroq (tejamkor taklif)."
        elif diff_percent >= 8.0:
            category = "above_market"
            category_label = "Bozor narxidan yuqori (Above Market)"
            explanation = f"Tuman bo‘yicha o‘xshash variantlardan {diff_percent}% qimmatroq (ta’mirlash yoki qulayliklar hisobiga bo‘lishi mumkin)."
        else:
            category = "fair_price"
            category_label = "Bozor narxida (Fair Price)"
            explanation = "Narx tuman o‘rtacha bozor darajasiga to‘liq mos keladi."

        return {
            "category": category,
            "category_label": category_label,
            "current_price_uzs": current_price,
            "estimated_market_price": estimated_market,
            "diff_percent": diff_percent,
            "diff_uzs": diff_uzs,
            "explanation": explanation,
        }

    async def record_price_change_if_any(
        self, session: AsyncSession, listing: Listing, old_price: int, new_price: int
    ) -> Optional[ListingPriceHistory]:
        """Record price reduction or increase and trigger alerts if dropped."""
        if not old_price or not new_price or old_price == new_price:
            return None

        diff_uzs = new_price - old_price
        diff_percent = round((diff_uzs / old_price) * 100, 2)

        history_item = ListingPriceHistory(
            listing_id=listing.id,
            old_price_uzs=old_price,
            new_price_uzs=new_price,
            diff_uzs=diff_uzs,
            diff_percent=diff_percent,
        )
        session.add(history_item)

        if diff_uzs < 0:
            logger.info(
                "PRICE DROP DETECTED for Listing #%d: %s -> %s UZS (%s%%)",
                listing.id,
                f"{old_price:,}",
                f"{new_price:,}",
                diff_percent,
            )

        return history_item


price_intelligence_service = PriceIntelligenceService()
