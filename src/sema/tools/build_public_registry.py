from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "definitions" / "registry.yaml"
OUTPUT_PATH = ROOT / "indexes" / "public_registry.yaml"
HEADER = """# GENERATED FILE — DO NOT EDIT
# Generated from definitions/registry.yaml
#
# This registry excludes draft words and draft versions: it is the ACTIVE
# surface (staging + published) that runtime generation and snapshots consume.
# Every entry carries its explicit status; the published subset is the
# immutable, hash-pinned part eligible for schemas.electricity.works serving
# and non-dev brokers. Staging words are mutable and run on dev brokers only.
"""

ACTIVE_STATUSES = {"staging", "published"}
ALLOWED_STATUSES = {"draft", "staging", "published"}
# Formats never stage: their two states are draft and published.
FORMAT_STATUSES = {"draft", "published"}


def load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open("r") as handle:
        return yaml.safe_load(handle)


def entry_status(label: str, entry: dict[str, Any]) -> str:
    """The explicit status of a word or version entry. Absence is an error —
    there is no default status."""
    status = entry.get("status")
    if status is None:
        raise ValueError(f"{label}: missing required 'status' field")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"{label}: status {status!r} is not one of {sorted(ALLOWED_STATUSES)}")
    return status


def is_active(label: str, entry: dict[str, Any]) -> bool:
    return entry_status(label, entry) in ACTIVE_STATUSES


def sorted_versions(versions: dict[str, Any]) -> dict[str, Any]:
    return {
        version: versions[version]
        for version in sorted(versions, key=int, reverse=True)
    }


def validate_status_placement(registry: dict[str, Any]) -> None:
    """Per spec, ``status`` is REQUIRED on every entry and SHALL appear:

    - on the word entry for formats, versionless types, and literal enums;
    - on the version entry for versioned enums and versioned types.

    Formats never stage (``draft``/``published`` only). Any other placement or
    value is rejected up front — there is no default status.
    """
    bad: list[str] = []

    for name, entry in registry["formats"].items():
        status = entry.get("status")
        if status not in FORMAT_STATUSES:
            bad.append(
                f"format {name}: status {status!r} is not one of "
                f"{sorted(FORMAT_STATUSES)} (formats never stage)"
            )

    for name, entry in registry["enums"].items():
        if entry.get("enum_type") == "literal":
            if entry.get("status") not in ALLOWED_STATUSES:
                bad.append(f"enum {name}: missing or invalid word-level 'status'")
            continue
        if "status" in entry:
            bad.append(
                f"enum {name}: word-level 'status' is not allowed on a versioned enum; "
                "place it on the relevant version entry"
            )
        for version, version_entry in entry.get("versions", {}).items():
            if version_entry.get("status") not in ALLOWED_STATUSES:
                bad.append(f"enum {name}:{version}: missing or invalid 'status'")

    for name, entry in registry["types"].items():
        if entry.get("versioning_strategy") == "none":
            if entry.get("status") not in ALLOWED_STATUSES:
                bad.append(f"type {name}: missing or invalid word-level 'status'")
            continue
        if "status" in entry:
            bad.append(
                f"type {name}: word-level 'status' is not allowed on a versioned type; "
                "place it on the relevant version entry"
            )
        for version, version_entry in entry.get("versions", {}).items():
            if version_entry.get("status") not in ALLOWED_STATUSES:
                bad.append(f"type {name}:{version}: missing or invalid 'status'")

    if bad:
        raise ValueError("Registry status errors:\n  " + "\n  ".join(bad))


def build_public_registry(registry: dict[str, Any]) -> dict[str, Any]:
    validate_status_placement(registry)

    public: dict[str, Any] = {
        "metadata": copy.deepcopy(registry["metadata"]),
        "formats": {},
        "enums": {},
        "types": {},
    }

    for name, entry in registry["formats"].items():
        if is_active(f"format {name}", entry):
            public["formats"][name] = copy.deepcopy(entry)

    for name, entry in registry["enums"].items():
        if entry["enum_type"] == "literal":
            if is_active(f"enum {name}", entry):
                public["enums"][name] = copy.deepcopy(entry)
            continue

        active_versions = {
            version: copy.deepcopy(version_entry)
            for version, version_entry in entry.get("versions", {}).items()
            if is_active(f"enum {name}:{version}", version_entry)
        }
        if not active_versions:
            continue

        public_entry = copy.deepcopy(entry)
        public_entry["versions"] = sorted_versions(active_versions)
        public_entry["latest_version"] = max(active_versions, key=int)
        public["enums"][name] = public_entry

    for name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            if is_active(f"type {name}", entry):
                public["types"][name] = copy.deepcopy(entry)
            continue

        active_versions = {
            version: copy.deepcopy(version_entry)
            for version, version_entry in entry.get("versions", {}).items()
            if is_active(f"type {name}:{version}", version_entry)
        }
        if not active_versions:
            continue

        public_entry = copy.deepcopy(entry)
        public_entry["versions"] = sorted_versions(active_versions)
        public_entry["latest_version"] = max(active_versions, key=int)
        public["types"][name] = public_entry

    validate_dependency_closure(public)
    validate_published_closure(public)
    return public


