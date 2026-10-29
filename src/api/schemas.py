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

