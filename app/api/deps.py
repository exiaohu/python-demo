from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size


async def get_pagination(
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 20,
) -> PaginationParams:
    return PaginationParams(page=page, size=size)


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (PyJWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from e
    user = await crud.user.get(db, id=int(token_data.sub))  # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user
