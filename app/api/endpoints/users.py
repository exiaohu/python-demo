from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.api import deps
from app.core.config import settings
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.rate_limit import limiter
from app.schemas.response import Page, ResponseBase
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[Page[User]])
@cache(expire=settings.CACHE_EXPIRATION)
async def read_users(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    pagination: deps.PaginationParams = Depends(deps.get_pagination),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(db, skip=pagination.skip, limit=pagination.size)
    total = await crud.user.count(db)
    # Convert SQLAlchemy models to Pydantic models for caching
    users_data = [User.model_validate(u) for u in users]
    return ResponseBase(data=Page(items=users_data, total=total, page=pagination.page, size=pagination.size))


@router.post("/", response_model=ResponseBase[User])
@limiter.limit("10/minute")
async def create_user(
    request: Request,
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise ValidationError(
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    return ResponseBase(data=user)


@router.get("/me", response_model=ResponseBase[User])
async def read_user_me(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return ResponseBase(data=current_user)


@router.get("/{user_id}", response_model=ResponseBase[User])
async def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(db, id=user_id)
    if user == current_user:
        return ResponseBase(data=user)
    if not current_user.is_superuser:
        raise ForbiddenError(detail="The user doesn't have enough privileges")
    return ResponseBase(data=user)


@router.put("/{user_id}", response_model=ResponseBase[User])
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise NotFoundError(
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return ResponseBase(data=user)
