"""
Verify that the schema files under definitions/ agree with registry.yaml on
publication status (active vs draft).

Per docs/sema-specification.md (Registry Status Field):
- registry status defaults to "active" when omitted
- formats and versionless types: status lives on the word entry
- versioned enums and versioned types: status lives on each version entry

Schema-side encoding: the schema's lifecycle is recorded in the ``$id`` URL
itself. An active schema lives at::

    https://schemas.electricity.works/<kind>s/<name>[/<version>]

A draft schema lives at::

    https://schemas.electricity.works/draft/<kind>s/<name>[/<version>]

This makes draft status visible at line 2 of the file and turns "publish a
draft" into a literal one-token edit (drop the ``/draft`` segment).
"""

from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFINITIONS_DIR = REPO_ROOT / "definitions"
REGISTRY_PATH = DEFINITIONS_DIR / "registry.yaml"

ALLOWED = {"active", "draft"}
DEFAULT_STATUS = "active"
DRAFT_URL_SEGMENT = "/draft/"


def _load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def _registry_status(entry: dict, version: str | None = None) -> str:
    """Status placement rule (per spec §Registry Status Field):

    - Word-level: ONLY for versionless types, literal enums, and formats.
    - Version-level: ONLY for versioned types and versioned enums.

    A separate test (test_registry_status_placement) enforces that versioned
    words don't carry word-level status.
    """
    if version is None:
        return entry.get("status", DEFAULT_STATUS)
    return entry["versions"][version].get("status", DEFAULT_STATUS)


def _schema_status(schema: dict) -> str:
    schema_id = schema.get("$id", "")
    return "draft" if DRAFT_URL_SEGMENT in schema_id else "active"


def _format_path(name: str) -> Path:
    return DEFINITIONS_DIR / "formats" / f"{name}.yaml"


def _enum_path(name: str, version: str) -> Path:
    return DEFINITIONS_DIR / "enums" / name / f"{version}.yaml"


def _versioned_type_path(name: str, version: str) -> Path:
    return DEFINITIONS_DIR / "types" / name / f"{version}.yaml"


def _versionless_type_path(name: str) -> Path:
    return DEFINITIONS_DIR / "types" / f"{name}.yaml"


def _collect_mismatches() -> list[str]:
    """Return human-readable schema/registry status mismatches."""
    registry = _load(REGISTRY_PATH)
    mismatches: list[str] = []

    def check(label: str, path: Path, registry_status: str) -> None:
        if registry_status not in ALLOWED:
            mismatches.append(
                f"{label}: registry status={registry_status!r} is not one of {sorted(ALLOWED)}"
            )
            return
        schema = _load(path)
        schema_status = _schema_status(schema)
        if schema_status != registry_status:
            mismatches.append(
                f"{label}: registry={registry_status!r} but $id implies "
                f"{schema_status!r} (path: {path}, $id: {schema.get('$id')!r})"
            )

    for name, entry in registry["formats"].items():
        check(f"format {name}", _format_path(name), _registry_status(entry))

    for name, entry in registry["enums"].items():
        if entry.get("enum_type") == "literal":
            check(f"enum {name}", _enum_path(name, "000"), _registry_status(entry))
        else:
            for version in entry["versions"]:
                check(
                    f"enum {name}:{version}",
                    _enum_path(name, version),
                    _registry_status(entry, version),
                )

    for name, entry in registry["types"].items():
        if entry.get("versioning_strategy") == "none":
            check(f"type {name}", _versionless_type_path(name), _registry_status(entry))
        else:
            for version in entry["versions"]:
                check(
                    f"type {name}:{version}",
                    _versioned_type_path(name, version),
                    _registry_status(entry, version),
                )

    return mismatches


def test_schema_status_matches_registry() -> None:
    mismatches = _collect_mismatches()
    assert not mismatches, "Schema/registry status mismatches:\n  " + "\n  ".join(mismatches)
