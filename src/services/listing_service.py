"""Listing Service for ingestion, deduplication, search querying, and favorites."""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Sequence
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.listing import (
    Listing,
    ListingClassification,
    ListingUpdateHistory,
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
        Idempotently ingest a raw listing with multi-layer duplicate detection:
        1. Primary: source and source_id
        2. Primary: Canonical URL (raw and normalized)
        3. Secondary: Content hash (normalized title + district + price + rooms)
        Returns (listing, is_new: bool).
        """
        from src.providers.parser import canonicalize_url, normalize_url_path, extract_source_id_from_url
        from src.services.queue_service import compute_content_hash, compute_image_fingerprint, queue_service

        # Normalize URL and extract missing source_id if possible
        if item.canonical_url:
            item.canonical_url = canonicalize_url(item.canonical_url)
            if not item.source_id:
                item.source_id = extract_source_id_from_url(item.canonical_url)

        c_hash = compute_content_hash(item.title, item.district, item.price_uzs, item.rooms)
        img_fp = compute_image_fingerprint(item.image_urls)
        now = datetime.now(timezone.utc)
        existing = None

        # 1. Primary check: source and source_id
        if item.source_id:
            stmt = select(Listing).where(
                and_(
                    Listing.source == item.source,
                    Listing.source_id == str(item.source_id),
                )
            )
            existing = (await session.execute(stmt)).scalars().first()

        # 2. Primary check: canonical URL (raw, clean, and normalized path)
        if not existing and item.canonical_url:
            clean_url = canonicalize_url(item.canonical_url)
            norm_url = normalize_url_path(item.canonical_url)
            stmt = select(Listing).where(
                or_(
                    Listing.canonical_url == item.canonical_url,
                    Listing.canonical_url == clean_url,
                    Listing.canonical_url == norm_url,
                )
            )
            existing = (await session.execute(stmt)).scalars().first()

        # 3. Secondary check: content hash (if title + district + price + rooms match an active listing)
        if not existing and c_hash:
            stmt = select(Listing).where(
                and_(
                    Listing.content_hash == c_hash,
                    Listing.is_active == True,
                )
            )
            existing = (await session.execute(stmt)).scalars().first()

        # 4. Secondary check: image fingerprint (if identical apartment photos match an active listing)
        if not existing and img_fp:
            stmt = select(Listing).where(
                and_(
                    Listing.image_fingerprint == img_fp,
                    Listing.is_active == True,
                )
            )
            existing = (await session.execute(stmt)).scalars().first()

        if existing:
            # Update last_seen timestamp and attributes if changed
            existing.last_seen_at = now
            if not existing.is_active:
                existing.is_active = True
                hist_reactivate = ListingUpdateHistory(
                    listing_id=existing.id,
                    change_type="status_reactivated",
                    old_values={"is_active": False},
                    new_values={"is_active": True},
                    detected_at=now,
                )
                session.add(hist_reactivate)

            if item.price_uzs and existing.price_uzs != item.price_uzs:
                old_p = existing.price_uzs or 0
                new_p = item.price_uzs
                diff = new_p - old_p
                pct = round((diff / old_p) * 100, 2) if old_p > 0 else 0.0

                from src.models.ecosystem import ListingPriceHistory
                price_hist = ListingPriceHistory(
                    listing_id=existing.id,
                    old_price_uzs=old_p,
                    new_price_uzs=new_p,
                    diff_uzs=diff,
                    diff_percent=pct,
                    detected_at=now,
                )
                session.add(price_hist)

                update_hist = ListingUpdateHistory(
                    listing_id=existing.id,
                    change_type="price_change",
                    old_values={"price_uzs": old_p, "price_raw": existing.price_raw},
                    new_values={"price_uzs": new_p, "price_raw": item.price_raw},
                    detected_at=now,
                )
                session.add(update_hist)

                existing.price_uzs = new_p
                existing.price_raw = item.price_raw

            if item.image_urls and not existing.image_urls:
                existing.image_urls = item.image_urls
                update_hist = ListingUpdateHistory(
                    listing_id=existing.id,
                    change_type="photo_update",
                    old_values={"images_count": 0},
                    new_values={"images_count": len(item.image_urls)},
                    detected_at=now,
                )
                session.add(update_hist)

            if not existing.source_id and item.source_id:
                existing.source_id = str(item.source_id)
            if not existing.content_hash and c_hash:
                existing.content_hash = c_hash
            if not existing.image_fingerprint and img_fp:
                existing.image_fingerprint = img_fp

            await session.commit()
            return existing, False

        # Step 2: New listing -> Classify and Persist
        classification_res = self.classifier.classify(
            title=item.title, description=item.description
        )

        from src.services.queue_service import compute_content_hash, compute_image_fingerprint, queue_service

        c_hash = compute_content_hash(item.title, item.district, item.price_uzs, item.rooms)
        img_fp = compute_image_fingerprint(item.image_urls)

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
            content_hash=c_hash,
            image_fingerprint=img_fp,
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
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            conditions = []
            if item.source_id:
                conditions.append(and_(Listing.source == item.source, Listing.source_id == str(item.source_id)))
            if item.canonical_url:
                conditions.append(Listing.canonical_url == item.canonical_url)
            if c_hash:
                conditions.append(Listing.content_hash == c_hash)
            stmt = select(Listing).options(selectinload(Listing.classification)).where(or_(*conditions))
            existing_race = (await session.execute(stmt)).scalars().first()
            if existing_race:
                return existing_race, False
            raise

        # Enqueue into persistent publishing queue
        try:
            await queue_service.enqueue_listing(session, listing)
        except Exception as q_err:
            logger.debug("Automatic queue enqueue for listing #%d: %s", listing.id, q_err)

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
        sort: str = "new",
        limit: int = 24,
        offset: int = 0,
    ) -> Tuple[Sequence[Listing], int]:
        """Search listings with filters, sorting, and pagination across the full database."""
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

        # Count total across entire dataset
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await session.execute(count_stmt)
        total = total_res.scalar_one()

        # Query paginated page with requested sorting
        if sort in ("lo", "price_asc"):
            order_clause = (Listing.price_uzs.asc().nullslast(), desc(Listing.id))
        elif sort in ("hi", "price_desc"):
            order_clause = (Listing.price_uzs.desc().nullslast(), desc(Listing.id))
        elif sort == "area_desc":
            order_clause = (Listing.area.desc().nullslast(), desc(Listing.id))
        else:  # "new"
            order_clause = (
                desc(Listing.publication_date).nullslast(),
                desc(Listing.first_seen_at),
                desc(Listing.id),
            )

        stmt = stmt.order_by(*order_clause).limit(limit).offset(offset)
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

