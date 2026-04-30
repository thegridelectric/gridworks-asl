"""Tiny accessors for the effortless-rulebook JSON shape.

Every emitter in this directory loads the rulebook through these helpers so that
table-shape changes ripple in one place. Intentionally small: anything bigger
belongs in the emitter that needs it.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_rulebook(path: str | Path) -> dict[str, Any]:
    """Load and return the rulebook JSON as a plain dict."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def by_table(rulebook: dict[str, Any], table: str) -> list[dict[str, Any]]:
    """Return the data[] array for a given table, or [] if absent."""
    return rulebook.get(table, {}).get("data") or []


def schema_for(rulebook: dict[str, Any], table: str) -> list[dict[str, Any]]:
    """Return the schema[] array for a given table, or [] if absent."""
    return rulebook.get(table, {}).get("schema") or []


def index_by(rows: list[dict[str, Any]], key: str) -> dict[Any, dict[str, Any]]:
    """Index a list of rows by a unique key column."""
    return {r[key]: r for r in rows if key in r}


def group_by(rows: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    """Group a list of rows by a (possibly repeating) key column."""
    out: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        out[r.get(key)].append(r)
    return dict(out)


def table_summary(rulebook: dict[str, Any]) -> list[tuple[str, int]]:
    """Return [(table_name, row_count), ...] sorted by table name."""
    summary: list[tuple[str, int]] = []
    for name, body in rulebook.items():
        if isinstance(body, dict) and isinstance(body.get("data"), list):
            summary.append((name, len(body["data"])))
    return sorted(summary)
