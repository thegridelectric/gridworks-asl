from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import db
from ..models import Type, TypeAttribute, TypeAxiom, TypeExample, TypeVersion

router = APIRouter(prefix="/api", tags=["types"])


def _full_name(type_name: str, version: str) -> str:
    """Compose the slash-bearing TypeVersion name from its parts."""
    return f"{type_name}/{version}"


@router.get("/types", response_model=list[Type])
async def list_types(owner: str | None = Query(default=None)) -> list[Type]:
    if owner:
        rows = await db.fetch_all(
            "SELECT * FROM vw_types WHERE owner = %s ORDER BY name", owner
        )
    else:
        rows = await db.fetch_all("SELECT * FROM vw_types ORDER BY name")
    return [Type(**r) for r in rows]


@router.get("/types/{name}", response_model=Type)
async def get_type(name: str) -> Type:
    row = await db.fetch_one("SELECT * FROM vw_types WHERE name = %s", name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"type not found: {name}")
    return Type(**row)


@router.get("/types/{name}/versions", response_model=list[TypeVersion])
async def list_type_versions(name: str) -> list[TypeVersion]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_type_versions WHERE type = %s ORDER BY version",
        name,
    )
    return [TypeVersion(**r) for r in rows]


@router.get("/type-versions", response_model=list[TypeVersion])
async def list_all_type_versions(
    status: str | None = Query(default=None),
    owner: str | None = Query(default=None),
) -> list[TypeVersion]:
    sql = "SELECT * FROM vw_type_versions"
    clauses: list[str] = []
    params: list[object] = []
    if status:
        clauses.append("status = %s")
        params.append(status)
    if owner:
        clauses.append("owner_name = %s")
        params.append(owner)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY name"
    rows = await db.fetch_all(sql, *params)
    return [TypeVersion(**r) for r in rows]


@router.get("/type-versions/{type_name}/{version}", response_model=TypeVersion)
async def get_type_version(type_name: str, version: str) -> TypeVersion:
    row = await db.fetch_one(
        "SELECT * FROM vw_type_versions WHERE name = %s",
        _full_name(type_name, version),
    )
    if row is None:
        raise HTTPException(
            status_code=404, detail=f"type version not found: {type_name}/{version}"
        )
    return TypeVersion(**row)


@router.get(
    "/type-versions/{type_name}/{version}/attributes",
    response_model=list[TypeAttribute],
)
async def list_type_version_attributes(
    type_name: str, version: str
) -> list[TypeAttribute]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_type_attributes WHERE type_version = %s ORDER BY idx, name",
        _full_name(type_name, version),
    )
    return [TypeAttribute(**r) for r in rows]


@router.get(
    "/type-versions/{type_name}/{version}/axioms", response_model=list[TypeAxiom]
)
async def list_type_version_axioms(type_name: str, version: str) -> list[TypeAxiom]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_type_axioms WHERE type_version = %s ORDER BY number, name",
        _full_name(type_name, version),
    )
    return [TypeAxiom(**r) for r in rows]


@router.get(
    "/type-versions/{type_name}/{version}/examples",
    response_model=list[TypeExample],
)
async def list_type_version_examples(
    type_name: str, version: str
) -> list[TypeExample]:
    rows = await db.fetch_all(
        "SELECT * FROM vw_type_examples WHERE type_version = %s ORDER BY name",
        _full_name(type_name, version),
    )
    return [TypeExample(**r) for r in rows]
