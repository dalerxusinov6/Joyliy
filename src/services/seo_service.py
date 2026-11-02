"""Enterprise SEO & XML Sitemap Service for Joyliy.uz."""

from __future__ import annotations

import os
import xml.sax.saxutils as xml_escape
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing

BASE_URL = "https://joyliy.uz"

# Tashkent District Metadata with exact transliteration, canonical slugs, and DB aliases
DISTRICT_METADATA = [
    {
        "slug": "chilonzor",
        "name_uz": "Chilonzor",
        "name_ru": "Чиланзар",
        "db_names": ["Chilonzor", "Чиланзар"],
        "priority": 0.8,
    },
    {
        "slug": "yunusobod",
        "name_uz": "Yunusobod",
        "name_ru": "Юнусабад",
        "db_names": ["Yunusobod", "Юнусабад"],
        "priority": 0.8,
    },
    {
        "slug": "mirzo-ulugbek",
        "name_uz": "Mirzo Ulug‘bek",
        "name_ru": "Мирзо-Улугбек",
        "db_names": ["Mirzo Ulug‘bek", "Mirzo Ulug'bek", "Mirzo Ulugbek", "Мирзо-Улугбек"],
        "priority": 0.8,
    },
    {
        "slug": "yakkasaroy",
        "name_uz": "Yakkasaroy",
        "name_ru": "Яккасарай",
        "db_names": ["Yakkasaroy", "Яккасарай"],
        "priority": 0.8,
    },
    {
        "slug": "mirobod",
        "name_uz": "Mirobod",
        "name_ru": "Мирабад",
        "db_names": ["Mirobod", "Мирабад"],
        "priority": 0.8,
    },
    {
        "slug": "shayxontohur",
        "name_uz": "Shayxontohur",
        "name_ru": "Шайхантахур",
        "db_names": ["Shayxontohur", "Шайхантахур"],
        "priority": 0.8,
    },
    {
        "slug": "olmazor",
        "name_uz": "Olmazor",
        "name_ru": "Алмазар",
        "db_names": ["Olmazor", "Алмазар"],
        "priority": 0.8,
    },
    {
        "slug": "uchtepa",
        "name_uz": "Uchtepa",
        "name_ru": "Учтепа",
        "db_names": ["Uchtepa", "Учтепа"],
        "priority": 0.8,
    },
    {
        "slug": "sergeli",
        "name_uz": "Sergeli",
        "name_ru": "Сергели",
        "db_names": ["Sergeli", "Сергели"],
        "priority": 0.8,
    },
    {
        "slug": "yashnobod",
        "name_uz": "Yashnobod",
        "name_ru": "Яшнабад",
        "db_names": ["Yashnobod", "Яшнабад"],
        "priority": 0.8,
    },
    {
        "slug": "bektemir",
        "name_uz": "Bektemir",
        "name_ru": "Бектемир",
        "db_names": ["Bektemir", "Бектемир"],
        "priority": 0.8,
    },
    {
        "slug": "yangihayot",
        "name_uz": "Yangi Hayot",
        "name_ru": "Янгихаёт",
        "db_names": ["Yangi Hayot", "Yangihayot", "Янгихаёт"],
        "priority": 0.8,
    },
]

ROOM_CATEGORIES = [
    {"rooms": 1, "slug": "1-xonali-kvartiralar", "name_uz": "1 xonali kvartiralar", "name_ru": "1-комнатные квартиры"},
    {"rooms": 2, "slug": "2-xonali-kvartiralar", "name_uz": "2 xonali kvartiralar", "name_ru": "2-комнатные квартиры"},
    {"rooms": 3, "slug": "3-xonali-kvartiralar", "name_uz": "3 xonali kvartiralar", "name_ru": "3-комнатные квартиры"},
    {"rooms": 4, "slug": "4-xonali-kvartiralar", "name_uz": "4 xonali kvartiralar", "name_ru": "4-комнатные квартиры"},
]


def escape_xml(val: Any) -> str:
    """Safely escape text for XML sitemaps."""
    if val is None:
        return ""
    return xml_escape.escape(str(val))


