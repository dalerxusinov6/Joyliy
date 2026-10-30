"""REST API routes for website integration and monitoring."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, text, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.models.user import User
from src.models.listing import Listing, ListingClassification
from src.services.listing_service import listing_service
from src.services.monitor_worker import monitor_worker
from src.services.auth_service import auth_service
from src.services.neighborhood_service import neighborhood_service, TASHKENT_METRO_STATIONS
from src.services.price_intelligence_service import price_intelligence_service
from src.services.ai_match_service import ai_match_service
from src.services.scam_detector_service import scam_detector_service
from src.services.roommate_service import roommate_service
from src.services.comparison_service import comparison_service
from src.services.assistant_service import assistant_service
from src.services.reverse_image_service import reverse_image_service
from src.providers.base import RawListingItem
from src.providers.parser import parse_price
from src.api.auth import get_api_key, get_current_user
from src.api.schemas import (
    ListingResponse,
    PaginatedListingsResponse,
    HealthResponse,
    MonitorStatusResponse,
    ManualListingIngestRequest,
    ClassificationResponse,
    TelegramLoginSessionResponse,
    TelegramSessionCheckResponse,
    TelegramWidgetAuthRequest,
    AuthUserResponse,
    MockConfirmAuthRequest,
    AIMatchRequest,
    CompareRequest,
    RoommateProfileCreate,
    RoommateConnectRequest,
    ListingReportRequest,
    ReverseImageSearchRequest,
    AssistantChatRequest,
)

api_router = APIRouter(prefix="/api")


def to_listing_response(item: Listing) -> ListingResponse:
    """Format ORM Listing into Pydantic ListingResponse with source attribution and contacts."""
    cls_data = None
    if item.classification:
        cls_data = ClassificationResponse(
            label=item.classification.label,
            confidence_score=item.classification.confidence_score,
            reasons=item.classification.reasons,
        )
    source_attributions = {
        "olx_uz": "Tashqi manba (OLX Uzbekistan)",
    }
    source_attr = source_attributions.get(item.source, f"Tashqi manba ({item.source})")

    # Coordinates fallback to district center if missing
    lat = item.coordinates_lat
    lon = item.coordinates_lon
    if not lat or not lon:
        lat, lon = neighborhood_service.get_district_coordinates(item.district)

    # Metro station fallback calculation if missing
    metro = item.metro_station
    metro_dist = item.metro_distance_m
    if not metro and lat and lon:
        nearest = neighborhood_service.find_nearest_metro(lat, lon)
        if nearest:
            metro = nearest["name"]
            metro_dist = nearest["distance_m"]

    return ListingResponse(
        id=item.id,
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
        contact_phone=item.contact_phone,
        contact_telegram=item.contact_telegram,
        target_audience=item.target_audience or "any",
        coordinates_lat=lat,
        coordinates_lon=lon,
        metro_station=metro,
        metro_distance_m=metro_dist,
        fair_price_category=item.fair_price_category or "fair_price",
        estimated_market_price=item.estimated_market_price,
        price_diff_percent=item.price_diff_percent,
        scam_risk_score=item.scam_risk_score or 10,
        scam_risk_level=item.scam_risk_level or "low",
        scam_risk_reasons=item.scam_risk_reasons or [],
        image_urls=item.image_urls or [],
        publication_date=item.publication_date,
        first_seen_at=item.first_seen_at,
        last_seen_at=item.last_seen_at,
        is_active=item.is_active,
        classification=cls_data,
        source_attribution=source_attr,
    )


@api_router.get("/health", response_model=HealthResponse)
async def check_health(session: AsyncSession = Depends(get_db_session)):
    """System health check verifying database connectivity."""
    db_ok = False
    try:
        await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return HealthResponse(
        status="OK" if db_ok else "DEGRADED",
        database_connected=db_ok,
        timestamp=datetime.now(timezone.utc),
    )


@api_router.get("/listings", response_model=PaginatedListingsResponse)
async def get_listings(
    district: Optional[str] = Query(None, description="Tashkent district filter"),
    min_price: Optional[int] = Query(None, description="Minimum price in UZS"),
    max_price: Optional[int] = Query(None, description="Maximum price in UZS"),
    rooms: Optional[int] = Query(None, description="Room count"),
    target_audience: Optional[str] = Query(None, description="Filter by target audience: 'family', 'female', 'male', 'any'"),
    owner_only: bool = Query(False, description="Filter only likely-owner listings"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve paginated listings with search filters and source attribution."""
    districts = [district] if district else None
    room_list = [rooms] if rooms is not None else None

    items, total = await listing_service.search_listings(
        session=session,
        districts=districts,
        min_price=min_price,
        max_price=max_price,
        rooms=room_list,
        target_audience=target_audience,
        owner_only=owner_only,
        limit=limit,
        offset=offset,
    )

    response_items = [to_listing_response(item) for item in items]

    return PaginatedListingsResponse(
        items=response_items,
        total=total,
        limit=limit,
        offset=offset,
    )


