"""OLX HTTP Listing Provider adhering to website access controls and conservative rates."""

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
from src.providers.parser import parse_olx_html_list

logger = logging.getLogger(__name__)


class OLXHttpListingProvider(BaseListingProvider):
    """
    HTTP provider for OLX Uzbekistan.
    Monitors endpoint accessibility, applies rate limiting and backoff,
    and handles anti-bot access blocks transparently.
    """

    def __init__(
        self,
        search_urls: Optional[List[str]] = None,
        max_retries: int = 3,
        request_delay: float = 2.0,
    ):
        self.search_urls = search_urls or settings.OLX_SEARCH_URLS
        self.max_retries = max_retries
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
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uz;q=0.6",
        }

    @property
    def name(self) -> str:
        return "olx_uz_http"

    async def _fetch_with_backoff(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """Fetch URL with exponential backoff on transient errors."""
        delay = self.request_delay
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await client.get(url, headers=self.headers, timeout=12.0)
                if response.status_code == 200:
                    self._consecutive_failures = 0
                    self._last_status = ProviderStatus.HEALTHY
                    self._last_message = "Successfully retrieved listings page."
                    return response.text
                elif response.status_code in (401, 403):
                    # Access restriction / anti-bot challenge
                    self._consecutive_failures += 1
                    self._last_status = ProviderStatus.BLOCKED_BY_ACCESS_CONTROL
                    self._last_message = (
                        f"Access restricted by OLX access control (HTTP {response.status_code}). "
                        "Automated collection requires authorized feed or manual submission."
                    )
                    logger.warning(
                        "OLX access restricted (HTTP %d) on %s. Bypasses are prohibited.",
                        response.status_code,
                        url,
                    )
                    return None
                elif response.status_code >= 500:
                    # Transient server error: retry with backoff
                    logger.warning(
                        "OLX returned transient server error %d. Attempt %d/%d.",
                        response.status_code,
                        attempt,
                        self.max_retries,
                    )
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    logger.warning("OLX returned unexpected status code %d for %s", response.status_code, url)
                    return None
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as exc:
                logger.warning(
                    "Network error fetching OLX %s (attempt %d/%d): %s",
                    url,
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    self._consecutive_failures += 1
                    self._last_status = ProviderStatus.DEGRADED
                    self._last_message = f"Network timeout/connection failure: {exc}"
                    return None
            except Exception as exc:
                logger.error("Unexpected error fetching %s: %s", url, exc)
                self._consecutive_failures += 1
                self._last_status = ProviderStatus.ERROR
                self._last_message = str(exc)
                return None
        return None

    async def fetch_listings(self) -> List[RawListingItem]:
        """Iterate configured search URLs, applying polite request delays."""
        self._last_check_at = datetime.now(timezone.utc)
        all_listings: List[RawListingItem] = []

        async with httpx.AsyncClient(follow_redirects=True) as client:
            for url in self.search_urls:
                html = await self._fetch_with_backoff(client, url)
                if html:
                    parsed = parse_olx_html_list(html, base_url=url)
                    all_listings.extend(parsed)
                # Polite pacing between multiple configured URLs
                if len(self.search_urls) > 1:
                    await asyncio.sleep(self.request_delay)

        return all_listings

    async def check_health(self) -> ProviderHealth:
        """Inspect provider health and OLX response code."""
        # Check robots.txt or search url header
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                test_url = "https://www.olx.uz/robots.txt"
                resp = await client.head(test_url, headers=self.headers, timeout=5.0)
                if resp.status_code == 403:
                    self._last_status = ProviderStatus.BLOCKED_BY_ACCESS_CONTROL
                    self._last_message = (
                        "OLX access rules returned HTTP 403. "
                        "Respecting access controls; using authorized feeds / manual submissions."
                    )
                elif resp.status_code == 200:
                    self._last_status = ProviderStatus.HEALTHY
                    self._last_message = "OLX is accessible."
                else:
                    self._last_status = ProviderStatus.DEGRADED
                    self._last_message = f"OLX returned HTTP {resp.status_code}."
            except Exception as e:
                self._last_status = ProviderStatus.OFFLINE
                self._last_message = f"Failed to connect to OLX: {e}"

        self._last_check_at = datetime.now(timezone.utc)
        return ProviderHealth(
            status=self._last_status,
            provider_name=self.name,
            last_check_at=self._last_check_at,
            consecutive_failures=self._consecutive_failures,
            message=self._last_message,
            details={"search_urls": self.search_urls},
        )

