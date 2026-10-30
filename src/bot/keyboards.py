"""Telegram reply and inline keyboards."""

from typing import List, Optional
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from src.models.user import UserSearchPreference

TASHKENT_DISTRICTS = [
    "Chilonzor",
    "Yunusobod",
    "Mirzo Ulug‘bek",
    "Yakkasaroy",
    "Sergeli",
    "Olmazor",
    "Shayxontohur",
    "Uchtepa",
    "Yashnobod",
    "Bektemir",
    "Yangi Hayot",
    "Mirobod",
]


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Primary 9-item ecosystem bottom menu keyboard."""
    keyboard = [
        [
            KeyboardButton(text="🏠 Kvartiralar"),
            KeyboardButton(text="🤖 AI Qidiruv"),
        ],
        [
            KeyboardButton(text="👥 Hamxonalar"),
            KeyboardButton(text="🗺 Xarita"),
        ],
        [
            KeyboardButton(text="📈 Bozor narxlari"),
            KeyboardButton(text="⚖️ Taqqoslash"),
        ],
        [
            KeyboardButton(text="❤️ Saqlanganlar"),
            KeyboardButton(text="🔔 Bildirishnomalar"),
        ],
        [
            KeyboardButton(text="💬 AI Maslahatchi"),
            KeyboardButton(text="⚙️ Sozlamalar"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Joyliy menyusidan tanlang...",
    )


def get_ai_search_quick_keyboard() -> InlineKeyboardMarkup:
    """Quick sample queries for AI apartment matching."""
    keyboard = [
        [
            InlineKeyboardButton(text="🚇 Chilonzor metro yaqinida 4 mln gacha", callback_data="ai_quick:chilonzor_metro"),
        ],
        [
            InlineKeyboardButton(text="👨‍👩‍👧 Yunusobodda 2-3 xona oila uchun", callback_data="ai_quick:yunusobod_family"),
        ],
        [
            InlineKeyboardButton(text="💼 Mirobodda maklersiz 600$ gacha", callback_data="ai_quick:mirobod_direct"),
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="nav:cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_roommate_menu_keyboard() -> InlineKeyboardMarkup:
    """Action buttons for roommate finder."""
    keyboard = [
        [
            InlineKeyboardButton(text="👥 Barcha e'lonlar", callback_data="rm:browse:0"),
            InlineKeyboardButton(text="➕ Anketa to'ldirish", callback_data="rm:create"),
        ],
        [
            InlineKeyboardButton(text="🎓 Talabalar", callback_data="rm:filter:student"),
            InlineKeyboardButton(text="💼 Ishlaydiganlar", callback_data="rm:filter:working"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_assistant_quick_keyboard() -> InlineKeyboardMarkup:
    """Quick prompt questions for AI rental advisor."""
    keyboard = [
        [
            InlineKeyboardButton(text="📄 Ijara shartnomasini soliqda ro'yxatdan o'tkazish", callback_data="ai_ask:soliq"),
        ],
        [
            InlineKeyboardButton(text="💵 Zalog (depozit) qaytarilish qoidalari", callback_data="ai_ask:zalog"),
        ],
        [
            InlineKeyboardButton(text="💡 Kommunal to'lovlarni kim to'lashi kerak?", callback_data="ai_ask:utilities"),
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="nav:cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_comparison_action_keyboard(listing_ids: list[int]) -> InlineKeyboardMarkup:
    """Action buttons after comparing apartments."""
    buttons = []
    row = []
    for lid in listing_ids[:3]:
        row.append(InlineKeyboardButton(text=f"🏠 #{lid} ko'rish", callback_data=f"view_listing:{lid}"))
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton(text="🔄 Yangi taqqoslash", callback_data="cmp:new"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_keyboard(pref: UserSearchPreference) -> InlineKeyboardMarkup:
    """Inline menu summarizing user preferences and allowing quick navigation to configure them."""
    districts_text = ", ".join(pref.districts) if pref.districts else "Barcha tumanlar"
    if len(districts_text) > 28:
        districts_text = f"{len(pref.districts)} ta tuman tanlangan"

    price_min_str = f"{pref.min_price:,}".replace(",", " ") if pref.min_price else "0"
    price_max_str = f"{pref.max_price:,}".replace(",", " ") if pref.max_price else "cheksiz"
    price_text = f"{price_min_str} - {price_max_str} so'm"

    rooms_text = ", ".join(map(str, pref.rooms)) if pref.rooms else "Ixtiyoriy"
    owner_text = "✅ Faqat egasidan" if pref.owner_only else "🌐 Barcha e'lonlar"
    quiet_text = f"🌙 {pref.quiet_hours_start}-{pref.quiet_hours_end}" if pref.quiet_hours_enabled else "O‘chirilgan"
    notif_text = "🔔 Yoqilgan" if pref.notifications_enabled else "🔕 O‘chirilgan"

    keyboard = [
        [
            InlineKeyboardButton(text=f"📍 Tuman: {districts_text}", callback_data="cfg:district"),
        ],
        [
            InlineKeyboardButton(text=f"💰 Narx: {price_text}", callback_data="cfg:price"),
        ],
        [
            InlineKeyboardButton(text=f"🛏 Xonalar: {rooms_text}", callback_data="cfg:rooms"),
        ],
        [
            InlineKeyboardButton(text=f"🏠 Rejim: {owner_text}", callback_data="cfg:owner_toggle"),
        ],
        [
            InlineKeyboardButton(text=f"🌙 Tinch rejim: {quiet_text}", callback_data="cfg:quiet"),
            InlineKeyboardButton(text=f"Xabarlar: {notif_text}", callback_data="cfg:notif_toggle"),
        ],
        [
            InlineKeyboardButton(text="🔎 Shu parametrlar bo‘yicha qidirish", callback_data="cfg:run_search"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_districts_keyboard(selected_districts: List[str]) -> InlineKeyboardMarkup:
    """Interactive multi-toggle keyboard for Tashkent districts."""
    keyboard: List[List[InlineKeyboardButton]] = []

    # 2 columns of districts
    row: List[InlineKeyboardButton] = []
    for d in TASHKENT_DISTRICTS:
        is_sel = d in selected_districts
        mark = "✅ " if is_sel else ""
        btn_text = f"{mark}{d}"
        row.append(InlineKeyboardButton(text=btn_text, callback_data=f"dist_toggle:{d}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Action controls
    keyboard.append([
        InlineKeyboardButton(text="🌐 Barchasi (tozalash)", callback_data="dist_action:all"),
        InlineKeyboardButton(text="💾 Saqlash", callback_data="dist_action:save"),
    ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="nav:back_to_settings"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_rooms_keyboard(selected_rooms: List[int]) -> InlineKeyboardMarkup:
    """Toggle keyboard for room counts."""
    room_options = [(0, "Studiya"), (1, "1 xona"), (2, "2 xona"), (3, "3 xona"), (4, "4+ xona")]
    row1: List[InlineKeyboardButton] = []
    row2: List[InlineKeyboardButton] = []

    for r_num, label in room_options[:3]:
        mark = "✅ " if r_num in selected_rooms else ""
        row1.append(InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"room_toggle:{r_num}"))
    for r_num, label in room_options[3:]:
        mark = "✅ " if r_num in selected_rooms else ""
        row2.append(InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"room_toggle:{r_num}"))

    keyboard = [
        row1,
        row2,
        [
            InlineKeyboardButton(text="🌐 Ixtiyoriy (barchasi)", callback_data="room_action:all"),
            InlineKeyboardButton(text="💾 Saqlash", callback_data="room_action:save"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="nav:back_to_settings"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Single cancel / back inline button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="nav:cancel")]
        ]
    )
