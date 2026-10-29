"""Abstract base class and data types for listing providers."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProviderStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BLOCKED_BY_ACCESS_CONTROL = "BLOCKED_BY_ACCESS_CONTROL"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"


class RawListingItem(BaseModel):
    """Normalized listing item extracted by a provider."""

    source: str = "olx_uz"
    source_id: Optional[str] = None
    canonical_url: str
    title: str
    price_raw: Optional[str] = None
    price_uzs: Optional[int] = None
    currency: str = "UZS"
    district: Optional[str] = None
    rooms: Optional[int] = None
    area: Optional[float] = None
    floor: Optional[str] = None
    description: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_telegram: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    # Publication date is None if not reliably known. Never fabricated.
    publication_date: Optional[datetime] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderHealth(BaseModel):
    """Health diagnostic for a provider."""

    status: ProviderStatus
    provider_name: str
    last_check_at: datetime
    consecutive_failures: int = 0
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class BaseListingProvider(ABC):
    """Interface for apartment listing sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        pass

    @abstractmethod
    async def fetch_listings(self) -> List[RawListingItem]:
        """Fetch newly published or available rental listings."""
        pass

    @abstractmethod
    async def check_health(self) -> ProviderHealth:
        """Check provider operational status and permitted access."""
        pass

