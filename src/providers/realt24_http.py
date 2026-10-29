"""Realt24.uz HTTP Listing Provider adhering to site access policies and respectful rates."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx

from src.config import settings
from src.providers.base import (
    BaseListingProvider,
    ProviderHealth,
    ProviderStatus,
    RawListingItem,
)
from src.providers.parser import parse_realt24_html

logger = logging.getLogger(__name__)


class Realt24HttpListingProvider(BaseListingProvider):
    """
    HTTP provider for Realt24.uz real estate platform.
    Extracts structured listings from Next.js server-rendered HTML and React Query hydration state.
    """

    def __init__(
        self,
        base_url: str = "https://realt24.uz",
        max_pages: int = 1,
        max_items: int = 30,
        request_delay: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "uz-UZ,uz;q=0.9,ru;q=0.8,en;q=0.7",
            "Referer": "https://realt24.uz/",
        }

    @property
    def name(self) -> str:
        return "realt24_uz_http"

    async def fetch_listings(self) -> List[RawListingItem]:
        """Fetch newly published rental apartment listings from Realt24."""
        self._last_check_at = datetime.now(timezone.utc)
        all_items: List[RawListingItem] = []

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for page in range(1, self.max_pages + 1):
                url = f"{self.base_url}/search/?categoryType=rent&sortBy=dateDesc&page={page}"
                try:
                    resp = await client.get(url, headers=self.headers)
                    if resp.status_code == 200:
                        page_items = parse_realt24_html(resp.text)
                        logger.info("Realt24 page %d extracted %d listings.", page, len(page_items))

                        for it in page_items:
                            if len(all_items) >= self.max_items:
                                break
                            all_items.append(it)

                        self._consecutive_failures = 0
                        self._last_status = ProviderStatus.HEALTHY
                        self._last_message = f"Successfully extracted {len(all_items)} listings."

                        if page < self.max_pages:
                            await asyncio.sleep(self.request_delay)
                    elif resp.status_code in (401, 403):
                        self._consecutive_failures += 1
                        self._last_status = ProviderStatus.BLOCKED_BY_ACCESS_CONTROL
                        self._last_message = f"Realt24 access restricted (HTTP {resp.status_code})."
                        logger.warning("Realt24 access restricted (HTTP %d).", resp.status_code)
                        break
                    else:
                        self._consecutive_failures += 1
                        self._last_status = ProviderStatus.DEGRADED
                        self._last_message = f"Realt24 returned HTTP {resp.status_code}."
                        logger.warning("Realt24 returned HTTP %d for %s", resp.status_code, url)
                        break
                except Exception as exc:
                    self._consecutive_failures += 1
                    self._last_status = ProviderStatus.ERROR
                    self._last_message = f"Realt24 request failed: {exc}"
                    logger.error("Realt24 collection error: %s", exc)
                    break

        return all_items

    async def check_health(self) -> ProviderHealth:
        """Check operational health and endpoint accessibility."""
        health_url = f"{self.base_url}/search/?categoryType=rent&page=1"
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
                        message="Realt24 search page accessible and healthy.",
                    )
                elif resp.status_code in (401, 403):
                    return ProviderHealth(
                        status=ProviderStatus.BLOCKED_BY_ACCESS_CONTROL,
                        provider_name=self.name,
                        last_check_at=now,
                        consecutive_failures=self._consecutive_failures + 1,
                        message=f"Realt24 access restricted (HTTP {resp.status_code}).",
                    )
                else:
                    return ProviderHealth(
                        status=ProviderStatus.DEGRADED,
                        provider_name=self.name,
                        last_check_at=now,
                        consecutive_failures=self._consecutive_failures + 1,
                        message=f"Realt24 returned unexpected status code {resp.status_code}.",
                    )
        except Exception as exc:
            return ProviderHealth(
                status=ProviderStatus.ERROR,
                provider_name=self.name,
                last_check_at=now,
                consecutive_failures=self._consecutive_failures + 1,
                message=f"Realt24 connection check failed: {exc}",
            )
