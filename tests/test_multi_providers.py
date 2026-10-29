"""Tests for Joymee, Realt24, and Composite Listing Providers."""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.providers.base import ProviderStatus, RawListingItem
from src.providers.parser import parse_joymee_data, parse_realt24_html
from src.providers.joymee_http import JoymeeHttpListingProvider
from src.providers.realt24_http import Realt24HttpListingProvider
from src.providers.composite import CompositeListingProvider


def test_parse_joymee_data_full():
    """Test parsing of Joymee list item combined with detail response."""
    list_item = {
        "id": 583361,
        "title": "АРЕНДА‼️Массив Куйлюк-3 Мирабад 1/3/4",
        "pricing": {
            "currency": 2,
            "price": "350.00",
            "currency_display": "y.e",
        },
        "image": "https://cdn.joymeemedia.uz/cover.jpg",
        "ads_at": "2026-10-28T21:51:23.407692+05:00",
        "address_line": "город Ташкент, Мирабадский район",
    }
    detail = {
        "id": 583361,
        "phone_number": "+998995768515",
        "description": "Kvartira ijaraga beriladi. Murojaat uchun @yunusobod_uylar yoki telefon qiling.",
        "district": {"id": 199, "name": "Mirobod tumani"},
        "detail": {
            "room_quantity": 1,
            "area_m2": "30.00",
            "floor_number": 3,
            "floors_count": 4,
        },
        "location": {"latitude": 41.28, "longitude": 69.31},
        "media": [
            {"file": {"id": 1, "url": "https://cdn.joymeemedia.uz/img1.jpg"}},
            {"file": {"id": 2, "url": "https://cdn.joymeemedia.uz/img2.jpg"}},
        ],
        "pricing": {
            "currency": 2,
            "price": "350.00",
            "currency_display": "y.e",
        },
    }

    item = parse_joymee_data(list_item, detail)

    assert item.source == "joymee_uz"
    assert item.source_id == "583361"
    assert item.canonical_url == "https://joymee.uz/announcements/583361"
    assert item.price_uzs == 350 * 12800
    assert item.currency == "USD"
    assert item.district == "Mirobod"
    assert item.rooms == 1
    assert item.area == 30.0
    assert item.floor == "3/4"
    assert item.contact_phone == "+998 99 576 85 15"
    assert item.contact_telegram == "@yunusobod_uylar"
    assert len(item.image_urls) == 2


def test_parse_realt24_html_mock():
    """Test parsing Realt24 Next.js React Query hydration state."""
    sample_next_data = {
        "props": {
            "pageProps": {
                "dehydratedState": {
                    "queries": [
                        {
                            "queryKey": ["/properties", "categoryType=rent"],
                            "state": {
                                "data": {
                                    "data": [
                                        {
                                            "id": "25004",
                                            "name": "3 xonali kvartira − 100 m², 5/9 qavat",
                                            "currency": "usd",
                                            "price": {
                                                "uzs": 11918980,
                                                "usd": 1000,
                                            },
                                            "phone": "+998935175229",
                                            "description": "Yangi remont, aloqa @arseniy_realtor",
                                            "address": {
                                                "fullAddress": "Toshkent, Mirzo-Ulug'bek tumani, 10",
                                                "area": "Mirzo Ulugbek",
                                                "geoLocation": {"latitude": 41.31, "longitude": 69.31},
                                            },
                                            "imageSets": [
                                                {"original": "https://storage.realt24.uz/img1.webp"},
                                                {"original": "https://storage.realt24.uz/img2.webp"},
                                            ],
                                            "publishedAt": "2026-10-27T06:03:26.283687+00:00",
                                            "categoryType": {"key": "rent"},
                                        }
                                    ]
                                }
                            },
                        }
                    ]
                }
            }
        }
    }

    html = f'<html><body><script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script></body></html>'

    items = parse_realt24_html(html)
    assert len(items) == 1
    it = items[0]
    assert it.source == "realt24_uz"
    assert it.source_id == "25004"
    assert it.canonical_url == "https://realt24.uz/listing/25004/"
    assert it.price_uzs == 11918980
    assert it.district == "Mirzo Ulug‘bek"
    assert it.rooms == 3
    assert it.area == 100.0
    assert it.floor == "5/9"
    assert it.contact_phone == "+998 93 517 52 29"
    assert it.contact_telegram == "@arseniy_realtor"
    assert len(it.image_urls) == 2


@pytest.mark.asyncio
async def test_composite_provider():
    """Test CompositeListingProvider aggregation and health checks."""
    p1 = MagicMock()
    p1.name = "source_1"
    item1 = RawListingItem(
        source="src1",
        source_id="1",
        canonical_url="https://src1.uz/1",
        title="1 xonali Chilonzor",
    )
    p1.fetch_listings = AsyncMock(return_value=[item1])
    p1.check_health = AsyncMock(
        return_value=MagicMock(status=ProviderStatus.HEALTHY, message="OK")
    )

    p2 = MagicMock()
    p2.name = "source_2"
    item2 = RawListingItem(
        source="src2",
        source_id="2",
        canonical_url="https://src2.uz/2",
        title="2 xonali Yunusobod",
    )
    p2.fetch_listings = AsyncMock(return_value=[item2])
    p2.check_health = AsyncMock(
        return_value=MagicMock(status=ProviderStatus.HEALTHY, message="OK")
    )

    composite = CompositeListingProvider([p1, p2])
    results = await composite.fetch_listings()
    assert len(results) == 2
    assert results[0].canonical_url == "https://src1.uz/1"
    assert results[1].canonical_url == "https://src2.uz/2"

    health = await composite.check_health()
    assert health.status == ProviderStatus.HEALTHY
