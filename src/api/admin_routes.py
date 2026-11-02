"""FastAPI Router for Joyliy Enterprise Administrative Dashboard."""

import csv
import io
import os
from typing import Any, Dict, List, Optional
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Header,
    Query,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db_session
from src.services.admin_service import admin_service
from src.services.seo_service import seo_service

admin_router = APIRouter(prefix="/api/admin", tags=["Enterprise Admin Dashboard"])


# --- Schemas ---
class AdminLoginRequest(BaseModel):
    username: str = Field(..., description="Admin username or email")
    password: str = Field(..., description="Admin password")


class ListingUpdateRequest(BaseModel):
    title: Optional[str] = None
    price_uzs: Optional[int] = None
    district: Optional[str] = None
    rooms: Optional[int] = None
    area: Optional[float] = None
    floor: Optional[str] = None
    deal_type: Optional[str] = None
    property_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    target_audience: Optional[str] = None
    is_furnished: Optional[bool] = None
    renovation_type: Optional[str] = None


class ListingCreateRequest(BaseModel):
    title: str
    price_uzs: int
    district: str
    rooms: int = 2
    area: float = 60.0
    floor: str = "3/9"
    deal_type: str = "rent"
    property_type: str = "secondary"
    description: Optional[str] = ""
    contact_phone: Optional[str] = None
    contact_telegram: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    target_audience: str = "any"
    is_furnished: bool = True


class BulkListingRequest(BaseModel):
    listing_ids: List[int]
    action: str  # 'archive', 'restore', 'delete'


class ParserRunRequest(BaseModel):
    deep: bool = True
    pages: int = 2


class ParserScheduleRequest(BaseModel):
    schedule_times: Optional[List[str]] = None
    morning_time: Optional[str] = None
    morning_enabled: Optional[bool] = None


class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    email: Optional[str] = None
    password: Optional[str] = None


# --- Authentication Dependency ---
async def get_current_admin(
    joyliy_admin_session: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """Verify administrator identity via HTTP-only cookie or Bearer token."""
    token = None
    if joyliy_admin_session:
        token = joyliy_admin_session
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = admin_service.decode_admin_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token",
        )

    return payload


def require_role(allowed_roles: List[str]):
    """Decorator to enforce granular RBAC permissions."""
    async def role_checker(admin: Dict[str, Any] = Depends(get_current_admin)) -> Dict[str, Any]:
        role = admin.get("role", "viewer")
        if role == "super_admin":
            return admin
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required role: {', '.join(allowed_roles)}",
            )
        return admin
    return role_checker


# =================================================================
# 1. Admin Authentication Routes
# =================================================================

@admin_router.post("/auth/login")
async def admin_login(
    payload: AdminLoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
):
    """Admin login endpoint setting HTTP-only session cookie."""
    auth_res = await admin_service.authenticate_admin(
        username=payload.username,
        password=payload.password,
        session=session,
    )
    if not auth_res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto‘g‘ri login yoki parol",
        )

    admin_data, token = auth_res

    # Set secure HTTP-only cookie
    response.set_cookie(
        key="joyliy_admin_session",
        value=token,
        max_age=settings.ADMIN_JWT_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,  # Set to True on strict production HTTPS
        samesite="lax",
        path="/",
    )

    return {
        "status": "success",
        "success": True,
        "token": token,
        "admin": admin_data,
        "user": admin_data,
    }


