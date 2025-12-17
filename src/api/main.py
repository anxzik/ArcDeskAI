from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AgentDesk API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Serve a tiny static UI (no Node required)
_UI_DIR = Path(__file__).resolve().parents[1] / "ui" / "web"
if _UI_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_UI_DIR), html=True), name="ui")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    # If the UI is mounted, StaticFiles will handle "/".
    # This is mainly here to keep behavior clear.
    return RedirectResponse(url="/docs")