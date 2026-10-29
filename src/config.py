"""Application configuration using Pydantic Settings."""

from typing import List, Union, Optional, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for the Joyliy Telegram Bot & Monitor."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot
    BOT_TOKEN: str = Field(
        default="mock_token_for_testing",
        description="Telegram bot token obtained from @BotFather",
    )
    BOT_USERNAME: str = Field(
        default="joyliy_bot",
        description="Telegram bot username without @",
    )
    ADMIN_IDS: Any = Field(
        default_factory=list,
        description="Telegram user IDs with administrative privileges",
    )
    CHANNEL_ID: Optional[str] = Field(
        default=None,
        description="Telegram channel username (e.g. @joyliy_channel) or numeric ID (-100...)",
    )
    WEBSITE_URL: str = Field(
        default="http://localhost:3000",
        description="Public URL of Joyliy frontend website",
    )
    JWT_SECRET: str = Field(
        default="joyliy-super-secret-jwt-key-2026",
        description="Secret key for signing auth tokens",
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./uyda.db",
        description="Async SQLAlchemy database URL (e.g. postgresql+asyncpg://... or sqlite+aiosqlite://...)",
    )
    DB_ECHO: bool = Field(default=False, description="Enable SQLAlchemy engine query logging")

    # Monitor & Provider Settings
    POLL_INTERVAL_SECONDS: int = Field(
        default=600,
        ge=60,
        description="Polling interval in seconds between monitor checks (min 60s)",
    )
    OLX_SEARCH_URLS: Any = Field(
        default_factory=lambda: [
            "https://www.olx.uz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/"
        ],
        description="Target search URLs to monitor on OLX Uzbekistan",
    )
    PROVIDER_TYPE: str = Field(
        default="auto",
        description="Collector provider: 'auto', 'olx_http', 'fixture', or 'feed'",
    )
    MAX_RETRIES: int = Field(default=3, description="Max retries for HTTP requests")
    REQUEST_DELAY_SECONDS: float = Field(
        default=2.0,
        description="Polite delay between consecutive external HTTP requests",
    )
    USD_TO_UZS_RATE: float = Field(
        default=12800.0,
        description="Reference exchange rate used when apartment price is quoted in USD",
    )

    # Web & REST API Integration
    HOST: str = Field(default="0.0.0.0", description="API host")
    PORT: int = Field(default=8000, description="API port")
    API_KEY: str = Field(
        default="uyda-platform-secret-key-change-in-production",
        description="Secret API key for authenticating internal/admin API endpoints",
    )

    # Rate Limiting & Notifications
    MAX_NOTIFICATIONS_PER_SECOND: float = Field(
        default=25.0,
        description="Conservative Telegram broadcast rate limit",
    )
    BATCH_SIZE: int = Field(default=10, description="Max batch size for sending notifications")
    QUIET_HOURS_DEFAULT_START: str = "23:00"
    QUIET_HOURS_DEFAULT_END: str = "08:00"

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Any) -> List[int]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return [int(x) for x in json.loads(v)]
                except Exception:
                    pass
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, list):
            return [int(x) for x in v if str(x).strip()]
        return []

    @field_validator("OLX_SEARCH_URLS", mode="before")
    @classmethod
    def parse_search_urls(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return [str(x) for x in json.loads(v)]
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        if isinstance(v, list):
            return [str(x) for x in v if str(x).strip()]
        return []


settings = Settings()

