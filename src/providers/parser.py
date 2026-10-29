"""OLX Uzbekistan HTML and metadata parser."""

import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from src.config import settings
from src.providers.base import RawListingItem

# Standard Tashkent districts mapping (Uzbek Latin canonical name -> regex pattern)
DISTRICT_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("Chilonzor", re.compile(r"\b(?:chilonzor|чиланзар(?:ский)?)\b", re.IGNORECASE)),
    ("Yunusobod", re.compile(r"\b(?:yunusobod|юнусабад(?:ский)?)\b", re.IGNORECASE)),
    ("Mirzo Ulug‘bek", re.compile(r"\b(?:mirzo[\s\-]*ulug['`‘ʻ’\u02bb\u02bc]?[\s\-]*bek|мирзо[\s\-]*улугбек(?:ский)?)\b", re.IGNORECASE)),
    ("Yakkasaroy", re.compile(r"\b(?:yakkasaroy|яккасарай(?:ский)?)\b", re.IGNORECASE)),
    ("Sergeli", re.compile(r"\b(?:sergeli|сергели(?:йский)?)\b", re.IGNORECASE)),
    ("Olmazor", re.compile(r"\b(?:olmazor|алмазар(?:ский)?)\b", re.IGNORECASE)),
    ("Shayxontohur", re.compile(r"\b(?:shayxontohur|shayxontoxur|шайхантахур(?:ский)?)\b", re.IGNORECASE)),
    ("Uchtepa", re.compile(r"\b(?:uchtepa|учтепа|учтепинский)\b", re.IGNORECASE)),
    ("Yashnobod", re.compile(r"\b(?:yashnobod|яшнабад(?:ский)?)\b", re.IGNORECASE)),
    ("Bektemir", re.compile(r"\b(?:bektemir|бектемир(?:ский)?)\b", re.IGNORECASE)),
    ("Yangi Hayot", re.compile(r"\b(?:yangi[\s\-]*hayot|янги[\s\-]*хаёт|янгихаёт(?:ский)?)\b", re.IGNORECASE)),
    ("Mirobod", re.compile(r"\b(?:mirobod|мирабад(?:ский)?)\b", re.IGNORECASE)),
]


def canonicalize_url(raw_url: str) -> str:
    """Strip tracking and ephemeral query parameters to obtain a canonical listing URL."""
    if not raw_url:
        return ""
    parsed = urllib.parse.urlparse(raw_url)
    # Always normalize base path without query and fragment
    clean_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    return clean_url.rstrip("/")


def extract_source_id_from_url(url: str) -> Optional[str]:
    """Extract OLX listing ID from URL, e.g. -ID12345.html -> 12345."""
    match = re.search(r"-ID([a-zA-Z0-9]+)(?:\.html)?", url)
    if match:
        return match.group(1)
    # Try digits at end of path if standard OLX id structure
    match2 = re.search(r"/(\d{6,})/?$", url)
    if match2:
        return match2.group(1)
    return None


def parse_price(raw_text: Optional[str]) -> Tuple[Optional[int], str, Optional[str]]:
    """
    Parse price string into integer in UZS, currency code, and cleaned raw text.
    Handles USD, U.E., and UZS formats.
    """
    if not raw_text:
        return None, "UZS", None

    clean_raw = raw_text.strip()
    lower = clean_raw.lower()

    # Detect currency
    is_usd = any(sym in lower for sym in ["$", "y.e", "у.е", "usd", "долл"])

    # Extract digits (handling spaces and commas/dots)
    # e.g. "3 500 000 сум" -> 3500000
    # e.g. "400 y.e." -> 400
    digits_match = re.search(r"(\d[\d\s.,]*)", clean_raw)
    if not digits_match:
        return None, "UZS", clean_raw

    num_str = digits_match.group(1)
    # Remove whitespace, non-breaking space, commas, dots if used as thousands separators
    clean_num = re.sub(r"[\s\u00a0\xa0]", "", num_str)

    # If format like 3.500.000 or 3,500,000, remove separators
    if clean_num.count(".") > 1 or clean_num.count(",") > 1:
        clean_num = clean_num.replace(".", "").replace(",", "")
    elif "." in clean_num and len(clean_num.split(".")[1]) == 3:
        clean_num = clean_num.replace(".", "")
    elif "," in clean_num and len(clean_num.split(",")[1]) == 3:
        clean_num = clean_num.replace(",", "")

    try:
        val = float(clean_num)
        if is_usd:
            # Convert USD to UZS based on configured rate
            uzs_val = int(round(val * settings.USD_TO_UZS_RATE))
            return uzs_val, "USD", clean_raw
        else:
            return int(round(val)), "UZS", clean_raw
    except ValueError:
        return None, "UZS", clean_raw


