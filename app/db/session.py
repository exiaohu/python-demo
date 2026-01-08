from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Construct engine arguments based on database type
engine_args = {
    "echo": settings.DEBUG,
    "future": True,
}

if "sqlite" in settings.DATABASE_URL:
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args["pool_size"] = settings.DB_POOL_SIZE
    engine_args["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_args["pool_timeout"] = settings.DB_POOL_TIMEOUT
    engine_args["pool_recycle"] = settings.DB_POOL_RECYCLE

engine = create_async_engine(settings.DATABASE_URL, **engine_args)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:  # type: ignore
        yield session
