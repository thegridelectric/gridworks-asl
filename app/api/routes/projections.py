from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..models import Projection, ProjectionMapping

router = APIRouter(prefix="/api/projections", tags=["projections"])


@router.get("", response_model=list[Projection])
async def list_projections() -> list[Projection]:
    rows = await db.fetch_all("SELECT * FROM vw_projections ORDER BY name")
    return [Projection(**r) for r in rows]


@router.get("/{name}", response_model=Projection)
async def get_projection(name: str) -> Projection:
    row = await db.fetch_one("SELECT * FROM vw_projections WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"projection not found: {name}")
    return Projection(**row)


@router.get("/{name}/mappings", response_model=list[ProjectionMapping])
async def list_projection_mappings(name: str) -> list[ProjectionMapping]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_projection_mappings WHERE projection = %s ORDER BY name",
        name,
    )
    return [ProjectionMapping(**r) for r in rows]