def extract_district(text: str) -> Optional[str]:
    """Detect Tashkent district from text or parameters."""
    if not text:
        return None
    for district_name, pattern in DISTRICT_PATTERNS:
        if pattern.search(text):
            return district_name
    return None


def extract_rooms(text: str) -> Optional[int]:
    """Extract room count from listing title or description."""
    if not text:
        return None

    # Studio
    if re.search(r"\b(?:studiya|студия)\b", text, re.IGNORECASE):
        return 0

    # Pattern like "2 xonali", "2-xona", "2 комн", "2-комнатная", "2 хона"
    match = re.search(
        r"\b([1-9])\s*[-–—]?\s*(?:xonali|xona|комнатная|комнат|комн|ком|хона|к\b)",
        text,
        re.IGNORECASE,
    )
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None


def extract_area(text: str) -> Optional[float]:
    """Extract area in square meters (m²)."""
    if not text:
        return None
    # Matches: 54 m², 54.5 м2, 54 кв.м, 54 kv.m
    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(?:m²|м²|m2|м2|кв\.?\s*м|kv\.?\s*m)",
        text,
        re.IGNORECASE,
    )
    if match:
        try:
            num = match.group(1).replace(",", ".")
            return float(num)
        except ValueError:
            pass
    return None


def parse_publication_date(val: Optional[str]) -> Optional[datetime]:
    """
    Parse explicit publication datetime if provided in ISO format.
    Never fabricates a timestamp.
    """
    if not val:
        return None
    try:
        # ISO format: 2026-10-28T14:30:00+05:00 or 2026-10-28T09:30:00Z
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


PHONE_REGEX = re.compile(
    r"(?:\+?998\s*[-.\s]?\(?\d{2}\)?|\(?\b(?:9[01345789]|33|88|77|71|55)\)?)\s*[-.\s]?\d{3}\s*[-.\s]?\d{2}\s*[-.\s]?\d{2}\b"
)

TG_USER_REGEX = re.compile(
    r"(?:(?:https?:\/\/)?t\.me\/|(?<!\w)@|tg:\s*@?|telegram:\s*@?)([a-zA-Z][a-zA-Z0-9_]{3,31})\b",
    re.IGNORECASE,
)

IGNORED_TG_USERS = {"joyliy_bot", "joyliy_uz", "olx", "olx_uz", "channel", "telegram", "admin", "gmail", "mail"}


def normalize_uz_phone(raw_phone: str) -> str:
    """Normalize phone string into +998 XX XXX XX XX format."""
    if not raw_phone:
        return ""
    digits = re.sub(r"\D", "", raw_phone)
    if len(digits) == 9:
        return f"+998 {digits[:2]} {digits[2:5]} {digits[5:7]} {digits[7:]}"
    elif len(digits) == 12 and digits.startswith("998"):
        return f"+998 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:]}"
    return raw_phone.strip()


def extract_phone(text: Optional[str]) -> Optional[str]:
    """Extract and normalize Uzbekistan phone number from text."""
    if not text:
        return None
    match = PHONE_REGEX.search(text)
    if match:
        return normalize_uz_phone(match.group(0))
    return None


