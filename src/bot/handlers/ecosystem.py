"""Ecosystem bot handlers: AI Apartment Match, Roommates, Price Intelligence, Comparison, and AI Advisor."""

import logging
import html
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.config import settings
from src.models.user import User
from src.models.listing import Listing
from src.services.listing_service import listing_service
from src.services.ai_match_service import ai_match_service
from src.services.assistant_service import assistant_service
from src.services.comparison_service import comparison_service
from src.services.price_intelligence_service import price_intelligence_service
from src.services.neighborhood_service import neighborhood_service
from src.services.roommate_service import roommate_service
from src.services.scam_detector_service import scam_detector_service
from src.bot.states import AIMatchState, AssistantChatState, ComparisonState, RoommateCreationState
from src.bot.keyboards import (
    get_main_menu_keyboard,
    get_ai_search_quick_keyboard,
    get_roommate_menu_keyboard,
    get_assistant_quick_keyboard,
    get_comparison_action_keyboard,
    get_cancel_keyboard,
)
from src.bot.formatter import format_listing_message, get_listing_inline_keyboard, format_price_uzs
from src.bot.handlers.common import get_or_create_user

logger = logging.getLogger(__name__)
ecosystem_router = Router(name="ecosystem_router")


# ==========================================
# 1. AI APARTMENT MATCH
# ==========================================