def split_dep(dep: str) -> tuple[str, str | None]:
    if ":" in dep:
        name, version = dep.rsplit(":", 1)
        return name, version
    return dep, None


def validate_dependency_closure(registry: dict[str, Any]) -> None:
    missing: list[str] = []

    for type_name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            version_entries = {None: entry}
        else:
            version_entries = entry.get("versions", {})

        for version, version_entry in version_entries.items():
            source = type_name if version is None else f"{type_name}:{version}"
            direct_dependencies = version_entry.get("direct_dependencies", {})
            deps = (
                direct_dependencies.get("structural", [])
                + direct_dependencies.get("axiom", [])
            )

            for dep in deps:
                dep_name, dep_version = split_dep(dep)
                if dep_version is None:
                    if dep_name in registry["formats"]:
                        continue
                    dep_type = registry["types"].get(dep_name)
                    if dep_type and dep_type["versioning_strategy"] == "none":
                        continue
                    missing.append(f"{source} references missing public dependency {dep}")
                    continue

                dep_type = registry["types"].get(dep_name)
                if (
                    dep_type
                    and dep_type["versioning_strategy"] != "none"
                    and dep_version in dep_type.get("versions", {})
                ):
                    continue

                dep_enum = registry["enums"].get(dep_name)
                if dep_enum:
                    if dep_enum["enum_type"] == "literal" and dep_version == "000":
                        continue
                    if dep_version in dep_enum.get("versions", {}):
                        continue

                missing.append(f"{source} references missing public dependency {dep}")

    if missing:
        raise ValueError(
            "Public registry is not closed under dependencies:\n"
            + "\n".join(sorted(missing))
        )


def _active_status(registry: dict[str, Any], dep_name: str, dep_version: str | None) -> str | None:
    """Status of a dependency within the active registry, or None if absent."""
    if dep_version is None:
        fmt = registry["formats"].get(dep_name)
        if fmt is not None:
            return fmt["status"]
        dep_type = registry["types"].get(dep_name)
        if dep_type is not None and dep_type["versioning_strategy"] == "none":
            return dep_type["status"]
        return None

    dep_type = registry["types"].get(dep_name)
    if dep_type is not None and dep_type["versioning_strategy"] != "none":
        version_entry = dep_type.get("versions", {}).get(dep_version)
        return version_entry["status"] if version_entry else None

    dep_enum = registry["enums"].get(dep_name)
    if dep_enum is not None:
        if dep_enum["enum_type"] == "literal":
            return dep_enum["status"] if dep_version == "000" else None
        version_entry = dep_enum.get("versions", {}).get(dep_version)
        return version_entry["status"] if version_entry else None
    return None


def validate_published_closure(registry: dict[str, Any]) -> None:
    """A published version's full dependency closure must itself be published.

    Staging may reference staging or published; published referencing staging
    (or anything weaker) would let a mutable word change the meaning of an
    immutable one.
    """
    violations: list[str] = []

    for type_name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            version_entries = {None: entry}
        else:
            version_entries = entry.get("versions", {})

        for version, version_entry in version_entries.items():
            if version_entry["status"] != "published":
                continue
            source = type_name if version is None else f"{type_name}:{version}"
            direct_dependencies = version_entry.get("direct_dependencies", {})
            deps = (
                direct_dependencies.get("structural", [])
                + direct_dependencies.get("axiom", [])
            )
            for dep in deps:
                dep_name, dep_version = split_dep(dep)
                dep_status = _active_status(registry, dep_name, dep_version)
                if dep_status != "published":
                    violations.append(
                        f"published {source} depends on {dep} (status: {dep_status})"
                    )

    if violations:
        raise ValueError(
            "Published words must have a fully published dependency closure:\n  "
            + "\n  ".join(sorted(violations))
        )


def build() -> dict[str, Any]:
    """Regenerate ``indexes/public_registry.yaml`` from ``registry.yaml``.

    Returns the public registry dict. Raises ``ValueError`` if the source
    registry is missing statuses, has misplaced status fields, if any active
    word references a missing (e.g. draft) dependency, or if a published
    version's closure is not fully published.
    """
    public = build_public_registry(load_registry())
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as handle:
        handle.write(HEADER + "\n")
        yaml.safe_dump(public, handle, sort_keys=False)
    print(f"Wrote public registry to {OUTPUT_PATH}")
    return public


if __name__ == "__main__":
    build()
