"""Intelligent Persistent Advertisement Queue and Multi-Layer Deduplication Service."""

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.listing import (
    Listing,
    ChannelPostHistory,
    ChannelPublishQueue,
    QueueStatus,
    utc_now,
)
from src.config import settings

logger = logging.getLogger(__name__)


def normalize_title(title: Optional[str]) -> str:
    """Normalize title for fuzzy comparison by removing punctuation, digits/spaces normalization."""
    if not title:
        return ""
    cleaned = re.sub(r"[^\w\s]", " ", title.lower())
    return " ".join(cleaned.split())


def compute_content_hash(
    title: str,
    district: Optional[str],
    price_uzs: Optional[int],
    rooms: Optional[int],
) -> str:
    """Generate deterministic SHA256 content signature based on key property attributes."""
    norm_t = normalize_title(title)
    dist = (district or "").strip().lower()
    p = str(price_uzs or 0)
    r = str(rooms or 0)
    raw = f"{norm_t}|{dist}|{p}|{r}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def compute_image_fingerprint(image_urls: Optional[List[str]]) -> Optional[str]:
    """Generate SHA256 fingerprint for image URLs ignoring sizing and query parameters."""
    if not image_urls:
        return None
    cleaned_urls = []
    for u in image_urls:
        if not u or not isinstance(u, str):
            continue
        base = u.split("?")[0].replace("1000x750", "").replace("{width}x{height}", "").strip()
        if base:
            cleaned_urls.append(base)
    if not cleaned_urls:
        return None
    raw = ";".join(sorted(cleaned_urls[:5]))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class QueueService:
    """
    Manages persistent channel publishing queue, atomic state transitions,
    and multi-layer duplicate detection.
    """

    @staticmethod
    def normalize_text_key(text: Optional[str]) -> str:
        return normalize_title(text)

    async def is_duplicate(
        self,
        session: AsyncSession,
        listing: Listing,
        in_memory_candidates: Optional[List[Listing]] = None,
        exclude_queue_id: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Multi-layer duplicate verification:
        1. Primary: Canonical URL and Source ID
        2. Secondary: Exact normalized title within district
        3. Secondary: Content hash (normalized title + district + price + rooms)
        4. Secondary: Image fingerprint
        5. Secondary: Contact phone + district + rooms
        6. Secondary: High lexical title similarity (>= 65%) with matching district and rooms

        Checks against:
        - In-memory candidates
        - ChannelPublishQueue (all statuses)
        - ChannelPostHistory (historical broadcast log)
        - Listing.posted_to_channel_at
        """
        # A. Already marked posted on listing record
        if listing.posted_to_channel_at is not None:
            return True, f"Listing #{listing.id} was already marked as posted to channel"

        norm_t = normalize_title(listing.title)
        c_hash = compute_content_hash(listing.title, listing.district, listing.price_uzs, listing.rooms)
        img_fp = compute_image_fingerprint(listing.image_urls)
        phone = (listing.contact_phone or "").strip()
        cand_words = set(norm_t.split())

        # B. Check in-memory candidates (if evaluating a batch before committing)
        if in_memory_candidates:
            for c in in_memory_candidates:
                if c.id == listing.id:
                    return True, f"Matches in-batch listing #{c.id}"
                if c.canonical_url and listing.canonical_url and c.canonical_url.strip() == listing.canonical_url.strip():
                    return True, f"Primary match: URL matches in-batch listing #{c.id}"
                if getattr(c, "source_id", None) and getattr(listing, "source_id", None) and c.source_id == listing.source_id:
                    return True, f"Primary match: source_id matches in-batch listing #{c.id}"
                c_norm = normalize_title(c.title)
                if norm_t and c_norm and norm_t == c_norm:
                    if not listing.district or not c.district or listing.district == c.district:
                        return True, f"Secondary match: Title matches in-batch listing #{c.id}"
                c_hash_other = compute_content_hash(c.title, c.district, c.price_uzs, c.rooms)
                if c_hash == c_hash_other:
                    return True, f"Secondary match: Content hash matches in-batch listing #{c.id}"
                if img_fp and getattr(c, "image_fingerprint", None) and img_fp == c.image_fingerprint:
                    return True, f"Secondary match: Image fingerprint matches in-batch listing #{c.id}"

        # C. Check ChannelPublishQueue (published, publishing, or pending)
        q_or_conditions = [
            ChannelPublishQueue.listing_id == listing.id,
            ChannelPublishQueue.canonical_url == listing.canonical_url,
            ChannelPublishQueue.content_hash == c_hash,
        ]
        if listing.source_id:
            q_or_conditions.append(
                and_(
                    ChannelPublishQueue.source_id.is_not(None),
                    ChannelPublishQueue.source_id == listing.source_id,
                )
            )
        if img_fp:
            q_or_conditions.append(
                and_(
                    ChannelPublishQueue.image_fingerprint.is_not(None),
                    ChannelPublishQueue.image_fingerprint == img_fp,
                )
            )

        q_conditions = [or_(*q_or_conditions)]
        if exclude_queue_id:
            q_conditions.append(ChannelPublishQueue.id != exclude_queue_id)

        q_stmt = select(ChannelPublishQueue).where(and_(*q_conditions))
        q_res = await session.execute(q_stmt)
        q_match = q_res.scalars().first()
        if q_match:
            return True, f"Matches existing queue entry #{q_match.id} (status: {q_match.status})"

        # D. Check ChannelPostHistory table
        h_stmt = select(ChannelPostHistory).where(
            or_(
                ChannelPostHistory.listing_id == listing.id,
                ChannelPostHistory.canonical_url == listing.canonical_url,
                ChannelPostHistory.content_hash == c_hash,
                and_(
                    ChannelPostHistory.image_fingerprint.is_not(None),
                    ChannelPostHistory.image_fingerprint == img_fp,
                ) if img_fp else False,
            )
        )
        h_res = await session.execute(h_stmt)
        h_match = h_res.scalars().first()
        if h_match:
            return True, f"Matches historical channel post #{h_match.id} (posted at {h_match.posted_at})"

        # E. Check fuzzy title + district + phone in ChannelPostHistory
        all_hist = (
            await session.execute(
                select(
                    ChannelPostHistory.id,
                    ChannelPostHistory.title,
                    ChannelPostHistory.normalized_title,
                    ChannelPostHistory.district,
                    ChannelPostHistory.rooms,
                    ChannelPostHistory.price_uzs,
                    ChannelPostHistory.contact_phone,
                )
            )
        ).fetchall()

        for h_id, h_title, h_norm, h_dist, h_rooms, h_price, h_phone in all_hist:
            # 1. Exact normalized title within district
            if norm_t and h_norm and norm_t == h_norm:
                if not listing.district or not h_dist or listing.district == h_dist:
                    return True, f"Secondary match: Normalized title matches historical post #{h_id}"

            # 2. Same contact phone + district + rooms
            h_p = (h_phone or "").strip()
            if phone and h_p and phone == h_p:
                if listing.district and h_dist and listing.district == h_dist:
                    if listing.rooms and h_rooms and listing.rooms == h_rooms:
                        return True, f"Secondary match: Contact phone matches historical post #{h_id}"

            # 3. Same district + rooms + high title lexical overlap
            if listing.district and h_dist and listing.district == h_dist:
                if listing.rooms and h_rooms and listing.rooms == h_rooms:
                    h_words = set((h_norm or "").split())
                    if cand_words and h_words:
                        overlap = len(cand_words & h_words) / max(len(cand_words), len(h_words))
                        if overlap >= 0.65:
                            return True, f"Secondary match: Title similarity {overlap:.2f} matches historical post #{h_id}"

        # F. Check previously posted listings in listings table
        p_stmt = select(
            Listing.id,
            Listing.canonical_url,
            Listing.title,
            Listing.district,
            Listing.rooms,
            Listing.price_uzs,
            Listing.contact_phone,
        ).where(
            Listing.posted_to_channel_at.is_not(None),
            Listing.id != listing.id,
        )
        p_res = await session.execute(p_stmt)
        posted_rows = p_res.fetchall()
        for p_id, p_url, p_title, p_dist, p_rooms, p_price, p_phone in posted_rows:
            if p_url and listing.canonical_url and p_url.strip() == listing.canonical_url.strip():
                return True, f"Primary match: URL matches posted listing #{p_id}"
            p_norm = normalize_title(p_title)
            if norm_t and p_norm and norm_t == p_norm:
                if not listing.district or not p_dist or listing.district == p_dist:
                    return True, f"Secondary match: Title matches posted listing #{p_id}"
            p_ph = (p_phone or "").strip()
            if phone and p_ph and phone == p_ph:
                if listing.district and p_dist and listing.district == p_dist:
                    if listing.rooms and p_rooms and listing.rooms == p_rooms:
                        return True, f"Secondary match: Phone matches posted listing #{p_id}"

        return False, "OK: unique"

    async def enqueue_listing(
        self,
        session: AsyncSession,
        listing: Listing,
    ) -> Tuple[Optional[ChannelPublishQueue], bool, str]:
        """
        Validate, check duplicates, and save unique advertisement to the persistent publishing queue.
        Returns: (queue_item, is_new: bool, reason: str)
        """
        # Ensure listing content hash and image fingerprint are saved
        norm_t = normalize_title(listing.title)
        c_hash = compute_content_hash(listing.title, listing.district, listing.price_uzs, listing.rooms)
        img_fp = compute_image_fingerprint(listing.image_urls)

        listing.content_hash = c_hash
        listing.image_fingerprint = img_fp

        # Check existing queue item for this listing
        existing_q = (
            await session.execute(
                select(ChannelPublishQueue).where(
                    or_(
                        ChannelPublishQueue.listing_id == listing.id,
                        ChannelPublishQueue.canonical_url == listing.canonical_url,
                    )
                )
            )
        ).scalars().first()

        if existing_q:
            return existing_q, False, f"Already in queue with status '{existing_q.status}'"

        # Check multi-layer duplicate detection
        is_dup, reason = await self.is_duplicate(session, listing)
        if is_dup:
            logger.info("Listing #%d rejected from queue: %s", listing.id, reason)
            return None, False, reason

        # Create new queue entry
        queue_item = ChannelPublishQueue(
            listing_id=listing.id,
            canonical_url=listing.canonical_url,
            source_id=listing.source_id,
            title=listing.title,
            normalized_title=norm_t,
            district=listing.district,
            rooms=listing.rooms,
            price_uzs=listing.price_uzs,
            contact_phone=listing.contact_phone,
            content_hash=c_hash,
            image_fingerprint=img_fp,
            status=QueueStatus.PENDING,
            attempts=0,
            publication_date=listing.publication_date,
            created_at=utc_now(),
        )

        try:
            session.add(queue_item)
            await session.commit()
            logger.info(
                "Successfully enqueued listing #%d for channel publishing (queue id #%d).",
                listing.id,
                queue_item.id,
            )
            return queue_item, True, "Enqueued successfully"
        except IntegrityError:
            await session.rollback()
            logger.warning("Race condition caught: listing #%d already enqueued.", listing.id)
            return None, False, "Concurrent duplicate prevented by DB unique constraint"
        except Exception as e:
            await session.rollback()
            logger.error("Failed to enqueue listing #%d: %s", listing.id, e)
            return None, False, str(e)

    async def get_next_eligible_item(
        self,
        session: AsyncSession,
    ) -> Optional[ChannelPublishQueue]:
        """
        Atomically selects the newest pending advertisement from the queue.
        Sorted by publication date (newest first), then creation date.
        Locks the item by transitioning status from 'pending' to 'publishing'.
        Prevents race conditions between concurrent workers.
        """
        stmt = (
            select(ChannelPublishQueue)
            .options(selectinload(ChannelPublishQueue.listing))
            .where(ChannelPublishQueue.status == QueueStatus.PENDING)
            .order_by(
                ChannelPublishQueue.publication_date.desc().nullslast(),
                ChannelPublishQueue.created_at.desc(),
                ChannelPublishQueue.id.desc(),
            )
            .limit(10)
        )
        res = await session.execute(stmt)
        candidates = res.scalars().all()

        for cand in candidates:
            # Verify if listing was already posted or inactive
            if cand.listing and (cand.listing.posted_to_channel_at is not None or not cand.listing.is_active):
                cand.status = QueueStatus.PUBLISHED if cand.listing.posted_to_channel_at else QueueStatus.REJECTED
                session.add(cand)
                await session.commit()
                continue

            # Atomic lock via UPDATE WHERE status='pending'
            lock_stmt = (
                update(ChannelPublishQueue)
                .where(
                    ChannelPublishQueue.id == cand.id,
                    ChannelPublishQueue.status == QueueStatus.PENDING,
                )
                .values(
                    status=QueueStatus.PUBLISHING,
                    attempts=ChannelPublishQueue.attempts + 1,
                )
            )
            lock_res = await session.execute(lock_stmt)
            if lock_res.rowcount == 1:
                await session.commit()
                # Reload locked candidate
                cand_reloaded = (
                    await session.execute(
                        select(ChannelPublishQueue)
                        .options(selectinload(ChannelPublishQueue.listing))
                        .where(ChannelPublishQueue.id == cand.id)
                    )
                ).scalars().first()
                logger.info(
                    "Acquired publishing lock on queue item #%d (Listing #%d).",
                    cand.id,
                    cand.listing_id,
                )
                return cand_reloaded

        return None

    async def mark_published(
        self,
        session: AsyncSession,
        queue_item: ChannelPublishQueue,
        telegram_message_id: Optional[int] = None,
        slot_name: Optional[str] = None,
    ) -> None:
        """
        Record successful channel publication:
        - Update queue status to 'published'
        - Save publication timestamp and Telegram message ID
        - Update Listing.posted_to_channel_at
        - Insert into ChannelPostHistory for permanent historical deduplication
        """
        now = utc_now()
        queue_item.status = QueueStatus.PUBLISHED
        queue_item.published_at = now
        queue_item.telegram_message_id = telegram_message_id
        queue_item.scheduled_slot = slot_name
        session.add(queue_item)

        # Update listing
        if queue_item.listing:
            queue_item.listing.posted_to_channel_at = now
            session.add(queue_item.listing)

        # Insert ChannelPostHistory
        post_record = ChannelPostHistory(
            listing_id=queue_item.listing_id,
            canonical_url=queue_item.canonical_url,
            title=queue_item.title,
            normalized_title=queue_item.normalized_title,
            district=queue_item.district,
            rooms=queue_item.rooms,
            price_uzs=queue_item.price_uzs,
            contact_phone=queue_item.contact_phone,
            content_hash=queue_item.content_hash,
            image_fingerprint=queue_item.image_fingerprint,
            telegram_message_id=telegram_message_id,
            posted_at=now,
            channel_id=settings.CHANNEL_ID or "@joyliy_uz",
        )
        session.add(post_record)

        # Retires any other unposted duplicate listings in the database
        retire_stmt = (
            update(Listing)
            .where(
                Listing.posted_to_channel_at.is_(None),
                or_(
                    Listing.content_hash == queue_item.content_hash,
                    Listing.canonical_url == queue_item.canonical_url,
                ),
            )
            .values(posted_to_channel_at=now, is_active=False)
        )
        await session.execute(retire_stmt)
        await session.commit()
        logger.info(
            "Queue item #%d successfully marked PUBLISHED (msg_id=%s, slot=%s).",
            queue_item.id,
            telegram_message_id,
            slot_name,
        )

    async def mark_failed(
        self,
        session: AsyncSession,
        queue_item: ChannelPublishQueue,
        error_message: str,
    ) -> None:
        """Mark queue item as failed with error details."""
        queue_item.status = QueueStatus.FAILED
        queue_item.error_message = error_message
        session.add(queue_item)
        await session.commit()
        logger.warning(
            "Queue item #%d marked FAILED: %s",
            queue_item.id,
            error_message,
        )

    async def get_queue_stats(self, session: AsyncSession) -> dict:
        """Retrieve full status summary of the publishing queue."""
        total = (await session.execute(select(func.count(ChannelPublishQueue.id)))).scalar() or 0
        pending = (
            await session.execute(
                select(func.count(ChannelPublishQueue.id)).where(
                    ChannelPublishQueue.status == QueueStatus.PENDING
                )
            )
        ).scalar() or 0
        publishing = (
            await session.execute(
                select(func.count(ChannelPublishQueue.id)).where(
                    ChannelPublishQueue.status == QueueStatus.PUBLISHING
                )
            )
        ).scalar() or 0
        published = (
            await session.execute(
                select(func.count(ChannelPublishQueue.id)).where(
                    ChannelPublishQueue.status == QueueStatus.PUBLISHED
                )
            )
        ).scalar() or 0
        failed = (
            await session.execute(
                select(func.count(ChannelPublishQueue.id)).where(
                    ChannelPublishQueue.status == QueueStatus.FAILED
                )
            )
        ).scalar() or 0

        # Peek next item
        next_item = (
            await session.execute(
                select(ChannelPublishQueue)
                .where(ChannelPublishQueue.status == QueueStatus.PENDING)
                .order_by(
                    ChannelPublishQueue.publication_date.desc().nullslast(),
                    ChannelPublishQueue.created_at.desc(),
                )
                .limit(1)
            )
        ).scalars().first()

        return {
            "total": total,
            "pending": pending,
            "publishing": publishing,
            "published": published,
            "failed": failed,
            "next_item": {
                "id": next_item.id,
                "title": next_item.title,
                "price_uzs": next_item.price_uzs,
                "district": next_item.district,
            } if next_item else None,
        }


queue_service = QueueService()