@ecosystem_router.message(Command("ai"))
@ecosystem_router.message(F.text == "🤖 AI Qidiruv")
async def handle_ai_search_prompt(message: Message, state: FSMContext):
    """Initiate AI natural language search."""
    await state.set_state(AIMatchState.waiting_query)
    text = (
        "🤖 <b>Joyliy AI Qidiruv tizimi</b>\n\n"
        "O'zingizga kerakli kvartirani <b>oddiy so'zlar bilan</b> yozing:\n\n"
        "<i>Masalan:</i>\n"
        "• «Chilonzorda metro yaqinida 4 mln gacha 2 xonali kvartira oila uchun»\n"
        "• «Yunusobodda maklersiz 500$ gacha talaba yigitlar uchun»\n"
        "• «Mirobod tumanida yevroremont 3 xona jihozlangan»\n\n"
        "Yoki quyidagi tayyor variantlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_ai_search_quick_keyboard(), parse_mode="HTML")


@ecosystem_router.callback_query(F.data.startswith("ai_quick:"))
async def handle_ai_quick_query(callback: CallbackQuery, state: FSMContext):
    """Handle quick sample click for AI matching."""
    sample_key = callback.data.split(":", 1)[1]
    queries = {
        "chilonzor_metro": "Chilonzorda metro yaqinida 4 million so'mgacha kvartira",
        "yunusobod_family": "Yunusobodda 2-3 xonali kvartira oila uchun",
        "mirobod_direct": "Mirobod tumanida maklersiz 600$ gacha toza kvartira",
    }
    query_text = queries.get(sample_key, "Toshkentda 2 xonali kvartira")
    await callback.answer("Qidirilmoqda...")
    await run_ai_search(callback.message, query_text, state)


@ecosystem_router.message(AIMatchState.waiting_query)
async def handle_ai_query_input(message: Message, state: FSMContext):
    """Process user's natural language input."""
    await run_ai_search(message, message.text or "", state)


async def run_ai_search(message: Message, query: str, state: FSMContext):
    """Core logic to parse and search with AI match engine."""
    await state.clear()
    wait_msg = await message.answer("🔍 <i>AI so'rovingizni tahlil qilmoqda va eng mos e'lonlarni saralamoqda...</i>", parse_mode="HTML")

    async with AsyncSessionLocal() as session:
        search_res = await ai_match_service.search_and_rank_matches(session, query, limit=5)
        parsed = search_res.get("parsed_filters", {})
        matches = search_res.get("results", [])

    try:
        await wait_msg.delete()
    except Exception:
        pass

    # Summary of parsed criteria
    criteria_lines = []
    if parsed.get("district"):
        criteria_lines.append(f"📍 Tuman: <b>{parsed['district']}</b>")
    if parsed.get("metro"):
        criteria_lines.append(f"🚇 Metro: <b>{parsed['metro']}</b>")
    if parsed.get("max_price_uzs"):
        criteria_lines.append(f"💰 Maksimal byudjet: <b>{format_price_uzs(parsed['max_price_uzs'])}</b>")
    if parsed.get("rooms"):
        r_val = parsed["rooms"]
        r_str = ", ".join(map(str, r_val)) if isinstance(r_val, list) else f"{r_val} xonali"
        criteria_lines.append(f"🛏 Xonalar: <b>{r_str}</b>")
    if parsed.get("owner_only"):
        criteria_lines.append("👤 Faqat <b>egasidan</b>")
    if parsed.get("target_audience") and parsed["target_audience"] != "any":
        criteria_lines.append(f"👥 Moslik: <b>{parsed['target_audience'].capitalize()}</b>")

    criteria_summary = "\n".join(criteria_lines) if criteria_lines else "Umumiy parametrlar"

    if not matches:
        await message.answer(
            f"🤖 <b>AI Qidiruv natijalari:</b>\n\n"
            f"<b>Aniqlangan parametrlar:</b>\n{criteria_summary}\n\n"
            f"Afsuski, kiritilgan talablarga mos keluvchi yangi e'lonlar hozircha topilmadi. "
            f"Byudjetni biroz oshirib yoki tuman doirasini kengaytirib ko'ring.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    await message.answer(
        f"🎯 <b>Topildi: {len(matches)} ta mos kvartira</b>\n\n"
        f"<b>Aniqlangan parametrlar:</b>\n{criteria_summary}\n\n"
        f"Quyida eng yuqori moslik ko'rsatkichiga ega e'lonlar:",
        parse_mode="HTML",
    )

    for item in matches:
        listing = item["listing"]
        score = item["match_score"]
        pros_list = item.get("pros", [])
        pros_text = " • " + "\n • ".join(pros_list[:3]) if pros_list else ""

        score_badge = "🟢" if score >= 85 else ("🟡" if score >= 70 else "⚪️")
        match_header = f"{score_badge} <b>Moslik darajasi: {score}%</b>\n{pros_text}\n"

        base_msg = format_listing_message(listing)
        full_msg = f"{match_header}\n{base_msg}"
        kb = get_listing_inline_keyboard(listing)
        await message.answer(full_msg, reply_markup=kb, parse_mode="HTML")


# ==========================================
# 2. SMART MAP SEARCH LINK
# ==========================================

@ecosystem_router.message(Command("map"))
@ecosystem_router.message(F.text == "🗺 Xarita")
async def handle_map_navigation(message: Message):
    """Direct user to the interactive real estate map."""
    map_url = f"{settings.WEBSITE_URL}/?view=map"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Interaktiv xaritani ochish", url=map_url)],
            [InlineKeyboardButton(text="🚇 Metro bekatlari xaritasi", callback_data="map:metro_info")],
        ]
    )
    text = (
        "🗺 <b>Toshkent Interaktiv Ijara Xaritasi</b>\n\n"
        "Joyliy veb-platformasida barcha e'lonlar xaritada narxlari bilan ko'rsatilgan:\n\n"
        "• 📍 Aniq joylashuv va narx belgilari\n"
        "• 🚇 Toshkent metro bekatlariga yaqinlik (500m, 1km, 2km radius)\n"
        "• 🏫 Maktab, universitet, supermarket va parklar joylashuvi\n"
        "• 📐 Xaritadan maydon chizib qidirish imkoniyati\n\n"
        "Xaritani ochish uchun quyidagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@ecosystem_router.callback_query(F.data == "map:metro_info")
async def handle_metro_info(callback: CallbackQuery):
    """Show quick summary of metro lines in Tashkent."""
    metros = neighborhood_service.get_all_metro_stations()
    lines_count = {}
    for m in metros:
        lines_count[m["line"]] = lines_count.get(m["line"], 0) + 1

    lines_summary = "\n".join([f"• <b>{line}:</b> {cnt} ta bekat" for line, cnt in lines_count.items()])
    await callback.message.answer(
        f"🚇 <b>Toshkent Metropoliteni Ma'lumotlari:</b>\n\n"
        f"Jami bekatlar: <b>{len(metros)} ta</b>\n\n"
        f"{lines_summary}\n\n"
        f"Kvartira qidirishda metro nomi bo'yicha qidirishingiz mumkin (masalan: <i>Novza, Beruniy, Buyuk Ipak Yo'li</i>).",
        parse_mode="HTML"
    )
    await callback.answer()


# ==========================================
# 3. FAIR PRICE AI — DISTRICT INTELLIGENCE
# ==========================================

@ecosystem_router.message(Command("market"))
@ecosystem_router.message(F.text == "📈 Bozor narxlari")
async def handle_market_intelligence(message: Message):
    """Display real-time Tashkent rental price intelligence."""
    async with AsyncSessionLocal() as session:
        stats = await price_intelligence_service.get_district_market_stats(session)

    room_breakdown = stats.get("room_breakdown", {})
    summary_rows = []
    for r, pinfo in room_breakdown.items():
        avg_p = pinfo.get("avg_uzs", 0)
        p_str = f"{avg_p / 1_000_000:.1f} mln" if avg_p else "-"
        summary_rows.append(f"• <b>{r} xonali:</b> o'rtacha ~{p_str} so'm ({pinfo.get('count', 0)} e'lon)")

    text = (
        "📈 <b>Toshkent Shahri Bozor Narxlari Tahlili</b>\n\n"
        "Joyliy algoritmlari har soatda minglab e'lonlarni tahlil qilib, haqqoniy bozor narxini aniqlaydi:\n\n"
        f"Jami faol tahlil qilingan: <b>{stats.get('sample_size', 0)} ta</b> e'lon\n"
        f"{chr(10).join(summary_rows) if summary_rows else '• Ma’lumotlar bazada hisoblanmoqda'}\n\n"
        "💡 <b>Tavsiya:</b> Har bir e'lon ostida uning bozor narxiga nisbatan bahosi berilgan:\n"
        "🟢 <i>Bozordan arzon</i> — eng foydali takliflar\n"
        "🟡 <i>Bozor narxida</i> — adolatli o'rtacha narx\n"
        "🔴 <i>Bozordan qimmat</i> — muzokaraga sabab bo'luvchi narx"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Saytda to'liq tahlilni ko'rish", url=f"{settings.WEBSITE_URL}/?view=market")],
            [InlineKeyboardButton(text="🎯 Bozor narxidan arzonlarni topish", callback_data="ai_quick:chilonzor_metro")],
        ]
    )
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ==========================================
# 4. ROOMMATE FINDER
# ==========================================

