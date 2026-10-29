# 🏠 Uyda — Toshkentda Maklersiz Ijara Telegram Bot & OLX Monitor

Production-ready Telegram bot, asynchronous background listing monitor, and REST API service for discovering apartment rentals in Tashkent, Uzbekistan. Built with Python 3.12+, aiogram 3.x, async SQLAlchemy 2.x, PostgreSQL, and FastAPI.

---

## 🌟 Asosiy Xususiyatlar (Key Features)

1. **Maklersiz Classification Engine (O‘zbek va Rus tillarida)**:
   - Ko‘p qatlamli aniq qoidalar va kontekst tahlili.
   - **Ijobiy belgilar**: `maklersiz`, `maklersiz ijara`, `egasidan`, `bevosita egasidan`, `vositachilarsiz`, `o'zimning uyim`, `без посредников`, `от собственника`, `сдаю свою`, `напрямую от владельца`.
   - **Salbiy / Agentlik belgilari**: `makler`, `rieltor`, `agentlik`, `komissiya 50%`, `услуги агентства`, `посреднические услуги`.
   - **Kontekstual inkor (Contextual Negation)**: «Maklerlar bezovta qilmasin», «риелторам не беспокоить», «без комиссии» kabi iboralar agentlik belgisi deb EMAS, balki **kuchli uy egasi belgisi** deb to‘g‘ri baholanadi.
   - Natijaviy yorliqlar: `LIKELY_OWNER` («Egasi bo‘lishi mumkin»), `NEEDS_REVIEW` («Tekshirilmoqda»), `LIKELY_AGENT` («Rieltor / Agentlik»).
   - Ogohlantirish: «⚠️ Egasidan ekanligi mustaqil tasdiqlanmagan».

2. **OLX Uzbekistan Listing Monitor**:
   - Toshkent uzoq muddatli kvartira ijarasi bo‘yicha e'lonlarni kuzatish.
   - Kanonik URL va manba ID bo‘yicha e'lonlarni idempotent deduplikatsiya qilish.
   - Narxlarni UZS (so‘m) formatida normallashtirish (dollar va sh.b. kurs bo‘yicha avtomatik o‘girish).
   - E'lon maydoni (m²), xonalar soni, tuman (Chilonzor, Yunusobod, Mirzo Ulug‘bek va h.k.) va rasmlarini ajratib olish.
   - Manba kirish qoidalari (robots.txt, WAF, Cloudflare) cheklovlariga qat'iy rioya etish.
   - Pluggable provayder arxitekturasi: `OLXHttpListingProvider`, `FixtureListingProvider`, `ManualListingProvider`.

3. **Telegram Bot Foydalanuvchi Tajribasi (aiogram 3.x)**:
   - Buyruqlar: `/start`, `/help`, `/search`, `/settings`, `/favorites`, `/subscription`, `/stop`, `/resume`, `/privacy`.
   - Asosiy menyu tugmalari:
     - 🔎 Kvartira qidirish
     - 🆕 Yangi e'lonlar
     - 🏠 Maklersiz kvartiralar
     - ❤️ Saqlanganlar
     - ⚙️ Sozlamalar
   - Interaktiv FSM va inline klaviaturalar orqali tumanlar (ko‘p tanlovli), narx oralig‘i, xonalar soni (studiya, 1, 2, 3, 4+), faqat egasidan rejimi va tinch rejim (quiet hours)ni boshqarish.
   - E'lon xabari formati va qulay tugmalar: «🔗 OLX’da ko‘rish», «❤️ Saqlash», «🚫 Yashirish».

4. **Bildirishnoma Dvigateli (Notification Engine)**:
   - Har bir foydalanuvchi bo‘yicha individual filtrlash.
   - Deduplikatsiya: bir xil e'lon bir foydalanuvchiga hech qachon takroran yuborilmaydi (`notification_history` jadvali).
   - Telegram cheklovlari (Rate limit & flood control): `TelegramRetryAfter` avtomatik kutish va qayta urinish.
   - Tinch rejim (Quiet hours, masalan 23:00 - 08:00): foydalanuvchi oromini buzmaslik.
   - Botni bloklagan foydalanuvchilarni (`TelegramForbiddenError`) avtomatik aniqlab nofaol holatga o‘tkazish.

5. **Admin Boshqaruvi (`ADMIN_IDS`)**:
   - `/admin_stats` — Foydalanuvchilar soni, umumiy e'lonlar va bugungi yangi e'lonlar statistikasi.
   - `/admin_health` — Monitor va provayder holati.
   - `/admin_test` — E'lon formatini sinovdan o‘tkazish.
   - `/admin_sources` — Sozlangan havolalar va manbalar.
   - `/admin_review` — Noaniq deb belgilangan e'lonlarni tekshirish.
   - `/admin_pause` va `/admin_resume` — Monitorni vaqtincha to‘xtatish va qayta yoqish.

