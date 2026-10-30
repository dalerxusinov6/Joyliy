"""Telegram message and keyboard formatter for apartment listings."""

import html
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.models.listing import Listing
from src.classification.types import ClassificationLabel

# Tashkent local timezone offset: UTC+5
TASHKENT_TZ = timezone(timedelta(hours=5))


def clean_description_for_telegram(desc: Optional[str], max_len: int = 400) -> str:
    """Clean and safely truncate description text for Telegram captions."""
    if not desc:
        return ""
    # Convert <br> or <p> tags to newlines
    text = re.sub(r"<br\s*/?>", "\n", desc, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove metadata notes like [OLX parametri: ...]
    text = re.sub(r"\[OLX parametri:.*?\]", "", text, flags=re.DOTALL)
    # Strip excessive repeated whitespace and linebreaks
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    non_empty = [l for l in lines if l]
    collapsed = "\n".join(non_empty)

    # Truncate at word boundary if exceeding max_len
    if len(collapsed) > max_len:
        cut = collapsed[:max_len]
        last_space = cut.rfind(" ")
        if last_space > max_len // 2:
            cut = cut[:last_space]
        collapsed = cut.strip() + "..."

    return html.escape(collapsed)


def get_source_platform_name(source: Optional[str]) -> str:
    """Get user-friendly platform title from source identifier."""
    return "OLX.uz"


def format_price_uzs(price: Optional[int]) -> str:
    """Format price in UZS with spaces, e.g. 3 500 000 so‘m."""
    if price is None:
        return "Kelishilgan"
    return f"{price:,}".replace(",", " ") + " so‘m/oy"


def format_listing_message(listing: Listing) -> str:
    """
    Format listing details into the exact Telegram message layout.
    Escapes all user input to prevent broken HTML.
    """
    # 1. Headline
    rooms_label = (
        f"{listing.rooms} xonali kvartira"
        if listing.rooms is not None and listing.rooms > 0
        else ("Studiya" if listing.rooms == 0 else "Kvartira")
    )
    district_label = listing.district or "Toshkent"
    clean_title = html.escape(listing.title.strip())
    headline = f"🏠 <b>{html.escape(rooms_label)} — {html.escape(district_label)}</b>"

    lines = [headline, ""]

    # 2. Price
    if listing.price_uzs is not None:
        lines.append(f"💰 Narxi: {format_price_uzs(listing.price_uzs)}")
    elif listing.price_raw:
        lines.append(f"💰 Narxi: {html.escape(listing.price_raw.strip())}")

    # 3. District
    if listing.district:
        lines.append(f"📍 Hudud: {html.escape(listing.district.strip())}")

    # 4. Area
    if listing.area:
        lines.append(f"📐 Maydon: {int(listing.area) if listing.area.is_integer() else listing.area} m²")

    # 5. Rooms
    if listing.rooms is not None:
        lines.append(f"🛏 Xonalar: {listing.rooms}")

    # 5b. Metro proximity if available
    if getattr(listing, "metro_station", None):
        dist_str = f" ({listing.metro_distance_m} m)" if getattr(listing, "metro_distance_m", None) else ""
        lines.append(f"🚇 Metro: <b>{html.escape(listing.metro_station)}</b>{dist_str}")

    # 5c. Furnished & Renovation
    if getattr(listing, "is_furnished", None) is not None:
        lines.append(f"🛋 Jihozlangan: {'Ha' if listing.is_furnished else 'Yo‘q'}")
    if getattr(listing, "renovation_type", None):
        lines.append(f"✨ Ta'mir: {html.escape(listing.renovation_type.capitalize())}")

    # 5d. Fair Price evaluation
    fp_cat = getattr(listing, "fair_price_category", None)
    if fp_cat:
        cat_badge = {
            "BELOW_MARKET": "🟢 Bozordan arzon",
            "FAIR_PRICE": "🟡 Bozor narxida",
            "ABOVE_MARKET": "🔴 Bozordan qimmat",
        }.get(fp_cat, fp_cat)
        diff = getattr(listing, "price_diff_percent", None)
        diff_str = f" ({diff:+.1f}%)" if diff is not None else ""
        lines.append(f"📊 Bozor tahlili: <b>{cat_badge}</b>{diff_str}")

    # 5e. Scam Risk indicator
    scam_score = getattr(listing, "scam_risk_score", None)
    if scam_score is not None:
        if scam_score < 35:
            risk_badge = "🟢 Xavfsiz"
        elif scam_score < 70:
            risk_badge = "🟡 O'rtacha xavf"
        else:
            risk_badge = "🔴 Yuqori xavf (Ehtiyot bo'ling)"
        lines.append(f"🛡 Xavfsizlik: <b>{risk_badge}</b>")

    # 6. Source Attribution based on Maklersiz classification
    classification = None
    if "classification" in listing.__dict__:
        classification = listing.__dict__["classification"]
    else:
        try:
            from sqlalchemy.orm.attributes import NO_VALUE
            from sqlalchemy.orm import inspect as sa_inspect
            insp = sa_inspect(listing)
            loaded = insp.attrs.classification.loaded_value
            if loaded is not NO_VALUE:
                classification = loaded
        except Exception:
            classification = None

    label = classification.label if classification else ClassificationLabel.NEEDS_REVIEW.value

    if label == ClassificationLabel.LIKELY_OWNER.value:
        source_text = "Egasi bo‘lishi mumkin"
    elif label == ClassificationLabel.LIKELY_AGENT.value:
        source_text = "Rieltor / Agentlik"
    else:
        source_text = "Tekshirilmoqda"

    lines.append(f"👤 Manba: {source_text}")

    # 6b. Target Audience (Family, Female, Male)
    aud = getattr(listing, "target_audience", "any")
    if aud == "family":
        lines.append("👨‍👩‍👧 Mos keladi: <b>Oila uchun</b>")
    elif aud == "female":
        lines.append("👩 Mos keladi: <b>Qizlar / Ayollar uchun</b>")
    elif aud == "male":
        lines.append("👨 Mos keladi: <b>Yigitlar / Talabalar uchun</b>")

    # 7. Discovered time in Tashkent local time (UTC+5)
    discovered_dt = listing.first_seen_at or datetime.now(timezone.utc)
    tashkent_time = discovered_dt.astimezone(TASHKENT_TZ)
    lines.append(f"🕒 Aniqlangan vaqt: {tashkent_time.strftime('%H:%M')}")

    # 8. Disclaimer for likely-owner listings
    if label == ClassificationLabel.LIKELY_OWNER.value:
        lines.append("")
        lines.append("⚠️ Egasidan ekanligi mustaqil tasdiqlanmagan.")

    return "\n".join(lines)


def get_listing_inline_keyboard(listing: Listing, is_favorited: bool = False) -> InlineKeyboardMarkup:
    """Create inline action buttons for an apartment listing message."""
    fav_text = "💔 Saqlangandan o‘chirish" if is_favorited else "❤️ Saqlash"
    fav_cb = f"unfav:{listing.id}" if is_favorited else f"fav:{listing.id}"
    platform = get_source_platform_name(getattr(listing, "source", None))

    keyboard = [
        [
            InlineKeyboardButton(text=f"🔗 {platform}’da ko‘rish", url=listing.canonical_url),
        ],
        [
            InlineKeyboardButton(text=fav_text, callback_data=fav_cb),
            InlineKeyboardButton(text="⚖️ Taqqoslash", callback_data=f"cmp_add:{listing.id}"),
        ],
        [
            InlineKeyboardButton(text="🚩 Shikoyat", callback_data=f"rep:{listing.id}"),
            InlineKeyboardButton(text="🚫 Yashirish", callback_data=f"hide:{listing.id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_channel_message(listing: Listing) -> str:
    """
    Format professional Telegram channel advertisement according to exact specification:
    🏠 [Advertisement Title]
    💰 Price: [Price]
    📍 Location: [Location]
    📅 Published: [Publication Date]
    📝 [Clean and readable description]
    🔗 View advertisement: [Original URL]
    """
    from src.providers.parser import extract_phone, extract_telegram_user

    clean_title = html.escape(listing.title.strip())
    lines = [f"🏠 <b>{clean_title}</b>", ""]

    # Price
    if listing.price_uzs is not None:
        lines.append(f"💰 <b>Narxi:</b> {format_price_uzs(listing.price_uzs)}")
    elif listing.price_raw:
        lines.append(f"💰 <b>Narxi:</b> {html.escape(listing.price_raw.strip())}")

    # Location
    location_parts = []
    if listing.district:
        location_parts.append(listing.district.strip())
    if location_parts:
        lines.append(f"📍 <b>Manzil:</b> {html.escape(', '.join(location_parts))}")

    # Rooms and area if available
    specs = []
    if listing.rooms is not None and listing.rooms > 0:
        specs.append(f"{listing.rooms} xona")
    elif listing.rooms == 0:
        specs.append("Studiya")
    if listing.area:
        specs.append(f"{int(listing.area) if listing.area.is_integer() else listing.area} m²")
    if listing.floor:
        specs.append(f"{listing.floor}-qavat")
    if specs:
        lines.append(f"📐 <b>Parametrlar:</b> {html.escape(' • '.join(specs))}")

    # Publication Date
    pub_dt = (listing.publication_date or listing.first_seen_at or datetime.now(timezone.utc)).astimezone(TASHKENT_TZ)
    lines.append(f"📅 <b>E’lon qilingan:</b> {pub_dt.strftime('%d.%m.%Y, %H:%M')}")

    # Source / Maklersiz status
    classification = None
    if "classification" in listing.__dict__:
        classification = listing.__dict__["classification"]
    else:
        try:
            from sqlalchemy.orm.attributes import NO_VALUE
            from sqlalchemy.orm import inspect as sa_inspect
            insp = sa_inspect(listing)
            loaded = insp.attrs.classification.loaded_value
            if loaded is not NO_VALUE:
                classification = loaded
        except Exception:
            classification = None

    label = classification.label if classification else ClassificationLabel.NEEDS_REVIEW.value
    if label == ClassificationLabel.LIKELY_OWNER.value:
        lines.append("👤 <b>Manba:</b> Egasidan (Maklersiz)")
    elif label == ClassificationLabel.LIKELY_AGENT.value:
        lines.append("👤 <b>Manba:</b> Agentlik / Rieltor")

    # Clean description (without raw HTML, stripped of excess newlines)
    clean_desc = clean_description_for_telegram(listing.description, max_len=420)
    if clean_desc:
        lines.append("")
        lines.append(f"📝 <b>Tavsif:</b>\n{clean_desc}")

    # Contacts
    phone = getattr(listing, "contact_phone", None)
    if not phone:
        phone = extract_phone(f"{listing.title} {listing.description or ''}")

    tg_user = getattr(listing, "contact_telegram", None)
    if not tg_user:
        tg_user = extract_telegram_user(f"{listing.title} {listing.description or ''}")

    contact_lines = []
    if phone:
        contact_lines.append(f"📞 <b>Telefon:</b> <code>{html.escape(phone)}</code>")
    if tg_user:
        clean_tg = tg_user.lstrip("@")
        contact_lines.append(f"💬 <b>Telegram:</b> <a href=\"https://t.me/{clean_tg}\">@{html.escape(clean_tg)}</a>")

    if contact_lines:
        lines.append("")
        lines.extend(contact_lines)

    # Link & Channel attribution
    platform = get_source_platform_name(getattr(listing, "source", None))
    lines.append("")
    lines.append(f"🔗 <b>E’lonni ko‘rish:</b> <a href=\"{listing.canonical_url}\">{platform} orqali ochish</a>")
    lines.append("🤖 <b>Joyliy:</b> @joyliy_uz | @joyliy_bot")

    return "\n".join(lines)


def get_channel_inline_keyboard(listing: Listing) -> InlineKeyboardMarkup:
    """Create inline buttons for channel postings including direct Telegram contact."""
    from src.providers.parser import extract_telegram_user

    tg_user = getattr(listing, "contact_telegram", None)
    if not tg_user:
        tg_user = extract_telegram_user(f"{listing.title} {listing.description or ''}")

    platform = get_source_platform_name(getattr(listing, "source", None))

    buttons_row1 = []
    if tg_user:
        clean_tg = tg_user.lstrip("@")
        buttons_row1.append(
            InlineKeyboardButton(text="💬 Egasiga yozish", url=f"https://t.me/{clean_tg}")
        )

    buttons_row1.append(
        InlineKeyboardButton(text=f"🔗 {platform}’da ko‘rish", url=listing.canonical_url)
    )

    buttons_row2 = [
        InlineKeyboardButton(text="🤖 Joyliy Bot", url="https://t.me/joyliy_bot"),
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons_row1, buttons_row2])


def get_channel_inline_keyboard(listing: Listing) -> InlineKeyboardMarkup:
    """Create inline buttons for channel postings including direct Telegram contact."""
    from src.providers.parser import extract_telegram_user

    tg_user = getattr(listing, "contact_telegram", None)
    if not tg_user:
        tg_user = extract_telegram_user(f"{listing.title} {listing.description or ''}")

    platform = get_source_platform_name(getattr(listing, "source", None))

    buttons_row1 = []
    if tg_user:
        clean_tg = tg_user.lstrip("@")
        buttons_row1.append(
            InlineKeyboardButton(text="💬 Egasiga yozish", url=f"https://t.me/{clean_tg}")
        )

    buttons_row1.append(
        InlineKeyboardButton(text=f"🔗 {platform}’da ko‘rish", url=listing.canonical_url)
    )

    buttons_row2 = [
        InlineKeyboardButton(text="🤖 Joyliy Bot", url="https://t.me/joyliy_bot"),
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons_row1, buttons_row2])