@ecosystem_router.message(Command("roommates"))
@ecosystem_router.message(F.text == "👥 Hamxonalar")
async def handle_roommate_menu(message: Message):
    """Open roommate finder dashboard."""
    async with AsyncSessionLocal() as session:
        profiles = await roommate_service.list_profiles(session, limit=3)

    text = (
        "👥 <b>Joyliy — Hamxona Topish Xizmati</b>\n\n"
        "Toshkentda birgalikda kvartira ijaraga olish yoki sherik topish uchun maxsus bo'lim:\n\n"
        "• Talabalar va yosh mutaxassislar anketalari\n"
        "• Moslik foizi (0-100% kompatibilite)\n"
        "• Byudjet, tuman va turmush tarzi bo'yicha moslashuv\n"
        "• Shaxsiy ma'lumotlar himoyasi\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_roommate_menu_keyboard(), parse_mode="HTML")

    if profiles:
        for p in profiles:
            p_districts = ", ".join(p.preferred_districts) if p.preferred_districts else "Toshkent"
            p_text = (
                f"👤 <b>{html.escape(p.name)}</b> ({p.age or 22} yosh)\n"
                f"📍 Tuman: <b>{html.escape(p_districts)}</b>\n"
                f"💰 Byudjet: <b>{format_price_uzs(p.budget_uzs)}</b>\n"
                f"💼 Kasb/Mashg'ulot: <b>{html.escape(p.occupation or 'Talaba')}</b>\n"
                f"📝 <i>«{html.escape(p.bio or 'Toza va tinch turmush tarzini qadrlayman.')}»</i>"
            )
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💌 Bog'lanish so'rovi", callback_data=f"rm_req:{p.id}")],
                ]
            )
            await message.answer(p_text, reply_markup=kb, parse_mode="HTML")


