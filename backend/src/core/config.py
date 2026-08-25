"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from .env or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- App ----
    APP_NAME: str = "ApeAdmin"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # ---- Database ----
    DB_TYPE: Literal["mysql", "sqlite"] = "sqlite"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "apeadmin"
    DB_ECHO: bool = False  # SQL echo for debugging
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ---- Redis ----
    REDIS_URL: str | None = "redis://localhost:6379/1"

    # ---- JWT / Auth ----
    JWT_SECRET: str = Field(default="change-me-in-production-please-32chars!")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # ---- CORS ----
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8000"]

    # ---- MCP ----
    MCP_ENABLED: bool = True
    MCP_PREFIX: str = "/mcp"

    # ---- Plugin ----
    PLUGINS_ENABLED: bool = True
    PLUGINS_BUILTIN_DIR: str = str(Path(__file__).resolve().parent.parent / "plugins" / "builtin")
    PLUGINS_UPLOAD_DIR: str = str(Path(__file__).resolve().parent.parent / "uploads" / "plugins")

    # ---- Super admin ----
    SUPER_ADMIN_USERNAME: str = "admin"
    SUPER_ADMIN_PASSWORD: str = "admin123"

    # ---- Pagination ----
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy async database URL."""
        if self.DB_TYPE == "mysql":
            return (
                f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
            )
        return f"sqlite+aiosqlite:///./{self.DB_NAME}.db"

    @property
    def sync_database_url(self) -> str:
        """Build a synchronous database URL for Alembic migrations."""
        if self.DB_TYPE == "mysql":
            return (
                f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
            )
        return f"sqlite:///{self.DB_NAME}.db"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
