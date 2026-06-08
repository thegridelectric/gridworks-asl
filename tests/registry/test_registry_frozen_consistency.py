"""Validate the frozen_at word-status (see spec/registry/structure.md).

frozen_at marks a word's version lineage as closed. It is a word-level field
(never on a version entry), an RFC 3339 timestamp, and gates new versions: no
version of a frozen word may be created after the freeze. replaced_by, where
present, must name existing words (it does not delete or invalidate anything).
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "definitions" / "registry.yaml"

SECTIONS = ("formats", "enums", "types")


def _load() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text())


def _parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


def _version_entries(entry: dict[str, Any]) -> dict[str, Any]:
    return entry.get("versions") or {}


def _created_timestamps(entry: dict[str, Any]) -> list[str]:
    versions = _version_entries(entry)
    if versions:
        return [v["created"] for v in versions.values() if "created" in v]
    return [entry["created"]] if "created" in entry else []


def test_frozen_at_is_word_level_and_well_formed() -> None:
    registry = _load()
    findings: list[str] = []

    for section in SECTIONS:
        for name, entry in registry.get(section, {}).items():
            for version, version_entry in _version_entries(entry).items():
                if "frozen_at" in version_entry:
                    findings.append(
                        f"{section} {name}:{version}: frozen_at is word-level only, "
                        "not allowed on a version entry"
                    )
            if "frozen_at" not in entry:
                continue
            try:
                _parse_ts(entry["frozen_at"])
            except (ValueError, TypeError):
                findings.append(
                    f"{section} {name}: frozen_at {entry['frozen_at']!r} is not an "
                    "RFC 3339 UTC timestamp (YYYY-MM-DDTHH:MM:SSZ)"
                )

    assert not findings, "\n".join(findings)


def test_frozen_word_has_no_version_created_after_freeze() -> None:
    registry = _load()
    findings: list[str] = []

    for section in SECTIONS:
        for name, entry in registry.get(section, {}).items():
            if "frozen_at" not in entry:
                continue
            try:
                frozen_at = _parse_ts(entry["frozen_at"])
            except (ValueError, TypeError):
                continue  # well-formedness covered by the other test
            for created in _created_timestamps(entry):
                if _parse_ts(created) > frozen_at:
                    findings.append(
                        f"{section} {name}: a version was created {created} after "
                        f"frozen_at {entry['frozen_at']} (no new versions once frozen)"
                    )

    assert not findings, "\n".join(findings)


def test_replaced_by_targets_exist() -> None:
    registry = _load()
    known = {
        name
        for section in SECTIONS
        for name in registry.get(section, {})
    }
    findings: list[str] = []

    for section in SECTIONS:
        for name, entry in registry.get(section, {}).items():
            replaced_by = entry.get("replaced_by")
            if replaced_by is None:
                continue
            assert isinstance(replaced_by, list), f"{name}: replaced_by must be a list"
            for target in replaced_by:
                if ":" in str(target):
                    findings.append(f"{name}: replaced_by {target!r} must not carry a version")
                elif target not in known:
                    findings.append(f"{name}: replaced_by {target!r} is not a registered word")

    assert not findings, "\n".join(findings)