def extract_telegram_user(text: Optional[str]) -> Optional[str]:
    """Extract Telegram username from text."""
    if not text:
        return None
    for match in TG_USER_REGEX.finditer(text):
        username = match.group(1).strip()
        if username.lower() not in IGNORED_TG_USERS:
            return f"@{username}"
    return None


def _parse_prerendered_state(html_content: str, base_url: str = "https://www.olx.uz") -> List[RawListingItem]:
    """Extract structured listing data from window.__PRERENDERED_STATE__ if present in the page."""
    import json
    m = re.search(r'window\.__PRERENDERED_STATE__\s*=\s*\"(.*?)\";\s*window\.', html_content, re.DOTALL)
    if not m:
        m = re.search(r'window\.__PRERENDERED_STATE__\s*=\s*(\{.*?\});\s*(?:window\.|<\/script>)', html_content, re.DOTALL)
        if not m:
            return []
        try:
            state = json.loads(m.group(1))
        except Exception:
            return []
    else:
        try:
            parsed = json.loads('"' + m.group(1) + '"')
            state = json.loads(parsed)
        except Exception:
            return []

    ads = state.get("listing", {}).get("listing", {}).get("ads", [])
    if not ads:
        return []

    listings: List[RawListingItem] = []
    for ad in ads:
        try:
            ad_id = str(ad.get("id"))
            raw_url = ad.get("url") or ""
            canonical = canonicalize_url(raw_url)
            title = ad.get("title", "")
            description = ad.get("description", "")

            # Price
            price_data = ad.get("price", {})
            regular_price = price_data.get("regularPrice", {})
            price_val = regular_price.get("value")
            currency = regular_price.get("currencyCode", "UZS")
            raw_price = price_data.get("displayValue")

            price_uzs = None
            if price_val is not None:
                if currency == "USD":
                    price_uzs = int(round(price_val * settings.USD_TO_UZS_RATE))
                else:
                    price_uzs = int(round(price_val))

            # Parameters
            params_dict = {}
            for p in ad.get("params", []):
                key = p.get("key")
                val = p.get("normalizedValue") or p.get("value")
                if key:
                    params_dict[key] = val

            # Rooms
            rooms = None
            if "number_of_rooms" in params_dict:
                try:
                    rooms = int(str(params_dict["number_of_rooms"]).strip())
                except Exception:
                    rooms = extract_rooms(str(params_dict["number_of_rooms"]))
            if rooms is None:
                rooms = extract_rooms(title)

            # Area
            area = None
            if "total_area" in params_dict:
                try:
                    area = float(str(params_dict["total_area"]).strip().replace(",", "."))
                except Exception:
                    area = extract_area(str(params_dict["total_area"]))
            if area is None:
                area = extract_area(title)

            # Floor
            floor = None
            fl_val = params_dict.get("floor")
            fl_tot = params_dict.get("total_floors")
            if fl_val and fl_tot:
                floor = f"{str(fl_val).strip()}/{str(fl_tot).strip()}"
            elif fl_val:
                floor = str(fl_val).strip()

            # District from location
            location = ad.get("location", {})
            district_name = location.get("districtName") or location.get("pathName") or ""
            district = extract_district(district_name) or extract_district(title)

            # Photos
            photos = ad.get("photos", [])
            image_urls = [p for p in photos if isinstance(p, str) and p.startswith("http")]

            # Publication date (prefer lastRefreshTime which represents the current 3-day active listing window)
            effective_time_str = ad.get("lastRefreshTime") or ad.get("createdTime")
            pub_date = parse_publication_date(effective_time_str)

            # Include comission note in description if present
            if params_dict.get("comission") == "yes":
                if description:
                    description += "\n[OLX parametri: Комиссионные: Да]"
                else:
                    description = "[OLX parametri: Комиссионные: Да]"
            elif params_dict.get("comission") == "no":
                if description:
                    description += "\n[OLX parametri: Комиссионные: Нет]"
                else:
                    description = "[OLX parametri: Комиссионные: Нет]"

            # Contact extraction
            combined_contact_text = f"{title} {description}"
            phone = extract_phone(combined_contact_text)
            tg_user = extract_telegram_user(combined_contact_text)
            contact_obj = ad.get("contact", {})
            if not phone and isinstance(contact_obj.get("phone"), str):
                phone = extract_phone(contact_obj.get("phone"))

            item = RawListingItem(
                source="olx_uz",
                source_id=ad_id,
                canonical_url=canonical,
                title=title,
                price_raw=raw_price,
                price_uzs=price_uzs,
                currency=currency,
                district=district,
                rooms=rooms,
                area=area,
                floor=floor,
                description=description,
                contact_phone=phone,
                contact_telegram=tg_user,
                image_urls=image_urls,
                publication_date=pub_date,
            )
            listings.append(item)
        except Exception:
            continue

    return listings


