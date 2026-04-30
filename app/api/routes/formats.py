from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import db
from ..models import Format, FormatExample

router = APIRouter(prefix="/api", tags=["formats"])


@router.get("/formats", response_model=list[Format])
async def list_formats(owner: str | None = Query(default=None)) -> list[Format]:
    if owner:
        rows = await db.fetch_all(
            "SELECT * FROM vw_formats WHERE owner_name = %s ORDER BY name", owner
        )
    else:
        rows = await db.fetch_all("SELECT * FROM vw_formats ORDER BY name")
    return [Format(**r) for r in rows]


@router.get("/formats/{name}", response_model=Format)
async def get_format(name: str) -> Format:
    row = await db.fetch_one("SELECT * FROM vw_formats WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"format not found: {name}")
    return Format(**row)


@router.get("/formats/{name}/examples", response_model=list[FormatExample])
async def list_format_examples(name: str) -> list[FormatExample]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_format_examples WHERE format = %s ORDER BY name",
        name,
    )
    return [FormatExample(**r) for r in rows]