@api_router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: int, session: AsyncSession = Depends(get_db_session)
):
    """Get detailed information for a single listing."""
    listing = await listing_service.get_listing_by_id(session, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing {listing_id} not found",
        )

    return to_listing_response(listing)


@api_router.get(
    "/admin/monitor-status",
    response_model=MonitorStatusResponse,
    dependencies=[Depends(get_api_key)],
)
async def get_monitor_status():
    """Retrieve operational status of the periodic listing collector."""
    summary = monitor_worker.status_summary
    return MonitorStatusResponse(
        provider=summary["provider"],
        is_running=summary["is_running"],
        is_paused=summary["is_paused"],
        poll_interval_seconds=summary["poll_interval_seconds"],
        consecutive_failures=summary["consecutive_failures"],
        last_run_at=summary["last_run_at"],
        last_status=summary["last_status"],
    )


@api_router.post(
    "/listings",
    response_model=ListingResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_api_key)],
)
async def ingest_manual_listing(
    req: ManualListingIngestRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Ingest a listing manually or via authorized feed."""
    price_uzs, currency, clean_raw = parse_price(req.price_raw)

    raw_item = RawListingItem(
        source="manual_or_feed",
        canonical_url=req.canonical_url,
        title=req.title,
        price_raw=clean_raw or req.price_raw,
        price_uzs=price_uzs,
        currency=currency,
        district=req.district,
        rooms=req.rooms,
        area=req.area,
        floor=req.floor,
        description=req.description,
        image_urls=req.image_urls,
    )

    listing, is_new = await listing_service.ingest_raw_listing(session, raw_item)

    return to_listing_response(listing)


# --- Telegram Authentication Routes ---


@api_router.post("/auth/telegram/session", response_model=TelegramLoginSessionResponse)
async def create_telegram_login_session(
    session: AsyncSession = Depends(get_db_session),
):
    """Initiate a deep-link Telegram login session for the website."""
    data = await auth_service.create_auth_session(session)
    return TelegramLoginSessionResponse(**data)


@api_router.get("/auth/telegram/check", response_model=TelegramSessionCheckResponse)
async def check_telegram_login_session(
    session_id: str = Query(..., description="Unique auth session id"),
    session: AsyncSession = Depends(get_db_session),
):
    """Poll session status: returns PENDING, AUTHENTICATED, EXPIRED, or NOT_FOUND."""
    res = await auth_service.get_session_status(session, session_id)
    status_str = res.get("status", "NOT_FOUND")

    if status_str == "AUTHENTICATED":
        user_dict = res.get("user")
        user_resp = AuthUserResponse(**user_dict) if user_dict else None
        return TelegramSessionCheckResponse(
            status=status_str,
            token=res.get("token"),
            user=user_resp,
        )

    return TelegramSessionCheckResponse(status=status_str)


@api_router.post("/auth/telegram/widget", response_model=TelegramSessionCheckResponse)
async def authenticate_telegram_widget(
    req: TelegramWidgetAuthRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Verify official Telegram Login Widget cryptographic HMAC-SHA256 signature."""
    payload = req.model_dump()
    res = await auth_service.authenticate_widget(session, payload)

    if res.get("status") != "AUTHENTICATED":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=res.get("error", "Telegram vidjeti orqali kirishda xatolik yuz berdi"),
        )

    user_dict = res.get("user")
    user_resp = AuthUserResponse(**user_dict) if user_dict else None
    return TelegramSessionCheckResponse(
        status="AUTHENTICATED",
        token=res.get("token"),
        user=user_resp,
    )


