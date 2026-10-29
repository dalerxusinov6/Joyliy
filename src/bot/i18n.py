"""Localization strings for Telegram Bot (Uzbek Latin default)."""

TEXTS = {
    "uz": {
        "welcome": (
            "Assalomu alaykum! <b>Joyliy</b> — Toshkent shahrida maklersiz va qulay ijara kvartiralar botiga xush kelibsiz! 🏠\n\n"
            "Bu bot Toshkentdagi yangi e'lonlarni monitoring qilib, bevosita <b>egasidan bo‘lgan e'lonlarni</b> "
            "aniqlaydi va sizga darhol xabar beradi.\n\n"
            "Quyidagi menyu orqali kerakli bo‘limni tanlang:"
        ),
        "help": (
            "ℹ️ <b>Botdan foydalanish bo‘yicha qo‘llanma:</b>\n\n"
            "🔎 <b>Kvartira qidirish</b> (/search) — qidiruv parametrlarini sozlash (tuman, narx, xonalar soni).\n"
            "🆕 <b>Yangi e'lonlar</b> — yaqinda joylangan eng so‘nggi kvartiralar.\n"
            "🏠 <b>Maklersiz kvartiralar</b> — faqat egasidan bo‘lishi mumkin bo‘lgan e'lonlar.\n"
            "❤️ <b>Saqlanganlar</b> (/favorites) — o‘zingiz saqlab qo‘ygan e'lonlar ro‘yxati.\n"
            "⚙️ <b>Sozlamalar</b> (/settings) — bildirishnomalar va filtrlarni boshqarish.\n"
            "⏸ <b>To‘xtatish</b> (/stop) — yangi bildirishnomalarni vaqtincha to‘xtatish.\n"
            "▶️ <b>Davom ettirish</b> (/resume) — bildirishnomalarni qayta yoqish.\n"
            "🔒 <b>Maxfiylik</b> (/privacy) — saqlanadigan ma'lumotlar haqida."
        ),
        "privacy": (
            "🔒 <b>Maxfiylik va Ma'lumotlar xavfsizligi:</b>\n\n"
            "Biz sizning shaxsiy ma'lumotlaringizni hurmat qilamiz:\n"
            "• Faqat Telegram ID, username va siz o‘rnatgan qidiruv sozlamalari (tuman, narx oralig‘i) saqlanadi.\n"
            "• Telefon raqamingiz yoki boshqa maxfiy ma'lumotlar yig‘ilmaydi.\n"
            "• Hech qanday ma'lumot uchinchi shaxslarga berilmaydi.\n"
            "• Istalgan vaqtda /stop orqali xizmatdan chiqishingiz mumkin."
        ),
        "menu_search": "🔎 Kvartira qidirish",
        "menu_latest": "🆕 Yangi e'lonlar",
        "menu_maklersiz": "🏠 Maklersiz kvartiralar",
        "menu_favorites": "❤️ Saqlanganlar",
        "menu_settings": "⚙️ Sozlamalar",
        "stop_success": "⏸ Bildirishnomalar to‘xtatildi. Qayta yoqish uchun /resume buyrug‘ini yuboring.",
        "resume_success": "▶️ Bildirishnomalar muvaffaqiyatli qayta yoqildi!",
        "no_favorites": "Sizda hali saqlangan e'lonlar yo‘q. E'lon ostidagi ❤️ Saqlash tugmasini bosib saqlashingiz mumkin.",
        "saved_to_favorites": "✅ E'lon saqlanganlarga qo‘shildi!",
        "removed_from_favorites": "🗑 E'lon saqlanganlardan o‘chirildi.",
        "hidden_listing": "🚫 E'lon yashirildi.",
        "unknown_command": "Kechirasiz, buyruq tushunarsiz. Yordam uchun /help buyrug‘ini bosing.",
    }
}


def get_text(key: str, lang: str = "uz") -> str:
    """Retrieve localized string with fallback."""
    return TEXTS.get(lang, TEXTS["uz"]).get(key, key)

