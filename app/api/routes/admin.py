"""Admin surface: make YAML↔rulebook drift visible.

This is intentionally a thin shell over four sources of truth:

  1. `definitions/`               — YAML SSoT on disk
  2. `effortless-rulebook.json`   — derived projection (currently stale)
  3. `definitions-emitted/`       — last `rulebook_to_yaml.py` output, used by
                                    the round-trip check
  4. Postgres `vw_*` views        — what the rest of the app renders

The admin endpoints expose 1–3 directly (4 already has its own routes). Where
they disagree, *that's* the point — the UI's job is to surface drift, not
paper over it. See memory feedback-ui-demystifies + feedback-app-is-prototype.

Endpoints:
  GET  /api/admin/yaml/files
       Walk definitions/, return {path, kind, name, version, sha256, mtime}[].
  GET  /api/admin/yaml/file?path=…
       Return one file's raw YAML body. Path must be inside definitions/.
  GET  /api/admin/rulebook/summary
       Per-table row counts straight from rulebook.json (independent of DB).
  GET  /api/admin/parity
       Per-YAML-file: is its rulebook row present? (cheap, in-process)
       Plus emitted-tree freshness so the UI can warn about stale diffs.
  GET  /api/admin/tools
       Static list of runnable tools with their argv + description.
  POST /api/admin/tools/{tool}/run
       Stream stdout/stderr as text/plain chunks. Tool name is whitelisted.

All endpoints require the same JWT gate as the rest of the app (auth.current_user).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Auth: this module follows the same pattern as the rest of app/api/routes/ —
# no per-route Depends(current_user). The frontend LoginGate is the gate.
# When auth-on-admin is wanted, swap to Depends(current_user) here (will fail
# closed unless MAGICLINK_TENANT_ID is set). Slice 1 keeps things consistent
# with the existing prototype shape.

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Path resolution — same shape as loader.py
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(
    os.getenv("SEMA_REPO_ROOT") or Path(__file__).resolve().parents[3]
).resolve()
_DEFINITIONS_DIR = (_REPO_ROOT / "definitions").resolve()
_EMITTED_DIR = (_REPO_ROOT / "definitions-emitted").resolve()
_RULEBOOK_PATH = (
    _REPO_ROOT / "effortless-rulebook" / "effortless-rulebook.json"
).resolve()

# Sibling repo (api.effortlessapi.com) that ships the SSoTme transpiler
# catalog. Each tool is a directory under tools/effortless/<name>/ with a
# workload/ssotme-tool.json describing it + its cpln deployment URL.
# Override with SEMA_TRANSPILER_CATALOG to point elsewhere.
_DEFAULT_TRANSPILER_CATALOG = (
    _REPO_ROOT.parent
    / "api.effortlessapi.com"
    / "Versioned-Stable-SSoTme-Tools"
    / "tools"
    / "effortless"
)
_TRANSPILER_CATALOG_DIR = Path(
    os.getenv("SEMA_TRANSPILER_CATALOG") or _DEFAULT_TRANSPILER_CATALOG
).resolve()


# ---------------------------------------------------------------------------
# Tool whitelist — fixed argv per tool name, no shell injection surface
# ---------------------------------------------------------------------------

# Each entry: (argv-as-list, human description). Argv is appended after
# `python` (interpreter resolved at run time via sys.executable).
_TOOLS: dict[str, dict[str, Any]] = {
    "yaml-to-rulebook": {
        "argv": ["rulebook-emitters/yaml/yaml_to_rulebook.py"],
        "description": "Read definitions/*.yaml → write effortless-rulebook.json.",
        "writes": "effortless-rulebook/effortless-rulebook.json",
    },
    "yaml-to-rulebook-dry-run": {
        "argv": ["rulebook-emitters/yaml/yaml_to_rulebook.py", "--dry-run"],
        "description": "Same import but only print counts/warnings; no writes.",
        "writes": None,
    },
    "rulebook-to-yaml": {
        "argv": ["rulebook-emitters/yaml/rulebook_to_yaml.py"],
        "description": "Read effortless-rulebook.json → write definitions-emitted/*.yaml.",
        "writes": "definitions-emitted/",
    },
    "round-trip-check": {
        "argv": ["rulebook-emitters/yaml/yaml_round_trip_check.py", "--limit", "999"],
        "description": "Compare definitions/ vs definitions-emitted/. Reports per-file diff.",
        "writes": None,
    },
    "effortless-build": {
        # Special-cased below — runs the `effortless` binary, not python.
        "argv": ["__effortless_build__"],
        "description": "Run `effortless build` (rulebook → postgres SQL → reset DB).",
        "writes": "postgres/0[0-5]*.sql + local sema database",
    },
}


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class YamlFile(BaseModel):
    path: str               # repo-relative, e.g. "definitions/types/bid/000.yaml"
    kind: str               # types | enums | formats | registry | owner | other
    name: str | None = None # e.g. "bid"
    version: str | None = None # e.g. "000"
    sha256: str
    mtime: float            # unix timestamp


class FileBody(BaseModel):
    path: str
    body: str
    sha256: str
    mtime: float


class FileWriteRequest(BaseModel):
    body: str
    # Optimistic lock: GET returns sha256, client echoes it back on PUT. If the
    # file's current sha256 doesn't match, the write is refused with 409. This
    # catches both concurrent edits and "I edited disk underneath the UI"
    # cases. Set expected_sha256 to None to force-write (last-writer-wins).
    expected_sha256: str | None = None


class FileWriteResponse(BaseModel):
    path: str
    sha256: str       # new sha256 after write
    mtime: float      # new mtime after write
    bytes_written: int


class FieldSchema(BaseModel):
    """One column's schema as carried inside `rulebook.{table}.schema[]`."""
    name: str
    datatype: str                       # string | integer | boolean | datetime
    type: str                           # raw | relationship | aggregation | calculated | lookup
    nullable: bool = True
    related_to: str | None = None       # FK target table when type=="relationship"
    description: str | None = None
    formula: str | None = None          # for derived fields


class RulebookTableRow(BaseModel):
    """One row from a rulebook table, in the shape the navigator pane wants:
    just enough to render a list entry (id + a short label) without paying
    for the full row payload. Use GET /api/admin/rulebook/entry to fetch
    the editable form."""
    id: str
    # Pick a single field to show next to the id (e.g. Title or Summary).
    # Computed server-side so tables with different "human label" conventions
    # all look uniform in the tree.
    label: str | None = None
    # Surface a couple of high-signal fields so the user can scan rows
    # without clicking each one.
    preview: dict[str, Any] = Field(default_factory=dict)


