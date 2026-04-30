from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

from . import auth, db, loader  # noqa: E402
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

app.include_router(auth.router)
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


@app.get("/api", tags=["meta"])
async def api_root() -> dict[str, str]:
    return {
        "name": "sema Registry Explorer API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/api/health",
    }


# ---------------------------------------------------------------------------
# SPA static mount (prod). When SEMA_SPA_DIST points at a built Vite dist,
# unknown non-/api routes serve index.html so client-side routing works.
# In dev, leave SEMA_SPA_DIST unset and `vite` proxies /api to this server.
# ---------------------------------------------------------------------------
from fastapi import Request  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

_spa_dist = Path(os.getenv("SEMA_SPA_DIST", "")).expanduser()
if _spa_dist.is_dir() and (_spa_dist / "index.html").is_file():
    # /assets, /favicon.ico, etc. as flat static files. html=False so SPA
    # fallback below handles client-side routes (Vite's hashed assets are
    # cache-busted by filename so html=True isn't needed here).
    app.mount(
        "/assets",
        StaticFiles(directory=str(_spa_dist / "assets")),
        name="spa-assets",
    )

    @app.get("/", include_in_schema=False)
    async def _spa_index() -> FileResponse:
        return FileResponse(_spa_dist / "index.html")

    # Catch-all for client-side router. /api/* still matches the routers
    # above because FastAPI evaluates declared routes before this one.
    @app.get("/{full_path:path}", include_in_schema=False)
    async def _spa_fallback(full_path: str, request: Request):
        if full_path.startswith("api/") or full_path == "api":
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        candidate = _spa_dist / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_spa_dist / "index.html")
else:
    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {
            "name": "sema Registry Explorer API",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/api/health",
            "note": "SPA dist not mounted; set SEMA_SPA_DIST to enable.",
        }