def parse_olx_html_list(html_content: str, base_url: str = "https://www.olx.uz") -> List[RawListingItem]:
    """
    Parse an OLX apartment listings search page.
    Extracts cards with resilient fallbacks for varied HTML structures.
    """
    if not html_content:
        return []

    # 1. Attempt extracting high-fidelity structured data from __PRERENDERED_STATE__
    state_listings = _parse_prerendered_state(html_content, base_url)
    if state_listings:
        return state_listings

    # 2. Resilient fallback to HTML DOM cards
    soup = BeautifulSoup(html_content, "html.parser")
    listings: List[RawListingItem] = []

    # Try common OLX card selectors:
    # 1. div[data-cy="l-card"]
    # 2. div[data-testid="listing-card"]
    # 3. general card wrappers with links
    cards = soup.select('div[data-cy="l-card"], div[data-testid="listing-card"], .css-1sw7q4x')
    if not cards:
        # Fallback: search for elements with links containing '/d/obyavlenie/' or '/d/oz/obyavlenie/'
        cards = soup.find_all("div", attrs={"data-id": True})

    for card in cards:
        try:
            # 1. URL and Title
            link_tag = card.find("a", href=True)
            if not link_tag:
                continue

            raw_href = link_tag.get("href", "")
            if not raw_href:
                continue

            # Join relative URL
            full_url = urllib.parse.urljoin(base_url, raw_href)
            canonical = canonicalize_url(full_url)
            source_id = card.get("data-id") or extract_source_id_from_url(canonical)

            # Title
            title_tag = card.find("h6") or card.find("h4") or card.find("h3") or link_tag
            title = title_tag.get_text(strip=True) if title_tag else ""
            if not title:
                continue

            # 2. Price
            price_tag = (
                card.find(attrs={"data-testid": "ad-price"})
                or card.find(class_=re.compile(r"price", re.IGNORECASE))
                or card.find("p", string=re.compile(r"(?:сум|so['`‘]?m|у\.е|\$)", re.IGNORECASE))
            )
            raw_price = price_tag.get_text(strip=True) if price_tag else None
            price_uzs, currency, price_clean = parse_price(raw_price)

            # 3. Location / District / Date
            location_tag = (
                card.find(attrs={"data-testid": "location-date"})
                or card.find(class_=re.compile(r"location", re.IGNORECASE))
            )
            loc_text = location_tag.get_text(separator=" ", strip=True) if location_tag else ""

            combined_text = f"{title} {loc_text}"
            district = extract_district(combined_text)
            rooms = extract_rooms(combined_text)
            area = extract_area(combined_text)

            # 4. Images
            img_urls: List[str] = []
            img_tag = card.find("img")
            if img_tag:
                src = img_tag.get("src") or img_tag.get("data-src")
                if src and src.startswith("http"):
                    img_urls.append(src)

            # 5. Publication date: only record if explicit ISO or timestamp available; else None
            pub_date: Optional[datetime] = None
            time_tag = card.find("time")
            if time_tag and time_tag.get("datetime"):
                pub_date = parse_publication_date(time_tag.get("datetime"))

            phone = extract_phone(combined_text)
            tg_user = extract_telegram_user(combined_text)

            item = RawListingItem(
                source="olx_uz",
                source_id=str(source_id) if source_id else None,
                canonical_url=canonical,
                title=title,
                price_raw=price_clean or raw_price,
                price_uzs=price_uzs,
                currency=currency,
                district=district,
                rooms=rooms,
                area=area,
                floor=None,
                description=None,
                contact_phone=phone,
                contact_telegram=tg_user,
                image_urls=img_urls,
                publication_date=pub_date,
            )
            listings.append(item)
        except Exception:
            continue

    return listings


