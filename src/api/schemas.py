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
    age: Optional[int] = None
    gender: str = "any"
    budget_uzs: int
    preferred_districts: List[str] = Field(default_factory=lambda: ["Chilonzor"])
    occupation: str = "student"
    lifestyle_cleanliness: str = "very_clean"
    lifestyle_sleep: str = "flexible"
    smoking_allowed: bool = False
    pets_allowed: bool = False
    bio: str = ""
    contact_telegram: str
    move_in_date: Optional[str] = None


class RoommateConnectRequest(BaseModel):
    from_name: str
    from_contact: str
    message: str


class ListingReportRequest(BaseModel):
    reason: str
    details: Optional[str] = None


class ReverseImageSearchRequest(BaseModel):
    image_url: str


class AssistantChatRequest(BaseModel):
    message: str
    listing_id: Optional[int] = None
    language: str = "uz"


