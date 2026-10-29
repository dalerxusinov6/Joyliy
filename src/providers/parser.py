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


def parse_joymee_data(
    item: Dict[str, Any], detail: Optional[Dict[str, Any]] = None
) -> RawListingItem:
    """
    Parse Joymee.uz announcement data (from API list or detail) into RawListingItem.
    """
    jid = str(item.get("id"))
    title = str(item.get("title") or "").strip()

    detail_data = detail or {}

    pricing = detail_data.get("pricing") or item.get("pricing") or {}
    curr = pricing.get("currency")
    price_val = pricing.get("price")
    price_uzs = None
    currency = "UZS"
    price_raw = None

    if price_val is not None:
        try:
            val_f = float(price_val)
            if curr == 2:  # USD (y.e)
                price_uzs = int(round(val_f * settings.USD_TO_UZS_RATE))
                currency = "USD"
                price_raw = f"${int(val_f)}"
            else:
                price_uzs = int(round(val_f))
                currency = "UZS"
                price_raw = f"{price_uzs:,}".replace(",", " ") + " so‘m"
        except (ValueError, TypeError):
            pass

    # District extraction
    district_obj = detail_data.get("district")
    district_name = district_obj.get("name") if isinstance(district_obj, dict) else None
    address_line = detail_data.get("address_line") or item.get("address_line") or ""
    district = extract_district(f"{district_name or ''} {address_line}")

    # Media / images
    media_list = detail_data.get("media") or []
    image_urls: List[str] = []
    for m in media_list:
        if isinstance(m, dict) and "file" in m and isinstance(m["file"], dict):
            url = m["file"].get("url")
            if url:
                image_urls.append(url)
    if not image_urls:
        cover_img = item.get("image")
        if cover_img:
            image_urls.append(cover_img)

    # Details: rooms, area, floor
    det_info = detail_data.get("detail") or {}
    rooms = det_info.get("room_quantity") or extract_rooms(title)

    area: Optional[float] = None
    if det_info.get("area_m2"):
        try:
            area = float(det_info.get("area_m2"))
        except (ValueError, TypeError):
            pass
    if area is None:
        area = extract_area(title)

    fl_num = det_info.get("floor_number")
    fl_cnt = det_info.get("floors_count")
    floor = f"{fl_num}/{fl_cnt}" if fl_num and fl_cnt else None

    # Description and contacts
    description = detail_data.get("description") or item.get("description") or ""
    seller = detail_data.get("seller") or item.get("created_by") or {}
    seller_bio = seller.get("bio", "") if isinstance(seller, dict) else ""
    seller_user = seller.get("username", "") if isinstance(seller, dict) else ""

    phone = normalize_uz_phone(
        detail_data.get("phone_number") or extract_phone(f"{description} {seller_bio}")
    )
    tg_user = extract_telegram_user(f"{description} {seller_bio} @{seller_user}")

    pub_date = parse_publication_date(detail_data.get("ads_at") or item.get("ads_at"))

    location = detail_data.get("location") or {}
    raw_meta = {
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "address": address_line,
    }

    return RawListingItem(
        source="joymee_uz",
        source_id=jid,
        canonical_url=f"https://joymee.uz/announcements/{jid}",
        title=title,
        price_raw=price_raw,
        price_uzs=price_uzs,
        currency=currency,
        district=district,
        rooms=rooms,
        area=area,
        floor=floor,
        description=description or None,
        contact_phone=phone,
        contact_telegram=tg_user,
        image_urls=image_urls,
        publication_date=pub_date,
        raw_metadata=raw_meta,
    )


def parse_realt24_html(html: str) -> List[RawListingItem]:
    """
    Parse Realt24.uz search page HTML extracting React Query hydration state (__NEXT_DATA__).
    """
    if not html:
        return []

    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except Exception:
        return []

    queries = (
        data.get("props", {})
        .get("pageProps", {})
        .get("dehydratedState", {})
        .get("queries", [])
    )

    items: List[RawListingItem] = []
    seen_ids = set()

    for q in queries:
        qk = q.get("queryKey")
        if isinstance(qk, list) and "/properties" in qk:
            query_items = q.get("state", {}).get("data", {}).get("data", [])
            if not isinstance(query_items, list):
                continue

            for it in query_items:
                if not isinstance(it, dict):
                    continue
                iid = str(it.get("id"))
                if not iid or iid in seen_ids:
                    continue

                # Filter strictly for rental listings
                cat_type = it.get("categoryType")
                if isinstance(cat_type, dict) and cat_type.get("key") and cat_type.get("key") != "rent":
                    continue

                seen_ids.add(iid)

                name = it.get("name") or it.get("secondaryName") or "Kvartira"
                price_obj = it.get("price") or {}
                price_uzs = price_obj.get("uzs")
                usd_val = price_obj.get("usd")
                curr = str(it.get("currency", "usd")).upper()

                price_raw = None
                if usd_val:
                    price_raw = f"${usd_val}"
                elif price_uzs:
                    price_raw = f"{price_uzs:,}".replace(",", " ") + " so‘m"

                addr_obj = it.get("address") or {}
                full_addr = addr_obj.get("fullAddress") or ""
                area_str = addr_obj.get("area") or ""
                district = extract_district(f"{full_addr} {area_str}")

                rooms = extract_rooms(name)
                area = extract_area(name)

                fl_m = re.search(r"(\d+/\d+)\s*qavat", name, re.IGNORECASE)
                floor = fl_m.group(1) if fl_m else None

                desc = it.get("description") or ""
                phone = normalize_uz_phone(it.get("phone") or extract_phone(desc))
                tg_user = extract_telegram_user(desc)

                image_urls: List[str] = []
                for img in it.get("imageSets") or []:
                    if isinstance(img, dict):
                        u = img.get("original") or img.get("w600") or img.get("w450")
                        if u:
                            image_urls.append(u)

                geo = addr_obj.get("geoLocation") or {}
                pub_date = parse_publication_date(it.get("publishedAt") or it.get("createdAt"))

                raw_meta = {
                    "latitude": geo.get("latitude"),
                    "longitude": geo.get("longitude"),
                    "address": full_addr,
                }

                item = RawListingItem(
                    source="realt24_uz",
                    source_id=iid,
                    canonical_url=f"https://realt24.uz/listing/{iid}/",
                    title=str(name).strip(),
                    price_raw=price_raw,
                    price_uzs=price_uzs,
                    currency=curr,
                    district=district,
                    rooms=rooms,
                    area=area,
                    floor=floor,
                    description=desc or None,
                    contact_phone=phone,
                    contact_telegram=tg_user,
                    image_urls=image_urls,
                    publication_date=pub_date,
                    raw_metadata=raw_meta,
                )
                items.append(item)

    return items