@ecosystem_router.callback_query(F.data.startswith("rm_req:"))
async def handle_roommate_connect(callback: CallbackQuery):
    """Handle roommate connection request."""
    profile_id = int(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
        )
        req = await roommate_service.send_connection_request(
            session=session,
            from_user_id=user.id,
            to_profile_id=profile_id,
            message="Salom! Sizning Joyliy dagi hamxona anketangiz bilan tanishdim.",
            contact_info=f"@{callback.from_user.username}" if callback.from_user.username else str(callback.from_user.id),
        )

    await callback.answer("✅ Bog'lanish so'rovingiz qabul qilindi!", show_alert=True)


# ==========================================
# 5. SHORTLIST BATTLE — APARTMENT COMPARISON
# ==========================================

@ecosystem_router.message(Command("compare"))
@ecosystem_router.message(F.text == "⚖️ Taqqoslash")
async def handle_compare_prompt(message: Message, state: FSMContext):
    """Initiate side-by-side apartment comparison."""
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        favorites = await listing_service.get_user_favorites(session, user_id=user.id, limit=6)

    fav_ids = [str(f.id) for f in favorites]

    text = (
        "⚖️ <b>Kvartiralarni Taqqoslash (Shortlist Battle)</b>\n\n"
        "2 tadan 5 tagacha kvartirani yonma-yon solishtirib, narx/m², metro masofasi va "
        "AI g'olib bahosini bilib oling!\n\n"
        "Qanday solishtirish mumkin:\n"
        "1. E'lonlar ostidagi <b>«⚖️ Taqqoslash»</b> tugmasini bosing\n"
        "2. Yoki e'lon ID raqamlarini probel bilan yozib yuboring (masalan: <code>101 105</code>)"
    )

    if len(favorites) >= 2:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"❤️ Saqlangan {min(3, len(favorites))} tani taqqoslash",
                        callback_data=f"cmp_run:{','.join(fav_ids[:3])}"
                    )
                ],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="nav:cancel")],
            ]
        )
    else:
        kb = get_cancel_keyboard()

    await state.set_state(ComparisonState.waiting_listing_ids)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@ecosystem_router.callback_query(F.data.startswith("cmp_add:"))
async def handle_comparison_add(callback: CallbackQuery, state: FSMContext):
    """Add a listing to comparison queue."""
    listing_id = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    comp_list = data.get("comp_ids", [])
    if listing_id not in comp_list:
        comp_list.append(listing_id)
        await state.update_data(comp_ids=comp_list)
        await callback.answer(f"✅ #{listing_id} taqqoslashga qo'shildi ({len(comp_list)} ta)!")
    else:
        await callback.answer(f"#{listing_id} allaqachon taqqoslashda mavjud.")

    if len(comp_list) >= 2:
        id_str = ",".join(map(str, comp_list[-3:]))
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"⚖️ {len(comp_list)} ta kvartirani taqqoslash", callback_data=f"cmp_run:{id_str}")],
            ]
        )
        try:
            await callback.message.reply(f"⚖️ Taqqoslash uchun {len(comp_list)} ta e'lon yig'ildi.", reply_markup=kb)
        except Exception:
            pass


