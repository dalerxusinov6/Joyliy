"""Composite Listing Provider that aggregates multiple real estate listing sources."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from src.providers.base import (
    BaseListingProvider,
    ProviderHealth,
    ProviderStatus,
    RawListingItem,
)

logger = logging.getLogger(__name__)


class CompositeListingProvider(BaseListingProvider):
    """
    Combines multiple listing providers (e.g., OLX, Joymee, Realt24)
    into a unified aggregation pipeline with fault isolation.
    """

    def __init__(self, providers: Optional[List[BaseListingProvider]] = None):
        self.providers = providers or []

    @property
    def name(self) -> str:
        names = [p.name for p in self.providers]
        return f"composite({','.join(names)})"

    def add_provider(self, provider: BaseListingProvider) -> None:
        self.providers.append(provider)

    async def fetch_listings(self) -> List[RawListingItem]:
        """Fetch listings from all registered providers with fault isolation."""
        all_items: List[RawListingItem] = []
        seen_urls = set()

        for provider in self.providers:
            try:
                logger.info("Polling provider '%s'...", provider.name)
                items = await provider.fetch_listings()
                logger.info("Provider '%s' returned %d listings.", provider.name, len(items))

                for it in items:
                    if it.canonical_url not in seen_urls:
                        seen_urls.add(it.canonical_url)
                        all_items.append(it)
            except Exception as exc:
                logger.error("Error during polling provider '%s': %s", provider.name, exc, exc_info=True)

        logger.info("Composite provider aggregation total: %d unique listings.", len(all_items))
        return all_items

    async def check_health(self) -> ProviderHealth:
        """Check operational health of all child providers."""
        now = datetime.now(timezone.utc)
        if not self.providers:
            return ProviderHealth(
                status=ProviderStatus.OFFLINE,
                provider_name=self.name,
                last_check_at=now,
                message="No providers configured.",
            )

        provider_statuses: Dict[str, Any] = {}
        healthy_count = 0
        blocked_count = 0
        error_count = 0

        for provider in self.providers:
            try:
                health = await provider.check_health()
                provider_statuses[provider.name] = {
                    "status": health.status.value,
                    "message": health.message,
                }
                if health.status == ProviderStatus.HEALTHY:
                    healthy_count += 1
                elif health.status == ProviderStatus.BLOCKED_BY_ACCESS_CONTROL:
                    blocked_count += 1
                else:
                    error_count += 1
            except Exception as exc:
                provider_statuses[provider.name] = {
                    "status": ProviderStatus.ERROR.value,
                    "message": str(exc),
                }
                error_count += 1

        if healthy_count == len(self.providers):
            overall_status = ProviderStatus.HEALTHY
            msg = f"All {healthy_count} providers are healthy."
        elif healthy_count > 0:
            overall_status = ProviderStatus.DEGRADED
            msg = f"{healthy_count}/{len(self.providers)} providers healthy."
        elif blocked_count > 0:
            overall_status = ProviderStatus.BLOCKED_BY_ACCESS_CONTROL
            msg = "All providers blocked or restricted."
        else:
            overall_status = ProviderStatus.ERROR
            msg = "All providers reported errors."

        return ProviderHealth(
            status=overall_status,
            provider_name=self.name,
            last_check_at=now,
            consecutive_failures=0 if healthy_count > 0 else 1,
            message=msg,
            details=provider_statuses,
        )

