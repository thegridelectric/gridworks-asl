"""
Three invariants over registry.yaml and indexes/public_registry.yaml:

1. ``indexes/public_registry.yaml`` is exactly what
   ``build_public_registry`` produces from the current ``registry.yaml``
   (non-draft words and non-draft versions only). Catches stale on-disk
   public registry files.

2. The public registry is closed under dependency. Active words SHALL NOT
   depend on draft words, transitively or directly. ``build_public_registry``
   calls ``validate_dependency_closure`` internally and raises ``ValueError``
   if any active word references something missing from the active surface.

3. Every registry entry's ``schema_url`` includes the ``/draft/`` path
   segment iff that entry's status is ``"draft"``. This keeps the URL on
   the registry side aligned with the schema file's ``$id`` (which already
   uses the same convention).
"""

from pathlib import Path

import yaml

from sema.tools.build_public_registry import build_public_registry, load_registry


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REGISTRY_PATH = REPO_ROOT / "indexes" / "public_registry.yaml"
DRAFT_URL_SEGMENT = "/draft/"


def test_public_registry_matches_registry_yaml() -> None:
    registry = load_registry()
    # Raises ValueError if any active word depends on a draft (or otherwise
    # missing) dependency, OR if status is misplaced (word-level on a
    # versioned word).
    expected = build_public_registry(registry)

    on_disk = yaml.safe_load(PUBLIC_REGISTRY_PATH.read_text())

    assert on_disk == expected, (
        "indexes/public_registry.yaml is stale. Regenerate with:\n"
        "  uv run python -m sema.tools.build_public_registry"
    )


def _check_schema_url_status(label: str, schema_url: str, status: str) -> str | None:
    has_draft = DRAFT_URL_SEGMENT in schema_url
    if status == "draft" and not has_draft:
        return f"{label}: status='draft' but schema_url does not contain '/draft/' ({schema_url})"
    if status != "draft" and has_draft:
        return f"{label}: status='{status}' but schema_url contains '/draft/' ({schema_url})"
    return None


def test_registry_schema_url_matches_status() -> None:
    registry = load_registry()
    findings: list[str] = []

    for name, entry in registry["formats"].items():
        url = entry.get("schema_url")
        if url is None:
            continue
        status = entry.get("status", "active")
        if msg := _check_schema_url_status(f"format {name}", url, status):
            findings.append(msg)

    for name, entry in registry["enums"].items():
        if entry.get("enum_type") == "literal":
            url = entry.get("schema_url")
            if url is None:
                continue
            status = entry.get("status", "active")
            if msg := _check_schema_url_status(f"enum {name}", url, status):
                findings.append(msg)
            continue
        for version, vd in entry.get("versions", {}).items():
            url = vd.get("schema_url")
            if url is None:
                continue
            status = vd.get("status", "active")
            if msg := _check_schema_url_status(f"enum {name}:{version}", url, status):
                findings.append(msg)

    for name, entry in registry["types"].items():
        if entry.get("versioning_strategy") == "none":
            url = entry.get("schema_url")
            if url is None:
                continue
            status = entry.get("status", "active")
            if msg := _check_schema_url_status(f"type {name}", url, status):
                findings.append(msg)
            continue
        for version, vd in entry.get("versions", {}).items():
            url = vd.get("schema_url")
            if url is None:
                continue
            status = vd.get("status", "active")
            if msg := _check_schema_url_status(f"type {name}:{version}", url, status):
                findings.append(msg)

    assert not findings, (
        "Registry schema_url / status mismatches:\n  " + "\n  ".join(findings)
    )