@ecosystem_router.callback_query(F.data.startswith("cmp_run:"))
async def handle_run_comparison_cb(callback: CallbackQuery, state: FSMContext):
    """Execute comparison via callback."""
    ids_str = callback.data.split(":", 1)[1]
    listing_ids = [int(x.strip()) for x in ids_str.split(",") if x.strip().isdigit()]
    await run_comparison(callback.message, listing_ids)
    await callback.answer()


@ecosystem_router.message(ComparisonState.waiting_listing_ids)
async def handle_comparison_text_input(message: Message, state: FSMContext):
    """Parse listing IDs from user input and compare."""
    await state.clear()
    raw = message.text or ""
    ids = [int(tok) for tok in raw.replace(",", " ").split() if tok.isdigit()]
    if len(ids) < 2:
        await message.answer("Kamida 2 ta e'lon ID raqamini kiritishingiz kerak. Masalan: <code>101 105</code>", parse_mode="HTML")
        return
    await run_comparison(message, ids[:4])


async def run_comparison(message: Message, listing_ids: list[int]):
    """Execute side-by-side comparison and present AI winner."""
    async with AsyncSessionLocal() as session:
        result = await comparison_service.compare_listings(session, listing_ids)

    if not result.listings or len(result.listings) < 2:
        await message.answer("Taqqoslanadigan e'lonlar topilmadi yoki 2 tadan kam.", reply_markup=get_main_menu_keyboard())
        return

    cards = []
    for l in result.listings:
        sqm_p = f"{l['price_per_sqm_uzs']:,}".replace(",", " ") if l.get("price_per_sqm_uzs") else "-"
        cards.append(
            f"🏠 <b>#{l['id']} — {html.escape(l['title'][:28])}</b>\n"
            f"💰 Narxi: <b>{format_price_uzs(l['price_uzs'])}</b>\n"
            f"📐 Maydon: {l['area'] or '-'} m² (1 m² = {sqm_p} so'm)\n"
            f"📍 Tuman: {l['district'] or '-'}\n"
            f"🚇 Metro: {l.get('metro_station') or 'Yo‘q'}\n"
            f"⭐ Ball: <b>{l['overall_score']}/100</b>\n"
        )

    winner_text = (
        f"🏆 <b>AI G'OLIBI: E'LON #{result.winner_listing_id}</b>\n\n"
        f"<i>{html.escape(result.ai_winner_summary or 'Eng muvozanatli va xavfsiz taklif.')}</i>"
    )

    full_text = (
        f"⚖️ <b>Kvartiralar Taqqoslash Natijasi:</b>\n\n"
        f"{chr(10).join(cards)}\n"
        f"-------------------------------\n"
        f"{winner_text}"
    )

    kb = get_comparison_action_keyboard(listing_ids)
    await message.answer(full_text, reply_markup=kb, parse_mode="HTML")


# ==========================================
# 6. AI VIRTUAL RENTAL ADVISOR
# ==========================================

@ecosystem_router.message(Command("advisor"))
@ecosystem_router.message(Command("ask"))
@ecosystem_router.message(F.text == "💬 AI Maslahatchi")
async def handle_advisor_prompt(message: Message, state: FSMContext):
    """Initiate consultation with Joyliy AI assistant."""
    await state.set_state(AssistantChatState.waiting_question)
    text = (
        "💬 <b>Joyliy AI — Ijara Maslahatchisi</b>\n\n"
        "O'zbekistonda ijara shartnomasi, soliq, zalog (depozit), kommunal to'lovlar yoki "
        "firibgarlikdan saqlanish bo'yicha savolingizni bering:\n\n"
        "<i>Masalan:</i>\n"
        "• «Ijara shartnomasini soliq saytida qanday ro'yxatdan o'tkazamiz?»\n"
        "• «Maklerlik xizmati uchun qancha to'lanadi?»\n"
        "• «Kvartirani bo'shatganda zalogni qaytarish tartibi qanday?»\n\n"
        "Yoki pastdagi tayyor savollardan birini bosing:"
    )
    await message.answer(text, reply_markup=get_assistant_quick_keyboard(), parse_mode="HTML")


