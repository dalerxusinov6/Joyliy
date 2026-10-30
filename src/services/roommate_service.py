"""Roommate Matching Engine: Profiles, Compatibility Scoring, and Connection Requests."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ecosystem import RoommateProfile, RoommateConnectionRequest

logger = logging.getLogger(__name__)

INITIAL_SEED_ROOMMATES = [
    {
        "name": "Javohir Karimov",
        "age": 22,
        "gender": "male",
        "budget_uzs": 1800000,
        "preferred_districts": ["Chilonzor", "Yakkasaroy"],
        "occupation": "student",
        "lifestyle_cleanliness": "very_clean",
        "lifestyle_sleep": "flexible",
        "smoking_allowed": False,
        "pets_allowed": False,
        "bio": "TATU 4-bosqich talabasiman. Dasturlash bilan shug‘ullanaman, tinchlikni va tozalikni yaxshi ko‘raman. Chilonzor yoki Yakkasaroydan 2-3 xonali uyga sherik qidiryapman.",
        "move_in_date": "Noyabr boshi",
        "contact_telegram": "javohir_dev",
        "is_verified": True,
    },
    {
        "name": "Madina Rahimova",
        "age": 23,
        "gender": "female",
        "budget_uzs": 2200000,
        "preferred_districts": ["Mirzo Ulug‘bek", "Yunusobod"],
        "occupation": "professional",
        "lifestyle_cleanliness": "very_clean",
        "lifestyle_sleep": "early_bird",
        "smoking_allowed": False,
        "pets_allowed": False,
        "bio": "Westminster yaqinida marketing sohasida ishlayman. Tartibli va xushmuomala qizlar bilan birga ijara turish uchun sherik izlayapman.",
        "move_in_date": "Darhol",
        "contact_telegram": "madina_mktg",
        "is_verified": True,
    },
    {
        "name": "Sardorbek & Bobur",
        "age": 21,
        "gender": "male",
        "budget_uzs": 1500000,
        "preferred_districts": ["Olmazor", "Shayxontohur"],
        "occupation": "student",
        "lifestyle_cleanliness": "moderate",
        "lifestyle_sleep": "night_owl",
        "smoking_allowed": False,
        "pets_allowed": False,
        "bio": "O‘zMU talabalarimiz. Beruniy metrosi atrofidan 3 kishilik sheriklikka 1 nafar toza yigit qidiryapmiz. Hamma sharoit bor.",
        "move_in_date": "15-noyabrgacha",
        "contact_telegram": "sardor_ozmu",
        "is_verified": True,
    },
    {
        "name": "Shahnoza Alimova",
        "age": 25,
        "gender": "female",
        "budget_uzs": 2500000,
        "preferred_districts": ["Mirobod", "Yakkasaroy"],
        "occupation": "professional",
        "lifestyle_cleanliness": "very_clean",
        "lifestyle_sleep": "early_bird",
        "smoking_allowed": False,
        "pets_allowed": True,
        "bio": "Xalqaro IT kompaniyada UI/UX dizaynerman. Kichik mushugim bor, juda madaniyatli. Mirobod yoki Oybek metro yaqinidan xonadon sherigi qidiryapman.",
        "move_in_date": "Shu oy oxiri",
        "contact_telegram": "shahnoza_design",
        "is_verified": True,
    },
]


class RoommateService:
    """Manages roommate discovery, compatibility calculations, and requests."""

    async def seed_initial_roommates_if_empty(self, session: AsyncSession) -> None:
        """Seed authentic Tashkent roommate profiles if table is empty."""
        count_stmt = select(func.count(RoommateProfile.id))
        count = (await session.execute(count_stmt)).scalar() or 0
        if count == 0:
            for item in INITIAL_SEED_ROOMMATES:
                p = RoommateProfile(**item)
                session.add(p)
            await session.commit()
            logger.info("Seeded %d initial roommate profiles.", len(INITIAL_SEED_ROOMMATES))

    async def list_profiles(
        self,
        session: AsyncSession,
        district: Optional[str] = None,
        gender: Optional[str] = None,
        max_budget: Optional[int] = None,
        occupation: Optional[str] = None,
        limit: int = 30,
        offset: int = 0,
    ) -> List[RoommateProfile]:
        """Query roommate profiles with multi-attribute filtering."""
        await self.seed_initial_roommates_if_empty(session)

        conditions = [RoommateProfile.is_active == True]
        if gender and gender != "any":
            conditions.append(or_(RoommateProfile.gender == gender, RoommateProfile.gender == "any"))
        if max_budget:
            conditions.append(RoommateProfile.budget_uzs <= max_budget)
        if occupation:
            conditions.append(RoommateProfile.occupation == occupation)

        stmt = select(RoommateProfile).where(and_(*conditions)).order_by(RoommateProfile.created_at.desc()).offset(offset).limit(limit)
        profiles = (await session.execute(stmt)).scalars().all()

        if district:
            d_clean = district.strip().lower()
            return [
                p for p in profiles
                if any(d_clean in (dist or "").lower() for dist in p.preferred_districts)
            ]
        return list(profiles)

    def calculate_compatibility(
        self, user_prefs: Dict[str, Any], profile: RoommateProfile
    ) -> Dict[str, Any]:
        """
        Calculate a compatibility match score (0-100%) between user requirements and profile.
        """
        score = 50
        reasons = []

        # 1. Budget alignment (up to +30%)
        user_budget = user_prefs.get("budget_uzs")
        if user_budget and profile.budget_uzs:
            diff_ratio = abs(user_budget - profile.budget_uzs) / max(user_budget, profile.budget_uzs)
            if diff_ratio <= 0.15:
                score += 30
                reasons.append("Byudjetingiz bir-biriga deyarli teng")
            elif diff_ratio <= 0.35:
                score += 15
                reasons.append("Byudjet oralig‘i yaqin")
            else:
                score -= 15

        # 2. District alignment (up to +25%)
        user_districts = [d.lower() for d in user_prefs.get("preferred_districts", [])]
        prof_districts = [d.lower() for d in (profile.preferred_districts or [])]
        common = set(user_districts).intersection(set(prof_districts))
        if common:
            score += 25
            reasons.append(f"Qidirayotgan tumanlaringiz mos keldi ({', '.join([c.capitalize() for c in common])})")
        else:
            score -= 10

        # 3. Gender alignment (up to +20%)
        user_gender = user_prefs.get("gender")
        if user_gender and profile.gender != "any":
            if user_gender == profile.gender:
                score += 20
                reasons.append("Jins talabi mos keldi")
            else:
                score -= 40
                reasons.append("Jins talabi to‘g‘ri kelmadi")

        # 4. Lifestyle & habits (up to +15%)
        if user_prefs.get("smoking") is not None:
            if user_prefs["smoking"] == profile.smoking_allowed:
                score += 10
                reasons.append("Chekishga munosabat bir xil")
        if user_prefs.get("pets") is not None:
            if user_prefs["pets"] == profile.pets_allowed:
                score += 10
                reasons.append("Uy hayvonlariga munosabat mos")

        final_score = max(20, min(99, score))
        return {
            "compatibility_percent": final_score,
            "score": final_score,
            "reasons": reasons[:3],
        }

    async def create_profile(
        self, session: AsyncSession, data: Dict[str, Any]
    ) -> RoommateProfile:
        """Create or update a user's roommate seeker profile."""
        profile = RoommateProfile(
            name=data["name"],
            age=data.get("age"),
            gender=data.get("gender", "any"),
            budget_uzs=int(data["budget_uzs"]),
            preferred_districts=data.get("preferred_districts", ["Chilonzor"]),
            occupation=data.get("occupation", "student"),
            lifestyle_cleanliness=data.get("lifestyle_cleanliness", "very_clean"),
            lifestyle_sleep=data.get("lifestyle_sleep", "flexible"),
            smoking_allowed=bool(data.get("smoking_allowed", False)),
            pets_allowed=bool(data.get("pets_allowed", False)),
            bio=data.get("bio", ""),
            move_in_date=data.get("move_in_date"),
            contact_telegram=data.get("contact_telegram", "").lstrip("@"),
            is_verified=True,
            is_active=True,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    async def send_connection_request(
        self, session: AsyncSession, roommate_id: int, from_name: str, from_contact: str, message: str
    ) -> RoommateConnectionRequest:
        """Send connection request to a prospective roommate."""
        req = RoommateConnectionRequest(
            roommate_id=roommate_id,
            from_name=from_name,
            from_contact=from_contact,
            message=message,
            status="pending",
        )
        session.add(req)
        await session.commit()
        return req


roommate_service = RoommateService()
