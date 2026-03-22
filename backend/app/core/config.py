from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "What2Do"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database — accepts any postgres URL format, normalizes for asyncpg
    DATABASE_URL: str = "postgresql+asyncpg://what2do:what2do@localhost:5432/what2do"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Ensure the URL uses asyncpg driver."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Get a sync-compatible URL using psycopg2."""
        url = self.DATABASE_URL
        for prefix in ("postgresql+asyncpg://", "postgres://"):
            if url.startswith(prefix):
                url = url.replace(prefix, "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # X/Twitter
    X_BEARER_TOKEN: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Scraping
    SCRAPE_TIMEOUT_S: int = 30
    SCRAPE_MAX_RETRIES: int = 2

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