@ecosystem_router.callback_query(F.data.startswith("ai_ask:"))
async def handle_advisor_quick_cb(callback: CallbackQuery, state: FSMContext):
    """Quick prompt questions for AI advisor."""
    key = callback.data.split(":", 1)[1]
    prompts = {
        "soliq": "Ijara shartnomasini ijara.soliq.uz portalida qanday ro'yxatdan o'tkazamiz va qanday hujjatlar kerak?",
        "zalog": "Zalog depoziti qanday holatlarda qaytariladi va qachon ushlab qolinishi mumkin?",
        "utilities": "Kvartira ijarasida kommunal to'lovlarni ijarachi to'laydimi yoki uy egasi?",
    }
    q = prompts.get(key, "Ijara shartnomasi qoidalari")
    await callback.answer("Javob tayyorlanmoqda...")
    await run_advisor_answer(callback.message, q, state)


@ecosystem_router.message(AssistantChatState.waiting_question)
async def handle_advisor_user_input(message: Message, state: FSMContext):
    """Process user's legal or rental question."""
    await run_advisor_answer(message, message.text or "", state)


async def run_advisor_answer(message: Message, question: str, state: FSMContext):
    """Generate answer from assistant service."""
    await state.clear()
    wait_msg = await message.answer("✍️ <i>Joyliy AI maslahatchisi javob tayyorlamoqda...</i>", parse_mode="HTML")

    async with AsyncSessionLocal() as session:
        res = await assistant_service.get_response(session=session, user_message=question)

    try:
        await wait_msg.delete()
    except Exception:
        pass

    reply_str = res.get("reply", "Savolingizga javob tayyorlanmoqda.")
    legal_refs = res.get("legal_references", [])
    practical_tips = res.get("practical_tips", [])

    refs_str = ""
    if legal_refs:
        refs_str = "\n\n📚 <b>Qonuniy asos:</b>\n• " + "\n• ".join(legal_refs)

    tips_str = ""
    if practical_tips:
        tips_str = "\n\n💡 <b>Amaliy maslahat:</b>\n• " + "\n• ".join(practical_tips)

    reply_text = f"🤖 <b>Joyliy AI Maslahatchi:</b>\n\n{html.escape(reply_str)}{refs_str}{tips_str}"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Boshqa savol berish", callback_data="ai_ask:new")],
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="nav:back_to_menu")],
        ]
    )
    await message.answer(reply_text, reply_markup=kb, parse_mode="HTML")


@ecosystem_router.callback_query(F.data == "ai_ask:new")
async def handle_ask_new(callback: CallbackQuery, state: FSMContext):
    """Prompt for another question."""
    await handle_advisor_prompt(callback.message, state)
    await callback.answer()


@ecosystem_router.callback_query(F.data == "nav:back_to_menu")
async def handle_back_menu_cb(callback: CallbackQuery, state: FSMContext):
    """Return to main menu."""
    await state.clear()
    await callback.message.answer("🏠 Asosiy menyudasiz:", reply_markup=get_main_menu_keyboard())
    await callback.answer()


# ==========================================
# 7. SCAM REPORTING CALLBACK
# ==========================================

@ecosystem_router.callback_query(F.data.startswith("rep:"))
async def handle_report_callback(callback: CallbackQuery):
    """Handle user reporting a suspicious listing."""
    listing_id = int(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
        )
        report = await scam_detector_service.submit_report(
            session=session,
            listing_id=listing_id,
            reporter_user_id=user.id,
            reason="SHUBHALI_ELON",
            details="Telegram foydalanuvchisi tomonidan shikoyat bildirildi",
        )

    await callback.answer("⚠️ Shikoyatingiz qabul qilindi. Moderatsiya jamoasi ushbu e'lonni tekshiradi!", show_alert=True)
