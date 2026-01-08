from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import engine as global_engine
from app.db.session import get_db
from app.main import create_app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_cache():
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.inmemory import InMemoryBackend

    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    # No explicit cleanup needed for in-memory backend in function scope
    # But FastAPICache is global, so maybe we should reset?
    # FastAPICache.reset() # method doesn't exist, but re-init overwrites


@pytest_asyncio.fixture(scope="function", autouse=True)
async def dispose_global_engine() -> AsyncGenerator[None, None]:
    yield
    await global_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database for each test function.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True,
    )

    testing_session_local = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with testing_session_local() as session:  # type: ignore
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a fresh FastAPI client for each test function, overriding the DB dependency.
    """
    app = create_app()

    # Override the dependency with the testing session
    app.dependency_overrides[get_db] = lambda: db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def superuser_token_headers(client: AsyncClient, db: AsyncSession) -> dict[str, str]:
    from app import crud
    from app.core import security
    from app.schemas.user import UserCreate

    email = "admin@example.com"
    password = "admin_password"
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = await crud.user.create(db, obj_in=user_in)

    access_token = security.create_access_token(user.id)
    return {"Authorization": f"Bearer {access_token}"}
