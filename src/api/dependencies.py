"""API dependencies for dependency injection."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session

    Example:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
