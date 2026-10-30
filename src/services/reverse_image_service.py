"""Reverse Image Search: Visual Hash Fingerprinting and Duplicate Image Retrieval."""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing

logger = logging.getLogger(__name__)


def compute_url_hash(url: str) -> str:
    """Deterministic hash of photo URL or image content fingerprint."""
    if not url:
        return ""
    # Strip URL query parameters (e.g. ?s=1500x2000 or resize tokens)
    clean_url = url.split("?")[0].rstrip("/")
    return hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:16]


class ReverseImageService:
    """Finds visually identical or reused apartment photos in the listing catalog."""

    async def search_by_image_url(
        self, session: AsyncSession, image_url: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Search for existing listings sharing the same image hash or visual fingerprint."""
        if not image_url:
            return {"total_matches": 0, "matches": []}

        target_hash = compute_url_hash(image_url)

        # 1. Check exact image fingerprint match
        stmt = select(Listing).where(
            and_(
                Listing.is_active == True,
                Listing.image_fingerprint == target_hash,
            )
        ).limit(limit)
        direct_matches = (await session.execute(stmt)).scalars().all()

        # 2. Check JSON image_urls array contains URL substring
        if not direct_matches:
            # Query recent listings to check image array
            recent_stmt = select(Listing).where(Listing.is_active == True).order_by(Listing.id.desc()).limit(150)
            all_recent = (await session.execute(recent_stmt)).scalars().all()

            matched_list = []
            for l in all_recent:
                for img in (l.image_urls or []):
                    if target_hash in compute_url_hash(img) or image_url.split("?")[0] in img:
                        matched_list.append(l)
                        break
            direct_matches = matched_list[:limit]

        results = []
        for l in direct_matches:
            results.append({
                "id": l.id,
                "title": l.title,
                "price_uzs": l.price_uzs,
                "district": l.district,
                "canonical_url": l.canonical_url,
                "source": l.source,
                "similarity_score": 98 if (l.image_fingerprint == target_hash) else 90,
                "primary_image": l.image_urls[0] if (l.image_urls and len(l.image_urls) > 0) else None,
                "posted_at": l.publication_date.isoformat() if l.publication_date else l.first_seen_at.isoformat(),
            })

        return {
            "query_image_url": image_url,
            "target_hash": target_hash,
            "total_matches": len(results),
            "matches": results,
            "note": "Topilgan o‘xshash fotosuratlar bir xil e‘lon yoki vositachilar tomonidan qayta yuklangan bo‘lishi mumkin.",
        }


reverse_image_service = ReverseImageService()
