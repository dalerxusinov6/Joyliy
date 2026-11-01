"""AI Apartment Match: Natural Language Query Parsing, Semantic Scoring, and Recommendation Explanations."""

from __future__ import annotations

import re
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing, ListingClassification
from src.services.neighborhood_service import TASHKENT_DISTRICTS, TASHKENT_METRO_STATIONS

logger = logging.getLogger(__name__)

USD_RATE = 12800.0


class AIMatchService:
    """Parses natural-language queries into structured filters and ranks listings with match percentages."""

    def parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Extract structured search criteria from natural-language text in Uzbek, Russian, or English.
        Example: 'Chilonzor metrosi yonida 3 xonali kvartira, 4 million so‘mgacha, maklersiz'
        """
        text = query.lower()
        extracted: Dict[str, Any] = {
            "original_query": query,
            "district": None,
            "metro": None,
            "max_price_uzs": None,
            "min_price_uzs": None,
            "rooms": None,
            "owner_only": False,
            "near_metro": False,
            "is_furnished": None,
            "target_audience": "any",
            "tags": [],
        }

        # 1. District extraction
        for dist_key, dist_info in TASHKENT_DISTRICTS.items():
            names = [
                dist_key.lower(),
                dist_info["name_ru"].lower(),
                dist_info["name_en"].lower(),
            ]
            if any(n in text for n in names):
                extracted["district"] = dist_key
                extracted["tags"].append(f"📍 {dist_key}")
                break

        # 2. Metro station extraction
        for station in TASHKENT_METRO_STATIONS:
            aliases = station.get("aliases", [station["name"].lower()])
            if any(a in text for a in aliases):
                extracted["metro"] = station["name"]
                extracted["near_metro"] = True
                extracted["tags"].append(f"🚇 {station['name']} metro")
                if not extracted["district"]:
                    extracted["district"] = station["district"]
                break

        if not extracted["near_metro"]:
            if any(w in text for w in ["metro", "метро", "subway"]):
                extracted["near_metro"] = True
                extracted["tags"].append("🚇 Metroga yaqin")

        # 3. Price extraction
        # USD check ($500, 500$, 500 dollar, 500 usd)
        usd_match = re.search(r'(\d+)\s*(?:\$|usd|долл|dollar)', text)
        if usd_match:
            val_usd = int(usd_match.group(1))
            extracted["max_price_uzs"] = int(val_usd * USD_RATE)
            extracted["tags"].append(f"💰 Max {val_usd}$ (~{int(val_usd * USD_RATE / 1e6)} mln)")
        else:
            # UZS check: e.g. "4 mln", "4.5 million", "4 000 000", "4000000"
            mln_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:mln|million|миллион|млн)', text)
            if mln_match:
                mln_val = float(mln_match.group(1).replace(",", "."))
                extracted["max_price_uzs"] = int(mln_val * 1_000_000)
                extracted["tags"].append(f"💰 Max {mln_val} mln so‘m")
            else:
                num_match = re.search(r'(\d[\d\s]{5,})\s*(?:so[\'‘]m|сум|uzs)?', text)
                if num_match:
                    raw_num = int(re.sub(r'\s+', '', num_match.group(1)))
                    extracted["max_price_uzs"] = raw_num
                    extracted["tags"].append(f"💰 Max {raw_num:,} so‘m")

        # 4. Rooms extraction
        # e.g. "3 xonali", "3-xonali", "3 комнатная", "3 комн", "3 room", "3 bedroom", "studiya"
        if "studiya" in text or "студия" in text or "studio" in text:
            extracted["rooms"] = 1
            extracted["tags"].append("🏠 Studiya / 1 xona")
        else:
            room_match = re.search(r'(\d)\s*(?:xona|xonali|комн|комнат|комнатная|комнатную|room|bedroom|bdr)', text)
            if room_match:
                extracted["rooms"] = int(room_match.group(1))
                extracted["tags"].append(f"🏠 {extracted['rooms']} xonali")

        # 5. Owner only / Maklersiz check
        if any(w in text for w in [
            "maklersiz", "egasidan", "bez makler", "без маклера", "без риелтора",
            "без риэлтора", "без комиссии", "no broker", "without broker", "without realtor",
            "no agent", "direct from owner", "owner", "sobstvennik",
        ]):
            extracted["owner_only"] = True
            extracted["tags"].append("🔑 Egasidan (Maklersiz)")

        # 6. Target Audience check
        if any(w in text for w in ["oila", "oilaviy", "oilaga", "семья", "для семьи", "family"]):
            extracted["target_audience"] = "family"
            extracted["tags"].append("👨‍👩‍👧 Oila uchun")
        elif any(w in text for w in ["qizlar", "qizlarga", "ayollar", "девушк", "женщин", "female"]):
            extracted["target_audience"] = "female"
            extracted["tags"].append("👩 Faqat qizlar/ayollar")
        elif any(w in text for w in ["yigitlar", "bolalar", "yigitlarga", "парн", "мужчин", "male"]):
            extracted["target_audience"] = "male"
            extracted["tags"].append("👨 Yigitlar uchun")
        elif any(w in text for w in ["talaba", "talabalar", "студент", "students"]):
            extracted["target_audience"] = "students"
            extracted["tags"].append("🎓 Talabalar uchun")

        # 7. Furnished check
        if any(w in text for w in ["mebel", "jihozlangan", "с мебелью", "furnished", "evroremont", "evro"]):
            extracted["is_furnished"] = True
            extracted["tags"].append("🛋 Mebelli / Jihozlangan")

        return extracted

    async def parse_natural_language_query_async(self, query: str) -> Dict[str, Any]:
        """
        Asynchronously parse natural language query with LLM extraction where available,
        fusing with deterministic local Tashkent rules for guaranteed precision.
        """
        deterministic = self.parse_natural_language_query(query)
        try:
            from src.services.free_llm_service import free_llm_service
            llm_extracted = await free_llm_service.extract_search_criteria(query)
            if llm_extracted and isinstance(llm_extracted, dict):
                # Fuse LLM insights into deterministic extraction
                if not deterministic["district"] and llm_extracted.get("district"):
                    deterministic["district"] = llm_extracted["district"]
                    deterministic["tags"].append(f"📍 {llm_extracted['district']}")

                if not deterministic["metro"] and llm_extracted.get("metro"):
                    deterministic["metro"] = llm_extracted["metro"]
                    deterministic["near_metro"] = True
                    deterministic["tags"].append(f"🚇 {llm_extracted['metro']} metro")

                if not deterministic["rooms"] and llm_extracted.get("rooms"):
                    deterministic["rooms"] = llm_extracted["rooms"]
                    deterministic["tags"].append(f"🏠 {llm_extracted['rooms']} xonali")

                if not deterministic["max_price_uzs"] and llm_extracted.get("max_price_uzs"):
                    deterministic["max_price_uzs"] = int(llm_extracted["max_price_uzs"])
                    deterministic["tags"].append(f"💰 Max {deterministic['max_price_uzs']:,} so‘m")

                if llm_extracted.get("owner_only") and not deterministic["owner_only"]:
                    deterministic["owner_only"] = True
                    deterministic["tags"].append("🔑 Egasidan (Maklersiz)")

                if deterministic["target_audience"] == "any" and llm_extracted.get("target_audience") and llm_extracted["target_audience"] != "any":
                    deterministic["target_audience"] = llm_extracted["target_audience"]
                    deterministic["tags"].append(f"👥 {llm_extracted['target_audience']}")

                if llm_extracted.get("reasoning"):
                    deterministic["reasoning"] = llm_extracted["reasoning"]
        except Exception as e:
            logger.debug("LLM query parse skipped, using deterministic output: %s", e)

        return deterministic

    async def search_and_rank_matches(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Execute AI Match search powered by Groq Qwen:
        1. Parse natural query into semantic constraints
        2. Retrieve best matching candidate pool
        3. Deeply evaluate each listing via Groq LLM for genuine Uzbek pros, cons, and match percentages
        4. Fallback smoothly to deterministic matching if LLM is unavailable
        """
        parsed = await self.parse_natural_language_query_async(query)

        # 1. Build targeted candidate query
        user_wants_roommate = any(w in query.lower() for w in [
            "sherik", "sherig", "koika", "yotoqxona", "roommate", "joy", "подселен", "койка"
        ])

        conditions = [Listing.is_active == True]
        if not user_wants_roommate:
            for sh_word in ["%sherik%", "%sherig%", "%koika%", "%койка%", "%подселен%", "%подслени%"]:
                conditions.append(Listing.title.not_ilike(sh_word))

        if parsed["district"]:
            d = parsed["district"]
            conditions.append(
                or_(
                    Listing.district.ilike(f"%{d}%"),
                    Listing.title.ilike(f"%{d}%"),
                    Listing.description.ilike(f"%{d}%"),
                )
            )

        if parsed["rooms"] is not None:
            r = parsed["rooms"]
            conditions.append(Listing.rooms.in_([r, r + 1, max(1, r - 1)]))

        if parsed["max_price_uzs"]:
            # Give 25% upper headroom so AI can evaluate near-matches
            conditions.append(Listing.price_uzs <= int(parsed["max_price_uzs"] * 1.25))

        stmt = (
            select(Listing)
            .where(and_(*conditions))
            .order_by(Listing.publication_date.desc().nullslast(), Listing.id.desc())
            .limit(20)
        )
        candidates = list((await session.execute(stmt)).scalars().all())

        # Fallback if specific conditions returned too few results
        if len(candidates) < 8:
            fallback_conds = [Listing.is_active == True]
            if not user_wants_roommate:
                for sh_word in ["%sherik%", "%sherig%", "%koika%", "%койка%", "%подселен%"]:
                    fallback_conds.append(Listing.title.not_ilike(sh_word))
            if parsed["district"]:
                fallback_conds.append(Listing.district.ilike(f"%{parsed['district']}%"))
            elif parsed["max_price_uzs"]:
                fallback_conds.append(Listing.price_uzs <= int(parsed["max_price_uzs"] * 1.35))
            stmt2 = select(Listing).where(and_(*fallback_conds)).order_by(Listing.id.desc()).limit(20)
            more_candidates = (await session.execute(stmt2)).scalars().all()
            seen_ids = {c.id for c in candidates}
            for mc in more_candidates:
                if mc.id not in seen_ids:
                    candidates.append(mc)
                    seen_ids.add(mc.id)

        # If still empty (e.g. database has few listings), get general active listings
        if not candidates:
            stmt3 = select(Listing).where(Listing.is_active == True).order_by(Listing.id.desc()).limit(20)
            candidates = list((await session.execute(stmt3)).scalars().all())

        # 2. Invoke Groq Qwen for deep listing analysis
        candidate_dicts = []
        for l in candidates:
            is_owner = False
            if l.classification and l.classification.label == "LIKELY_OWNER":
                is_owner = True
            elif "maklersiz" in (l.title or "").lower() or "egasidan" in (l.title or "").lower():
                is_owner = True

            candidate_dicts.append({
                "id": l.id,
                "title": l.title,
                "price_uzs": l.price_uzs,
                "district": l.district or "",
                "rooms": l.rooms if l.rooms is not None else 1,
                "target_audience": l.target_audience or "any",
                "is_owner": is_owner,
                "metro_station": l.metro_station or "",
                "description": l.description or "",
            })

        from src.services.free_llm_service import free_llm_service
        llm_ranks = await free_llm_service.rank_listings_for_query(query, candidate_dicts)
        llm_map = {item["id"]: item for item in llm_ranks if isinstance(item, dict) and "id" in item}

        user_wants_roommate = any(w in query.lower() for w in ["sherik", "koika", "yotoqxona", "roommate", "joy"])

        scored_results = []
        for l in candidates:
            llm_eval = llm_map.get(l.id)
            if llm_eval and isinstance(llm_eval.get("match_score"), (int, float)):
                score = max(0, min(100, int(llm_eval["match_score"])))
                pros = llm_eval.get("pros") or []
                cons = llm_eval.get("cons") or []
                is_relevant = llm_eval.get("is_relevant", True)
            else:
                score, pros, cons = self._calculate_match_score(l, parsed)
                is_relevant = score >= 40

            # Guard against shared room being offered when user wants full apartment
            is_shared = (
                "sherik" in (l.title or "").lower()
                or "sheriklik" in (l.description or "").lower()
                or "koika" in (l.description or "").lower()
                or (l.rooms == 0)
            )
            if is_shared and not user_wants_roommate:
                score = min(score, 25)
                is_relevant = False
                if not any("sheriklik" in c.lower() for c in cons):
                    cons.append("Alohida kvartira emas, sheriklik joy")

            scored_results.append({
                "listing": l,
                "match_score": score,
                "match_percentage": score,
                "pros": pros,
                "cons": cons,
                "is_relevant": is_relevant,
            })

        # Sort highest match score first
        scored_results.sort(key=lambda x: (x["is_relevant"], x["match_score"]), reverse=True)
        top_matches = scored_results[:limit]

        return {
            "query": query,
            "parsed_filters": parsed,
            "parsed_criteria": parsed,
            "total_matches": len(top_matches),
            "results": top_matches,
            "matches": top_matches,
        }

    def _calculate_match_score(
        self, listing: Listing, filters: Dict[str, Any]
    ) -> tuple[int, List[str], List[str]]:
        """Calculate score from 0 to 100 based on multi-dimensional criteria."""
        score = 60  # Base score
        pros = []
        cons = []

        is_shared = (
            "sherik" in (listing.title or "").lower()
            or "sherig" in (listing.title or "").lower()
            or "подселен" in (listing.title or "").lower()
            or "подслени" in (listing.title or "").lower()
            or "койка" in (listing.title or "").lower()
            or "sheriklik" in (listing.description or "").lower()
            or "koika" in (listing.description or "").lower()
            or (listing.rooms == 0)
        )
        if is_shared:
            score -= 50
            cons.append("Alohida kvartira emas, sheriklik joy")

        # 1. District match (+25%)
        req_district = filters.get("district")
        if req_district:
            if listing.district and req_district.lower() in listing.district.lower():
                score += 25
                pros.append(f"Tanlangan {listing.district} tumanida joylashgan")
            else:
                score -= 20
                cons.append(f"Tumani mos kelmadi ({listing.district or 'Boshqa tuman'})")

        # 2. Price match (+20%)
        max_p = filters.get("max_price_uzs")
        if max_p and listing.price_uzs:
            if listing.price_uzs <= max_p:
                savings = max_p - listing.price_uzs
                if savings > 0:
                    score += 20
                    pros.append(f"Byudjetingizga to‘liq mos (byudjetdan {savings:,} so‘m tejaysiz)")
                else:
                    score += 15
                    pros.append("Belgilangan byudjet chegarasiga to‘g‘ri keladi")
            else:
                over = listing.price_uzs - max_p
                pct_over = (over / max_p) * 100
                if pct_over <= 15:
                    score -= 5
                    cons.append(f"Byudjetdan sal qimmatroq (+{over:,} so‘m)")
                else:
                    score -= 25
                    cons.append(f"Byudjetdan ancha qimmat (+{over:,} so‘m)")

        # 3. Room count match (+20%)
        req_rooms = filters.get("rooms")
        if req_rooms and listing.rooms:
            if listing.rooms == req_rooms:
                score += 20
                pros.append(f"Aynan {req_rooms} xonali")
            elif abs(listing.rooms - req_rooms) == 1:
                score += 5
                pros.append(f"{listing.rooms} xonali variant (so‘ralgan: {req_rooms})")
            else:
                score -= 15
                cons.append(f"Xonalar soni so‘ralgandan farq qiladi ({listing.rooms} xona)")

        # 4. Owner only / Maklersiz (+15%)
        if filters.get("owner_only"):
            is_owner = False
            if listing.classification and listing.classification.label == "LIKELY_OWNER":
                is_owner = True
            elif "maklersiz" in (listing.description or "").lower() or "egasidan" in (listing.description or "").lower():
                is_owner = True

            if is_owner:
                score += 15
                pros.append("Egasidan (vositachisiz / makler komissiyasisiz)")
            else:
                score -= 15
                cons.append("Egasidan ekanligi to‘liq tasdiqlanmagan (makler bo‘lishi mumkin)")

        # 5. Metro proximity (+10%)
        if filters.get("near_metro"):
            if listing.metro_station:
                score += 10
                dist_info = f" ({listing.metro_distance_m}m)" if listing.metro_distance_m else ""
                pros.append(f"{listing.metro_station} metrosiga yaqin{dist_info}")
            elif any(w in (listing.description or "").lower() for w in ["metro", "метро"]):
                score += 8
                pros.append("Tavsifda metroga yaqinligi qayd etilgan")
            else:
                score -= 5
                cons.append("Metro masofasi ko‘rsatilmagan")

        # 6. Target Audience match (+10%)
        req_aud = filters.get("target_audience")
        if req_aud and req_aud != "any":
            list_aud = listing.target_audience or "any"
            if list_aud == req_aud or list_aud == "any":
                score += 10
                pros.append(f"{req_aud.capitalize()} ijarachilar uchun mos")
            else:
                score -= 15
                cons.append(f"Ijarachi cheklovi: faqat {list_aud} uchun")

        # Clamp score between 35 and 99
        final_score = max(35, min(99, score))
        return final_score, pros[:3], cons[:2]


ai_match_service = AIMatchService()