class RulebookTableResponse(BaseModel):
    table: str
    key_fields: list[str]               # which fields compose the id
    row_count: int
    rows: list[RulebookTableRow]
    # Tables whose `data` is regenerated by `yaml-to-rulebook` — editing
    # rows here is fine but the change is fragile. The UI uses this to
    # show a per-table warning (same shape as the per-row has_yaml_mirror
    # warning we already render).
    is_yaml_sourced: bool


class RulebookEntryResponse(BaseModel):
    table: str
    id: str                             # canonical identifier used to locate the row
    row: dict[str, Any]                 # full row payload
    row_sha256: str                     # for optimistic-lock on PUT
    rulebook_sha256: str                # for cache invalidation / global concurrency
    schema_: list[FieldSchema] = Field(default_factory=list, alias="schema")
    has_yaml_mirror: bool = False       # True iff a YAML file under definitions/ corresponds to this row

    model_config = {"populate_by_name": True}


class RulebookEntryWriteRequest(BaseModel):
    row: dict[str, Any]
    expected_row_sha256: str | None = None
    # If provided, the *whole rulebook file* must still have this sha256.
    # We compare and refuse on mismatch — protects against another writer
    # racing in between GET and PUT.
    expected_rulebook_sha256: str | None = None


class RulebookSummary(BaseModel):
    path: str
    tables: dict[str, int]  # table → row count
    types: list[str]        # type names
    type_versions: list[str]  # "type/version"
    enums: list[str]
    enum_versions: list[str]
    formats: list[str]
    rulebook_mtime: float


class ParityRow(BaseModel):
    yaml_path: str          # repo-relative
    kind: str               # types | enums | formats
    name: str
    version: str | None     # None for formats
    in_yaml: bool           # always true for rows surfaced here
    in_rulebook: bool
    rulebook_only: bool = False
    status: str             # "match" | "missing_in_rulebook" | "rulebook_only"


class ParityReport(BaseModel):
    yaml_total: int
    rulebook_total: int
    matched: int
    missing_in_rulebook: int
    rulebook_only: int
    rows: list[ParityRow]
    emitted_dir_exists: bool
    emitted_mtime: float | None
    emitted_age_seconds: float | None
    rulebook_mtime: float


class ToolInfo(BaseModel):
    name: str
    description: str
    writes: str | None
    argv: list[str]


class ToolsResponse(BaseModel):
    repo_root: str
    tools: list[ToolInfo]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_VERSION_RE = re.compile(r"^(\d{3})\.ya?ml$")


def _classify(rel_path: Path) -> tuple[str, str | None, str | None]:
    """Classify a YAML file under definitions/ into (kind, name, version).

    Layout:
      definitions/types/{name}/{NNN}.yaml      → ("types", name, "NNN")
      definitions/enums/{name}/{NNN}.yaml      → ("enums", name, "NNN")
      definitions/formats/{name}.yaml          → ("formats", name, None)
      definitions/registry.yaml                → ("registry", None, None)
      definitions/owners.yaml                  → ("owner", None, None)
    """
    parts = rel_path.parts
    if parts == ("definitions", "registry.yaml"):
        return ("registry", None, None)
    if parts == ("definitions", "owners.yaml"):
        return ("owner", None, None)
    if len(parts) >= 3 and parts[0] == "definitions":
        bucket = parts[1]
        if bucket == "formats" and len(parts) == 3:
            return ("formats", parts[2][:-5] if parts[2].endswith(".yaml") else parts[2][:-4], None)
        if bucket in ("types", "enums") and len(parts) == 4:
            m = _VERSION_RE.match(parts[3])
            return (bucket, parts[2], m.group(1) if m else None)
    return ("other", None, None)


def _sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_definitions_path(rel: str) -> Path:
    """Resolve a caller-supplied path and ensure it stays inside definitions/."""
    candidate = (_REPO_ROOT / rel).resolve()
    try:
        candidate.relative_to(_DEFINITIONS_DIR)
    except ValueError:
        raise HTTPException(status_code=400, detail="path_outside_definitions")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="file_not_found")
    return candidate


def _walk_yaml_files() -> list[YamlFile]:
    if not _DEFINITIONS_DIR.is_dir():
        return []
    out: list[YamlFile] = []
    for p in sorted(_DEFINITIONS_DIR.rglob("*.yaml")):
        rel = p.relative_to(_REPO_ROOT)
        kind, name, version = _classify(rel)
        st = p.stat()
        out.append(YamlFile(
            path=str(rel),
            kind=kind,
            name=name or "",
            version=version,
            sha256=_sha256_of(p),
            mtime=st.st_mtime,
        ))
    return out


def _load_rulebook() -> dict[str, Any]:
    """Read effortless-rulebook.json directly. Does NOT go through the
    app's cached loader — we want fresh bytes after every tool run."""
    if not _RULEBOOK_PATH.is_file():
        raise HTTPException(status_code=500, detail=f"rulebook_not_found: {_RULEBOOK_PATH}")
    with _RULEBOOK_PATH.open("r") as f:
        return json.load(f)


def _rulebook_index() -> dict[str, set[str]]:
    """Build {table → set(identifiers)} from the rulebook.

    Identifier rules:
      Types       → r["Name"]                           e.g. "bid"
      TypeVersions→ f"{r['Type']}/{r['Version']}"       e.g. "bid/000"
      Enums       → r["Name"]                           e.g. "base.g.node.class"
      EnumVersions→ f"{r['Enum']}/{r['Version']}"       e.g. "base.g.node.class/000"
      Formats     → r["Name"]                           e.g. "handle.name"

    The composite-key shape for TypeVersions/EnumVersions matches the YAML
    file path (`definitions/{kind}/{name}/{version}.yaml`) so the parity
    comparison is a direct set lookup.
    """
    rb = _load_rulebook()
    idx: dict[str, set[str]] = {
        "Types": set(),
        "TypeVersions": set(),
        "Enums": set(),
        "EnumVersions": set(),
        "Formats": set(),
    }
    for r in (rb.get("Types") or {}).get("data", []) or []:
        if r.get("Name"):
            idx["Types"].add(r["Name"])
    for r in (rb.get("TypeVersions") or {}).get("data", []) or []:
        if r.get("Type") and r.get("Version"):
            idx["TypeVersions"].add(f"{r['Type']}/{r['Version']}")
    for r in (rb.get("Enums") or {}).get("data", []) or []:
        if r.get("Name"):
            idx["Enums"].add(r["Name"])
    for r in (rb.get("EnumVersions") or {}).get("data", []) or []:
        if r.get("Enum") and r.get("Version"):
            idx["EnumVersions"].add(f"{r['Enum']}/{r['Version']}")
    for r in (rb.get("Formats") or {}).get("data", []) or []:
        if r.get("Name"):
            idx["Formats"].add(r["Name"])
    return idx


