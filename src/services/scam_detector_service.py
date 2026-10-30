"""Scam Detector: Multi-Signal Fraud Prevention, Risk Scoring, and Report Moderation."""

from __future__ import annotations

import re
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing
from src.models.ecosystem import ListingReport
from src.services.neighborhood_service import TASHKENT_DISTRICTS

logger = logging.getLogger(__name__)

SUSPICIOUS_PHRASES = [
    (r'(?:oldindan\s+to[\'‘]lov|предоплат|залог\s+до\s+просмотра)', "Ko‘rishdan oldin pul o‘tkazish (oldindan to‘lov) so‘ralgan", 30),
    (r'(?:zakalat|задат(?:ок|ка)|avans|аванс)', "Ko‘rishdan oldin zakalat yoki avans talab qilingan", 35),
    (r'(?:karta(?:ga)?\s+.*?(?:tashlang|o[\'‘]tkazing)|переве(?:дите|сти)\s+на\s+карту)', "Bank kartasiga pul talab qilingan", 35),
    (r'(?:t\.me\/(?:joinchat|\+[a-zA-Z0-9_-]+))', "Shubhali Telegram guruh yoki havola kiritilgan", 25),
    (r'(?:bit\.ly|tinyurl|clck\.ru|cutt\.ly)', "Qisqartirilgan tashqi havola (phishing xavfi)", 30),
    (r'(?:chet\s+elga\s+ketganman|уехал\s+за\s+границу)', "«Chet elga ketganman, kalitni pochta orqali beraman» kabi firibgarlik sxemasi", 40),
]


class ScamDetectorService:
    """Evaluates risk indicators for apartment advertisements to protect seekers from fraudulent offers."""

    async def analyze_listing_risk(
        self, session: AsyncSession, listing: Listing
    ) -> Dict[str, Any]:
        """
        Evaluate listing across multiple fraud signals:
        - Price anomaly vs district median
        - High-risk keywords (prepayment, phishing links)
        - Phone number multi-listing abuse
        - Photo/description reuse
        """
        risk_score = 5  # Baseline minimal risk
        reasons: List[str] = []

        desc = (listing.description or "")
        title = (listing.title or "")
        combined_text = f"{title}\n{desc}".lower()

        # 1. Suspicious phrase detection
        for pattern, warning_text, penalty in SUSPICIOUS_PHRASES:
            if re.search(pattern, combined_text, re.IGNORECASE):
                risk_score += penalty
                reasons.append(warning_text)

        # 2. Abnormal low price detection
        if listing.price_uzs and listing.price_uzs > 0 and listing.district:
            district_clean = listing.district.strip()
            dist_info = TASHKENT_DISTRICTS.get(district_clean)
            if dist_info:
                rooms = min(listing.rooms or 2, 3)
                bench_price = dist_info.get(f"avg_rent_{rooms}room_uzs", 4500000)
                # If price is lower than 50% of the district's average
                if listing.price_uzs < (bench_price * 0.45):
                    risk_score += 35
                    reasons.append(f"Narx shubhali darajada arzon ({listing.price_uzs:,} so‘m — o‘rtachadan 50%+ past)")
                elif listing.price_uzs < (bench_price * 0.65):
                    risk_score += 15
                    reasons.append(f"Narx tuman o‘rtacha ko‘rsatkichidan ancha past")

        # 3. Repeated phone number across unrelated listings check
        if listing.contact_phone:
            phone_count_stmt = select(func.count(Listing.id)).where(
                and_(
                    Listing.contact_phone == listing.contact_phone,
                    Listing.id != (listing.id or 0),
                    Listing.is_active == True,
                )
            )
            phone_count = (await session.execute(phone_count_stmt)).scalar() or 0
            if phone_count >= 8:
                risk_score += 20
                reasons.append(f"Ushbu raqam orqali 8 tadan ortiq boshqa e‘lonlar joylashtirilgan (vositachi bo‘lishi mumkin)")

        # 4. Repeated photo / image fingerprint reuse check
        if listing.image_fingerprint:
            img_count_stmt = select(func.count(Listing.id)).where(
                and_(
                    Listing.image_fingerprint == listing.image_fingerprint,
                    Listing.id != (listing.id or 0),
                )
            )
            img_count = (await session.execute(img_count_stmt)).scalar() or 0
            if img_count >= 3:
                risk_score += 25
                reasons.append("Ushbu e‘lon fotosuratlari boshqa e‘lonlarda ham aynan takrorlangan")

        # 5. Missing price or contact details
        if not listing.price_uzs or listing.price_uzs <= 0:
            risk_score += 10
            reasons.append("Aniq narx ko‘rsatilmagan")

        # Calculate final level
        final_score = max(5, min(100, risk_score))
        if final_score <= 25:
            level = "low"
            level_label = "Xavfsiz (Past xavf)"
            badge_color = "#10B981"  # Emerald green
        elif final_score <= 55:
            level = "medium"
            level_label = "Ehtiyot bo‘ling (O‘rta xavf)"
            badge_color = "#F59E0B"  # Amber
        else:
            level = "high"
            level_label = "Yuqori xavf (Shubhali)"
            badge_color = "#EF4444"  # Red

        return {
            "risk_score": final_score,
            "risk_level": level,
            "risk_level_label": level_label,
            "badge_color": badge_color,
            "reasons": reasons if reasons else ["Barcha asosiy xavfsizlik tekshiruvlaridan muvaffaqiyatli o‘tdi"],
        }

    async def submit_user_report(
        self,
        session: AsyncSession,
        listing_id: int,
        reason: str,
        details: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> ListingReport:
        """Submit a user complaint/report for a suspicious apartment listing."""
        report = ListingReport(
            listing_id=listing_id,
            user_id=user_id,
            reason=reason,
            details=details,
            status="pending",
        )
        session.add(report)
        await session.commit()
        logger.info("New scam/abuse report submitted for Listing #%d: reason=%s", listing_id, reason)
        return report

    async def get_all_reports(
        self, session: AsyncSession, status: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve recent reports for administrative moderation."""
        conditions = []
        if status:
            conditions.append(ListingReport.status == status)

        stmt = select(ListingReport).where(and_(*conditions)).order_by(ListingReport.created_at.desc()).limit(limit)
        reports = (await session.execute(stmt)).scalars().all()

        output = []
        for r in reports:
            output.append({
                "id": r.id,
                "listing_id": r.listing_id,
                "reason": r.reason,
                "details": r.details,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "listing_title": r.listing.title if r.listing else "O‘chirilgan e‘lon",
                "listing_url": r.listing.canonical_url if r.listing else None,
            })
        return output


scam_detector_service = ScamDetectorService()
