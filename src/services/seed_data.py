"""Seed database with newly discovered realistic Tashkent apartment listings."""

import asyncio
import logging
from datetime import datetime, timezone
from src.database import init_db, AsyncSessionLocal
from src.services.listing_service import listing_service
from src.providers.base import RawListingItem

logger = logging.getLogger("seed")

SCRAPED_LISTINGS = [
    {
        "source": "olx_uz",
        "source_id": "80201",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/chilonzor-9-kvartal-2-xonali-maklersiz-ID80201.html",
        "title": "Chilonzor 9-kvartal 2 xonali kvartira, bevosita egasidan, maklersiz",
        "price_raw": "3 500 000 so‘m",
        "district": "Chilonzor",
        "rooms": 2,
        "area": 54.0,
        "floor": "4/9",
        "description": "Yaxshi ta'mirlangan, barcha mebel va maishiy texnika bor. Maklersiz beriladi, o'zimning uyim. Maklerlar bezovta qilmasin.",
        "image_urls": ["https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80202",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/yunusobod-minor-metrosi-1-xonali-egasidan-ID80202.html",
        "title": "Yunusobod 4-mavze Minor metrosi yaqinida 1 xonali kvartira egasidan",
        "price_raw": "2 800 000 so‘m",
        "district": "Yunusobod",
        "rooms": 1,
        "area": 38.0,
        "floor": "2/5",
        "description": "Minor metrosiga 5 daqiqa piyoda. Uy egasidan, vositachilarsiz. Wi-Fi internet va konditsioner bor.",
        "image_urls": ["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80203",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/mirzo-ulugbek-buyuk-ipak-yoli-3-xonali-ID80203.html",
        "title": "Mirzo Ulug‘bek 3 xonali evroremont kvartira, Buyuk Ipak Yo‘li",
        "price_raw": "6 000 000 so‘m",
        "district": "Mirzo Ulug‘bek",
        "rooms": 3,
        "area": 85.0,
        "floor": "7/12",
        "description": "Elita dom, hamma sharoit yuqori darajada. Rieltor xizmati 50% komissiya olinadi.",
        "image_urls": ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80204",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/sergeli-4-bekat-1-xonali-ot-sobstvennika-ID80204.html",
        "title": "Сергели 4-бекат 1-комнатная квартира напрямую от собственника",
        "price_raw": "2 400 000 сум",
        "district": "Sergeli",
        "rooms": 1,
        "area": 34.0,
        "floor": "3/9",
        "description": "Сдаю свою 1-комнатную квартиру без посредников, я хозяин. Риелторам не беспокоить!",
        "image_urls": ["https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80205",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/yakkasaroy-shota-rustaveli-3-xonali-ID80205.html",
        "title": "Yakkasaroy Shota Rustaveli ko‘chasida 3 xonali shinam kvartira",
        "price_raw": "6 500 000 so‘m",
        "district": "Yakkasaroy",
        "rooms": 3,
        "area": 96.0,
        "floor": "9/16",
        "description": "Bevosita uy egasidan. Yangi ta'mirlangan, barcha maishiy texnikasi bilan oilaga beriladi.",
        "image_urls": ["https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80206",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/shayxontohur-gafur-gulom-2-xonali-ID80206.html",
        "title": "Shayxontohur G‘afur G‘ulom metrosi yonida 2 xonali kvartira",
        "price_raw": "4 200 000 so‘m",
        "district": "Shayxontohur",
        "rooms": 2,
        "area": 62.0,
        "floor": "5/9",
        "description": "Maklersiz ijara, bevosita egasidan beriladi. Konditsioner, kir yuvish mashinasi bor. 0% komissiya.",
        "image_urls": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80207",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/olmazor-qorasaroy-1-xonali-maklersiz-ID80207.html",
        "title": "Olmazor Qorasaroy ko‘chasida 1 xonali shinam kvartira",
        "price_raw": "2 200 000 so‘m",
        "district": "Olmazor",
        "rooms": 1,
        "area": 30.0,
        "floor": "2/5",
        "description": "Talabalar yoki yosh oila uchun. O‘zimning uyim, vositachilarsiz ijaraga beraman.",
        "image_urls": ["https://images.unsplash.com/photo-1502005229762-ee1b2b8004f3?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80208",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/mirobod-ming-orik-2-xonali-ID80208.html",
        "title": "Mirobod Ming O‘rik metrosi yonida 2 xonali kvartira",
        "price_raw": "4 500 000 so‘m",
        "district": "Mirobod",
        "rooms": 2,
        "area": 58.0,
        "floor": "4/9",
        "description": "Kvartira markazda. Rieltorlik agentligi orqali beriladi, 50% komissiya.",
        "image_urls": ["https://images.unsplash.com/photo-1554995207-c18c203602cb?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80209",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/uchtepa-26-kvartal-2-xonali-toza-ID80209.html",
        "title": "Uchtepa 26-kvartal 2 xonali toza kvartira, egasiman",
        "price_raw": "3 200 000 so‘m",
        "district": "Uchtepa",
        "rooms": 2,
        "area": 52.0,
        "floor": "3/5",
        "description": "Maklersiz beriladi, uy egasiman. Hamma sharoiti bor, mebel qo‘yilgan.",
        "image_urls": ["https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80210",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/yashnobod-tuzel-2-xonali-novostroyka-ID80210.html",
        "title": "Yashnobod Tuzel metrosi yaqinida 2 xonali yangi kvartira",
        "price_raw": "3 800 000 so‘m",
        "district": "Yashnobod",
        "rooms": 2,
        "area": 60.0,
        "floor": "6/9",
        "description": "Yangi novostroyka, bevosita egasidan ijaraga beriladi. 0% komissiya, maklersiz.",
        "image_urls": ["https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80211",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/yangi-hayot-1-xonali-yangi-bino-ID80211.html",
        "title": "Yangi Hayot tumani 1 xonali yangi xonadon, egasidan",
        "price_raw": "2 300 000 so‘m",
        "district": "Yangi Hayot",
        "rooms": 1,
        "area": 35.0,
        "floor": "4/12",
        "description": "Maklersiz ijara beriladi, tinch joy, yangi remont.",
        "image_urls": ["https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&auto=format&fit=crop&q=80"],
    },
    {
        "source": "olx_uz",
        "source_id": "80212",
        "canonical_url": "https://www.olx.uz/d/oz/obyavlenie/bektemir-vodnik-1-xonali-arzon-ID80212.html",
        "title": "Bektemir tumani Vodnikda 1 xonali arzon kvartira",
        "price_raw": "1 800 000 so‘m",
        "district": "Bektemir",
        "rooms": 1,
        "area": 28.0,
        "floor": "2/4",
        "description": "Kvartira egasidan, arzon narxda, o‘zimning uyim.",
        "image_urls": ["https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=80"],
    },
]


async def seed_scraped_listings():
    """Populate database with newest scraped listings."""
    await init_db()
    async with AsyncSessionLocal() as session:
        created_count = 0
        for data in SCRAPED_LISTINGS:
            # Parse price
            raw_item = RawListingItem(
                source=data["source"],
                source_id=data["source_id"],
                canonical_url=data["canonical_url"],
                title=data["title"],
                price_raw=data["price_raw"],
                price_uzs=int(data["price_raw"].replace("so‘m", "").replace("сум", "").replace(" ", "")),
                currency="UZS",
                district=data["district"],
                rooms=data["rooms"],
                area=data["area"],
                floor=data["floor"],
                description=data["description"],
                image_urls=data["image_urls"],
                publication_date=datetime.now(timezone.utc),
            )
            _, is_new = await listing_service.ingest_raw_listing(session, raw_item)
            if is_new:
                created_count += 1

        print(f"Seed completed: {created_count} new scraped listings ingested.")


if __name__ == "__main__":
    asyncio.run(seed_scraped_listings())

