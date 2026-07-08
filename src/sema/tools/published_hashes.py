"""Content-hash pins for published schema files — the immutability tripwire.

``definitions/published_hashes.yaml`` records the sha256 of every published
schema file. It is written by tooling (this module's CLI at the initial
write-out, ``sema promote`` afterwards) and committed; it is NOT a generated
index. ``tests/registry/test_published_hashes.py`` recomputes every hash, so
editing a published schema file fails the suite — the fix is a new version,
never an in-place change.

The CLI refuses to change an existing pin (that is the tripwire firing);
``--rewrite`` exists for a human-sanctioned correction and shows up as a
reviewable diff on the pin file.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_DIR = ROOT / "definitions"
PINS_PATH = DEFINITIONS_DIR / "published_hashes.yaml"
HEADER = """# Published schema content hashes — the immutability pin (OPS-445).
# Written by tooling (`python -m sema.tools.published_hashes`, `sema promote`),
# committed, and verified by tests/registry/test_published_hashes.py.
# A hash mismatch means a published schema file was edited in place;
# the fix is a NEW version, never an in-place change.
"""


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _schema_path(kind: str, name: str, version: str | None) -> Path:
    if version is None:
        return DEFINITIONS_DIR / kind / f"{name}.yaml"
    return DEFINITIONS_DIR / kind / name / f"{version}.yaml"


def compute_published_hashes(registry: dict[str, Any]) -> dict[str, Any]:
    """sha256 of every published schema file, keyed like the registry.

    Word-level published entries (formats, versionless types, literal enums)
    map name -> hash; versioned entries map name -> {version: hash}.
    """
    pins: dict[str, Any] = {"formats": {}, "enums": {}, "types": {}}

    for name, entry in registry["formats"].items():
        if entry["status"] == "published":
            pins["formats"][name] = _sha256(_schema_path("formats", name, None))

    for name, entry in registry["enums"].items():
        if entry["enum_type"] == "literal":
            if entry["status"] == "published":
                pins["enums"][name] = _sha256(_schema_path("enums", name, "000"))
            continue
        versions = {
            version: _sha256(_schema_path("enums", name, version))
            for version, version_entry in entry.get("versions", {}).items()
            if version_entry["status"] == "published"
        }
        if versions:
            pins["enums"][name] = dict(sorted(versions.items()))

    for name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            if entry["status"] == "published":
                pins["types"][name] = _sha256(_schema_path("types", name, None))
            continue
        versions = {
            version: _sha256(_schema_path("types", name, version))
            for version, version_entry in entry.get("versions", {}).items()
            if version_entry["status"] == "published"
        }
        if versions:
            pins["types"][name] = dict(sorted(versions.items()))

    return {kind: dict(sorted(pins[kind].items())) for kind in pins}


def load_pins() -> dict[str, Any]:
    if not PINS_PATH.exists():
        return {"formats": {}, "enums": {}, "types": {}}
    return yaml.safe_load(PINS_PATH.read_text())


def write_pins(pins: dict[str, Any]) -> None:
    with PINS_PATH.open("w") as handle:
        handle.write(HEADER + "\n")
        yaml.safe_dump(pins, handle, sort_keys=False)


def changed_pins(existing: dict[str, Any], computed: dict[str, Any]) -> list[str]:
    """Pins present in both whose hash differs — the tripwire condition."""
    changed: list[str] = []
    for kind in ("formats", "enums", "types"):
        for name, value in computed[kind].items():
            old = existing.get(kind, {}).get(name)
            if old is None:
                continue
            if isinstance(value, str):
                if isinstance(old, str) and old != value:
                    changed.append(f"{kind[:-1]} {name}")
                continue
            for version, digest in value.items():
                old_digest = old.get(version) if isinstance(old, dict) else None
                if old_digest is not None and old_digest != digest:
                    changed.append(f"{kind[:-1]} {name}:{version}")
    return sorted(changed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Allow changing an existing pin (human-sanctioned correction only).",
    )
    args = parser.parse_args()

    registry = yaml.safe_load((DEFINITIONS_DIR / "registry.yaml").read_text())
    computed = compute_published_hashes(registry)
    existing = load_pins()

    changed = changed_pins(existing, computed)
    if changed and not args.rewrite:
        print(
            "REFUSING to update pins — published schema files changed on disk:\n  "
            + "\n  ".join(changed)
            + "\nA published version is immutable; author a NEW version instead."
            "\n(--rewrite exists for a human-sanctioned correction.)"
        )
        return 1

    write_pins(computed)
    total = sum(
        1 if isinstance(v, str) else len(v)
        for kind in computed.values()
        for v in kind.values()
    )
    print(f"Wrote {total} published pins to {PINS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