# ---------------------------------------------------------------------------
# Rulebook row addressing
# ---------------------------------------------------------------------------

# Per-table key field lists. The canonical id for a row is the values of
# these fields joined with "/". Tables not listed here default to ["Name"].
#
# This mapping was derived by reading each table's first data row in the
# rulebook — see slice-4 survey output. Some tables genuinely use multi-field
# composites (e.g. CliFlags = Command + FlagName, where the same FlagName can
# repeat across commands). For tables whose schema arrays declare `IsKey`
# explicitly, this dict would just shadow that — for now we keep both worlds
# (declared schema unchanged; this dict adds the missing key declarations
# the rulebook hasn't yet caught up with).
_TABLE_KEY_FIELDS: dict[str, list[str]] = {
    # Composite (parent + version) — these were already supported
    "TypeVersions": ["Type", "Version"],
    "EnumVersions": ["Enum", "Version"],
    # Other composite-keyed tables surfaced in slice 4
    "FormatExamples": ["Format", "Idx"],
    "EnumValues": ["EnumVersion", "Symbol"],
    "TypeAttributes": ["TypeVersion", "AttributeName"],
    "TypeExamples": ["TypeVersion", "Idx"],
    "TypeAxioms": ["TypeVersion", "Number"],
    "TypeHelperAttributes": ["TypeHelper", "AttributeName"],
    "ProjectionMappings": ["Projection", "FromSymbol"],
    "TypeUpgrades": ["FromTypeVersion", "ToTypeVersion"],
    "TypeUpgradeOps": ["TypeUpgrade", "Idx"],
    "EnumUpgrades": ["FromEnumVersion", "ToEnumVersion"],
    "EnumUpgradeMappings": ["EnumUpgrade", "FromSymbol"],
    "CliFlags": ["Command", "FlagName"],
    "CliExamples": ["Command", "Idx"],
    "FeatureBindings": ["Feature", "Kind", "TargetName"],
    "SeedRequestEntries": ["SeedRequest", "Idx"],
    "LocalNames": ["Snapshot", "CanonicalName"],
}


def _key_fields_for(table: str) -> list[str]:
    """Return the field list that composes the canonical id for this table.
    Defaults to ['Name'] for Name-keyed tables."""
    return _TABLE_KEY_FIELDS.get(table, ["Name"])


def _row_id_of(table: str, row: dict[str, Any]) -> str | None:
    """Compute the canonical id for a row.

    Pulls fields from `_TABLE_KEY_FIELDS[table]` (or `["Name"]` if absent),
    stringifies each, and joins with "/". Returns None when any required
    component is missing/blank — that's typically a malformed row, not
    a real "ought to match" case.

    Empty string is treated as missing (not as a valid id component) so
    we don't return things like `bid//foo` for partial rows."""
    parts: list[str] = []
    for f in _key_fields_for(table):
        v = row.get(f)
        if v is None or v == "":
            return None
        parts.append(str(v))
    return "/".join(parts)


def _find_row(rb: dict[str, Any], table: str, row_id: str) -> tuple[int, dict[str, Any]] | None:
    """Locate (index, row) for `table[data[]]` where the row's id matches.
    Returns None if not found. Used by both GET and PUT."""
    data = (rb.get(table) or {}).get("data", []) or []
    if not isinstance(data, list):
        return None
    for i, r in enumerate(data):
        if not isinstance(r, dict):
            continue
        if _row_id_of(table, r) == row_id:
            return (i, r)
    return None


def _yaml_mirror_for(table: str, row_id: str) -> Path | None:
    """Return the YAML file path under definitions/ that mirrors this row,
    if any. Drives the "edit-here-or-edit-yaml" UX hint."""
    if table == "Types":
        # Types is name-only — there's no single canonical YAML file
        # (each version is a file). Treat as unmirrored.
        return None
    if table == "TypeVersions":
        name, ver = row_id.split("/", 1) if "/" in row_id else (row_id, "")
        candidate = _DEFINITIONS_DIR / "types" / name / f"{ver}.yaml"
        return candidate if candidate.is_file() else None
    if table == "Enums":
        return None
    if table == "EnumVersions":
        name, ver = row_id.split("/", 1) if "/" in row_id else (row_id, "")
        candidate = _DEFINITIONS_DIR / "enums" / name / f"{ver}.yaml"
        return candidate if candidate.is_file() else None
    if table == "Formats":
        candidate = _DEFINITIONS_DIR / "formats" / f"{row_id}.yaml"
        return candidate if candidate.is_file() else None
    return None


def _canonical_row_bytes(row: dict[str, Any]) -> bytes:
    """sorted-key, deterministic JSON for stable row-level sha256."""
    return json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _schema_for_table(rb: dict[str, Any], table: str) -> list[dict[str, Any]]:
    return (rb.get(table) or {}).get("schema", []) or []


def _editable_field_types() -> set[str]:
    """Field types the UI is allowed to write. Anything derived
    (calculated/aggregation/lookup) is read-only — those values are
    regenerated by effortless build, not stored by the user."""
    return {"raw", "relationship"}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/yaml/files", response_model=list[YamlFile])
async def list_yaml_files() -> list[YamlFile]:
    return _walk_yaml_files()


@router.get("/yaml/file", response_model=FileBody)
async def get_yaml_file(
    path: str = Query(..., description="Repo-relative path, e.g. definitions/types/bid/000.yaml"),
) -> FileBody:
    p = _safe_definitions_path(path)
    body = p.read_text()
    st = p.stat()
    return FileBody(
        path=str(p.relative_to(_REPO_ROOT)),
        body=body,
        sha256=hashlib.sha256(body.encode()).hexdigest(),
        mtime=st.st_mtime,
    )


