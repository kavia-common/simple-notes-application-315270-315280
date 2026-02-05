"""FastAPI application entrypoint for the Notes backend.

Provides:
- Health check endpoint
- Notes CRUD endpoints backed by SQLite
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.db import init_db
from src.routers.notes import router as notes_router

openapi_tags = [
    {
        "name": "health",
        "description": "Health and diagnostics endpoints.",
    },
    {
        "name": "notes",
        "description": "Create, read, update, and delete notes.",
    },
]

app = FastAPI(
    title="Simple Notes API",
    description="Backend API for a simple notes app (SQLite + FastAPI).",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Allow frontend dev server and optionally allow configured frontend URL.
# Note: these env vars are listed for this container; they may or may not be set.
frontend_url = os.getenv("REACT_APP_FRONTEND_URL")
allow_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if frontend_url:
    allow_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    """Initialize required database tables on app startup."""
    init_db()


@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Simple health check endpoint to verify the API is running.",
    operation_id="healthCheck",
)
def health_check() -> dict:
    """Return a simple health status payload."""
    return {"message": "Healthy"}


app.include_router(notes_router)
