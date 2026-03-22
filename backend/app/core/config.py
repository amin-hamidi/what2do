from pydantic_settings import BaseSettings
from functools import lru_cache


def _to_async_url(url: str) -> str:
    """Convert any postgres URL to asyncpg format."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _to_sync_url(url: str) -> str:
    """Convert any postgres URL to psycopg2 format."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Settings(BaseSettings):
    # App
    APP_NAME: str = "What2Do"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://what2do:what2do@localhost:5432/what2do"

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

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return _to_async_url(self.DATABASE_URL)

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return _to_sync_url(self.DATABASE_URL)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
