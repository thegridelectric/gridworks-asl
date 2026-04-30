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


def _upgrade_name(word: str, from_version: str, to_version: str) -> str:
    """Compose the canonical TypeUpgrade / EnumUpgrade name (matches vw_*.name)."""
    return f"{word}/{from_version} -> {word}/{to_version}"


@router.get("/type-upgrades", response_model=list[TypeUpgrade])
async def list_type_upgrades() -> list[TypeUpgrade]:
    rows = await db.fetch_all("SELECT * FROM vw_type_upgrades ORDER BY name")
    return [TypeUpgrade(**r) for r in rows]


@router.get(
    "/type-upgrades/{word}/{from_version}-to-{to_version}",
    response_model=TypeUpgrade,
)
async def get_type_upgrade(
    word: str, from_version: str, to_version: str
) -> TypeUpgrade:
    name = _upgrade_name(word, from_version, to_version)
    row = await db.fetch_one("SELECT * FROM vw_type_upgrades WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"type upgrade not found: {name}")
    return TypeUpgrade(**row)


@router.get(
    "/type-upgrades/{word}/{from_version}-to-{to_version}/ops",
    response_model=list[TypeUpgradeOp],
)
async def list_type_upgrade_ops(
    word: str, from_version: str, to_version: str
) -> list[TypeUpgradeOp]:
    name = _upgrade_name(word, from_version, to_version)
    rows = await db.fetch_all(
        "SELECT * FROM vw_type_upgrade_ops WHERE type_upgrade = %s ORDER BY idx, name",
        name,
    )
    return [TypeUpgradeOp(**r) for r in rows]


@router.get("/enum-upgrades", response_model=list[EnumUpgrade])
async def list_enum_upgrades() -> list[EnumUpgrade]:
    rows = await db.fetch_all("SELECT * FROM vw_enum_upgrades ORDER BY name")
    return [EnumUpgrade(**r) for r in rows]


@router.get(
    "/enum-upgrades/{word}/{from_version}-to-{to_version}",
    response_model=EnumUpgrade,
)
async def get_enum_upgrade(
    word: str, from_version: str, to_version: str
) -> EnumUpgrade:
    name = _upgrade_name(word, from_version, to_version)
    row = await db.fetch_one("SELECT * FROM vw_enum_upgrades WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"enum upgrade not found: {name}")
    return EnumUpgrade(**row)


@router.get(
    "/enum-upgrades/{word}/{from_version}-to-{to_version}/mappings",
    response_model=list[EnumUpgradeMapping],
)
async def list_enum_upgrade_mappings(
    word: str, from_version: str, to_version: str
) -> list[EnumUpgradeMapping]:
    name = _upgrade_name(word, from_version, to_version)
    rows = await db.fetch_all(
        "SELECT * FROM vw_enum_upgrade_mappings WHERE enum_upgrade = %s ORDER BY name",
        name,
    )
    return [EnumUpgradeMapping(**r) for r in rows]
