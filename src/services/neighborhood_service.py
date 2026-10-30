"""Neighborhood Intelligence Service: Tashkent Districts, Metro Stations, Infrastructure Scores."""

import math
from typing import Dict, List, Optional, Any


TASHKENT_METRO_STATIONS = [
    # Chilonzor Line (Red)
    {"name": "Chilonzor", "name_ru": "Чиланзар", "aliases": ["chilonzor", "чиланзар", "chilonzar"], "line": "Chilonzor", "lat": 41.2736, "lon": 69.2052, "district": "Chilonzor"},
    {"name": "Mirzo Ulug‘bek", "name_ru": "Мирзо Улугбек", "aliases": ["mirzo ulugbek", "мирзо улугбек"], "line": "Chilonzor", "lat": 41.2825, "lon": 69.2136, "district": "Chilonzor"},
    {"name": "Novza", "name_ru": "Новза", "aliases": ["novza", "новза", "hamza"], "line": "Chilonzor", "lat": 41.2922, "lon": 69.2281, "district": "Chilonzor"},
    {"name": "Milliy bog‘", "name_ru": "Миллий бог", "aliases": ["milliy bog", "миллий бог", "комсомольская"], "line": "Chilonzor", "lat": 41.3039, "lon": 69.2411, "district": "Chilonzor"},
    {"name": "Xalqlar do‘stligi", "name_ru": "Дружба народов", "aliases": ["xalqlar dostligi", "дружба народов", "дружба"], "line": "Chilonzor", "lat": 41.3114, "lon": 69.2419, "district": "Shayxontohur"},
    {"name": "Paxtakor", "name_ru": "Пахтакор", "aliases": ["paxtakor", "пахтакор", "pakhtakor"], "line": "Chilonzor", "lat": 41.3164, "lon": 69.2597, "district": "Shayxontohur"},
    {"name": "Mustaqillik maydoni", "name_ru": "Площадь Независимости", "aliases": ["mustaqillik", "площадь независимости", "ленина"], "line": "Chilonzor", "lat": 41.3175, "lon": 69.2694, "district": "Yunusobod"},
    {"name": "Amir Temur xiyoboni", "name_ru": "Сквер Амира Темура", "aliases": ["amir temur", "амир темур", "сквер"], "line": "Chilonzor", "lat": 41.3122, "lon": 69.2797, "district": "Mirobod"},
    {"name": "Hamid Olimjon", "name_ru": "Хамид Олимджан", "aliases": ["hamid olimjon", "хамид олимджан", "хамида алимджана"], "line": "Chilonzor", "lat": 41.3208, "lon": 69.2944, "district": "Mirzo Ulug‘bek"},
    {"name": "Pushkin", "name_ru": "Пушкин", "aliases": ["pushkin", "пушкин", "пушкинская"], "line": "Chilonzor", "lat": 41.3256, "lon": 69.3108, "district": "Mirzo Ulug‘bek"},
    {"name": "Buyuk Ipak Yo‘li", "name_ru": "Буюк Ипак Йули", "aliases": ["buyuk ipak yoli", "буюк ипак йули", "максим горький", "горький"], "line": "Chilonzor", "lat": 41.3267, "lon": 69.3342, "district": "Mirzo Ulug‘bek"},
    {"name": "Olmazor", "name_ru": "Олмазар", "aliases": ["olmazor", "олмазар", "собир рахимов"], "line": "Chilonzor", "lat": 41.2567, "lon": 69.1961, "district": "Chilonzor"},

    # O'zbekiston Line (Blue)
    {"name": "Beruniy", "name_ru": "Беруни", "aliases": ["beruniy", "беруни", "beruni"], "line": "O‘zbekiston", "lat": 41.3444, "lon": 69.2064, "district": "Olmazor"},
    {"name": "Tinchlik", "name_ru": "Тинчлик", "aliases": ["tinchlik", "тинчлик"], "line": "O‘zbekiston", "lat": 41.3328, "lon": 69.2253, "district": "Olmazor"},
    {"name": "Chorsu", "name_ru": "Чорсу", "aliases": ["chorsu", "чорсу"], "line": "O‘zbekiston", "lat": 41.3253, "lon": 69.2392, "district": "Shayxontohur"},
    {"name": "G‘afur G‘ulom", "name_ru": "Гафур Гулям", "aliases": ["gafur gulom", "гафур гулям"], "line": "O‘zbekiston", "lat": 41.3217, "lon": 69.2483, "district": "Shayxontohur"},
    {"name": "Alisher Navoiy", "name_ru": "Алишера Навои", "aliases": ["alisher navoiy", "алишер навои", "навои"], "line": "O‘zbekiston", "lat": 41.3158, "lon": 69.2589, "district": "Shayxontohur"},
    {"name": "O‘zbekiston", "name_ru": "Узбекистан", "aliases": ["ozbekiston", "узбекистан"], "line": "O‘zbekiston", "lat": 41.3092, "lon": 69.2611, "district": "Yakkasaroy"},
    {"name": "Kosmonavtlar", "name_ru": "Космонавтов", "aliases": ["kosmonavtlar", "космонавтов", "космонавты"], "line": "O‘zbekiston", "lat": 41.3028, "lon": 69.2667, "district": "Yakkasaroy"},
    {"name": "Oybek", "name_ru": "Айбек", "aliases": ["oybek", "айбек"], "line": "O‘zbekiston", "lat": 41.2981, "lon": 69.2817, "district": "Mirobod"},
    {"name": "Toshkent", "name_ru": "Ташкент", "aliases": ["toshkent", "ташкент", "северный вокзал"], "line": "O‘zbekiston", "lat": 41.2936, "lon": 69.2906, "district": "Mirobod"},
    {"name": "Mashinasozlar", "name_ru": "Машинасозлар", "aliases": ["mashinasozlar", "машинасозлар", "ташсельмаш"], "line": "O‘zbekiston", "lat": 41.2975, "lon": 69.3103, "district": "Yashnobod"},
    {"name": "Do‘stlik", "name_ru": "Дустлик", "aliases": ["dostlik", "дустлик", "чкаловская"], "line": "O‘zbekiston", "lat": 41.2942, "lon": 69.3275, "district": "Yashnobod"},

    # Yunusobod Line (Green)
    {"name": "Turkiston", "name_ru": "Туркистан", "aliases": ["turkiston", "туркистон", "туркестан"], "line": "Yunusobod", "lat": 41.3789, "lon": 69.2944, "district": "Yunusobod"},
    {"name": "Yunusobod", "name_ru": "Юнусабад", "aliases": ["yunusobod", "юнусабад"], "line": "Yunusobod", "lat": 41.3653, "lon": 69.2897, "district": "Yunusobod"},
    {"name": "Shahriston", "name_ru": "Шахристан", "aliases": ["shahriston", "шахристан", "хабиб абдуллаев"], "line": "Yunusobod", "lat": 41.3536, "lon": 69.2872, "district": "Yunusobod"},
    {"name": "Bodomzor", "name_ru": "Бадамзар", "aliases": ["bodomzor", "бадамзар"], "line": "Yunusobod", "lat": 41.3364, "lon": 69.2847, "district": "Yunusobod"},
    {"name": "Minor", "name_ru": "Минор", "aliases": ["minor", "минор"], "line": "Yunusobod", "lat": 41.3267, "lon": 69.2811, "district": "Yunusobod"},
    {"name": "Yunus Rajabiy", "name_ru": "Юнус Раджаби", "aliases": ["yunus rajabiy", "юнус раджаби"], "line": "Yunusobod", "lat": 41.3128, "lon": 69.2789, "district": "Mirobod"},
    {"name": "Ming O‘rik", "name_ru": "Минг Урик", "aliases": ["ming orik", "минг урик"], "line": "Yunusobod", "lat": 41.2989, "lon": 69.2828, "district": "Mirobod"},

    # Sergeli / Halqa Line (Circle / Purple)
    {"name": "Choshtepa", "name_ru": "Чоштепа", "aliases": ["choshtepa", "чоштепа"], "line": "Sergeli", "lat": 41.2464, "lon": 69.2131, "district": "Sergeli"},
    {"name": "O‘zgarish", "name_ru": "Узгариш", "aliases": ["ozgarish", "узгариш"], "line": "Sergeli", "lat": 41.2347, "lon": 69.2169, "district": "Sergeli"},
    {"name": "Sergeli", "name_ru": "Сергели", "aliases": ["sergeli", "сергели"], "line": "Sergeli", "lat": 41.2225, "lon": 69.2214, "district": "Sergeli"},
    {"name": "Yangihayot", "name_ru": "Янгихаёт", "aliases": ["yangihayot", "янгихаёт"], "line": "Sergeli", "lat": 41.2106, "lon": 69.2222, "district": "Yangihayot"},
    {"name": "Qipchoq", "name_ru": "Кипчак", "aliases": ["qipchoq", "кипчак"], "line": "Sergeli", "lat": 41.2003, "lon": 69.2164, "district": "Yangihayot"},
]

