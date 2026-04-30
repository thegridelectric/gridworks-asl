from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import db
from ..models import Enum, EnumValue, EnumVersion

router = APIRouter(prefix="/api", tags=["enums"])


def _full_name(enum_name: str, version: str) -> str:
    return f"{enum_name}/{version}"


@router.get("/enums", response_model=list[Enum])
async def list_enums(owner: str | None = Query(default=None)) -> list[Enum]:
    if owner:
        rows = await db.fetch_all(
            "SELECT * FROM vw_enums WHERE owner = %s ORDER BY name", owner
        )
    else:
        rows = await db.fetch_all("SELECT * FROM vw_enums ORDER BY name")
    return [Enum(**r) for r in rows]


@router.get("/enums/{name}", response_model=Enum)
async def get_enum(name: str) -> Enum:
    row = await db.fetch_one("SELECT * FROM vw_enums WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"enum not found: {name}")
    return Enum(**row)


@router.get("/enums/{name}/versions", response_model=list[EnumVersion])
async def list_enum_versions(name: str) -> list[EnumVersion]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_enum_versions WHERE enum = %s ORDER BY version",
        name,
    )
    return [EnumVersion(**r) for r in rows]


@router.get("/enum-versions/{enum_name}/{version}", response_model=EnumVersion)
async def get_enum_version(enum_name: str, version: str) -> EnumVersion:
    row = await db.fetch_one(
        "SELECT * FROM vw_enum_versions WHERE name = %s",
        _full_name(enum_name, version),
    )
    if row is None:
        raise HTTPException(
            status_code=404, detail=f"enum version not found: {enum_name}/{version}"
        )
    return EnumVersion(**row)


@router.get(
    "/enum-versions/{enum_name}/{version}/values", response_model=list[EnumValue]
)
async def list_enum_values(enum_name: str, version: str) -> list[EnumValue]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_enum_values WHERE enum_version = %s ORDER BY idx, name",
        _full_name(enum_name, version),
    )
    return [EnumValue(**r) for r in rows]