6. **Web Sayt Integratsiyasi uchun REST API (FastAPI)**:
   - `GET /api/listings` — Filtrlangan va sahifalangan e'lonlar (tashqi manba asl havolasi va muallifligi saqlangan holda).
   - `GET /api/listings/{id}` — E'lon tafsilotlari.
   - `GET /api/health` — Tizim va DB holati.
   - `GET /api/admin/monitor-status` — API kalit orqali himoyalangan monitor holati.
   - `POST /api/listings` — Qo‘lda yoki hamkor manbalar orqali e'lon kiritish (API kalit bilan).

---

## 🏗 Loyiha Strukturasi (Project Architecture)

```
Uyda/
├── .env.example               # Muhit o‘zgaruvchilari namunasi
├── .gitignore                 # Git e'tiborsiz qoldiradigan fayllar
├── requirements.txt           # Python qaramliklari (muhrlangan)
├── pyproject.toml             # Loyiha metadata va pytest konfiguratsiyasi
├── Dockerfile                 # Docker konteyner fayli
├── docker-compose.yml         # PostgreSQL + App orkestratsiyasi
├── alembic.ini                # Alembic migratsiya konfiguratsiyasi
├── README.md                  # Ushbu qo‘llanma
├── alembic/
│   ├── env.py                 # Async SQLAlchemy migratsiya muhiti
│   └── versions/
│       └── 001_initial_schema.py # 8 ta asosiy jadval va indekslar
├── src/
│   ├── config.py              # Pydantic Settings konfiguratsiyasi
│   ├── database.py            # Async SQLAlchemy engine va session
│   ├── main.py                # Asosiy kirish nuqtasi (CLI rejimlar: all, bot, worker, api)
│   ├── models/                # Ma'lumotlar bazasi modellari
│   │   ├── user.py            # User va UserSearchPreference
│   │   ├── listing.py         # Listing, Classification, Favorite, NotificationHistory
│   │   └── system.py          # SourceMonitorRun va AdminAuditLog
│   ├── classification/        # Maklersiz klassifikatsiya dvigateli
│   │   ├── engine.py          # O‘zbek va Rus tillari regex va kontekst qoidalari
│   │   └── types.py           # ClassificationLabel va Result modellari
│   ├── providers/             # Pluggable ma'lumot yetkazib beruvchilar
│   │   ├── base.py            # BaseListingProvider abstrakt klassi
│   │   ├── parser.py          # OLX HTML va ma'lumotlar parseri
│   │   ├── olx_http.py        # Hurmatli HTTP mijoz (backoff va 403 aniqlash)
│   │   └── fixture.py         # FixtureListingProvider & ManualListingProvider
│   ├── bot/                   # aiogram 3.x Telegram boti
│   │   ├── bot_instance.py    # Bot va Dispatcher yaratish
│   │   ├── i18n.py            # Mahalliylashtirish (O‘zbek lotincha)
│   │   ├── keyboards.py       # Asosiy va inline klaviaturalar
│   │   ├── states.py          # FSM holatlari (tuman, narx, xonalar)
│   │   ├── formatter.py       # E'lon xabarlarini standart formatga keltirish
│   │   └── handlers/          # Bot marshrutizatorlari (common, search, favorites, ...)
│   ├── services/              # Biznes mantiq xizmatlari
│   │   ├── listing_service.py # Ingestion, qidiruv va saqlanganlar
│   │   ├── notification_service.py # Foydalanuvchilarni topish va yuborish
│   │   └── monitor_worker.py  # Foniy monitoring va jadval
│   └── api/                   # FastAPI REST API integratsiyasi
│       ├── app.py             # FastAPI ilovasi va CORS
│       ├── auth.py            # X-API-Key xavfsizlik bog‘lamasi
│       ├── routes.py          # API yo‘llari (/api/listings, /api/health, ...)
│       └── schemas.py         # Pydantic javob sxemalari
└── tests/                     # 34 ta to‘liq avtomatlashtirilgan testlar
    ├── conftest.py            # Test muhiti va Mock bot
    ├── fixtures/              # OLX HTML sahifa namunalari
    ├── test_classification.py # Maklersiz klassifikatsiya testlari
    ├── test_parser.py         # Narx, tuman va HTML parsing testlari
    ├── test_deduplication.py  # Bir xil e'lonlar deduplikatsiyasi
    ├── test_filtering.py      # Qidiruv filtrlari
    ├── test_notification.py   # Bildirishnomalar va flood control
    ├── test_subscription.py   # Obunani boshqarish
    ├── test_db_persistence.py # DB yaxlitligi va kaskadlar
    └── test_api.py            # REST API integratsiya testlari
```

---

## ⚙️ Ishga Tushirish va O‘rnatish (Local Setup)

