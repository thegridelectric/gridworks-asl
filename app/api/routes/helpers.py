from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..models import TypeHelper, TypeHelperAttribute

router = APIRouter(prefix="/api/helpers", tags=["helpers"])


@router.get("", response_model=list[TypeHelper])
async def list_helpers() -> list[TypeHelper]:
    rows = await db.fetch_all("SELECT * FROM vw_type_helpers ORDER BY name")
    return [TypeHelper(**r) for r in rows]


@router.get("/{name}", response_model=TypeHelper)
async def get_helper(name: str) -> TypeHelper:
    row = await db.fetch_one("SELECT * FROM vw_type_helpers WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"helper not found: {name}")
    return TypeHelper(**row)


@router.get("/{name}/attributes", response_model=list[TypeHelperAttribute])
async def list_helper_attributes(name: str) -> list[TypeHelperAttribute]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_type_helper_attributes WHERE type_helper = %s ORDER BY idx, name",
        name,
    )
    return [TypeHelperAttribute(**r) for r in rows]
