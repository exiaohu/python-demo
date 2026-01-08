import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.core.logger import logger
from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreate


async def init_db(db: AsyncSession) -> None:
    # Create first superuser
    user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.user.create(db, obj_in=user_in)
        logger.info(f"Superuser {settings.FIRST_SUPERUSER} created")
    else:
        logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists")


async def main() -> None:
    logger.info("Creating initial data")
    async with AsyncSessionLocal() as session:  # type: ignore
        await init_db(session)
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
