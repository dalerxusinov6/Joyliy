"""Pydantic schemas for the REST API."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class ClassificationResponse(BaseModel):
    label: str
    confidence_score: float
    reasons: List[Dict[str, Any]] = Field(default_factory=list)


class ListingResponse(BaseModel):
    id: int
    source: str
    source_id: Optional[str]
    canonical_url: str
    title: str
    price_raw: Optional[str]
    price_uzs: Optional[int]
    currency: str
    district: Optional[str]
    rooms: Optional[int]
    area: Optional[float]
    floor: Optional[str]
    description: Optional[str]
    contact_phone: Optional[str] = None
    contact_telegram: Optional[str] = None
    target_audience: str = "any"
    deal_type: Optional[str] = "rent"
    property_type: Optional[str] = None
    coordinates_lat: Optional[float] = None
    coordinates_lon: Optional[float] = None
    metro_station: Optional[str] = None
    metro_distance_m: Optional[int] = None
    fair_price_category: Optional[str] = "fair_price"
    estimated_market_price: Optional[int] = None
    price_diff_percent: Optional[float] = None
    scam_risk_score: Optional[int] = 10
    scam_risk_level: Optional[str] = "low"
    scam_risk_reasons: List[str] = Field(default_factory=list)
    image_urls: List[str]
    publication_date: Optional[datetime]
    first_seen_at: datetime
    last_seen_at: datetime
    is_active: bool
    classification: Optional[ClassificationResponse]
    source_attribution: str = "Tashqi manba (OLX Uzbekistan)"
    disclaimer: str = "Egasidan ekanligi mustaqil tasdiqlanmagan. Asl manba havolasi saqlangan."

    model_config = ConfigDict(from_attributes=True)


class PaginatedListingsResponse(BaseModel):
    items: List[ListingResponse]
    total: int
    limit: int
    offset: int
    page: int = 1
    total_pages: int = 1
    has_next: bool = False
    has_previous: bool = False


class ParserLogEntry(BaseModel):
    timestamp: str
    level: str
    message: str


class ParserDashboardResponse(BaseModel):
    provider: str
    is_running: bool
    is_paused: bool
    poll_interval_seconds: int
    consecutive_failures: int
    last_run_at: Optional[str] = None
    last_scan_duration_seconds: float = 0.0
    last_status: str
    scheduled_times: List[str] = Field(default_factory=list)
    completed_slots_today: List[str] = Field(default_factory=list)
    next_scheduled_run: Optional[str] = None
    total_discovered_today: int = 0
    new_discovered_today: int = 0
    updated_today: int = 0
    duplicates_detected_today: int = 0
    active_listings_count: int = 0
    unposted_channel_count: int = 0
    telegram_queue_pending: int = 0
    telegram_queue_total: int = 0
    channel_posts_published_total: int = 0
    server_tashkent_time: str
    morning_scrape_enabled: bool = True
    morning_scrape_time: str = "08:00"
    morning_done_today: bool = False


class ParserRunResponse(BaseModel):
    status: str
    listings_found: int
    listings_new: int
    duration_seconds: float
    error_message: Optional[str] = None


class ParserLogsResponse(BaseModel):
    logs: List[ParserLogEntry]


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    timestamp: datetime


class MonitorStatusResponse(BaseModel):
    provider: str
    is_running: bool
    is_paused: bool
    poll_interval_seconds: int
    consecutive_failures: int
    last_run_at: Optional[datetime]
    last_status: str


class ManualListingIngestRequest(BaseModel):
    canonical_url: str
    title: str
    price_raw: Optional[str] = None
    district: Optional[str] = None
    rooms: Optional[int] = None
    area: Optional[float] = None
    floor: Optional[str] = None
    description: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)


class PublicAdSubmissionRequest(BaseModel):
    title: Optional[str] = None
    district: str
    rooms: int = 2
    price: Optional[int] = None
    price_uzs: Optional[int] = None
    currency: str = "UZS"
    area: float = 55.0
    floor: Optional[str] = "3/9"
    total_floors: Optional[int] = 9
    deal_type: str = "rent"
    property_type: str = "secondary"
    audience: Optional[str] = "all"
    target_audience: Optional[str] = "all"
    phone: Optional[str] = None
    telegram: Optional[str] = None
    description: Optional[str] = ""
    is_owner: bool = True
    image_urls: List[str] = Field(default_factory=list)


class AuthUserResponse(BaseModel):
    id: int
    telegram_id: int
    first_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    is_admin: bool = False


class TelegramLoginSessionResponse(BaseModel):
    session_id: str
    bot_username: str
    bot_url: str
    expires_in: int


class TelegramSessionCheckResponse(BaseModel):
    status: str  # PENDING, AUTHENTICATED, EXPIRED, NOT_FOUND
    token: Optional[str] = None
    user: Optional[AuthUserResponse] = None


class TelegramWidgetAuthRequest(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class MockConfirmAuthRequest(BaseModel):
    session_id: str
    telegram_id: Optional[int] = 5079685694
    first_name: Optional[str] = "Ali"
    username: Optional[str] = "alivaliyev"


# --- AI Ecosystem Schemas ---

class AIMatchRequest(BaseModel):
    query: str
    limit: int = 15


class CompareRequest(BaseModel):
    listing_ids: List[int]


class RoommateProfileCreate(BaseModel):
    name: str
    age: Optional[int] = 21
    gender: Optional[str] = "male"
    budget_uzs: int
    preferred_districts: Optional[List[str]] = None
    preferred_district: Optional[str] = None
    occupation: Optional[str] = "Talaba"
    lifestyle_tags: Optional[List[str]] = None
    lifestyle_cleanliness: Optional[str] = "clean"
    lifestyle_sleep: Optional[str] = "flexible"
    smoking_allowed: Optional[bool] = False
    pets_allowed: Optional[bool] = False
    bio: Optional[str] = ""
    about: Optional[str] = None
    contact_telegram: str
    move_in_date: Optional[str] = None
    is_active: Optional[bool] = False
    is_verified: Optional[bool] = False


class RoommateConnectRequest(BaseModel):
    from_name: Optional[str] = "Foydalanuvchi"
    from_contact: Optional[str] = None
    contact_info: Optional[str] = None
    message: Optional[str] = "Salom, anketangiz bo‘yicha bog‘lanmoqdaman."
    to_profile_id: Optional[int] = None


class ListingReportRequest(BaseModel):
    reason: str
    details: Optional[str] = None


class ReverseImageSearchRequest(BaseModel):
    image_url: str


class AssistantChatRequest(BaseModel):
    message: str
    listing_id: Optional[int] = None
    language: str = "uz"


