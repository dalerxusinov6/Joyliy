"""FastAPI application factory and middleware configuration."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from src.api.routes import api_router
from src.database import init_db


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

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        html_file = os.path.join(base_dir, "Joyliy — Toshkentda maklersiz ijara.html")
        if not os.path.exists(html_file):
            html_file = os.path.join(base_dir, "Uyda — Toshkentda maklersiz ijara.html")
        if os.path.exists(html_file):
            return FileResponse(html_file, media_type="text/html")
        return HTMLResponse("<h1>Joyliy Apartment Rental Platform</h1>")

    return app


app = create_app()

