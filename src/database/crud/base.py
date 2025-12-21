"""Base CRUD operations with generic methods."""

from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with generic database operations.

    Provides standard CRUD operations that can be inherited by specific model CRUD classes.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, session: AsyncSession, id: UUID) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            session: Database session
            id: Record UUID

        Returns:
            Model instance or None if not found
        """
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            session: Database session
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            filters: Optional dictionary of filters

        Returns:
            List of model instances
        """
        query = select(self.model).offset(skip).limit(limit)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        session: AsyncSession,
        filters: Optional[dict] = None,
    ) -> int:
        """
        Count records matching filters.

        Args:
            session: Database session
            filters: Optional dictionary of filters

        Returns:
            Count of matching records
        """
        query = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        result = await session.execute(query)
        return result.scalar_one()

    async def create(
        self,
        session: AsyncSession,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        """
        Create a new record.

        Args:
            session: Database session
            obj_in: Pydantic schema with creation data

        Returns:
            Created model instance
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            session: Database session
            db_obj: Existing model instance
            obj_in: Pydantic schema or dict with update data

        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """
        Delete a record (hard delete).

        Args:
            session: Database session
            id: Record UUID

        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get(session, id)
        if db_obj:
            await session.delete(db_obj)
            await session.flush()
            return True
        return False

    async def soft_delete(self, session: AsyncSession, id: UUID) -> Optional[ModelType]:
        """
        Soft delete a record (if model has SoftDeleteMixin).

        Args:
            session: Database session
            id: Record UUID

        Returns:
            Soft-deleted model instance or None if not found
        """
        db_obj = await self.get(session, id)
        if db_obj and hasattr(db_obj, 'soft_delete'):
            db_obj.soft_delete()
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            return db_obj
        return None
