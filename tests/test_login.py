import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import user as crud_user

# Global test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"


@pytest_asyncio.fixture(scope="function")
async def db_session(db: AsyncSession):
    yield db


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        f"{settings.API_V1_STR}/users/",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    # We expect 401 because create_user requires superuser privileges
    assert response.status_code == 401 or response.status_code == 403

    # But we can verify the DB is empty of this user
    user = await crud_user.get_by_email(db_session, email=TEST_USER_EMAIL)
    assert user is None


@pytest.mark.asyncio
async def test_login_access_token(client: AsyncClient, db_session: AsyncSession):
    # First create a user manually
    from app.schemas.user import UserCreate

    user_in = UserCreate(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
    await crud_user.create(db_session, obj_in=user_in)

    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    response = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"
