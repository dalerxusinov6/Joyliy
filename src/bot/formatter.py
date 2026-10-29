"""Telegram message and keyboard formatter for apartment listings."""

from datetime import datetime, timezone, timedelta
from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.models.listing import Listing
from src.classification.types import ClassificationLabel

# Tashkent local timezone offset: UTC+5
TASHKENT_TZ = timezone(timedelta(hours=5))


def get_source_platform_name(source: Optional[str]) -> str:
    """Get user-friendly platform title from source identifier."""
    mapping = {
        "olx_uz": "OLX.uz",
        "joymee_uz": "Joymee.uz",
        "realt24_uz": "Realt24.uz",
    }
    return mapping.get(source or "olx_uz", "Asl manba")


def format_price_uzs(price: Optional[int]) -> str:
    """Format price in UZS with spaces, e.g. 3 500 000 so‘m."""
    if price is None:
        return "Kelishilgan"
    return f"{price:,}".replace(",", " ") + " so‘m/oy"


def format_listing_message(listing: Listing) -> str:
    """
    Format listing details into the exact Telegram message layout.
    Does not invent missing fields or publication times.
    """
    # 1. Headline
    rooms_label = (
        f"{listing.rooms} xonali kvartira"
        if listing.rooms is not None and listing.rooms > 0
        else ("Studiya" if listing.rooms == 0 else "Kvartira")
    )
    district_label = listing.district or "Toshkent"
    headline = f"🏠 {rooms_label} — {district_label}"

    lines = [headline, ""]

    # 2. Price
    if listing.price_uzs is not None:
        lines.append(f"💰 Narxi: {format_price_uzs(listing.price_uzs)}")
    elif listing.price_raw:
        lines.append(f"💰 Narxi: {listing.price_raw}")

    # 3. District
    if listing.district:
        lines.append(f"📍 Hudud: {listing.district}")

    # 4. Area
    if listing.area:
        lines.append(f"📐 Maydon: {int(listing.area) if listing.area.is_integer() else listing.area} m²")

    # 5. Rooms
    if listing.rooms is not None:
        lines.append(f"🛏 Xonalar: {listing.rooms}")

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
            InlineKeyboardButton(text="🚫 Yashirish", callback_data=f"hide:{listing.id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_channel_message(listing: Listing) -> str:
    """Format listing message for Telegram channel broadcasting with phone and telegram contacts."""
    from src.providers.parser import extract_phone, extract_telegram_user

    base_text = format_listing_message(listing)
    platform = get_source_platform_name(getattr(listing, "source", None))

    # 1. Resolve phone and telegram handle
    phone = getattr(listing, "contact_phone", None)
    if not phone:
        phone = extract_phone(f"{listing.title} {listing.description or ''}")

    tg_user = getattr(listing, "contact_telegram", None)
    if not tg_user:
        tg_user = extract_telegram_user(f"{listing.title} {listing.description or ''}")

    contact_lines = []
    if phone:
        contact_lines.append(f"📞 Telefon: <code>{phone}</code>")
    if tg_user:
        clean_tg = tg_user.lstrip("@")
        contact_lines.append(f"💬 Telegram: <a href=\"https://t.me/{clean_tg}\">@{clean_tg}</a>")

    if not phone and not tg_user:
        contact_lines.append(f"📞 Aloqa: <a href=\"{listing.canonical_url}\">{platform} orqali ko‘rish</a>")

    contacts_block = "\n".join(contact_lines)

    footer = (
        f"\n\n🔗 <a href=\"{listing.canonical_url}\">{platform}’da ko‘rish</a>"
        f" | 🤖 <a href=\"https://t.me/joyliy_bot\">@joyliy_bot</a>"
    )

    if "⚠️ Egasidan" in base_text:
        parts = base_text.split("⚠️ Egasidan")
        return f"{parts[0].rstrip()}\n\n{contacts_block}\n\n⚠️ Egasidan{parts[1]}{footer}"
    else:
        return f"{base_text}\n\n{contacts_block}{footer}"


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
