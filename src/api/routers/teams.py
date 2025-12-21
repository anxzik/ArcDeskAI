"""API router for Team endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..exceptions import EntityNotFoundError, EntityAlreadyExistsError
from ...database.crud import team
from ...database.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
)

router = APIRouter()


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: TeamCreate,
    session: AsyncSession = Depends(get_db)
):
    """Create a new Team."""
    existing = await team.get_by_team_id(session, team_in.team_id)
    if existing:
        raise EntityAlreadyExistsError("Team", team_in.team_id)
    
    new_team = await team.create(session, team_in)
    return new_team


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    session: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List Teams with pagination."""
    skip = (page - 1) * page_size
    teams = await team.get_multi(session, skip=skip, limit=page_size)
    total = await team.count(session)
    
    return TeamListResponse(
        items=teams,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific Team."""
    team_obj = await team.get(session, team_id)
    if not team_obj:
        raise EntityNotFoundError("Team", str(team_id))
    return team_obj


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    team_in: TeamUpdate,
    session: AsyncSession = Depends(get_db)
):
    """Update a Team."""
    team_obj = await team.get(session, team_id)
    if not team_obj:
        raise EntityNotFoundError("Team", str(team_id))
    
    team_obj = await team.update(session, team_obj, team_in)
    return team_obj


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Soft delete a Team."""
    team_obj = await team.soft_delete(session, team_id)
    if not team_obj:
        raise EntityNotFoundError("Team", str(team_id))
