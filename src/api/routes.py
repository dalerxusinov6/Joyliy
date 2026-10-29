"""REST API routes for website integration and monitoring."""

from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.models.user import User
from src.services.listing_service import listing_service
from src.services.monitor_worker import monitor_worker
from src.services.auth_service import auth_service
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
        "joymee_uz": "Tashqi manba (Joymee.uz)",
        "realt24_uz": "Tashqi manba (Realt24.uz)",
    }
    source_attr = source_attributions.get(item.source, f"Tashqi manba ({item.source})")
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