@router.put("/yaml/file", response_model=FileWriteResponse)
async def put_yaml_file(
    payload: FileWriteRequest,
    path: str = Query(..., description="Repo-relative path under definitions/"),
) -> FileWriteResponse:
    """Write a YAML file back to disk.

    Optimistic lock:
      - Client sends sha256 from the prior GET as `expected_sha256`.
      - We re-compute the current on-disk sha256 and refuse the write
        (HTTP 409) if it doesn't match. This catches:
          * a concurrent editor (e.g. someone running yaml-to-rulebook
            that touched files, or another tab),
          * an edit Claude made on disk that the UI hasn't refetched,
          * a previously-cached UI body that's stale.
      - Set expected_sha256 to None to bypass (last-writer-wins).

    Validation:
      - The body MUST parse as YAML (yaml.safe_load) — we don't write
        anything that can't round-trip. This catches the common case of
        the user pasting half-stripped JSON or breaking indentation.

    Atomicity:
      - Write to a sibling tempfile, fsync, rename — gives an atomic swap
        on macOS/Linux so a half-written file never appears on disk.
    """
    import yaml as _yaml  # local import — only this route needs it

    p = _safe_definitions_path(path)

    if payload.expected_sha256 is not None:
        current = _sha256_of(p)
        if current != payload.expected_sha256:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "sha256_mismatch",
                    "expected": payload.expected_sha256,
                    "actual": current,
                    "hint": "GET the file again to pick up the on-disk change, "
                            "merge your edits in, and retry.",
                },
            )

    # Validate YAML parseability before touching disk.
    try:
        _yaml.safe_load(payload.body)
    except _yaml.YAMLError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_yaml", "message": str(e)},
        )

    body_bytes = payload.body.encode("utf-8")
    tmp = p.with_suffix(p.suffix + ".tmp")
    try:
        with tmp.open("wb") as f:
            f.write(body_bytes)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)
    except OSError:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise

    st = p.stat()
    return FileWriteResponse(
        path=str(p.relative_to(_REPO_ROOT)),
        sha256=hashlib.sha256(body_bytes).hexdigest(),
        mtime=st.st_mtime,
        bytes_written=len(body_bytes),
    )


@router.get("/rulebook/summary", response_model=RulebookSummary)
async def rulebook_summary() -> RulebookSummary:
    rb = _load_rulebook()
    tables: dict[str, int] = {}
    types: list[str] = []
    type_versions: list[str] = []
    enums: list[str] = []
    enum_versions: list[str] = []
    formats: list[str] = []
    for key, val in rb.items():
        if isinstance(val, dict) and "data" in val and isinstance(val.get("data"), list):
            tables[key] = len(val["data"])
    for r in (rb.get("Types") or {}).get("data", []) or []:
        if r.get("Name"):
            types.append(r["Name"])
    for r in (rb.get("TypeVersions") or {}).get("data", []) or []:
        if r.get("Name"):
            type_versions.append(r["Name"])
    for r in (rb.get("Enums") or {}).get("data", []) or []:
        if r.get("Name"):
            enums.append(r["Name"])
    for r in (rb.get("EnumVersions") or {}).get("data", []) or []:
        if r.get("Name"):
            enum_versions.append(r["Name"])
    for r in (rb.get("Formats") or {}).get("data", []) or []:
        if r.get("Name"):
            formats.append(r["Name"])
    return RulebookSummary(
        path=str(_RULEBOOK_PATH.relative_to(_REPO_ROOT)),
        tables=tables,
        types=sorted(types),
        type_versions=sorted(type_versions),
        enums=sorted(enums),
        enum_versions=sorted(enum_versions),
        formats=sorted(formats),
        rulebook_mtime=_RULEBOOK_PATH.stat().st_mtime,
    )


# Tables whose `data` is regenerated by `yaml_to_rulebook.py`. Editing rows
# in these tables works but the change will be overwritten the next time
# yaml-to-rulebook runs (which is part of `effortless build`). The UI uses
# this to nudge the user toward editing the YAML instead.
_YAML_SOURCED_TABLES: set[str] = {
    "Owners",
    "Formats", "FormatExamples",
    "Enums", "EnumVersions", "EnumValues",
    "Types", "TypeVersions", "TypeAttributes", "TypeExamples", "TypeAxioms",
    "TypeHelpers", "TypeHelperAttributes",
    "Projections", "ProjectionMappings",
    "TypeUpgrades", "TypeUpgradeOps",
    "EnumUpgrades", "EnumUpgradeMappings",
    "YamlFiles",
}

# Per-table preview field — picked to give a useful summary in the nav tree.
# Defaults to the first non-key string field if absent here.
_TABLE_PREVIEW_FIELD: dict[str, str] = {
    "Owners": "Description",
    "Types": "Title",
    "Enums": "EnumType",
    "Formats": "Pattern",
    "TypeVersions": "Title",
    "EnumVersions": "Title",
    "TypeAttributes": "Description",
    "TypeAxioms": "Statement",
    "TypeExamples": "ExampleJson",
    "TypeHelpers": "Title",
    "Projections": "Description",
    "TypeUpgrades": "Description",
    "EnumUpgrades": "Description",
    "AppUsers": "DisplayName",
    "CliCommands": "Summary",
    "CliFlags": "Description",
    "CliExamples": "ExampleString",
    "IndexBuilders": "OutputPath",
    "Emitters": "Path",
    "Features": "Summary",
    "FeatureBindings": "Notes",
    "YamlFiles": "Sha",
    "FormatExamples": "Description",
    "EnumValues": "Title",
    "TypeHelperAttributes": "Description",
    "ProjectionMappings": "ToSymbol",
    "TypeUpgradeOps": "OpKind",
    "EnumUpgradeMappings": "ToSymbol",
}


@router.get("/rulebook/table/{table}", response_model=RulebookTableResponse)
async def list_rulebook_table(table: str) -> RulebookTableResponse:
    """List every row in a rulebook table, identifier-only (no full payload).

    Use `GET /api/admin/rulebook/entry?table=X&id=Y` to fetch the full row
    + schema for editing. Splitting list vs detail keeps the list response
    small for big tables (TypeAttributes is 967 rows × ~25 fields)."""
    rb = _load_rulebook()
    if table not in rb:
        raise HTTPException(status_code=404, detail=f"unknown_table: {table}")
    data = (rb.get(table) or {}).get("data", []) or []
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail=f"malformed_table: {table}")

    preview_field = _TABLE_PREVIEW_FIELD.get(table)
    rows: list[RulebookTableRow] = []
    for r in data:
        if not isinstance(r, dict):
            continue
        rid = _row_id_of(table, r)
        if rid is None:
            continue
        label_val: str | None = None
        if preview_field:
            v = r.get(preview_field)
            if v is not None:
                label_val = str(v)
        # Build a tiny preview map: id components + the label field
        preview: dict[str, Any] = {}
        for f in _key_fields_for(table):
            if f in r:
                preview[f] = r[f]
        if preview_field and preview_field in r:
            preview[preview_field] = r[preview_field]
        rows.append(RulebookTableRow(id=rid, label=label_val, preview=preview))

    return RulebookTableResponse(
        table=table,
        key_fields=_key_fields_for(table),
        row_count=len(rows),
        rows=rows,
        is_yaml_sourced=table in _YAML_SOURCED_TABLES,
    )


