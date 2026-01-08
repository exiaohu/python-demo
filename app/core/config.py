from typing import List, Optional, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Playground"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8080
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("sqlite://") and not v.startswith("sqlite+aiosqlite://"):
            return v.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return v

    # Database Pool
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Security
    # SECRET_KEY must be set in .env file or environment variable
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE_CHANGE_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    WORKERS: int = 1

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str):
            # Let Pydantic handle JSON string parsing for list
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(env_file=".env")

    API_V1_STR: str = "/api/v1"

    # Rate Limit
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_STORAGE_URL: str = "memory://"

    # Cache
    CACHE_ENABLED: bool = True
    CACHE_EXPIRATION: int = 60  # seconds

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "python-demo"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "local"

    # Admin
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"


settings = Settings()