### 1. Talablar
- Python 3.12 yoki undan yuqori
- PostgreSQL (yoki sinov uchun SQLite)
- Telegram Bot Token ([@BotFather](https://t.me/BotFather) orqali olingan)

### 2. Virtual muhit yaratish va qaramliklarni o‘rnatish

```bash
# Virtual muhitni faollashtirish
python3 -m venv .venv
source .venv/bin/activate

# Qaramliklarni o‘rnatish
pip install -r requirements.txt
```

### 3. Konfiguratsiya faylini tayyorlash

```bash
cp .env.example .env
```

`.env` faylini ochib, quyidagi asosiy parametrlarni kiriting:
```ini
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/uyda
API_KEY=my-super-secret-key-2026
POLL_INTERVAL_SECONDS=600
```

### 4. Ma'lumotlar bazasi migratsiyasini ishga tushirish

```bash
# Alembic migratsiyasi orqali 8 ta jadvalni yaratish
alembic upgrade head
```

### 5. Avtomatlashtirilgan testlarni ishga tushirish

```bash
pytest -v
```
Barcha 34 ta unit va integratsiya testlari muvaffaqiyatli o‘tishi kerak.

### 6. Ilovani mahalliy ishga tushirish

```bash
# Barcha qismlarni birga ishga tushirish (Bot + Monitor + REST API):
python -m src.main --mode all

# Yoki alohida-alohida:
python -m src.main --mode bot      # Faqat Telegram bot
python -m src.main --mode worker   # Faqat foniy monitor
python -m src.main --mode api      # Faqat FastAPI veb-serveri
```

---

## 🚀 Docker va Docker Compose orqali Ishga Tushirish (VPS Deployment)

Loyiha to‘liq konteynerlashtirilgan va PostgreSQL bilan birgalikda bir komanda orqali ko‘tariladi.

```bash
# 1. Konteynerlarni yig‘ish va fonda ishga tushirish
docker compose up -d --build

# 2. Konteynerlar holatini tekshirish
docker compose ps

# 3. Loglarni real vaqtda kuzatish
docker compose logs -f app
```

Konteyner ishga tushganda:
- PostgreSQL avtomatik boshlanadi va sog‘lom holatga (`healthy`) keladi.
- Alembic migratsiyalari avtomatik qo‘llanadi (`alembic upgrade head`).
- Telegram bot, foniy monitoring va FastAPI veb-serveri 8000-portda ochiladi.

---

## 🌐 REST API Integratsiyasi (Website Integration)

Uyda veb-sayti backendga ulanishi uchun tayyor REST API mavjud:

### 1. Salomatlik tekshiruvi:
```bash
curl -s http://localhost:8000/api/health
```
Javob:
```json
{
  "status": "OK",
  "database_connected": true,
  "timestamp": "2026-10-28T15:00:00Z"
}
```

### 2. Kvartiralar ro‘yxatini olish (Filtrlash va sahifalash):
```bash
curl -s "http://localhost:8000/api/listings?district=Chilonzor&owner_only=true&limit=10"
```
Har bir qaytarilgan e'lon asl manba atributini o‘zida saqlaydi (`source_attribution`, `canonical_url`, `disclaimer`).

### 3. Monitoring holatini tekshirish (Himoyalangan):
```bash
curl -s -H "X-API-Key: my-super-secret-key-2026" http://localhost:8000/api/admin/monitor-status
```

### 4. E'lonni qo‘lda kiritish (Manual / Partner Feed Ingest):
```bash
curl -s -X POST http://localhost:8000/api/listings \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-super-secret-key-2026" \
  -d '{
    "canonical_url": "https://olx.uz/d/oz/obyavlenie/chilonzor-maklersiz-ID888.html",
    "title": "Chilonzor 2 xonali kvartira, egasidan maklersiz beriladi",
    "price_raw": "3 500 000 so‘m",
    "district": "Chilonzor",
    "rooms": 2,
    "area": 54.0,
    "description": "Maklerlar bezovta qilmasin. O‘zimning uyim."
  }'
```

---

## 🛡 Manba Huquqlari va OLX Kirish Qoidalari (Access Controls & Ethics)

1. **Kirish qoidalariga rioya etish**:
   OLX Uzbekistan serverlari to‘g‘ridan-to‘g‘ri dasturiy so‘rovlarga `HTTP 403 Forbidden` yoki Cloudflare / WAF to‘sig‘ini qaytaradi.
   Dasturimiz platforma xavfsizlik devorlarini buzib o‘tish, CAPTCHA aylanib o‘tish yoki qoidalarni chetlab o‘tish kabi xavfli amallarni **qilmaydi**.
2. **Pluggable Provider Interface**:
   - `OLXHttpListingProvider`: Ruxsat etilgan rejimda va belgilangan muddatlarda so‘rov yuboradi. Agar 403 qaytsa, manba holatini `BLOCKED_BY_ACCESS_CONTROL` deb belgilaydi va administratorga bildirishnoma beradi.
   - `FixtureListingProvider`: Tizimni tarmoqsiz sinovdan o‘tkazish va CI/CD muhiti uchun haqiqiy namunaviy e'lonlar to‘plami.
   - `ManualListingProvider`: Telegram boti yoki REST API orqali kiritiladigan avtorizatsiyalangan e'lonlar oqimi.
3. **Mualliflik huquqi va havolalar**:
   Har bir e'lon asl manba havolasi (`canonical_url`), aniqlangan vaqti va «Tashqi manba (OLX Uzbekistan)» yorlig‘i bilan saqlanadi. Platforma foydalanuvchilariga e'lon platforma foydalanuvchisi tomonidan kiritilgan deb soxtalashtirilmaydi.