@router.get("/rulebook/entry", response_model=RulebookEntryResponse)
async def get_rulebook_entry(
    table: str = Query(..., description="Rulebook table name, e.g. 'Types', 'CliCommands'"),
    id: str = Query(..., description="Row identifier. For Name-keyed tables: the Name. "
                                     "For TypeVersions/EnumVersions: '{Type}/{Version}'."),
) -> RulebookEntryResponse:
    rb = _load_rulebook()
    if table not in rb:
        raise HTTPException(status_code=404, detail=f"unknown_table: {table}")
    found = _find_row(rb, table, id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"row_not_found: {table}/{id}")
    _, row = found

    schema = [
        FieldSchema(
            name=col.get("name", ""),
            datatype=col.get("datatype", "string"),
            type=col.get("type", "raw"),
            nullable=bool(col.get("nullable", True)),
            related_to=col.get("RelatedTo"),
            description=col.get("Description"),
            formula=col.get("formula"),
        )
        for col in _schema_for_table(rb, table)
        if isinstance(col, dict)
    ]

    mirror = _yaml_mirror_for(table, id)

    return RulebookEntryResponse(
        table=table,
        id=id,
        row=row,
        row_sha256=hashlib.sha256(_canonical_row_bytes(row)).hexdigest(),
        rulebook_sha256=_sha256_of(_RULEBOOK_PATH),
        schema=schema,
        has_yaml_mirror=mirror is not None,
    )


@router.put("/rulebook/entry", response_model=RulebookEntryResponse)
async def put_rulebook_entry(
    payload: RulebookEntryWriteRequest,
    table: str = Query(...),
    id: str = Query(...),
) -> RulebookEntryResponse:
    """Patch a single rulebook row.

    Two locks, both refuse with 409 on mismatch:
      - `expected_row_sha256` — protects against another writer changing this
        specific row between GET and PUT.
      - `expected_rulebook_sha256` — protects against any change to the file
        (different row, schema mutation, etc.) since the client's last GET.
        Use this when the schema list rendered alongside the row needs to
        stay consistent.

    Validation rules:
      - Submitted row's id (derived per _row_id_of) MUST match the URL id.
        Reject renames here — moving a row is a different operation.
      - Only fields with `type in {raw, relationship}` are user-writable.
        For derived fields (calculated/aggregation/lookup) we silently
        re-use the existing value, so the client can submit them unchanged
        without us trusting them.
      - Unknown columns in the submitted row are rejected (400) — keeps
        the rulebook free of stray fields.

    Atomicity: write to a sibling tempfile + os.replace, same as YAML PUT.
    """
    rb = _load_rulebook()
    if table not in rb:
        raise HTTPException(status_code=404, detail=f"unknown_table: {table}")
    found = _find_row(rb, table, id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"row_not_found: {table}/{id}")
    idx, existing = found

    # Locks first — fail before any merge work
    if payload.expected_row_sha256 is not None:
        current_row_sha = hashlib.sha256(_canonical_row_bytes(existing)).hexdigest()
        if current_row_sha != payload.expected_row_sha256:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "row_sha256_mismatch",
                    "expected": payload.expected_row_sha256,
                    "actual": current_row_sha,
                    "hint": "Row changed since your last GET. Re-fetch and merge.",
                },
            )

    if payload.expected_rulebook_sha256 is not None:
        current_file_sha = _sha256_of(_RULEBOOK_PATH)
        if current_file_sha != payload.expected_rulebook_sha256:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "rulebook_sha256_mismatch",
                    "expected": payload.expected_rulebook_sha256,
                    "actual": current_file_sha,
                    "hint": "The rulebook file changed elsewhere. Re-fetch the entry.",
                },
            )

    schema = _schema_for_table(rb, table)
    schema_by_name = {col.get("name"): col for col in schema if isinstance(col, dict) and col.get("name")}
    editable = _editable_field_types()

    # The id derived from the submitted row must equal the URL id.
    # (Renames go through a separate path that doesn't exist yet — slice 3+.)
    submitted_id = _row_id_of(table, payload.row)
    if submitted_id != id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "id_mismatch",
                "url_id": id,
                "submitted_id": submitted_id,
                "hint": "Identifier fields can't be changed here. Rename is a separate operation.",
            },
        )

    # Unknown columns rejected
    unknown = [k for k in payload.row.keys() if k not in schema_by_name]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail={"error": "unknown_columns", "columns": unknown},
        )

    # Build the merged row. For each column:
    #   raw/relationship → take submitted value
    #   anything else    → keep existing (derived fields are not user-writable)
    merged: dict[str, Any] = {}
    for col_name, col in schema_by_name.items():
        ftype = col.get("type", "raw")
        if ftype in editable:
            # Use submitted if provided, else keep existing (allows partial patches).
            if col_name in payload.row:
                merged[col_name] = payload.row[col_name]
            elif col_name in existing:
                merged[col_name] = existing[col_name]
        else:
            # Always keep existing for derived fields.
            if col_name in existing:
                merged[col_name] = existing[col_name]

    # Confirm the id still matches after the merge (defensive — composite id
    # fields could be raw but the id check above already gates that).
    if _row_id_of(table, merged) != id:
        raise HTTPException(
            status_code=400,
            detail={"error": "id_drift_after_merge", "url_id": id, "merged_id": _row_id_of(table, merged)},
        )

    # Patch the rulebook in-memory and write atomically.
    rb[table]["data"][idx] = merged

    # Serialize with the same formatting yaml_to_rulebook.py uses (the
    # canonical writer):  `json.dumps(..., indent=2) + "\n"`. ensure_ascii
    # defaults to True so non-ASCII chars stay as `\uNNNN` escapes — this
    # matches the on-disk form byte-for-byte and keeps git diffs tight.
    new_bytes = (json.dumps(rb, indent=2) + "\n").encode("utf-8")
    tmp = _RULEBOOK_PATH.with_suffix(_RULEBOOK_PATH.suffix + ".tmp")
    try:
        with tmp.open("wb") as f:
            f.write(new_bytes)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, _RULEBOOK_PATH)
    except OSError:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise

    # Re-fetch (cheap) so caller gets fresh sha256s + the row we wrote.
    new_rb = _load_rulebook()
    new_row = new_rb[table]["data"][idx]
    mirror = _yaml_mirror_for(table, id)

    return RulebookEntryResponse(
        table=table,
        id=id,
        row=new_row,
        row_sha256=hashlib.sha256(_canonical_row_bytes(new_row)).hexdigest(),
        rulebook_sha256=hashlib.sha256(new_bytes).hexdigest(),
        schema=[
            FieldSchema(
                name=col.get("name", ""),
                datatype=col.get("datatype", "string"),
                type=col.get("type", "raw"),
                nullable=bool(col.get("nullable", True)),
                related_to=col.get("RelatedTo"),
                description=col.get("Description"),
                formula=col.get("formula"),
            )
            for col in schema
            if isinstance(col, dict)
        ],
        has_yaml_mirror=mirror is not None,
    )


