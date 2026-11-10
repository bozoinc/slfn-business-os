from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SLFN Nexus Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://hl_user:***@localhost:5432/hl_nexus"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALCHEMY_KEY: str = ""  # For AI calls

    # Authentik OIDC
    AUTHENTIK_URL: str = "http://localhost:9000"
    AUTHENTIK_CLIENT_ID: str = "6S8KcTVwB0euO1owAmU1y1XRLcTVoJCLkGdhCa9b"
    AUTHENTIK_CLIENT_SECRET: str = "xY5agRJieDMHDdlGEUkHLt6ZATbp8bUiJOd6ZDd0jfnPBsaGtdQUPGqYQgYDJMWabgHFa9yaFDwYxmpX84RADVJqu4pFSK2uiNZqTcx0V4nkDBYUKQK6hKXbWtfTbOEv"
    AUTHENTIK_REALM: str = "slfn-business-os"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ]

    # API
    API_V1_STR: str = "/api/v1"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


settings = Settings()