from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from ..database.session import engine, init_db
from .routers import agent_desks, tasks, teams


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Handles database initialization on startup and cleanup on shutdown.
    """
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: Dispose engine
    await engine.dispose()


app = FastAPI(
    title="ArcDeskAI API",
    version="0.1.0",
    description="Hierarchical Multi-Agent AI Organization System API",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_desks.router, prefix="/api/v1/desks", tags=["Agent Desks"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


# Serve a tiny static UI (no Node required)
_UI_DIR = Path(__file__).resolve().parents[1] / "ui" / "web"
if _UI_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_UI_DIR), html=True), name="ui")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")