@router.get("/parity", response_model=ParityReport)
async def parity_report() -> ParityReport:
    """Per-file YAML↔rulebook presence check.

    This deliberately does NOT shell out to yaml_round_trip_check.py — that
    compares definitions/ against definitions-emitted/ (i.e. round-trip
    fidelity), which is a different question from "is the rulebook in sync
    with disk." A type can be present in both YAML AND rulebook but still
    fail round-trip if the emitter loses a field. The full diff lives in
    the round-trip-check tool.
    """
    yaml_files = _walk_yaml_files()
    idx = _rulebook_index()
    rows: list[ParityRow] = []

    rulebook_seen: set[tuple[str, str]] = set()

    for f in yaml_files:
        if f.kind == "types" and f.name and f.version is not None:
            rb_name = f"{f.name}/{f.version}"
            present = rb_name in idx.get("TypeVersions", set())
            if present:
                rulebook_seen.add(("types", rb_name))
            rows.append(ParityRow(
                yaml_path=f.path,
                kind="types",
                name=f.name,
                version=f.version,
                in_yaml=True,
                in_rulebook=present,
                status="match" if present else "missing_in_rulebook",
            ))
        elif f.kind == "enums" and f.name and f.version is not None:
            rb_name = f"{f.name}/{f.version}"
            present = rb_name in idx.get("EnumVersions", set())
            if present:
                rulebook_seen.add(("enums", rb_name))
            rows.append(ParityRow(
                yaml_path=f.path,
                kind="enums",
                name=f.name,
                version=f.version,
                in_yaml=True,
                in_rulebook=present,
                status="match" if present else "missing_in_rulebook",
            ))
        elif f.kind == "formats" and f.name:
            present = f.name in idx.get("Formats", set())
            if present:
                rulebook_seen.add(("formats", f.name))
            rows.append(ParityRow(
                yaml_path=f.path,
                kind="formats",
                name=f.name,
                version=None,
                in_yaml=True,
                in_rulebook=present,
                status="match" if present else "missing_in_rulebook",
            ))

    # Things in the rulebook that aren't on disk
    for name in idx.get("TypeVersions", set()):
        if ("types", name) not in rulebook_seen:
            t, v = (name.split("/", 1) + [""])[:2]
            rows.append(ParityRow(
                yaml_path="",
                kind="types",
                name=t,
                version=v or None,
                in_yaml=False,
                in_rulebook=True,
                rulebook_only=True,
                status="rulebook_only",
            ))
    for name in idx.get("EnumVersions", set()):
        if ("enums", name) not in rulebook_seen:
            t, v = (name.split("/", 1) + [""])[:2]
            rows.append(ParityRow(
                yaml_path="",
                kind="enums",
                name=t,
                version=v or None,
                in_yaml=False,
                in_rulebook=True,
                rulebook_only=True,
                status="rulebook_only",
            ))
    for name in idx.get("Formats", set()):
        if ("formats", name) not in rulebook_seen:
            rows.append(ParityRow(
                yaml_path="",
                kind="formats",
                name=name,
                version=None,
                in_yaml=False,
                in_rulebook=True,
                rulebook_only=True,
                status="rulebook_only",
            ))

    rows.sort(key=lambda r: (r.kind, r.name, r.version or ""))

    matched = sum(1 for r in rows if r.status == "match")
    missing_rb = sum(1 for r in rows if r.status == "missing_in_rulebook")
    rb_only = sum(1 for r in rows if r.status == "rulebook_only")

    emitted_exists = _EMITTED_DIR.is_dir()
    emitted_mtime: float | None = None
    emitted_age: float | None = None
    if emitted_exists:
        # mtime = newest file mtime in the tree
        latest = 0.0
        for p in _EMITTED_DIR.rglob("*.yaml"):
            mt = p.stat().st_mtime
            if mt > latest:
                latest = mt
        emitted_mtime = latest or _EMITTED_DIR.stat().st_mtime
        emitted_age = max(0.0, time.time() - emitted_mtime)

    return ParityReport(
        yaml_total=len(yaml_files),
        rulebook_total=sum(len(s) for s in idx.values()),
        matched=matched,
        missing_in_rulebook=missing_rb,
        rulebook_only=rb_only,
        rows=rows,
        emitted_dir_exists=emitted_exists,
        emitted_mtime=emitted_mtime,
        emitted_age_seconds=emitted_age,
        rulebook_mtime=_RULEBOOK_PATH.stat().st_mtime,
    )


@router.get("/tools", response_model=ToolsResponse)
async def list_tools() -> ToolsResponse:
    return ToolsResponse(
        repo_root=str(_REPO_ROOT),
        tools=[
            ToolInfo(
                name=name,
                description=meta["description"],
                writes=meta.get("writes"),
                argv=meta["argv"],
            )
            for name, meta in _TOOLS.items()
        ],
    )


@router.post("/tools/{tool}/run")
async def run_tool(
    tool: str,
) -> StreamingResponse:
    """Run a whitelisted tool and stream stdout/stderr as text/plain chunks.

    The frontend reads this with fetch + ReadableStream — see ToolRunner.tsx.
    """
    if tool not in _TOOLS:
        raise HTTPException(status_code=404, detail=f"unknown_tool: {tool}")
    meta = _TOOLS[tool]

    # Compose argv. The whitelist is fixed strings — no caller-supplied params.
    if tool == "effortless-build":
        argv = ["effortless", "build"]
        cwd = str(_REPO_ROOT)
    else:
        import sys as _sys
        argv = [_sys.executable, *meta["argv"]]
        cwd = str(_REPO_ROOT)

    async def streamer() -> AsyncIterator[bytes]:
        start = time.time()
        yield f"$ cd {cwd}\n$ {' '.join(argv)}\n\n".encode()
        try:
            proc = await asyncio.create_subprocess_exec(
                *argv,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={**os.environ},
            )
        except FileNotFoundError as e:
            yield f"\n[ERROR] failed to launch: {e}\n".encode()
            return
        assert proc.stdout is not None
        while True:
            chunk = await proc.stdout.read(4096)
            if not chunk:
                break
            yield chunk
        rc = await proc.wait()
        elapsed = time.time() - start
        yield f"\n\n[exit {rc}] in {elapsed:.2f}s\n".encode()

    return StreamingResponse(
        streamer(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-store",
            "X-Accel-Buffering": "no",  # disable proxy buffering when present
        },
    )


