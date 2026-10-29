"""Fixture and Authorized Feed Listing Providers for testing and fallback."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from src.providers.base import (
    BaseListingProvider,
    ProviderHealth,
    ProviderStatus,
    RawListingItem,
)
from src.providers.parser import parse_olx_html_list

logger = logging.getLogger(__name__)


# Default high-fidelity synthetic fixture dataset representing authentic OLX Tashkent listings
DEFAULT_FIXTURE_LISTINGS = [
    {
        "source": "olx_uz",
        "source_id": "70101",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/chilonzorda-2-xonali-kvartira-maklersiz-ID70101.html",
        "title": "Chilonzor 9-kvartal 2 xonali kvartira ijaraga beriladi, maklersiz",
        "price_raw": "3 500 000 so'm",
        "price_uzs": 3500000,
        "currency": "UZS",
        "district": "Chilonzor",
        "rooms": 2,
        "area": 54.0,
        "floor": "4/9",
        "description": "Kvartira toza, barcha jihozlari bor. Maklersiz beriladi, o'zimning uyim. Maklerlar bezovta qilmasin.",
        "image_urls": ["https://img.olx.uz/images/sample_chilonzor_1.jpg"],
        "publication_date": None,
    },
    {
        "source": "olx_uz",
        "source_id": "70102",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/yunusobod-minor-metr-oldida-1-xonali-egasidan-ID70102.html",
        "title": "Yunusobod Minor metrosi yonida 1 xonali kvartira egasidan",
        "price_raw": "2 600 000 so'm",
        "price_uzs": 2600000,
        "currency": "UZS",
        "district": "Yunusobod",
        "rooms": 1,
        "area": 36.0,
        "floor": "2/5",
        "description": "Metro Minor 5 daqiqa. Uy egasidan, vositachilarsiz. Mebel va internet mavjud.",
        "image_urls": ["https://img.olx.uz/images/sample_yunusobod_1.jpg"],
        "publication_date": None,
    },
    {
        "source": "olx_uz",
        "source_id": "70103",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/mirzo-ulugbek-3-xonali-lyuks-kvartira-agentlik-ID70103.html",
        "title": "Mirzo Ulug‘bek 3 xonali evroremont kvartira",
        "price_raw": "5 800 000 so'm",
        "price_uzs": 5800000,
        "currency": "UZS",
        "district": "Mirzo Ulug‘bek",
        "rooms": 3,
        "area": 82.0,
        "floor": "7/12",
        "description": "Elit uy, hamma sharoit bor. Rieltor xizmati 50%. Komissiya mavjud.",
        "image_urls": ["https://img.olx.uz/images/sample_mirzo_1.jpg"],
        "publication_date": None,
    },
    {
        "source": "olx_uz",
        "source_id": "70104",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/sergeli-4-bekat-1-xonali-kvartira-bez-posrednikov-ID70104.html",
        "title": "Сергели 4-бекат 1-комнатная квартира без посредников",
        "price_raw": "2 200 000 сум",
        "price_uzs": 2200000,
        "currency": "UZS",
        "district": "Sergeli",
        "rooms": 1,
        "area": 32.0,
        "floor": "3/9",
        "description": "Сдаю свою 1 комнатную квартиру напрямую от владельца. Риелторам не беспокоить.",
        "image_urls": ["https://img.olx.uz/images/sample_sergeli_1.jpg"],
        "publication_date": None,
    },
    {
        "source": "olx_uz",
        "source_id": "70105",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/yakkasaroy-shota-rustaveli-3-xonali-ID70105.html",
        "title": "Yakkasaroy Shota Rustaveli ko‘chasi 3 xonali shinam kvartira",
        "price_raw": "6 500 000 so'm",
        "price_uzs": 6500000,
        "currency": "UZS",
        "district": "Yakkasaroy",
        "rooms": 3,
        "area": 96.0,
        "floor": "9/16",
        "description": "Bevosita egasidan. Yangi ta'mirlangan, oilaga yoki talabalarga beriladi.",
        "image_urls": ["https://img.olx.uz/images/sample_yakkasaroy_1.jpg"],
        "publication_date": None,
    },
]


class FixtureListingProvider(BaseListingProvider):
    """
    Fixture-based provider using predefined listings or HTML fixture files.
    Allows testing, offline development, and demonstration without hitting rate limits or access controls.
    """

    def __init__(self, fixture_path: Optional[str] = None):
        self.fixture_path = fixture_path
        self._iteration = 0

    @property
    def name(self) -> str:
        return "fixture_provider"

    async def fetch_listings(self) -> List[RawListingItem]:
        self._iteration += 1

        # If a custom HTML or JSON file path is provided, load from it
        if self.fixture_path and Path(self.fixture_path).exists():
            path = Path(self.fixture_path)
            if path.suffix == ".html":
                content = path.read_text(encoding="utf-8")
                return parse_olx_html_list(content)
            elif path.suffix == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
                return [RawListingItem(**item) for item in data]

        # Use in-memory realistic fixture dataset
        items = []
        for raw in DEFAULT_FIXTURE_LISTINGS:
            items.append(RawListingItem(**raw))

        # On subsequent poll cycles, we can simulate an occasional new listing
        if self._iteration > 1:
            dynamic_id = f"7010{self._iteration + 5}"
            items.append(
                RawListingItem(
                    source="olx_uz",
                    source_id=dynamic_id,
                    canonical_url=f"https://www.olx.uz/d/oz/obyavlenie/toshkent-yangi-kvartira-maklersiz-ID{dynamic_id}.html",
                    title=f"Shayxontohur 2 xonali kvartira egasidan #{self._iteration}",
                    price_raw="4 200 000 so'm",
                    price_uzs=4200000,
                    currency="UZS",
                    district="Shayxontohur",
                    rooms=2,
                    area=61.0,
                    floor="5/9",
                    description="Kvartira toza, barcha qulayliklar bor. Egasidan, vositachilarsiz.",
                    image_urls=["https://img.olx.uz/images/sample_shayxontohur_1.jpg"],
                )
            )

        return items

    async def check_health(self) -> ProviderHealth:
        return ProviderHealth(
            status=ProviderStatus.HEALTHY,
            provider_name=self.name,
            last_check_at=datetime.now(timezone.utc),
            consecutive_failures=0,
            message="Fixture provider active and operational.",
            details={"fixture_count": len(DEFAULT_FIXTURE_LISTINGS), "iteration": self._iteration},
        )


class ManualListingProvider(BaseListingProvider):
    """
    Queue provider for listings submitted manually by users or via authorized partner feeds.
    """

    def __init__(self):
        self._queue: List[RawListingItem] = []

    @property
    def name(self) -> str:
        return "manual_feed_provider"

    def submit_listing(self, item: RawListingItem) -> None:
        self._queue.append(item)

    async def fetch_listings(self) -> List[RawListingItem]:
        items = list(self._queue)
        self._queue.clear()
        return items

    async def check_health(self) -> ProviderHealth:
        return ProviderHealth(
            status=ProviderStatus.HEALTHY,
            provider_name=self.name,
            last_check_at=datetime.now(timezone.utc),
            consecutive_failures=0,
            message="Manual and feed provider active.",
            details={"queued_items": len(self._queue)},
        )

