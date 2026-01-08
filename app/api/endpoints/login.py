from datetime import timedelta
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import PyJWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.token import Token, TokenPayload

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request, db: AsyncSession = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return {
        "access_token": security.create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": security.create_refresh_token(user.id, expires_delta=refresh_token_expires),
        "token_type": "bearer",
    }


@router.post("/login/refresh-token", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Refresh access token using a valid refresh token
    """
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

    except (PyJWTError, ValidationError) as e:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        ) from e

    user = await crud.user.get(db, id=int(token_data.sub))  # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Rotate refresh token as well for security
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return {
        "access_token": security.create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": security.create_refresh_token(user.id, expires_delta=refresh_token_expires),
        "token_type": "bearer",
    }