@api_router.get("/auth/me", response_model=AuthUserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve currently logged in user profile using Bearer JWT token."""
    return AuthUserResponse(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        first_name=current_user.first_name,
        username=current_user.username,
        photo_url=current_user.photo_url,
        is_admin=current_user.is_admin,
    )


@api_router.post("/auth/telegram/mock_confirm", response_model=TelegramSessionCheckResponse)
async def mock_confirm_session(
    req: MockConfirmAuthRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Confirm a session directly (for test suites and automated verification)."""
    success, user = await auth_service.confirm_auth_session(
        session=session,
        session_id=req.session_id,
        telegram_id=req.telegram_id or 5079685694,
        username=req.username or "joyliy_user",
        first_name=req.first_name or "Ali",
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session expired or not found",
        )

    token = auth_service.create_jwt_token(
        user_id=user.id,
        telegram_id=user.telegram_id,
        is_admin=user.is_admin,
    )
    return TelegramSessionCheckResponse(
        status="AUTHENTICATED",
        token=token,
        user=AuthUserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            username=user.username,
            photo_url=user.photo_url,
            is_admin=user.is_admin,
        ),
    )


# --- 1. AI Apartment Match Endpoints ---

@api_router.post("/ai/match")
async def ai_apartment_match(
    req: AIMatchRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute AI Natural-Language apartment search with match percentages and explanations."""
    result = await ai_match_service.search_and_rank_matches(session, req.query, limit=req.limit)
    formatted_results = []
    for item in result["results"]:
        formatted_results.append({
            "listing": to_listing_response(item["listing"]),
            "match_score": item["match_score"],
            "pros": item["pros"],
            "cons": item["cons"],
        })
    return {
        "query": result["query"],
        "parsed_filters": result["parsed_filters"],
        "total_matches": len(formatted_results),
        "results": formatted_results,
    }


@api_router.get("/ai/parse-query")
async def ai_parse_query(q: str = Query(..., description="Natural language search query")):
    """Extract structured filter entities from natural language text."""
    return ai_match_service.parse_natural_language_query(q)


# --- 2. Smart Map Search Endpoints ---

@api_router.get("/map/listings")
async def get_map_listings(
    district: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None),
    rooms: Optional[int] = Query(None),
    owner_only: bool = Query(False),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve map-optimized lightweight apartment markers with coordinates and price badges."""
    conditions = [Listing.is_active == True]
    if district:
        conditions.append(Listing.district.ilike(f"%{district.strip()}%"))
    if max_price:
        conditions.append(Listing.price_uzs <= max_price)
    if rooms:
        conditions.append(Listing.rooms == rooms)

    stmt = select(Listing).where(and_(*conditions)).limit(200)
    rows = (await session.execute(stmt)).scalars().all()

    markers = []
    for item in rows:
        if owner_only and item.classification and item.classification.label != "LIKELY_OWNER":
            continue

        lat = item.coordinates_lat
        lon = item.coordinates_lon
        if not lat or not lon:
            lat, lon = neighborhood_service.get_district_coordinates(item.district)
            # Add subtle deterministic jitter so apartments in same district don't overlap completely
            jitter = ((item.id % 17) - 8) * 0.0018
            jitter_lon = ((item.id % 13) - 6) * 0.0022
            lat += jitter
            lon += jitter_lon

        price_tag = f"{int(item.price_uzs / 1e6)}M" if (item.price_uzs and item.price_uzs >= 1_000_000) else "Kelish."
        markers.append({
            "id": item.id,
            "title": item.title,
            "price_uzs": item.price_uzs,
            "price_tag": price_tag,
            "district": item.district or "Toshkent",
            "rooms": item.rooms or 1,
            "area": item.area,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "image_url": item.image_urls[0] if (item.image_urls and len(item.image_urls) > 0) else None,
            "is_owner": bool(item.classification and item.classification.label == "LIKELY_OWNER"),
            "metro_station": item.metro_station,
        })
    return {"total": len(markers), "markers": markers}


@api_router.get("/map/metros")
async def get_tashkent_metros():
    """Retrieve all Tashkent metro stations with coordinates and line attribution."""
    return {"stations": TASHKENT_METRO_STATIONS}


# --- 3. Fair Price AI — Price Intelligence Endpoints ---

@api_router.get("/price-intelligence/stats")
async def get_price_intelligence_stats(
    district: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve district-level market benchmarks, medians, and room averages from live database."""
    return await price_intelligence_service.get_district_market_stats(session, district)


@api_router.get("/price-intelligence/{listing_id}")
async def get_listing_price_intelligence(
    listing_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Evaluate an apartment's price against comparable listings in the neighborhood."""
    stmt = select(Listing).where(Listing.id == listing_id)
    listing = (await session.execute(stmt)).scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return await price_intelligence_service.evaluate_listing_price(session, listing)


# --- 4. Shortlist Battle — Apartment Comparison ---

@api_router.post("/compare")
async def compare_apartments(
    req: CompareRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Side-by-side comparison of 2-5 apartments with composite value scoring and AI winner badge."""
    return await comparison_service.compare_listings(session, req.listing_ids)


# --- 5. Roommate Finder Endpoints ---

@api_router.get("/roommates")
async def list_roommates(
    district: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    max_budget: Optional[int] = Query(None),
    occupation: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
):
    """List active roommate search profiles in Tashkent."""
    profiles = await roommate_service.list_profiles(
        session, district=district, gender=gender, max_budget=max_budget, occupation=occupation
    )
    return {
        "total": len(profiles),
        "profiles": [
            {
                "id": p.id,
                "name": p.name,
                "age": p.age,
                "gender": p.gender,
                "budget_uzs": p.budget_uzs,
                "budget_formatted": f"{p.budget_uzs:,} so‘m",
                "preferred_districts": p.preferred_districts,
                "occupation": p.occupation,
                "lifestyle_cleanliness": p.lifestyle_cleanliness,
                "lifestyle_sleep": p.lifestyle_sleep,
                "smoking_allowed": p.smoking_allowed,
                "pets_allowed": p.pets_allowed,
                "bio": p.bio,
                "move_in_date": p.move_in_date,
                "contact_telegram": p.contact_telegram,
                "is_verified": p.is_verified,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in profiles
        ],
    }


@api_router.post("/roommates")
async def create_roommate_profile(
    req: RoommateProfileCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Publish a new roommate seeker profile."""
    prof = await roommate_service.create_profile(session, req.model_dump())
    return {"status": "created", "profile_id": prof.id, "name": prof.name}


@api_router.post("/roommates/{roommate_id}/connect")
async def connect_roommate(
    roommate_id: int,
    req: RoommateConnectRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Send connection request to a prospective roommate."""
    conn_req = await roommate_service.send_connection_request(
        session,
        roommate_id=roommate_id,
        from_name=req.from_name,
        from_contact=req.from_contact,
        message=req.message,
    )
    return {"status": "sent", "request_id": conn_req.id}


# --- 6. Neighborhood Intelligence ---

@api_router.get("/neighborhoods")
async def list_neighborhoods():
    """Retrieve scorecards and infrastructure benchmarks for all 12 Tashkent districts."""
    return {"districts": neighborhood_service.get_all_districts()}


@api_router.get("/neighborhoods/{district_name}")
async def get_neighborhood_detail(district_name: str):
    """Retrieve detailed infrastructure, scores, and landmarks for a specific district."""
    details = neighborhood_service.get_district_details(district_name)
    if not details:
        raise HTTPException(status_code=404, detail="District not found")
    return details


# --- 7. Scam Detector & Reporting Endpoints ---

@api_router.post("/listings/{listing_id}/report")
async def report_suspicious_listing(
    listing_id: int,
    req: ListingReportRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Report a suspicious, fraudulent, or broker listing."""
    report = await scam_detector_service.submit_user_report(
        session, listing_id=listing_id, reason=req.reason, details=req.details
    )
    return {"status": "reported", "report_id": report.id}


@api_router.get("/listings/{listing_id}/risk")
async def get_listing_risk_assessment(
    listing_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Run multi-signal fraud evaluation on an apartment listing."""
    stmt = select(Listing).where(Listing.id == listing_id)
    listing = (await session.execute(stmt)).scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return await scam_detector_service.analyze_listing_risk(session, listing)


# --- 8. Reverse Image Search ---

@api_router.post("/listings/reverse-image-search")
async def reverse_image_search(
    req: ReverseImageSearchRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Identify duplicate or cross-posted apartment photos via perceptual hash fingerprinting."""
    return await reverse_image_service.search_by_image_url(session, req.image_url)


# --- 9. Joyliy AI Virtual Assistant ---

@api_router.post("/ai/assistant-chat")
@api_router.post("/assistant/chat")
async def ai_virtual_assistant_chat(
    req: AssistantChatRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Conversational assistant consultation regarding lease agreements, zalog, utilities, or specific listings."""
    return await assistant_service.get_response(
        session, user_message=req.message, listing_id=req.listing_id, language=req.language
    )


# --- 10. Admin Ecosystem Moderation & Stats ---

@api_router.get("/admin/ecosystem-stats")
async def get_ecosystem_stats(
    session: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(get_api_key),
):
    """Comprehensive administrative metrics for Joyliy Real Estate Ecosystem."""
    from src.models.user import User
    from src.models.listing import ChannelPublishQueue, ChannelPostHistory
    from src.models.ecosystem import RoommateProfile, ListingReport

    total_listings = (await session.execute(select(func.count(Listing.id)))).scalar() or 0
    active_listings = (await session.execute(select(func.count(Listing.id)).where(Listing.is_active == True))).scalar() or 0
    likely_owners = (await session.execute(select(func.count(Listing.id)).join(Listing.classification).where(ListingClassification.label == "LIKELY_OWNER"))).scalar() or 0
    total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
    total_roommates = (await session.execute(select(func.count(RoommateProfile.id)))).scalar() or 0
    total_reports = (await session.execute(select(func.count(ListingReport.id)))).scalar() or 0
    queue_count = (await session.execute(select(func.count(ChannelPublishQueue.id)).where(ChannelPublishQueue.status == "pending"))).scalar() or 0
    channel_posts = (await session.execute(select(func.count(ChannelPostHistory.id)))).scalar() or 0

    return {
        "total_listings": total_listings,
        "active_listings": active_listings,
        "likely_owners": likely_owners,
        "owner_percentage": round((likely_owners / total_listings * 100), 1) if total_listings else 0,
        "total_users": total_users,
        "total_roommate_profiles": total_roommates,
        "pending_reports": total_reports,
        "channel_queue_pending": queue_count,
        "channel_posts_published": channel_posts,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@api_router.get("/admin/reports")
async def get_admin_reports(
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(get_api_key),
):
    """Retrieve user complaint logs for moderation."""
    return await scam_detector_service.get_all_reports(session, status=status)



# --- Telegram Webhook Integration (Eliminates Render Rolling Deploy Conflicts) ---

_telegram_bot = None
_telegram_dp = None


def register_bot_webhook(bot, dp):
    """Register active Bot and Dispatcher references for webhook handling."""
    global _telegram_bot, _telegram_dp
    _telegram_bot = bot
    _telegram_dp = dp


@api_router.post("/telegram-webhook", include_in_schema=False)
async def handle_telegram_webhook(request: Request):
    """Receive Telegram webhook updates and process them with aiogram dispatcher."""
    if _telegram_bot and _telegram_dp:
        try:
            payload = await request.json()
            asyncio.create_task(_telegram_dp.feed_raw_update(bot=_telegram_bot, update=payload))
        except Exception as exc:
            import logging
            logging.getLogger("joyliy.webhook").warning("Error processing telegram webhook payload: %s", exc)
    return {"ok": True}



