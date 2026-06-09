"""Every *superseded* type version MUST carry an `examples:` block.

Spec: ``spec/authoring/types.md`` "Examples" / "Superseded versions". A version
is superseded once a numerically higher version of the same type exists; the
latest version (and versionless types) stay optional. The example is the fixture
the snapshot round-trip exercises along the ``decode-old -> upgrade() ->
decode-current`` path, so a superseded version without one is silently untested.

Hard gate: the one-time backfill of existing old versions landed (OPS-380
thread 4), so every superseded version now carries an example.
"""

from __future__ import annotations

from pathlib import Path

import yaml

TYPES_DIR = Path("definitions/types")


def _superseded_versions_missing_examples() -> list[str]:
    # Collect versioned type files: definitions/types/<name>/<NNN>.yaml
    by_type: dict[str, list[tuple[str, Path]]] = {}
    for path in sorted(TYPES_DIR.rglob("*.yaml")):
        rel = path.relative_to(TYPES_DIR)
        if len(rel.parts) != 2:
            continue  # versionless type file at the top level
        version = rel.parts[1].removesuffix(".yaml")
        if not (len(version) == 3 and version.isdigit()):
            continue
        by_type.setdefault(rel.parts[0], []).append((version, path))

    missing: list[str] = []
    for type_name, versions in by_type.items():
        versions.sort()
        latest = versions[-1][0]
        for version, path in versions:
            if version == latest:
                continue  # latest stays optional
            schema = yaml.safe_load(path.read_text())
            if not schema.get("examples"):
                missing.append(f"{type_name}/{version}")
    return missing


def test_superseded_type_versions_have_examples() -> None:
    missing = _superseded_versions_missing_examples()
    assert not missing, (
        "Superseded type versions missing a required `examples:` block:\n  "
        + "\n  ".join(sorted(missing))
    )
