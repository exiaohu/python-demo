from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

import sentry_sdk
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.api import api_router
from app.core.config import settings
from app.core.errors import (
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
)
from app.core.exceptions import AppError
from app.core.logger import logger
from app.core.rate_limit import limiter
from app.core.telemetry import setup_opentelemetry
from app.core.watcher import start_config_watcher
from app.db.session import engine
from app.middleware.monitoring import PrometheusMiddleware, metrics_endpoint
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application starting up...")

    # Start config watcher
    observer = start_config_watcher()

    # Initialize Cache
    if settings.CACHE_ENABLED:
        try:
            from fastapi_cache import FastAPICache
            from fastapi_cache.backends.redis import RedisBackend
            from redis import asyncio as aioredis

            redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
            FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
            logger.info("Cache initialized with Redis")
        except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
            # Fallback to in-memory cache for testing or if Redis fails
            from fastapi_cache import FastAPICache
            from fastapi_cache.backends.inmemory import InMemoryBackend

            FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
            logger.info("Cache initialized with InMemoryBackend")

    yield

    # Cleanup if needed
    if observer:
        observer.stop()
        observer.join()
    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=1.0,
        )
        logger.info("Sentry initialized")

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="A production-ready FastAPI project with Async SQLAlchemy, Alembic, and Prometheus metrics.",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        responses={
            400: {
                "description": "Bad Request",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}},
            },
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
            404: {"description": "Not Found"},
            422: {"description": "Validation Error"},
        },
    )

    setup_opentelemetry(app)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
    app.add_middleware(SlowAPIMiddleware)

    # Trusted Host
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    # GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Request ID
    app.add_middleware(RequestIDMiddleware)

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    elif settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Prometheus Metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics_endpoint)

    app.include_router(api_router, prefix="/api/v1")

    # Exception Handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore
    app.add_exception_handler(AppError, app_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, general_exception_handler)

    @app.get("/")
    def read_root() -> Dict[str, str]:
        logger.info("Root endpoint called")
        return {"message": f"Welcome to {settings.APP_NAME}"}

    @app.get("/healthz", tags=["health"])
    async def healthz() -> Dict[str, str]:
        # Basic DB check
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception as e:
            logger.error(f"DB health check failed: {e}")
            db_status = "error"

        # Redis check
        redis_status = "n/a"
        if settings.CACHE_ENABLED:
            try:
                from redis import asyncio as aioredis

                redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
                await redis.ping()
                await redis.close()
                redis_status = "ok"
            except Exception as e:
                logger.error(f"Redis health check failed: {e}")
                redis_status = "error"

        status = "ok" if db_status == "ok" and redis_status != "error" else "error"
        return {
            "status": status,
            "version": settings.VERSION,
            "database": db_status,
            "redis": redis_status,
        }

    return app


app = create_app()