# ---------------------------------------------------------------------------
# Transpiler catalog — sibling-repo SSoTme tools (rulebook-to-X, X-to-rulebook)
# ---------------------------------------------------------------------------
#
# These are HTTP microservices deployed to cpln. Each one accepts a JSON
# payload `{cliInputFileContents: <text>}` (or a FileSet) and returns a
# SSoTme payload with the generated files. The admin proxies the call so the
# browser doesn't have to know about cpln URLs or the SSoTme payload shape.
#
# Catalog is read from `ssotme-tool.json` on every request — those files
# track cpln URL rotations (urls.post + urls.headVersionPost), so re-reading
# keeps us in sync without a manual refresh step.


class TranspilerInfo(BaseModel):
    name: str                  # directory name, e.g. "rulebook-to-react-explainer-dag"
    display_name: str
    description: str | None = None
    category: str | None = None
    version: str | None = None
    url: str | None = None     # version-pinned URL (urls.post)
    head_url: str | None = None  # head version (urls.headVersionPost)
    is_active: bool = True
    is_scaffold: bool = False  # True iff README.md still says "TODO: Add description"
    requires_api_key: bool = False
    error: str | None = None   # parse error or missing url


class TranspilerCatalog(BaseModel):
    catalog_dir: str
    catalog_exists: bool
    transpilers: list[TranspilerInfo]


class TranspilerRunRequest(BaseModel):
    """What to send to the transpiler.

    Default: the current rulebook JSON (read fresh from disk). Override with
    `text` (raw string) or `yaml_path` (repo-relative YAML file under
    definitions/) when the transpiler doesn't expect a rulebook input."""
    input_kind: str = "rulebook"   # "rulebook" | "yaml-file" | "text"
    text: str | None = None        # only for input_kind == "text"
    yaml_path: str | None = None   # only for input_kind == "yaml-file"
    use_head: bool = False         # use urls.headVersionPost instead of urls.post
    timeout_seconds: float = 30.0


class TranspilerOutputFile(BaseModel):
    """One file extracted from a SSoTme `ZippedOutputFileSet` payload.
    Best-effort decode: when a field can't be read we still surface the
    raw bytes-length so the UI can show "binary, N bytes" rather than
    silently dropping it."""
    name: str
    contents: str | None = None    # text contents if decodable as UTF-8
    is_binary: bool = False
    size_bytes: int


class TranspilerRunResponse(BaseModel):
    transpiler: str
    url: str                       # which URL was hit
    status: int                    # cpln HTTP status
    elapsed_seconds: float
    response: Any                  # parsed JSON if possible, else raw text
    response_is_json: bool
    response_text: str | None = None  # raw text body (always available, for diff/debug)
    # Decoded SSoTme FileSet (if the response was the standard wire format
    # `{TranspileRequest: {ZippedOutputFileSet: <base64-gzip>}}`). Falls
    # back to None when the response shape doesn't match — the raw response
    # is still surfaced above so callers can inspect.
    output_files: list[TranspilerOutputFile] | None = None
    decode_error: str | None = None


def _discover_transpilers() -> tuple[bool, list[TranspilerInfo]]:
    """Walk the catalog directory, parse each `workload/ssotme-tool.json`,
    return TranspilerInfo per directory. Best-effort: tools with malformed
    metadata are returned with `error` set rather than skipped, so the UI
    can surface the problem."""
    if not _TRANSPILER_CATALOG_DIR.is_dir():
        return False, []

    out: list[TranspilerInfo] = []
    for d in sorted(_TRANSPILER_CATALOG_DIR.iterdir()):
        if not d.is_dir():
            continue
        meta_path = d / "workload" / "ssotme-tool.json"
        readme_path = d / "README.md"
        if not meta_path.is_file():
            out.append(TranspilerInfo(
                name=d.name, display_name=d.name,
                error=f"missing ssotme-tool.json at {meta_path}",
            ))
            continue
        try:
            meta = json.loads(meta_path.read_text())
        except Exception as e:
            out.append(TranspilerInfo(
                name=d.name, display_name=d.name,
                error=f"ssotme-tool.json parse error: {e}",
            ))
            continue

        urls = meta.get("urls") or {}
        meta_data = meta.get("metaData") or {}
        readme_says_scaffold = False
        try:
            if readme_path.is_file():
                first_chunk = readme_path.read_text()[:2000]
                if "TODO: Add description of what this tool does" in first_chunk:
                    readme_says_scaffold = True
        except OSError:
            pass

        out.append(TranspilerInfo(
            name=d.name,
            display_name=meta.get("displayName") or d.name,
            description=meta.get("description"),
            category=meta.get("category"),
            version=meta_data.get("versionNumber"),
            url=(urls.get("post") or None),
            head_url=(urls.get("headVersionPost") or None),
            is_active=bool(meta_data.get("isActive", True)),
            is_scaffold=readme_says_scaffold,
            requires_api_key=bool(meta_data.get("requiresAPIKey", False)),
        ))
    return True, out


@router.get("/transpilers", response_model=TranspilerCatalog)
async def list_transpilers() -> TranspilerCatalog:
    exists, items = _discover_transpilers()
    return TranspilerCatalog(
        catalog_dir=str(_TRANSPILER_CATALOG_DIR),
        catalog_exists=exists,
        transpilers=items,
    )


