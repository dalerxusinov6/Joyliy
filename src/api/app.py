"""FastAPI application factory and middleware configuration."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.routes import api_router
from src.api.admin_routes import admin_router
from src.database import init_db, get_db_session, AsyncSessionLocal
from src.services.seo_service import seo_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database initialization."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI instance for web and integration services."""
    app = FastAPI(
        title="Joyliy Apartment Rental Integration API",
        version="1.0.0",
        description="Integration API for discovered rental apartment listings in Tashkent, Uzbekistan.",
        lifespan=lifespan,
    )

    # Enable CORS for web frontend (e.g. Joyliy landing page or admin dashboards)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    app.include_router(admin_router)

    # Mount modern compiled Nuxt frontend (frontend_dist) if available
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    frontend_dist = os.path.join(base_dir, "frontend_dist")
    frontend_public = os.path.join(base_dir, "frontend", ".output", "public")
    frontend_raw_public = os.path.join(base_dir, "frontend", "public")

    def _find_static_file(filename: str):
        for candidate_dir in [frontend_dist, frontend_public, frontend_raw_public]:
            fpath = os.path.join(candidate_dir, filename)
            if os.path.exists(fpath):
                return fpath
        return None

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon_ico():
        p = _find_static_file("favicon.ico")
        if p:
            return FileResponse(p, media_type="image/x-icon")
        return Response(status_code=404)

    @app.get("/favicon.svg", include_in_schema=False)
    async def favicon_svg():
        p = _find_static_file("favicon.svg")
        if p:
            return FileResponse(p, media_type="image/svg+xml")
        return Response(status_code=404)

    @app.get("/favicon-32x32.png", include_in_schema=False)
    async def favicon_32():
        p = _find_static_file("favicon-32x32.png")
        if p:
            return FileResponse(p, media_type="image/png")
        return Response(status_code=404)

    @app.get("/favicon-16x16.png", include_in_schema=False)
    async def favicon_16():
        p = _find_static_file("favicon-16x16.png")
        if p:
            return FileResponse(p, media_type="image/png")
        return Response(status_code=404)

    @app.get("/apple-touch-icon.png", include_in_schema=False)
    async def apple_touch_icon():
        p = _find_static_file("apple-touch-icon.png")
        if p:
            return FileResponse(p, media_type="image/png")
        return Response(status_code=404)

    # --- Technical SEO & XML Sitemaps Endpoints ---
    @app.get("/robots.txt", include_in_schema=False)
    async def robots_txt():
        p = _find_static_file("robots.txt")
        if p:
            return FileResponse(p, media_type="text/plain; charset=utf-8")
        return Response(
            content=(
                "User-agent: *\n"
                "Allow: /\n"
                "Allow: /elon/\n"
                "Allow: /toshkent/\n"
                "Disallow: /admin/\n"
                "Disallow: /api/\n"
                "Disallow: /*?*token=*\n"
                "Disallow: /*?*auth=*\n"
                "Disallow: /_nuxt/\n\n"
                "Sitemap: https://joyliy.uz/sitemap.xml\n"
                "Sitemap: https://joyliy.uz/sitemap-listings.xml\n"
                "Sitemap: https://joyliy.uz/sitemap-locations.xml\n"
                "Sitemap: https://joyliy.uz/sitemap-categories.xml\n"
                "Sitemap: https://joyliy.uz/sitemap-pages.xml\n"
            ),
            media_type="text/plain; charset=utf-8",
        )

    @app.get("/sitemap.xml", include_in_schema=False)
    async def sitemap_index():
        content = seo_service.generate_sitemap_index()
        return Response(content=content, media_type="application/xml; charset=utf-8")

    @app.get("/sitemap-pages.xml", include_in_schema=False)
    async def sitemap_pages():
        content = seo_service.generate_pages_sitemap()
        return Response(content=content, media_type="application/xml; charset=utf-8")

    @app.get("/sitemap-locations.xml", include_in_schema=False)
    async def sitemap_locations():
        content = seo_service.generate_locations_sitemap()
        return Response(content=content, media_type="application/xml; charset=utf-8")

    @app.get("/sitemap-categories.xml", include_in_schema=False)
    async def sitemap_categories():
        content = seo_service.generate_categories_sitemap()
        return Response(content=content, media_type="application/xml; charset=utf-8")

    @app.get("/sitemap-listings.xml", include_in_schema=False)
    async def sitemap_listings(session: AsyncSession = Depends(get_db_session)):
        content = await seo_service.generate_listings_sitemap(session)
        return Response(content=content, media_type="application/xml; charset=utf-8")

    from fastapi.staticfiles import StaticFiles

    upload_dir = os.path.join(base_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

    static_dir = None
    if os.path.exists(frontend_dist) and os.path.exists(os.path.join(frontend_dist, "index.html")):
        static_dir = frontend_dist
    elif os.path.exists(frontend_public) and os.path.exists(os.path.join(frontend_public, "index.html")):
        static_dir = frontend_public

    if static_dir:
        @app.get("/admin", include_in_schema=False)
        @app.get("/admin/{subpath:path}", include_in_schema=False)
        async def serve_admin_spa(subpath: str = ""):
            # Check direct file or HTML in static_dir
            candidates = [
                os.path.join(static_dir, "admin", subpath),
                os.path.join(static_dir, "admin", f"{subpath}.html"),
                os.path.join(static_dir, "admin", subpath, "index.html"),
                os.path.join(static_dir, "admin", "index.html"),
                os.path.join(static_dir, "200.html"),
                os.path.join(static_dir, "index.html"),
            ]
            for c in candidates:
                if os.path.exists(c) and not os.path.isdir(c):
                    return FileResponse(c)
            return Response(status_code=404)

        @app.get("/elon/{listing_id}", include_in_schema=False)
        async def serve_elon_page(listing_id: str):
            candidates = [
                os.path.join(static_dir, "elon", f"{listing_id}.html"),
                os.path.join(static_dir, "elon", listing_id, "index.html"),
                os.path.join(static_dir, "200.html"),
                os.path.join(static_dir, "index.html"),
            ]
            for c in candidates:
                if os.path.exists(c) and not os.path.isdir(c):
                    return FileResponse(c)
            return Response(status_code=404)

        @app.get("/toshkent", include_in_schema=False)
        @app.get("/toshkent/{subpath:path}", include_in_schema=False)
        async def serve_toshkent_pages(subpath: str = ""):
            clean_sub = subpath.strip("/")
            candidates = [
                os.path.join(static_dir, "toshkent", clean_sub, "index.html") if clean_sub else "",
                os.path.join(static_dir, "toshkent", f"{clean_sub}.html") if clean_sub else "",
                os.path.join(static_dir, "toshkent", "index.html"),
                os.path.join(static_dir, "200.html"),
                os.path.join(static_dir, "index.html"),
            ]
            for c in candidates:
                if c and os.path.exists(c) and not os.path.isdir(c):
                    return FileResponse(c)
            return Response(status_code=404)

        app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    else:
        @app.get("/", response_class=HTMLResponse)
        async def serve_index():
            html_file = os.path.join(base_dir, "Joyliy — Toshkentda maklersiz ijara.html")
            if not os.path.exists(html_file):
                html_file = os.path.join(base_dir, "Uyda — Toshkentda maklersiz ijara.html")
            if os.path.exists(html_file):
                return FileResponse(html_file, media_type="text/html")
            return HTMLResponse("<h1>Joyliy Apartment Rental Platform</h1>")

    return app


app = create_app()

