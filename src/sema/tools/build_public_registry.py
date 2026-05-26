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
# This registry excludes draft words and draft versions. It is the publishable
# registry surface for schemas.electricity.works and public dependency indexes.
"""


def load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open("r") as handle:
        return yaml.safe_load(handle)


def is_published(entry: dict[str, Any]) -> bool:
    return entry.get("status", "published") == "published"


def sorted_versions(versions: dict[str, Any]) -> dict[str, Any]:
    return {
        version: versions[version]
        for version in sorted(versions, key=int, reverse=True)
    }


def validate_status_placement(registry: dict[str, Any]) -> None:
    """Per spec, ``status`` SHALL appear:

    - on the word entry for formats, versionless types, and literal enums;
    - on the version entry for versioned enums and versioned types.

    Any other placement is rejected up front so we never silently default a
    misplaced ``status`` to published.
    """
    bad: list[str] = []
    for name, entry in registry["enums"].items():
        if entry.get("enum_type") != "literal" and "status" in entry:
            bad.append(
                f"enum {name}: word-level 'status' is not allowed on a versioned enum; "
                "place it on the relevant version entry"
            )
    for name, entry in registry["types"].items():
        if entry.get("versioning_strategy") != "none" and "status" in entry:
            bad.append(
                f"type {name}: word-level 'status' is not allowed on a versioned type; "
                "place it on the relevant version entry"
            )
    if bad:
        raise ValueError("Misplaced status fields in registry:\n  " + "\n  ".join(bad))


def build_public_registry(registry: dict[str, Any]) -> dict[str, Any]:
    validate_status_placement(registry)

    public: dict[str, Any] = {
        "metadata": copy.deepcopy(registry["metadata"]),
        "formats": {},
        "enums": {},
        "types": {},
    }

    for name, entry in registry["formats"].items():
        if is_published(entry):
            public["formats"][name] = copy.deepcopy(entry)

    for name, entry in registry["enums"].items():
        if entry["enum_type"] == "literal":
            if is_published(entry):
                public["enums"][name] = copy.deepcopy(entry)
            continue

        published_versions = {
            version: copy.deepcopy(version_entry)
            for version, version_entry in entry.get("versions", {}).items()
            if is_published(version_entry)
        }
        if not published_versions:
            continue

        public_entry = copy.deepcopy(entry)
        public_entry["versions"] = sorted_versions(published_versions)
        public_entry["latest_version"] = max(published_versions, key=int)
        public["enums"][name] = public_entry

    for name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            if is_published(entry):
                public["types"][name] = copy.deepcopy(entry)
            continue

        published_versions = {
            version: copy.deepcopy(version_entry)
            for version, version_entry in entry.get("versions", {}).items()
            if is_published(version_entry)
        }
        if not published_versions:
            continue

        public_entry = copy.deepcopy(entry)
        public_entry["versions"] = sorted_versions(published_versions)
        public_entry["latest_version"] = max(published_versions, key=int)
        public["types"][name] = public_entry

    validate_dependency_closure(public)
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


def build() -> dict[str, Any]:
    """Regenerate ``indexes/public_registry.yaml`` from ``registry.yaml``.

    Returns the public registry dict. Raises ``ValueError`` if the source
    registry has misplaced status fields or if any published word references
    a missing (e.g. draft) dependency.
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