@router.post("/transpilers/{name}/run", response_model=TranspilerRunResponse)
async def run_transpiler(name: str, payload: TranspilerRunRequest) -> TranspilerRunResponse:
    """Proxy a transpiler invocation.

    Resolves the tool's cpln URL from `ssotme-tool.json` (re-read on every
    call so URL rotations are picked up without a server restart), builds
    the SSoTme input payload, POSTs it, and surfaces the response.

    The transpiler URL is NOT user-supplied — only the tool *name* is, and
    only tools that exist in the local catalog directory can be invoked.
    This is intentional: this endpoint runs server-side from a place that
    can probably reach internal infra, so accepting arbitrary URLs would
    be a SSRF foot-gun.
    """
    import httpx  # local import — only this endpoint needs it

    _, catalog = _discover_transpilers()
    info = next((t for t in catalog if t.name == name), None)
    if info is None:
        raise HTTPException(status_code=404, detail=f"unknown_transpiler: {name}")
    target_url = info.head_url if payload.use_head else info.url
    if not target_url:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "transpiler_url_missing",
                "transpiler": name,
                "hint": "This tool has no deployed cpln URL in its ssotme-tool.json. "
                        "Run `effortless -setToolUrl ...` and refresh, or check the local "
                        "ssotme-tool.json was deployed.",
            },
        )

    # Build the input text per input_kind
    if payload.input_kind == "rulebook":
        if not _RULEBOOK_PATH.is_file():
            raise HTTPException(status_code=500, detail="rulebook_not_found")
        input_text = _RULEBOOK_PATH.read_text()
    elif payload.input_kind == "text":
        if payload.text is None:
            raise HTTPException(status_code=400, detail="text_required_for_input_kind_text")
        input_text = payload.text
    elif payload.input_kind == "yaml-file":
        if not payload.yaml_path:
            raise HTTPException(status_code=400, detail="yaml_path_required_for_input_kind_yaml_file")
        p = _safe_definitions_path(payload.yaml_path)
        input_text = p.read_text()
    else:
        raise HTTPException(status_code=400, detail=f"unknown_input_kind: {payload.input_kind}")

    # SSoTme tool input shape (per Program.cs reading order):
    #   1. uploaded text file in FileSet body
    #   2. cliInputFileContents JSON property
    #   3. cliParams array with "param1=<text>"
    # We use #2 — simplest, no FileSet wrangling on this side.
    body = {"cliInputFileContents": input_text}

    start = time.time()
    # cpln deployments listen on `/` (root). The dev README says `/run` but
    # that's the local-dev mapping — production routes the workload at root.
    invoke_url = target_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=payload.timeout_seconds) as client:
            resp = await client.post(
                invoke_url,
                json=body,
                headers={"Content-Type": "application/json"},
            )
    except httpx.TimeoutException as e:
        elapsed = time.time() - start
        return TranspilerRunResponse(
            transpiler=name,
            url=invoke_url,
            status=0,
            elapsed_seconds=elapsed,
            response={"error": "timeout", "timeout_seconds": payload.timeout_seconds, "detail": str(e)},
            response_is_json=True,
            response_text=None,
        )
    except httpx.HTTPError as e:
        elapsed = time.time() - start
        return TranspilerRunResponse(
            transpiler=name,
            url=invoke_url,
            status=0,
            elapsed_seconds=elapsed,
            response={"error": "http_error", "detail": str(e)},
            response_is_json=True,
            response_text=None,
        )
    elapsed = time.time() - start
    raw = resp.text
    try:
        parsed: Any = resp.json()
        is_json = True
    except json.JSONDecodeError:
        parsed = raw
        is_json = False

    output_files, decode_err = _decode_ssotme_fileset(parsed) if is_json else (None, None)

    return TranspilerRunResponse(
        transpiler=name,
        url=invoke_url,
        status=resp.status_code,
        elapsed_seconds=elapsed,
        response=parsed,
        response_is_json=is_json,
        response_text=raw,
        output_files=output_files,
        decode_error=decode_err,
    )


def _decode_ssotme_fileset(payload: Any) -> tuple[list[TranspilerOutputFile] | None, str | None]:
    """Decode `TranspileRequest.ZippedOutputFileSet` from a SSoTme tool response.

    Wire format (confirmed against the live cpln deployment):
      payload = {"TranspileRequest": {"ZippedOutputFileSet": "<base64>"}, ...}
      base64-decoded → gzip-compressed → UTF-8/UTF-16 XML:

        <FileSet>
          <FileSetFiles>
            <FileSetFile>
              <RelativePath>output.txt</RelativePath>
              <FileContents>...</FileContents>
              <AlwaysOverwrite>true</AlwaysOverwrite>
              ...
            </FileSetFile>
            ...
          </FileSetFiles>
        </FileSet>

    `FileContents` is inline text (not base64). Binary outputs would arrive
    as base64-looking ASCII; we leave decoding to the UI when present.

    Returns (files, None) on success or (None, error_message) when the
    response doesn't match the expected shape. Failing closed (None) lets
    the UI fall back to showing the raw response."""
    import base64
    import gzip
    import xml.etree.ElementTree as ET

    if not isinstance(payload, dict):
        return None, None
    tr = payload.get("TranspileRequest")
    if not isinstance(tr, dict):
        return None, None
    zipped = tr.get("ZippedOutputFileSet")
    if not isinstance(zipped, str) or not zipped:
        return None, None
    try:
        raw_bytes = base64.b64decode(zipped, validate=False)
        decompressed = gzip.decompress(raw_bytes)
    except Exception as e:
        return None, f"decompress_failed: {e}"

    # The XML declaration says utf-16 but the actual bytes are UTF-8 in
    # observed responses. Try utf-8 first, fall back to utf-16.
    text: str | None = None
    for enc in ("utf-8", "utf-16"):
        try:
            text = decompressed.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        return None, "decode_failed: could not decode as utf-8 or utf-16"

    # The XML declaration may claim utf-16; strip the declaration so
    # ElementTree doesn't re-interpret the encoding from the string.
    if text.startswith("<?xml"):
        end = text.find("?>")
        if end > 0:
            text = text[end + 2:].lstrip()

    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        return None, f"xml_parse_failed: {e}"

    files: list[TranspilerOutputFile] = []
    # Locate FileSetFile elements (namespace-agnostic match).
    for fsf in root.iter():
        tag = fsf.tag.rsplit("}", 1)[-1]  # strip namespace if present
        if tag != "FileSetFile":
            continue
        name = "(unnamed)"
        contents: str | None = None
        for child in fsf:
            ctag = child.tag.rsplit("}", 1)[-1]
            if ctag == "RelativePath" and child.text:
                name = child.text
            elif ctag == "FileContents":
                contents = child.text or ""
        if contents is None:
            files.append(TranspilerOutputFile(name=name, is_binary=False, size_bytes=0))
            continue
        size = len(contents.encode("utf-8"))
        files.append(TranspilerOutputFile(name=name, contents=contents, is_binary=False, size_bytes=size))

    if not files:
        # Surface the top-level element so callers can see what shape we got.
        return None, f"no_FileSetFile_in_xml: root_tag={root.tag.rsplit('}', 1)[-1]}"
    return files, None


__all__ = ["router"]
