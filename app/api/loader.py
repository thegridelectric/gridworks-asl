"""Thin shim over rulebook-emitters/shared/loader.py.

FastAPI imports `load_rulebook`, `by_table`, `schema_for`, etc. from here so the
single point of failure for rulebook-JSON shape stays in shared/loader.py.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Make rulebook-emitters/ importable as `rulebook_emitters`.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_EMITTERS_DIR = _REPO_ROOT / "rulebook-emitters"
if str(_EMITTERS_DIR) not in sys.path:
    sys.path.insert(0, str(_EMITTERS_DIR))

from shared.loader import (  # noqa: E402
    by_table,
    group_by,
    index_by,
    load_rulebook,
    schema_for,
    table_summary,
)

DEFAULT_RULEBOOK_PATH = (
    _REPO_ROOT / "effortless-rulebook" / "effortless-rulebook.json"
).resolve()

_cache: dict[str, Any] | None = None


def get_rulebook() -> dict[str, Any]:
    """Load the rulebook once per process; cached after first call."""
    global _cache
    if _cache is None:
        path = os.getenv("SEMA_RULEBOOK_PATH") or str(DEFAULT_RULEBOOK_PATH)
        _cache = load_rulebook(path)
    return _cache


__all__ = [
    "by_table",
    "get_rulebook",
    "group_by",
    "index_by",
    "load_rulebook",
    "schema_for",
    "table_summary",
]