def parse_olx_api_offer(offer: Dict[str, Any]) -> RawListingItem:
    """Parse offer object from OLX v1 API into RawListingItem."""
    oid = str(offer.get("id"))
    url = offer.get("url")
    title = str(offer.get("title") or "").strip()
    desc = str(offer.get("description") or "").strip()

    price_uzs = None
    currency = "UZS"
    price_raw = None

    rooms = None
    area = None
    floor_num = None
    total_floors = None
    commission_flag = None

    for p in offer.get("params", []):
        key = p.get("key")
        val = p.get("value", {}) if isinstance(p, dict) else {}
        if key == "price":
            price_raw = val.get("label")
            raw_p = val.get("converted_value") or val.get("value")
            try:
                price_uzs = int(round(float(raw_p))) if raw_p is not None else None
            except (ValueError, TypeError):
                price_uzs = None
            curr = val.get("currency")
            currency = "USD" if curr in ("UYE", "USD") else "UZS"
        elif key == "number_of_rooms":
            try:
                rooms = int(val.get("key") or val.get("label"))
            except Exception:
                pass
        elif key == "total_area":
            try:
                area = float(val.get("key") or val.get("label"))
            except Exception:
                pass
        elif key == "floor":
            floor_num = str(val.get("key") or val.get("label")).strip()
        elif key == "total_floors":
            total_floors = str(val.get("key") or val.get("label")).strip()
        elif key == "comission":
            commission_flag = val.get("label")

    if not rooms:
        rooms = extract_rooms(title)
    if not area:
        area = extract_area(title)

    floor = f"{floor_num}/{total_floors}" if floor_num and total_floors else floor_num

    loc = offer.get("location", {})
    dist_name = loc.get("district", {}).get("name") if isinstance(loc.get("district"), dict) else None
    district = extract_district(dist_name or "") or extract_district(title) or "Toshkent"

    geo = offer.get("map", {})
    lat = geo.get("lat")
    lon = geo.get("lon")

    images = []
    for ph in offer.get("photos", []):
        lnk = ph.get("link")
        if lnk:
            images.append(lnk.replace("{width}x{height}", "1000x750"))

    pub_date = parse_publication_date(offer.get("last_refresh_time") or offer.get("created_time"))

    desc_extra = f"{desc}\n[OLX parametri: Комиссионные: {commission_flag or 'Noma’lum'}]"

    raw_meta = {
        "latitude": lat,
        "longitude": lon,
        "comission": commission_flag,
        "is_business": offer.get("business"),
    }

    return RawListingItem(
        source="olx_uz",
        source_id=oid,
        canonical_url=url,
        title=title,
        price_raw=price_raw,
        price_uzs=price_uzs,
        currency=currency,
        district=district,
        rooms=rooms,
        area=area,
        floor=floor,
        description=desc_extra,
        contact_phone=normalize_uz_phone(extract_phone(desc)),
        contact_telegram=extract_telegram_user(desc),
        image_urls=images,
        publication_date=pub_date,
        raw_metadata=raw_meta,
    )


