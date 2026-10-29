"""Listing Service for ingestion, deduplication, search querying, and favorites."""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Sequence
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.listing import (
    Listing,
    ListingClassification,
    Favorite,
    NotificationHistory,
)
from src.models.user import User, UserSearchPreference
from src.classification.engine import ClassificationEngine, default_classifier
from src.classification.types import ClassificationLabel
from src.classification.audience import detect_target_audience
from src.providers.base import RawListingItem


class ListingService:
    """Manages listing persistence, deduplication, search queries, and user bookmarks."""

    def __init__(self, classifier: Optional[ClassificationEngine] = None):
        self.classifier = classifier or default_classifier

    async def ingest_raw_listing(
        self, session: AsyncSession, item: RawListingItem
    ) -> Tuple[Listing, bool]:
        """
        Idempotently ingest a raw listing.
        Returns (listing, is_new: bool).
        """
        # Step 1: Check existing by canonical URL or source_id
        stmt = select(Listing).where(Listing.canonical_url == item.canonical_url)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing:
            # Update last_seen timestamp and price if changed
            existing.last_seen_at = now
            if item.price_uzs and existing.price_uzs != item.price_uzs:
                existing.price_uzs = item.price_uzs
                existing.price_raw = item.price_raw
            if item.image_urls and not existing.image_urls:
                existing.image_urls = item.image_urls
            await session.commit()
            return existing, False

        # Step 2: New listing -> Classify and Persist
        classification_res = self.classifier.classify(
            title=item.title, description=item.description
        )

        listing = Listing(
            source=item.source,
            source_id=item.source_id,
            canonical_url=item.canonical_url,
            title=item.title,
            price_raw=item.price_raw,
            price_uzs=item.price_uzs,
            currency=item.currency,
            district=item.district,
            rooms=item.rooms,
            area=item.area,
            floor=item.floor,
            description=item.description,
            contact_phone=getattr(item, "contact_phone", None),
            contact_telegram=getattr(item, "contact_telegram", None),
            target_audience=item.target_audience or detect_target_audience(item.title, item.description),
            image_urls=item.image_urls,
            publication_date=item.publication_date,
            first_seen_at=now,
            last_seen_at=now,
            is_active=True,
        )
        session.add(listing)
        await session.flush()  # populate listing.id

        # Add Classification record
        reasons_data = [
            {"type": s.signal_type, "text": s.matched_text, "weight": s.weight, "desc": s.description}
            for s in classification_res.matched_signals
        ]
        classification = ListingClassification(
            listing_id=listing.id,
            label=classification_res.label.value,
            confidence_score=classification_res.confidence_score,
            reasons=reasons_data,
            checked_at=now,
        )
        session.add(classification)
        await session.commit()

        # Eager load classification
        listing.classification = classification
        return listing, True

    async def get_listing_by_id(
        self, session: AsyncSession, listing_id: int
    ) -> Optional[Listing]:
        """Retrieve listing with its classification by ID."""
        stmt = (
            select(Listing)
            .options(selectinload(Listing.classification))
            .where(Listing.id == listing_id)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def search_listings(
        self,
        session: AsyncSession,
        districts: Optional[List[str]] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        rooms: Optional[List[int]] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        target_audience: Optional[str] = None,
        owner_only: bool = False,
        include_agency: bool = True,
        max_age_hours: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[Sequence[Listing], int]:
        """Search listings with filters and return (items, total_count)."""
        stmt = select(Listing).options(selectinload(Listing.classification))

        # Join classification if filtering on owner/agency
        if owner_only or not include_agency:
            stmt = stmt.join(Listing.classification)

        conditions = [Listing.is_active.is_(True)]

        if districts:
            conditions.append(Listing.district.in_(districts))
        if min_price is not None:
            conditions.append(Listing.price_uzs >= min_price)
        if max_price is not None:
            conditions.append(Listing.price_uzs <= max_price)
        if rooms:
            conditions.append(Listing.rooms.in_(rooms))
        if min_area is not None:
            conditions.append(Listing.area >= min_area)
        if max_area is not None:
            conditions.append(Listing.area <= max_area)
        if target_audience and target_audience != "all":
            conditions.append(Listing.target_audience == target_audience)

        if owner_only:
            conditions.append(
                ListingClassification.label == ClassificationLabel.LIKELY_OWNER.value
            )
        elif not include_agency:
            conditions.append(
                ListingClassification.label != ClassificationLabel.LIKELY_AGENT.value
            )

        if max_age_hours is not None:
            # Per prompt: maximum listing age only applies when reliable publication timestamp exists
            cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            conditions.append(
                or_(
                    Listing.publication_date.is_(None),
                    Listing.publication_date >= cutoff,
                )
            )

        stmt = stmt.where(and_(*conditions))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await session.execute(count_stmt)
        total = total_res.scalar_one()

        # Query paginated page
        stmt = stmt.order_by(desc(Listing.first_seen_at)).limit(limit).offset(offset)
        res = await session.execute(stmt)
        listings = res.scalars().all()

        return listings, total

    async def add_favorite(
        self, session: AsyncSession, user_id: int, listing_id: int
    ) -> bool:
        """Add listing to user's favorites. Returns True if newly added, False if already present."""
        stmt = select(Favorite).where(
            and_(Favorite.user_id == user_id, Favorite.listing_id == listing_id)
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if existing:
            return False

        fav = Favorite(user_id=user_id, listing_id=listing_id)
        session.add(fav)
        await session.commit()
        return True

    async def remove_favorite(
        self, session: AsyncSession, user_id: int, listing_id: int
    ) -> bool:
        """Remove listing from user's favorites."""
        stmt = select(Favorite).where(
            and_(Favorite.user_id == user_id, Favorite.listing_id == listing_id)
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            return False
        await session.delete(existing)
        await session.commit()
        return True

    async def get_user_favorites(
        self, session: AsyncSession, user_id: int, limit: int = 10, offset: int = 0
    ) -> List[Listing]:
        """Fetch listings bookmarked by the user."""
        stmt = (
            select(Listing)
            .join(Favorite, Favorite.listing_id == Listing.id)
            .options(selectinload(Listing.classification))
            .where(Favorite.user_id == user_id)
            .order_by(desc(Favorite.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())


listing_service = ListingService()

