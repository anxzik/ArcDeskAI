"""API router for Task endpoints."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..exceptions import EntityNotFoundError, EntityAlreadyExistsError
from ...database.crud import task
from ...database.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskWithArtifacts,
    TaskListResponse,
)

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    session: AsyncSession = Depends(get_db)
):
    """Create a new Task."""
    existing = await task.get_by_task_id(session, task_in.task_id)
    if existing:
        raise EntityAlreadyExistsError("Task", task_in.task_id)
    
    new_task = await task.create(session, task_in)
    return new_task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    session: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
):
    """List Tasks with pagination and filtering."""
    skip = (page - 1) * page_size
    
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    
    tasks = await task.get_multi(session, skip=skip, limit=page_size, filters=filters)
    total = await task.count(session, filters=filters)
    
    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{task_id}", response_model=TaskWithArtifacts)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific Task with artifacts."""
    task_obj = await task.get_with_artifacts(session, task_id)
    if not task_obj:
        raise EntityNotFoundError("Task", str(task_id))
    return task_obj


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_in: TaskUpdate,
    session: AsyncSession = Depends(get_db)
):
    """Update a Task."""
    task_obj = await task.get(session, task_id)
    if not task_obj:
        raise EntityNotFoundError("Task", str(task_id))
    
    task_obj = await task.update(session, task_obj, task_in)
    return task_obj


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Soft delete a Task."""
    task_obj = await task.soft_delete(session, task_id)
    if not task_obj:
        raise EntityNotFoundError("Task", str(task_id))


@router.get("/{task_id}/subtasks", response_model=List[TaskResponse])
async def get_subtasks(
    task_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get all subtasks of a task."""
    task_obj = await task.get(session, task_id)
    if not task_obj:
        raise EntityNotFoundError("Task", str(task_id))
    
    subtasks = await task.get_subtasks(session, task_id)
    return subtasks
