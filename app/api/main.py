from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

from . import db, loader  # noqa: E402
from .models import HealthResponse, TableSummary  # noqa: E402
from .routes import (  # noqa: E402
    enums,
    formats,
    helpers,
    owners,
    projections,
    search,
    types,
    upgrades,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_pool()
    try:
        yield
    finally:
        await db.close_pool()


app = FastAPI(
    title="sema Registry Explorer API",
    description="Read/write surface for the sema rulebook. Reads vw_* views, writes base tables.",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = [
    o.strip()
    for o in os.getenv(
        "SEMA_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(owners.router)
app.include_router(types.router)
app.include_router(enums.router)
app.include_router(formats.router)
app.include_router(helpers.router)
app.include_router(projections.router)
app.include_router(upgrades.router)
app.include_router(search.router)


@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    db_ok = False
    rb_ok = False
    summary: list[TableSummary] = []
    try:
        row = await db.fetch_one("SELECT 1 AS ok")
        db_ok = bool(row and row.get("ok") == 1)
    except Exception:
        db_ok = False
    try:
        rb = loader.get_rulebook()
        rb_ok = bool(rb)
        summary = [TableSummary(table=t, row_count=n) for t, n in loader.table_summary(rb)]
    except Exception:
        rb_ok = False
    return HealthResponse(ok=db_ok and rb_ok, db=db_ok, rulebook=rb_ok, tables=summary)


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {
        "name": "sema Registry Explorer API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/api/health",
    }
