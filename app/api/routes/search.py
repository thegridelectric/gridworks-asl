from __future__ import annotations

from fastapi import APIRouter, Query

from .. import db
from ..models import SearchHit

router = APIRouter(prefix="/api/search", tags=["search"])


# (view, label, title_col, desc_col) — None means "this view doesn't expose
# that column, fall back to NULL". Matches what vw_* actually publishes.
_TARGETS = [
    ("vw_owners", "owner", None, "description"),
    ("vw_types", "type", "title", "description"),
    ("vw_type_versions", "type_version", "title", "description"),
    ("vw_enums", "enum", None, "description"),
    ("vw_enum_versions", "enum_version", "title", "description"),
    ("vw_formats", "format", "title", "description"),
    ("vw_type_helpers", "helper", "title", "description"),
    ("vw_type_axioms", "type_axiom", None, "statement"),
]


@router.get("", response_model=list[SearchHit])
async def search(q: str = Query(min_length=1), limit: int = Query(default=50, le=200)) -> list[SearchHit]:
    needle = f"%{q.lower()}%"
    hits: list[SearchHit] = []
    for view, label, title_col, desc_col in _TARGETS:
        title_expr = title_col or "NULL"
        desc_expr = desc_col or "NULL"
        sql = (
            f"SELECT name, {title_expr} AS title, {desc_expr} AS description "
            f"FROM {view} "
            f"WHERE LOWER(name) LIKE %s "
            f"   OR LOWER(COALESCE({title_expr}, '')) LIKE %s "
            f"   OR LOWER(COALESCE({desc_expr}, '')) LIKE %s "
            f"LIMIT %s"
        )
        rows = await db.fetch_all(sql, needle, needle, needle, limit)
        for r in rows:
            hits.append(
                SearchHit(
                    table=label,
                    id=r["name"],
                    name=r["name"],
                    title=r.get("title"),
                    description=r.get("description"),
                )
            )
    hits.sort(key=lambda h: (h.table, h.name))
    return hits[:limit]
