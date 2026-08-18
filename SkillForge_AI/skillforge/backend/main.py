"""FastAPI application entry point for SkillForge Phase 14."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.agent import router as agent_router
from backend.careers import router as careers_router
from backend.config import API_TITLE, API_VERSION
from backend.gap import router as gap_router
from backend.profile import router as profile_router
from backend.roadmap import router as roadmap_router


app = FastAPI(title=API_TITLE, version=API_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(profile_router)
app.include_router(careers_router)
app.include_router(gap_router)
app.include_router(roadmap_router)
app.include_router(agent_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "14"}


app.mount(
    "/",
    StaticFiles(directory=Path(__file__).resolve().parent / "static", html=True),
    name="static",
)


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
    )