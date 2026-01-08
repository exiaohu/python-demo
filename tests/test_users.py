import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user_by_superuser(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    email = "newuser@example.com"
    password = "newuserpassword"
    data = {"email": email, "password": password}
    
    r = await client.post(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 200
    created_user = r.json()["data"]
    assert created_user["email"] == email
    
    user_in_db = await crud.user.get_by_email(db, email=email)
    assert user_in_db
    assert user_in_db.email == email

@pytest.mark.asyncio
async def test_read_users_by_superuser(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    # Create an extra user
    email = "extra@example.com"
    password = "password"
    user_in = UserCreate(email=email, password=password)
    await crud.user.create(db, obj_in=user_in)

    r = await client.get(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) >= 2  # superuser + extra user

@pytest.mark.asyncio
async def test_read_user_me(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    assert r.status_code == 200
    current_user = r.json()["data"]
    assert current_user["is_superuser"] is True
    assert current_user["email"] == "admin@example.com"