@admin_router.get("/auth/me")
async def admin_get_me(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Retrieve authenticated administrator profile."""
    admin_info = {
        "id": int(current_admin.get("sub", 1)),
        "username": current_admin.get("username", "admin"),
        "role": current_admin.get("role", "admin"),
        "is_admin": True,
    }
    return {
        "status": "success",
        "success": True,
        "authenticated": True,
        "admin": admin_info,
        "user": admin_info,
    }


@admin_router.post("/auth/logout")
async def admin_logout(response: Response):
    """Clear administrator session cookie."""
    response.delete_cookie(key="joyliy_admin_session", path="/")
    return {"status": "logged_out", "success": True}


# =================================================================
# 2. Overview Dashboard
# =================================================================

@admin_router.get("/overview")
@admin_router.get("/overview/stats")
async def get_overview_dashboard(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve full dashboard statistics directly from database."""
    stats = await admin_service.get_overview_stats(session)
    if isinstance(stats, dict) and "success" not in stats:
        stats["success"] = True
    return stats


# =================================================================
# 3. Listings Management
# =================================================================

@admin_router.get("/listings")
async def list_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    deal_type: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    rooms: Optional[int] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    telegram_status: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Paginated listing management across full database."""
    chosen_sort = sort or sort_by or "newest"
    return await admin_service.get_listings(
        session=session,
        page=page,
        limit=limit,
        search=search,
        district=district,
        deal_type=deal_type,
        property_type=property_type,
        rooms=rooms,
        min_price=min_price,
        max_price=max_price,
        source=source,
        status=status,
        is_active=is_active,
        telegram_status=telegram_status,
        sort_by=chosen_sort,
    )


@admin_router.post("/listings/{listing_id}/approve")
async def approve_listing(
    listing_id: int,
    publish_to_telegram: bool = Query(True),
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin", "editor"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Approve a pending listing, activate it on website, and optionally publish to Telegram."""
    admin_id = int(current_admin.get("sub", 1))
    res = await admin_service.approve_listing(
        session=session,
        listing_id=listing_id,
        admin_id=admin_id,
        publish_to_telegram=publish_to_telegram,
    )
    if not res:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {
        "success": True,
        "status": "success",
        "is_active": res.get("is_active", True),
        "telegram_posted": res.get("telegram_posted", False),
        "data": res,
    }


@admin_router.post("/listings/{listing_id}/reject")
async def reject_listing(
    listing_id: int,
    reason: Optional[str] = Query(None),
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin", "editor"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Reject a listing and deactivate it."""
    admin_id = int(current_admin.get("sub", 1))
    res = await admin_service.reject_listing(
        session=session,
        listing_id=listing_id,
        admin_id=admin_id,
        reason=reason,
    )
    if not res:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {
        "success": True,
        "status": "success",
        "is_active": res.get("is_active", False),
        "data": res,
    }


@admin_router.get("/listings/{listing_id}")
async def get_listing_detail(
    listing_id: int,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve complete listing dossier with history."""
    detail = await admin_service.get_listing_detail(session, listing_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {
        "success": True,
        "status": "success",
        "item": detail,
        **detail,
    }


@admin_router.post("/listings")
async def create_listing(
    payload: ListingCreateRequest,
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin", "editor"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Create manual property listing."""
    item = await admin_service.create_manual_listing(
        session=session,
        data=payload.model_dump(),
        admin_id=int(current_admin.get("sub", 1)),
    )
    return {"status": "created", "listing_id": item.id}


@admin_router.put("/listings/{listing_id}")
async def update_listing(
    listing_id: int,
    payload: ListingUpdateRequest,
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin", "editor"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Update listing attributes with audit trail."""
    data = payload.model_dump(exclude_unset=True)
    item = await admin_service.update_listing(
        session=session,
        listing_id=listing_id,
        data=data,
        admin_id=int(current_admin.get("sub", 1)),
    )
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"status": "updated", "listing_id": item.id}


@admin_router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: int,
    hard: bool = Query(False),
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Soft delete (archive) or hard delete listing."""
    ok = await admin_service.delete_listing(
        session=session,
        listing_id=listing_id,
        hard=hard,
        admin_id=int(current_admin.get("sub", 1)),
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"status": "deleted", "hard": hard}


@admin_router.post("/listings/bulk")
async def bulk_listings_action(
    payload: BulkListingRequest,
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Bulk action on listings: archive, restore, delete."""
    return await admin_service.bulk_action_listings(
        session=session,
        listing_ids=payload.listing_ids,
        action=payload.action,
        admin_id=int(current_admin.get("sub", 1)),
    )


# =================================================================
# 4. Parser Management Center
# =================================================================

@admin_router.get("/parser/status")
async def get_parser_status(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Telemetry and status of the automatic property parser."""
    return await admin_service.get_parser_status(session)


@admin_router.post("/parser/run")
async def trigger_parser_run(
    payload: ParserRunRequest,
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Trigger immediate on-demand discovery scan."""
    return await admin_service.trigger_parser_run(
        session=session,
        deep=payload.deep,
        pages=payload.pages,
        admin_id=int(current_admin.get("sub", 1)),
    )


@admin_router.post("/parser/pause")
async def pause_parser(
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Pause automatic background scanning."""
    return await admin_service.toggle_parser_pause(session, pause=True, admin_id=int(current_admin.get("sub", 1)))


@admin_router.post("/parser/resume")
async def resume_parser(
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Resume automatic background scanning."""
    return await admin_service.toggle_parser_pause(session, pause=False, admin_id=int(current_admin.get("sub", 1)))


@admin_router.post("/parser/schedule")
async def update_parser_schedule(
    payload: ParserScheduleRequest,
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Update Tashkent scraping schedules."""
    return await admin_service.update_parser_schedules(
        session=session,
        schedule_times=payload.schedule_times or [],
        morning_time=payload.morning_time,
        morning_enabled=payload.morning_enabled,
        admin_id=int(current_admin.get("sub", 1)),
    )


# =================================================================
# 5. Telegram Publishing Management
# =================================================================

@admin_router.get("/telegram")
@admin_router.get("/telegram/overview")
async def get_telegram_overview(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve Telegram broadcast queue and statistics."""
    return await admin_service.get_telegram_center(session)


@admin_router.post("/telegram/publish/{queue_id}")
async def publish_telegram_queue_item(
    queue_id: int,
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Immediately broadcast queued listing to Telegram."""
    return await admin_service.publish_now_telegram(
        session=session,
        queue_id=queue_id,
        admin_id=int(current_admin.get("sub", 1)),
    )


# =================================================================
# 6. User Management (RBAC)
# =================================================================

@admin_router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """List users with RBAC role filter."""
    return await admin_service.get_users_list(
        session=session,
        page=page,
        limit=limit,
        search=search,
        role=role,
        is_active=is_active,
    )


@admin_router.put("/users/{user_id}")
async def update_user_status(
    user_id: int,
    payload: UserUpdateRequest,
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Update user role, active status, or credentials."""
    user = await admin_service.update_user(
        session=session,
        user_id=user_id,
        data=payload.model_dump(exclude_unset=True),
        admin_id=int(current_admin.get("sub", 1)),
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "updated", "user_id": user.id}


# =================================================================
# 7. Interactive Property Map
# =================================================================

@admin_router.get("/map/listings")
async def get_map_listings(
    district: Optional[str] = Query(None),
    deal_type: Optional[str] = Query(None),
    limit: int = Query(300, ge=1, le=1000),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch geocoded listings for map clustering."""
    return await admin_service.get_map_listings(
        session=session,
        district=district,
        deal_type=deal_type,
        limit=limit,
    )


# =================================================================
# 8. Analytics & Data Export
# =================================================================

@admin_router.get("/analytics")
async def get_analytics_report(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve full analytical trends and distributions."""
    return await admin_service.get_overview_stats(session)


@admin_router.get("/analytics/export")
async def export_listings_csv(
    current_admin: Dict[str, Any] = Depends(require_role(["super_admin", "admin", "analyst"])),
    session: AsyncSession = Depends(get_db_session),
):
    """Export real database listings to CSV file."""
    data = await admin_service.get_listings(session=session, page=1, limit=500)
    items = data.get("items", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Title", "Price UZS", "District", "Rooms", "Area",
        "Deal Type", "Source", "Active", "Created At", "Telegram Published"
    ])

    for it in items:
        writer.writerow([
            it["id"],
            it["title"],
            it["price_uzs"],
            it["district"],
            it["rooms"],
            it["area"],
            it["deal_type"],
            it["source"],
            it["is_active"],
            it["first_seen_at"],
            it["posted_to_channel_at"],
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="joyliy_listings_export.csv"'},
    )


# =================================================================
# 9. System Settings & Health
# =================================================================

@admin_router.get("/settings")
async def get_system_settings(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve system configuration and database health metrics."""
    db_file = "uyda.db"
    db_size_mb = round(os.path.getsize(db_file) / (1024 * 1024), 2) if os.path.exists(db_file) else 0

    return {
        "general": {
            "platform_name": "Joyliy.uz",
            "base_url": settings.WEBSITE_URL,
            "currency": "UZS",
            "timezone": "Asia/Tashkent",
            "version": "2.4.0",
        },
        "parser": {
            "sources": ["olx_uz_http", "uybor", "joymee"],
            "morning_scrape_enabled": settings.MORNING_SCRAPE_ENABLED,
            "morning_scrape_time": settings.MORNING_SCRAPE_TIME,
        },
        "telegram": {
            "bot_username": settings.BOT_USERNAME,
            "channel_id": settings.CHANNEL_ID,
            "channel_title": "Joyliy | Toshkentda maklersiz ijara",
            "connected": bool(settings.BOT_TOKEN),
        },
        "database": {
            "type": "SQLite / PostgreSQL Compatible",
            "file_size_mb": db_size_mb,
            "pool_status": "Healthy",
        },
        "security": {
            "rbac_enabled": True,
            "session_lifetime_minutes": settings.ADMIN_JWT_EXPIRE_MINUTES,
        },
    }


# =================================================================
# 10. SEO Audit and Sitemap Sync
# =================================================================

@admin_router.get("/seo/summary")
async def get_seo_summary(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve comprehensive technical SEO audit data and sitemap statuses."""
    return await seo_service.get_seo_audit_summary(session)


@admin_router.post("/seo/sync")
async def sync_sitemaps(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Synchronize XML sitemaps into frontend public and static directories."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    frontend_public = os.path.join(base_dir, "frontend", "public")
    frontend_dist = os.path.join(base_dir, "frontend_dist")

    res = await seo_service.sync_static_sitemaps(frontend_public, session)
    if os.path.exists(frontend_dist):
        await seo_service.sync_static_sitemaps(frontend_dist, session)

    return {"success": True, "details": res}


# =================================================================
# 11. Roommate Profiles Moderation & Management
# =================================================================

@admin_router.get("/roommates")
async def get_admin_roommates(
    status: str = Query("all", description="all, pending, active, inactive"),
    search: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve roommate profiles with administrative moderation statuses."""
    res = await admin_service.get_roommates_list(
        session=session,
        status=status,
        search=search,
        gender=gender,
        district=district,
        limit=limit,
        offset=offset,
    )
    return res


@admin_router.post("/roommates/{profile_id}/approve")
async def approve_admin_roommate(
    profile_id: int,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Approve a roommate profile, setting is_active=True and is_verified=True."""
    res = await admin_service.approve_roommate(
        session=session,
        profile_id=profile_id,
        admin_id=current_admin.get("id"),
    )
    if not res:
        raise HTTPException(status_code=404, detail="Roommate profile not found")
    return {"success": True, "data": res, "is_active": True}


@admin_router.post("/roommates/{profile_id}/reject")
async def reject_admin_roommate(
    profile_id: int,
    payload: Optional[Dict[str, Any]] = None,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Reject or deactivate a roommate profile."""
    reason = payload.get("reason") if payload else None
    res = await admin_service.reject_roommate(
        session=session,
        profile_id=profile_id,
        admin_id=current_admin.get("id"),
        reason=reason,
    )
    if not res:
        raise HTTPException(status_code=404, detail="Roommate profile not found")
    return {"success": True, "data": res, "is_active": False}


@admin_router.delete("/roommates/{profile_id}")
async def delete_admin_roommate(
    profile_id: int,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Permanently delete a roommate profile."""
    ok = await admin_service.delete_roommate(
        session=session,
        profile_id=profile_id,
        admin_id=current_admin.get("id"),
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Roommate profile not found")
    return {"success": True, "message": "Roommate profile deleted successfully"}


