"""API router for AgentDesk endpoints."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..exceptions import EntityNotFoundError, EntityAlreadyExistsError
from ...database.crud import agent_desk
from ...database.schemas.agent_desk import (
    DeskCreate,
    DeskUpdate,
    DeskResponse,
    DeskListResponse,
)

router = APIRouter()


@router.post("/", response_model=DeskResponse, status_code=status.HTTP_201_CREATED)
async def create_desk(
    desk_in: DeskCreate,
    session: AsyncSession = Depends(get_db)
):
    """Create a new AgentDesk."""
    # Check if desk_id already exists
    existing = await agent_desk.get_by_desk_id(session, desk_in.desk_id)
    if existing:
        raise EntityAlreadyExistsError("AgentDesk", desk_in.desk_id)
    
    desk = await agent_desk.create(session, desk_in)
    return desk


@router.get("/", response_model=DeskListResponse)
async def list_desks(
    session: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str | None = None,
    team_id: UUID | None = None,
):
    """List AgentDesks with pagination and filtering."""
    skip = (page - 1) * page_size
    
    filters = {}
    if role:
        filters["role"] = role
    if team_id:
        filters["team_id"] = team_id
    
    desks = await agent_desk.get_multi(session, skip=skip, limit=page_size, filters=filters)
    total = await agent_desk.count(session, filters=filters)
    
    return DeskListResponse(
        items=desks,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{desk_id}", response_model=DeskResponse)
async def get_desk(
    desk_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific AgentDesk by ID."""
    desk = await agent_desk.get(session, desk_id)
    if not desk:
        raise EntityNotFoundError("AgentDesk", str(desk_id))
    return desk


@router.put("/{desk_id}", response_model=DeskResponse)
async def update_desk(
    desk_id: UUID,
    desk_in: DeskUpdate,
    session: AsyncSession = Depends(get_db)
):
    """Update an AgentDesk."""
    desk = await agent_desk.get(session, desk_id)
    if not desk:
        raise EntityNotFoundError("AgentDesk", str(desk_id))
    
    desk = await agent_desk.update(session, desk, desk_in)
    return desk


@router.delete("/{desk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_desk(
    desk_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Soft delete an AgentDesk."""
    desk = await agent_desk.soft_delete(session, desk_id)
    if not desk:
        raise EntityNotFoundError("AgentDesk", str(desk_id))


@router.get("/{desk_id}/subordinates", response_model=List[DeskResponse])
async def get_subordinates(
    desk_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get all subordinates of a desk."""
    desk = await agent_desk.get(session, desk_id)
    if not desk:
        raise EntityNotFoundError("AgentDesk", str(desk_id))
    
    subordinates = await agent_desk.get_subordinates(session, desk_id)
    return subordinates