TASHKENT_DISTRICTS: Dict[str, Dict[str, Any]] = {
    "Chilonzor": {
        "name_uz": "Chilonzor",
        "name_ru": "Чиланзар",
        "name_en": "Chilanzar",
        "center_lat": 41.2780,
        "center_lon": 69.2120,
        "overall_score": 9.3,
        "scores": {
            "metro": 9.8,
            "transport": 9.5,
            "markets": 9.2,
            "education": 9.0,
            "parks": 9.4,
            "healthcare": 8.9,
            "safety": 9.2,
        },
        "description_uz": "Toshkentning eng qulay va ko‘kalamzor tumanlaridan biri. Metro liniyasi zich joylashgan, talabalar va oilalar uchun arzon hamda qulay ijaralar ko‘p.",
        "description_ru": "Один из самых удобных и зеленых районов Ташкента с развитой линией метро. Очень популярен среди студентов и семей.",
        "highlights_uz": ["Milliy bog‘", "Gagarin ko‘chasi", "Chilonzor Buyum Bozori", "Toshkent Davlat Iqtisodiyot Universiteti filiallari"],
        "price_tier": "Hamyonbop (Affordable)",
        "avg_rent_1room_uzs": 3800000,
        "avg_rent_2room_uzs": 5200000,
        "avg_rent_3room_uzs": 6800000,
    },
    "Yunusobod": {
        "name_uz": "Yunusobod",
        "name_ru": "Юнусабад",
        "name_en": "Yunusabad",
        "center_lat": 41.3530,
        "center_lon": 69.2870,
        "overall_score": 9.5,
        "scores": {
            "metro": 9.6,
            "transport": 9.4,
            "markets": 9.7,
            "education": 9.1,
            "parks": 9.3,
            "healthcare": 9.2,
            "safety": 9.4,
        },
        "description_uz": "Zamonaviy infratuzilma, ko‘plab savdo markazlari va toza havo. Yunusobod bozori, Teleminora va Akvapark shu yerda joylashgan.",
        "description_ru": "Современный спальный и деловой район с отличной экологией, рынком Юнусабад, Телебашней и Аквапарком.",
        "highlights_uz": ["Toshkent Teleminorasi", "Yunusobod Bozori", "Mega Planet", "Akvapark"],
        "price_tier": "O‘rta-Yuqori (Mid-High)",
        "avg_rent_1room_uzs": 4200000,
        "avg_rent_2room_uzs": 5800000,
        "avg_rent_3room_uzs": 7500000,
    },
    "Mirzo Ulug‘bek": {
        "name_uz": "Mirzo Ulug‘bek",
        "name_ru": "Мирзо-Улугбекский",
        "name_en": "Mirzo Ulugbek",
        "center_lat": 41.3280,
        "center_lon": 69.3250,
        "overall_score": 9.4,
        "scores": {
            "metro": 9.2,
            "transport": 9.3,
            "markets": 9.1,
            "education": 9.8,
            "parks": 9.6,
            "healthcare": 9.3,
            "safety": 9.5,
        },
        "description_uz": "Akademik va intellektual tuman. Ko‘plab institutlar, xalqaro universitetlar (INHA, Westminster) va Ecopark joylashgan.",
        "description_ru": "Интеллектуальный и престижный район. Множество НИИ, вузов (INHA, Westminster, МГУ) и знаменитый Экопарк.",
        "highlights_uz": ["Ecopark", "Markaziy bog‘", "Inha Universiteti", "Buyuk Ipak Yo‘li savdo do‘konlari"],
        "price_tier": "Yuqori (Premium)",
        "avg_rent_1room_uzs": 4500000,
        "avg_rent_2room_uzs": 6500000,
        "avg_rent_3room_uzs": 8500000,
    },
    "Yakkasaroy": {
        "name_uz": "Yakkasaroy",
        "name_ru": "Яккасарайский",
        "name_en": "Yakkasaray",
        "center_lat": 41.2850,
        "center_lon": 69.2550,
        "overall_score": 9.3,
        "scores": {
            "metro": 8.8,
            "transport": 9.4,
            "markets": 9.0,
            "education": 9.2,
            "parks": 9.5,
            "healthcare": 9.3,
            "safety": 9.6,
        },
        "description_uz": "Tinch, elita va diplomatik tuman. Shota Rustaveli ko‘chasi, qahvaxonalar, elchixonalar va aeroportga yaqinlik.",
        "description_ru": "Престижный и дипломатический район с европейской атмосферой вдоль улицы Шота Руставели.",
        "highlights_uz": ["Shota Rustaveli ko‘chasi", "Grand Mir mehmonxonasi", "Glinka ko‘chasi", "Babur bog‘i"],
        "price_tier": "Yuqori (Premium)",
        "avg_rent_1room_uzs": 4600000,
        "avg_rent_2room_uzs": 6700000,
        "avg_rent_3room_uzs": 8900000,
    },
    "Mirobod": {
        "name_uz": "Mirobod",
        "name_ru": "Мирабадский",
        "name_en": "Mirabad",
        "center_lat": 41.2980,
        "center_lon": 69.2780,
        "overall_score": 9.6,
        "scores": {
            "metro": 9.7,
            "transport": 9.7,
            "markets": 9.5,
            "education": 9.4,
            "parks": 9.3,
            "healthcare": 9.5,
            "safety": 9.7,
        },
        "description_uz": "Poytaxtning ishbilarmon va moliyaviy markazi. Biznes markazlar, restoranlar va Toshkent Markaziy Temiryo‘l vokzali.",
        "description_ru": "Деловой и финансовый эпицентр города. Рестораны, бутики, банки и бизнес-центры мирового уровня.",
        "highlights_uz": ["Oybek metro", "Gospitalny Bozori (Mirobod)", "Shevchenko gastronomik ko‘chasi", "Shimoliy Vokzal"],
        "price_tier": "Elita (Luxury)",
        "avg_rent_1room_uzs": 5200000,
        "avg_rent_2room_uzs": 7800000,
        "avg_rent_3room_uzs": 10500000,
    },
    "Shayxontohur": {
        "name_uz": "Shayxontohur",
        "name_ru": "Шайхантахурский",
        "name_en": "Shaykhantakhur",
        "center_lat": 41.3200,
        "center_lon": 69.2450,
        "overall_score": 9.2,
        "scores": {
            "metro": 9.5,
            "transport": 9.3,
            "markets": 9.8,
            "education": 8.9,
            "parks": 9.0,
            "healthcare": 9.1,
            "safety": 9.1,
        },
        "description_uz": "Toshkentning tarixiy yuragi va zamonaviy Tashkent City loyihasini o‘zida birlashtirgan markaziy tuman.",
        "description_ru": "Историческое сердце Ташкента вместе с ультрасовременным проектом Tashkent City и рынком Чорсу.",
        "highlights_uz": ["Tashkent City Park", "Chorsu bozori", "Xadra maydoni", "Navoiy teatri yon-atrofi"],
        "price_tier": "O‘rta-Yuqori (Mid-High)",
        "avg_rent_1room_uzs": 4400000,
        "avg_rent_2room_uzs": 6300000,
        "avg_rent_3room_uzs": 8400000,
    },
    "Olmazor": {
        "name_uz": "Olmazor",
        "name_ru": "Алмазарский",
        "name_en": "Almazar",
        "center_lat": 41.3450,
        "center_lon": 69.2150,
        "overall_score": 8.9,
        "scores": {
            "metro": 9.0,
            "transport": 8.9,
            "markets": 9.3,
            "education": 9.8,
            "parks": 8.5,
            "healthcare": 8.8,
            "safety": 9.0,
        },
        "description_uz": "Talabalar shaharchasi markazi. O‘zbekiston Milliy Universiteti, Toshkent Davlat Texnika Universiteti va Turin universiteti shu yerda.",
        "description_ru": "Главный студенческий городок столицы (Вузгородок). Идеален для студентов и преподавателей.",
        "highlights_uz": ["Vuzgorodok (Talabalar shaharchasi)", "O‘zMU", "TATU", "Beruniy metro"],
        "price_tier": "Hamyonbop (Affordable)",
        "avg_rent_1room_uzs": 3600000,
        "avg_rent_2room_uzs": 4900000,
        "avg_rent_3room_uzs": 6400000,
    },
    "Uchtepa": {
        "name_uz": "Uchtepa",
        "name_ru": "Учтепинский",
        "name_en": "Uchtepa",
        "center_lat": 41.2900,
        "center_lon": 69.1750,
        "overall_score": 8.5,
        "scores": {
            "metro": 7.5,
            "transport": 8.6,
            "markets": 9.1,
            "education": 8.5,
            "parks": 8.8,
            "healthcare": 8.6,
            "safety": 9.0,
        },
        "description_uz": "Tinch va osoyishta yashash massivlari, Chilonzor metro stansiyalariga 10-15 daqiqa avtobus qatnovi bilan bog‘langan.",
        "description_ru": "Тихий спальный район с развитыми кварталами, зелеными дворами и доступными ценами на аренду.",
        "highlights_uz": ["O‘rikzor Bozori", "Farhod Bozori", "Lutfiy ko‘chasi", "Eko bog‘lar"],
        "price_tier": "Hamyonbop (Affordable)",
        "avg_rent_1room_uzs": 3400000,
        "avg_rent_2room_uzs": 4600000,
        "avg_rent_3room_uzs": 5900000,
    },
    "Yashnobod": {
        "name_uz": "Yashnobod",
        "name_ru": "Яшнабадский",
        "name_en": "Yashnabad",
        "center_lat": 41.2950,
        "center_lon": 69.3400,
        "overall_score": 8.8,
        "scores": {
            "metro": 9.1,
            "transport": 8.9,
            "markets": 8.8,
            "education": 8.6,
            "parks": 8.7,
            "healthcare": 8.8,
            "safety": 9.0,
        },
        "description_uz": "Katta tezlikda rivojlanayotgan tuman. Yerusti halqa metro liniyasi, yangi qad ko‘targan ko‘p qavatli massivlar va bog‘lar.",
        "description_ru": "Быстро развивающийся район с наземным кольцевым метро и множеством современных жилых комплексов.",
        "highlights_uz": ["Do‘stlik Bog‘i", "Kadisheva bozori", "Parkent ko‘chasi", "Aeroport yo‘li"],
        "price_tier": "O‘rta (Mid)",
        "avg_rent_1room_uzs": 3700000,
        "avg_rent_2room_uzs": 5100000,
        "avg_rent_3room_uzs": 6600000,
    },
    "Sergeli": {
        "name_uz": "Sergeli",
        "name_ru": "Сергелийский",
        "name_en": "Sergeli",
        "center_lat": 41.2250,
        "center_lon": 69.2200,
        "overall_score": 8.7,
        "scores": {
            "metro": 9.4,
            "transport": 8.8,
            "markets": 9.3,
            "education": 8.4,
            "parks": 8.5,
            "healthcare": 8.6,
            "safety": 9.0,
        },
        "description_uz": "Yangi qurilgan zamonaviy binolar, keng ko‘chalar va to‘g‘ridan-to‘g‘ri metro qatnovi. Yangi oilalar uchun juda qulay.",
        "description_ru": "Район новостроек с собственной веткой метро, широкими проспектами и доступными ценами на свежее жилье.",
        "highlights_uz": ["Sergeli avtomobil bozori", "Sergeli Park", "Yangi ko‘p qavatli uylar", "Sergeli metrosi"],
        "price_tier": "Hamyonbop (Affordable)",
        "avg_rent_1room_uzs": 3200000,
        "avg_rent_2room_uzs": 4400000,
        "avg_rent_3room_uzs": 5800000,
    },
    "Yangihayot": {
        "name_uz": "Yangihayot",
        "name_ru": "Янгихаётский",
        "name_en": "Yangikhayot",
        "center_lat": 41.2050,
        "center_lon": 69.2150,
        "overall_score": 8.2,
        "scores": {
            "metro": 9.2,
            "transport": 8.3,
            "markets": 8.5,
            "education": 8.0,
            "parks": 8.0,
            "healthcare": 8.0,
            "safety": 8.8,
        },
        "description_uz": "Toshkentning eng yangi tumani. Yangi infratuzilma, arzon ijara narxlari va tezkor metro liniyasi.",
        "description_ru": "Самый молодой район Ташкента. Новая застройка, низкие цены на аренду и прямое метро.",
        "highlights_uz": ["Qipchoq bekati", "Yangi yashash massivlari", "Yangi maktablar"],
        "price_tier": "Hamyonbop (Affordable)",
        "avg_rent_1room_uzs": 2900000,
        "avg_rent_2room_uzs": 4000000,
        "avg_rent_3room_uzs": 5200000,
    },
    "Bektemir": {
        "name_uz": "Bektemir",
        "name_ru": "Бектемирский",
        "name_en": "Bektemir",
        "center_lat": 41.2300,
        "center_lon": 69.3300,
        "overall_score": 7.9,
        "scores": {
            "metro": 7.2,
            "transport": 8.2,
            "markets": 9.0,
            "education": 7.6,
            "parks": 7.8,
            "healthcare": 7.7,
            "safety": 8.8,
        },
        "description_uz": "Qo‘yliq ulgurji bozoriga va Ohangaron trassasiga yaqin tuman. Sanoat va tinch mahallalar uyg‘unligi.",
        "description_ru": "Район рядом с рынком Куйлюк. Спокойные микрорайоны и самые доступные цены в городе.",
        "highlights_uz": ["Qo‘yliq bozori", "Compass savdo markazi", "Chirchiq daryosi qirg‘og‘i"],
        "price_tier": "Eng hamyonbop (Budget)",
        "avg_rent_1room_uzs": 2700000,
        "avg_rent_2room_uzs": 3800000,
        "avg_rent_3room_uzs": 4900000,
    },
}


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """Calculate Great Circle distance between two coordinates in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return int(R * c)


class NeighborhoodService:
    """Provides district intelligence, metro proximity, and infrastructure evaluation."""

    def get_all_districts(self) -> List[Dict[str, Any]]:
        """Return all 12 Tashkent districts with scores and highlights."""
        return [
            {"id": key, **val}
            for key, val in TASHKENT_DISTRICTS.items()
        ]

    def get_district_details(self, district_name: str) -> Optional[Dict[str, Any]]:
        """Find matching district profile by Uzbek, Russian or English query."""
        if not district_name:
            return None
        q = district_name.strip().lower()
        for key, info in TASHKENT_DISTRICTS.items():
            if (
                key.lower() in q
                or q in key.lower()
                or q in info["name_ru"].lower()
                or q in info["name_en"].lower()
            ):
                return {"id": key, **info}
        return None

    def find_nearest_metro(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Calculate the nearest metro station to a given GPS coordinate."""
        if not lat or not lon:
            return None

        best_station = None
        min_dist = float("inf")

        for station in TASHKENT_METRO_STATIONS:
            dist = haversine_distance_meters(lat, lon, station["lat"], station["lon"])
            if dist < min_dist:
                min_dist = dist
                best_station = station

        if best_station:
            # Estimate walking time (approx 80m per minute)
            walk_minutes = max(1, int(min_dist / 80))
            return {
                "name": best_station["name"],
                "line": best_station["line"],
                "distance_m": min_dist,
                "walk_minutes": walk_minutes,
                "district": best_station["district"],
            }
        return None

    def get_district_coordinates(self, district_name: Optional[str]) -> tuple[float, float]:
        """Return center coordinates for a district, defaulting to central Tashkent."""
        if district_name:
            details = self.get_district_details(district_name)
            if details:
                return details["center_lat"], details["center_lon"]
        return 41.311081, 69.240562  # Central Tashkent (Amir Temur)


neighborhood_service = NeighborhoodService()
