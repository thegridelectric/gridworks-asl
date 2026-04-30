from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..models import (
    EnumUpgrade,
    EnumUpgradeMapping,
    TypeUpgrade,
    TypeUpgradeOp,
)

router = APIRouter(prefix="/api", tags=["upgrades"])


@router.get("/type-upgrades", response_model=list[TypeUpgrade])
async def list_type_upgrades() -> list[TypeUpgrade]:
    rows = await db.fetch_all("SELECT * FROM vw_type_upgrades ORDER BY name")
    return [TypeUpgrade(**r) for r in rows]


@router.get("/type-upgrades/{name}", response_model=TypeUpgrade)
async def get_type_upgrade(name: str) -> TypeUpgrade:
    row = await db.fetch_one("SELECT * FROM vw_type_upgrades WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"type upgrade not found: {name}")
    return TypeUpgrade(**row)


@router.get("/type-upgrades/{name}/ops", response_model=list[TypeUpgradeOp])
async def list_type_upgrade_ops(name: str) -> list[TypeUpgradeOp]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_type_upgrade_ops WHERE type_upgrade = %s ORDER BY idx, name",
        name,
    )
    return [TypeUpgradeOp(**r) for r in rows]


@router.get("/enum-upgrades", response_model=list[EnumUpgrade])
async def list_enum_upgrades() -> list[EnumUpgrade]:
    rows = await db.fetch_all("SELECT * FROM vw_enum_upgrades ORDER BY name")
    return [EnumUpgrade(**r) for r in rows]


@router.get("/enum-upgrades/{name}", response_model=EnumUpgrade)
async def get_enum_upgrade(name: str) -> EnumUpgrade:
    row = await db.fetch_one("SELECT * FROM vw_enum_upgrades WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"enum upgrade not found: {name}")
    return EnumUpgrade(**row)


@router.get("/enum-upgrades/{name}/mappings", response_model=list[EnumUpgradeMapping])
async def list_enum_upgrade_mappings(name: str) -> list[EnumUpgradeMapping]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_enum_upgrade_mappings WHERE enum_upgrade = %s ORDER BY name",
        name,
    )
    return [EnumUpgradeMapping(**r) for r in rows]