class SeoService:
    """Manages dynamic sitemaps, structured data generation, and technical SEO metrics."""

    @staticmethod
    def get_district_info(slug: str) -> Optional[Dict[str, Any]]:
        """Find district metadata by canonical URL slug."""
        normalized = slug.lower().strip()
        for d in DISTRICT_METADATA:
            if d["slug"] == normalized:
                return d
        return None

    @staticmethod
    def get_now_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def generate_sitemap_index(self) -> str:
        """Produce the master sitemapindex document referencing specialized sitemaps."""
        now = self.get_now_iso()
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{BASE_URL}/sitemap-pages.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
  <sitemap>
    <loc>{BASE_URL}/sitemap-locations.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
  <sitemap>
    <loc>{BASE_URL}/sitemap-categories.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
  <sitemap>
    <loc>{BASE_URL}/sitemap-listings.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
</sitemapindex>"""

    def generate_pages_sitemap(self) -> str:
        """Produce sitemap for core evergreen static and intent landing pages."""
        now = self.get_now_iso()
        pages = [
            {"loc": f"{BASE_URL}/", "changefreq": "daily", "priority": "1.0"},
            {"loc": f"{BASE_URL}/toshkent", "changefreq": "daily", "priority": "0.9"},
            {"loc": f"{BASE_URL}/toshkent/arzon-kvartiralar", "changefreq": "daily", "priority": "0.85"},
            {"loc": f"{BASE_URL}/toshkent/sotiladigan-uylar", "changefreq": "daily", "priority": "0.85"},
            {"loc": f"{BASE_URL}/toshkent/ijaraga-kvartiralar", "changefreq": "daily", "priority": "0.85"},
        ]

        url_tags = []
        for p in pages:
            url_tags.append(f"""  <url>
    <loc>{p['loc']}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>{p['changefreq']}</changefreq>
    <priority>{p['priority']}</priority>
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(url_tags)}
</urlset>"""

    def generate_locations_sitemap(self) -> str:
        """Produce sitemap for all 12 Tashkent district landing pages."""
        now = self.get_now_iso()
        url_tags = []
        for d in DISTRICT_METADATA:
            url_tags.append(f"""  <url>
    <loc>{BASE_URL}/toshkent/{d['slug']}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{d['priority']}</priority>
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(url_tags)}
</urlset>"""

    def generate_categories_sitemap(self) -> str:
        """Produce sitemap for rooms and district category pages."""
        now = self.get_now_iso()
        url_tags = []

        # Room count pages
        for r in ROOM_CATEGORIES:
            url_tags.append(f"""  <url>
    <loc>{BASE_URL}/toshkent/{r['slug']}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>""")

        # District + kvartiralar pages
        for d in DISTRICT_METADATA:
            url_tags.append(f"""  <url>
    <loc>{BASE_URL}/toshkent/{d['slug']}/kvartiralar</loc>
    <lastmod>{now}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.75</priority>
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(url_tags)}
</urlset>"""

    async def generate_listings_sitemap(self, session: AsyncSession) -> str:
        """Produce sitemap containing all active listings with Google Images metadata."""
        query = (
            select(Listing)
            .where(Listing.is_active == True)
            .order_by(Listing.id.desc())
        )
        result = await session.execute(query)
        listings = result.scalars().all()

        url_tags = []
        for l in listings:
            lastmod = (l.last_seen_at or l.first_seen_at or datetime.now(timezone.utc)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            image_tags = ""
            if l.image_urls and isinstance(l.image_urls, list) and len(l.image_urls) > 0:
                first_img = escape_xml(l.image_urls[0])
                img_title = escape_xml(l.title)
                image_tags = f"""
    <image:image>
      <image:loc>{first_img}</image:loc>
      <image:title>{img_title}</image:title>
    </image:image>"""

            url_tags.append(f"""  <url>
    <loc>{BASE_URL}/elon/{l.id}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>{image_tags}
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(url_tags)}
</urlset>"""

    async def get_seo_audit_summary(self, session: AsyncSession) -> Dict[str, Any]:
        """Calculate real-time technical SEO health metrics across the database."""
        total_active = await session.scalar(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        ) or 0

        with_images = await session.scalar(
            select(func.count(Listing.id)).where(
                and_(Listing.is_active == True, Listing.image_urls != "[]", Listing.image_urls != None)
            )
        ) or 0

        with_price = await session.scalar(
            select(func.count(Listing.id)).where(
                and_(Listing.is_active == True, Listing.price_uzs > 0)
            )
        ) or 0

        with_district = await session.scalar(
            select(func.count(Listing.id)).where(
                and_(Listing.is_active == True, Listing.district != None, Listing.district != "")
            )
        ) or 0

        with_rooms = await session.scalar(
            select(func.count(Listing.id)).where(
                and_(Listing.is_active == True, Listing.rooms > 0)
            )
        ) or 0

        locations_count = len(DISTRICT_METADATA)
        categories_count = len(ROOM_CATEGORIES) + len(DISTRICT_METADATA)
        static_pages_count = 5
        total_indexable_urls = total_active + locations_count + categories_count + static_pages_count

        health_score = 100
        issues = []

        if total_active == 0:
            health_score -= 50
            issues.append("Bazada faol e'lonlar mavjud emas")
        else:
            missing_images_pct = ((total_active - with_images) / total_active) * 100
            if missing_images_pct > 20:
                health_score -= 10
                issues.append(f"{total_active - with_images} ta e'londa fotosurat yo'q")

            missing_district_pct = ((total_active - with_district) / total_active) * 100
            if missing_district_pct > 5:
                health_score -= 10
                issues.append(f"{total_active - with_district} ta e'londa tuman belgilanmagan")

        return {
            "health_score": max(0, health_score),
            "total_active_listings": total_active,
            "total_indexable_urls": total_indexable_urls,
            "listings_with_images": with_images,
            "listings_with_price": with_price,
            "listings_with_district": with_district,
            "listings_with_rooms": with_rooms,
            "district_landing_pages": locations_count,
            "category_landing_pages": categories_count,
            "static_pages": static_pages_count,
            "issues": issues,
            "sitemaps": [
                {"name": "sitemap.xml (Index)", "url": f"{BASE_URL}/sitemap.xml", "type": "index"},
                {"name": "sitemap-pages.xml", "url": f"{BASE_URL}/sitemap-pages.xml", "count": static_pages_count},
                {"name": "sitemap-locations.xml", "url": f"{BASE_URL}/sitemap-locations.xml", "count": locations_count},
                {"name": "sitemap-categories.xml", "url": f"{BASE_URL}/sitemap-categories.xml", "count": categories_count},
                {"name": "sitemap-listings.xml", "url": f"{BASE_URL}/sitemap-listings.xml", "count": total_active},
            ],
            "robots_txt": {
                "url": f"{BASE_URL}/robots.txt",
                "status": "active",
                "sitemaps_declared": 5,
            },
        }

    async def sync_static_sitemaps(self, output_dir: str, session: AsyncSession) -> Dict[str, Any]:
        """Save static copies of all sitemaps into frontend/public or frontend_dist."""
        os.makedirs(output_dir, exist_ok=True)

        idx_xml = self.generate_sitemap_index()
        with open(os.path.join(output_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(idx_xml)

        pages_xml = self.generate_pages_sitemap()
        with open(os.path.join(output_dir, "sitemap-pages.xml"), "w", encoding="utf-8") as f:
            f.write(pages_xml)

        locations_xml = self.generate_locations_sitemap()
        with open(os.path.join(output_dir, "sitemap-locations.xml"), "w", encoding="utf-8") as f:
            f.write(locations_xml)

        cat_xml = self.generate_categories_sitemap()
        with open(os.path.join(output_dir, "sitemap-categories.xml"), "w", encoding="utf-8") as f:
            f.write(cat_xml)

        listings_xml = await self.generate_listings_sitemap(session)
        with open(os.path.join(output_dir, "sitemap-listings.xml"), "w", encoding="utf-8") as f:
            f.write(listings_xml)

        return {
            "success": True,
            "files_generated": [
                "sitemap.xml",
                "sitemap-pages.xml",
                "sitemap-locations.xml",
                "sitemap-categories.xml",
                "sitemap-listings.xml",
            ],
            "output_dir": output_dir,
        }


seo_service = SeoService()
