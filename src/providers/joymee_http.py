"""Joymee.uz HTTP Listing Provider adhering to site access policies and respectful rate limits."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import httpx

from src.config import settings
from src.providers.base import (
    BaseListingProvider,
    ProviderHealth,
    ProviderStatus,
    RawListingItem,
)
from src.providers.parser import parse_joymee_data

logger = logging.getLogger(__name__)


class JoymeeHttpListingProvider(BaseListingProvider):
    """
    HTTP provider for Joymee.uz real estate platform.
    Fetches newly listed apartment rentals with full contact, photo, and geolocation data.
    """

    def __init__(
        self,
        base_api_url: str = "https://api.joymee.uz/api/v1",
        max_pages: int = 1,
        max_items: int = 25,
        request_delay: float = 0.4,
    ):
        self.base_api_url = base_api_url.rstrip("/")
        self.max_pages = max_pages
        self.max_items = max_items
        self.request_delay = request_delay
        self._consecutive_failures = 0
        self._last_check_at = datetime.now(timezone.utc)
        self._last_status = ProviderStatus.HEALTHY
        self._last_message = "Initialized"

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "uz-UZ,uz;q=0.9,ru;q=0.8,en;q=0.7",
            "Referer": "https://joymee.uz/",
            "Origin": "https://joymee.uz",
        }

    @property
    def name(self) -> str:
        return "joymee_uz_http"

    async def _fetch_detail(
        self, client: httpx.AsyncClient, announcement_id: int
    ) -> Optional[Dict[str, Any]]:
        """Fetch rich detail including phone, coordinates, and media for a Joymee announcement."""
        url = f"{self.base_api_url}/announcement/{announcement_id}/"
        try:
            resp = await client.get(url, headers=self.headers, timeout=8.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception as exc:
            logger.debug("Failed fetching Joymee detail for %d: %s", announcement_id, exc)
        return None

    async def fetch_listings(self) -> List[RawListingItem]:
        """Fetch newly published rental apartment listings from Joymee."""
        self._last_check_at = datetime.now(timezone.utc)
        all_items: List[RawListingItem] = []

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for page in range(1, self.max_pages + 1):
                list_url = (
                    f"{self.base_api_url}/announcement/"
                    f"?deal_type=2&property_type=1&ordering=newest&page={page}"
                )
                try:
                    resp = await client.get(list_url, headers=self.headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results") or []
                        logger.info("Joymee page %d returned %d listings.", page, len(results))

                        for it in results:
                            if len(all_items) >= self.max_items:
                                break

                            aid = it.get("id")
                            detail = None
                            if aid:
                                await asyncio.sleep(self.request_delay)
                                detail = await self._fetch_detail(client, aid)

                            try:
                                raw_item = parse_joymee_data(it, detail)
                                all_items.append(raw_item)
                            except Exception as parse_err:
                                logger.warning("Error parsing Joymee item %s: %s", aid, parse_err)

                        self._consecutive_failures = 0
                        self._last_status = ProviderStatus.HEALTHY
                        self._last_message = f"Successfully retrieved {len(all_items)} listings."
                    elif resp.status_code in (401, 403):
                        self._consecutive_failures += 1
                        self._last_status = ProviderStatus.BLOCKED_BY_ACCESS_CONTROL
                        self._last_message = f"Joymee access restricted (HTTP {resp.status_code})."
                        logger.warning("Joymee access restricted (HTTP %d).", resp.status_code)
                        break
                    else:
                        self._consecutive_failures += 1
                        self._last_status = ProviderStatus.DEGRADED
                        self._last_message = f"Joymee returned HTTP {resp.status_code}."
                        logger.warning("Joymee returned HTTP %d for %s", resp.status_code, list_url)
                        break
                except Exception as exc:
                    self._consecutive_failures += 1
                    self._last_status = ProviderStatus.ERROR
                    self._last_message = f"Joymee request failed: {exc}"
                    logger.error("Joymee collection error: %s", exc)
                    break

        return all_items

    async def check_health(self) -> ProviderHealth:
        """Check operational health and endpoint accessibility."""
        health_url = f"{self.base_api_url}/announcement/?deal_type=2&property_type=1&ordering=newest&page=1"
        now = datetime.now(timezone.utc)
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(health_url, headers=self.headers)
                if resp.status_code == 200:
                    return ProviderHealth(
                        status=ProviderStatus.HEALTHY,
                        provider_name=self.name,
                        last_check_at=now,
                        consecutive_failures=0,
                        message="Joymee API accessible and healthy.",
                    )
                elif resp.status_code in (401, 403):
                    return ProviderHealth(
                        status=ProviderStatus.BLOCKED_BY_ACCESS_CONTROL,
                        provider_name=self.name,
                        last_check_at=now,
                        consecutive_failures=self._consecutive_failures + 1,
                        message=f"Joymee access restricted (HTTP {resp.status_code}).",
                    )
                else:
                    return ProviderHealth(
                        status=ProviderStatus.DEGRADED,
                        provider_name=self.name,
                        last_check_at=now,
                        consecutive_failures=self._consecutive_failures + 1,
                        message=f"Joymee returned unexpected status code {resp.status_code}.",
                    )
        except Exception as exc:
            return ProviderHealth(
                status=ProviderStatus.ERROR,
                provider_name=self.name,
                last_check_at=now,
                consecutive_failures=self._consecutive_failures + 1,
                message=f"Joymee connection check failed: {exc}",
            )
