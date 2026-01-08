from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import PaginationParams, get_pagination
from app.core.config import settings
from app.db.session import get_db
from app.schemas.item import Item as ItemSchema
from app.schemas.item import ItemCreate
from app.schemas.response import Page, ResponseBase

router = APIRouter()


@router.get("/", response_model=ResponseBase[Page[ItemSchema]])
@cache(expire=settings.CACHE_EXPIRATION)
async def read_items(
    pagination: PaginationParams = Depends(get_pagination), db: AsyncSession = Depends(get_db)
) -> ResponseBase[Page[ItemSchema]]:
    # Note: fastapi-cache needs serializable objects.
    # SQLAlchemy models are not directly serializable by default JSON encoder.
    # However, since we return Pydantic models (ResponseBase[Page[ItemSchema]]),
    # FastAPI converts them before sending. But @cache runs on the return value of the function.
    # We must ensure the return value is Pydantic models, not ORM models mixed in.

    db_items = await crud.item.get_multi(db, skip=pagination.skip, limit=pagination.size)
    total = await crud.item.count(db)

    # Explicitly convert ORM objects to Pydantic models
    items = [ItemSchema.model_validate(item) for item in db_items]

    return ResponseBase(data=Page(items=items, total=total, page=pagination.page, size=pagination.size))


@router.post("/", response_model=ResponseBase[ItemSchema])
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)) -> ResponseBase[ItemSchema]:
    db_item = await crud.item.create(db, obj_in=item)
    return ResponseBase(data=db_item)


@router.get("/{item_id}", response_model=ResponseBase[ItemSchema])
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)) -> ResponseBase[ItemSchema]:
    item = await crud.item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ResponseBase(data=item)
