from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..models import Owner

router = APIRouter(prefix="/api/owners", tags=["owners"])


@router.get("", response_model=list[Owner])
async def list_owners() -> list[Owner]:
    rows = await db.fetch_all("SELECT * FROM vw_owners ORDER BY name")
    return [Owner(**r) for r in rows]


@router.get("/{name}", response_model=Owner)
async def get_owner(name: str) -> Owner:
    row = await db.fetch_one("SELECT * FROM vw_owners WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"owner not found: {name}")
    return Owner(**row)
