"""Listing providers module."""

from src.providers.base import (
    BaseListingProvider,
    ProviderHealth,
    ProviderStatus,
    RawListingItem,
)
from src.providers.parser import (
    canonicalize_url,
    extract_source_id_from_url,
    parse_price,
    extract_district,
    extract_rooms,
    extract_area,
    extract_phone,
    extract_telegram_user,
    parse_olx_html_list,
    parse_joymee_data,
    parse_realt24_html,
)
from src.providers.olx_http import OLXHttpListingProvider
from src.providers.joymee_http import JoymeeHttpListingProvider
from src.providers.realt24_http import Realt24HttpListingProvider
from src.providers.composite import CompositeListingProvider
from src.providers.fixture import (
    FixtureListingProvider,
    ManualListingProvider,
    DEFAULT_FIXTURE_LISTINGS,
)

__all__ = [
    "BaseListingProvider",
    "ProviderHealth",
    "ProviderStatus",
    "RawListingItem",
    "canonicalize_url",
    "extract_source_id_from_url",
    "parse_price",
    "extract_district",
    "extract_rooms",
    "extract_area",
    "extract_phone",
    "extract_telegram_user",
    "parse_olx_html_list",
    "parse_joymee_data",
    "parse_realt24_html",
    "OLXHttpListingProvider",
    "JoymeeHttpListingProvider",
    "Realt24HttpListingProvider",
    "CompositeListingProvider",
    "FixtureListingProvider",
    "ManualListingProvider",
    "DEFAULT_FIXTURE_LISTINGS",
]

