# tests/registry/test_structural_dependency_consistency.py

import re
from pathlib import Path
from typing import Any

import yaml
from yaml import YAMLError


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFINITIONS_DIR = REPO_ROOT / "definitions"


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def load_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def extract_refs(schema: dict) -> set[str]:
    """
    Recursively extract normalized external $ref dependencies from schema.
    """
    refs: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "$ref":
                    norm = normalize_ref(v)
                    if norm:
                        refs.add(norm)
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema)
    return refs


def normalize_ref(ref: str) -> str | None:
    """
    Convert $ref URLs to canonical dependency identifiers.

    Examples:
      https://schemas.electricity.works/types/foo.bar/001
        → foo.bar:001

      https://schemas.electricity.works/enums/gw1.unit/001
        → gw1.unit:001

      https://schemas.electricity.works/formats/uuid4.str
        → uuid4.str

      #/definitions/... → ignored
    """

    if ref.startswith("#"):
        return None  # internal reference

    parts = ref.strip("/").split("/")

    try:
        if "types" in parts:
            idx = parts.index("types")
            name = parts[idx + 1]
            version = parts[idx + 2]
            assert re.match(r"^\d{3}$", version)
            return f"{name}:{version}"

        if "enums" in parts:
            idx = parts.index("enums")
            name = parts[idx + 1]
            version = parts[idx + 2]
            assert re.match(r"^\d{3}$", version)
            return f"{name}:{version}"

        if "formats" in parts:
            idx = parts.index("formats")
            name = parts[idx + 1]
            return name

    except (IndexError, AssertionError):
        raise AssertionError(f"Malformed $ref: {ref}")

    raise AssertionError(f"Unrecognized $ref format: {ref}")


def schema_path_for(kind: str, name: str, version: str | None) -> Path:
    """
    Resolve schema path based on your folder structure.
    """

    if version is None:
        return DEFINITIONS_DIR / kind / f"{name}.yaml"

    return DEFINITIONS_DIR / kind / name / f"{version}.yaml"


# -----------------------------------------------------------------------------
# TEST
# -----------------------------------------------------------------------------

def test_structural_dependencies_match_schema_refs():
    registry = load_yaml(DEFINITIONS_DIR / "registry.yaml")

    types = registry["types"]
    mismatches: list[str] = []

    for type_name, entry in types.items():

        strategy = entry["versioning_strategy"]
        status = entry.get("status", "active")

        # Skip draft types (allowed to be inconsistent)
        if status == "draft":
            continue

        # ---------------------------------------------------------------------
        # Versionless types
        # ---------------------------------------------------------------------

        if strategy == "none":
            schema_path = schema_path_for("types", type_name, None)
            assert schema_path.exists(), f"Missing schema file for {type_name}"

            try:
                schema = load_yaml(schema_path)
            except YAMLError as e:
                mismatches.extend(
                    [
                        f"{type_name} schema could not be parsed",
                        f"  path: {schema_path}",
                        f"  error: {e}",
                    ]
                )
                continue
            refs = extract_refs(schema)

            expected = set(
                entry.get("direct_dependencies", {}).get("structural", [])
            )

            actual = set(refs)

            if expected != actual:
                missing_from_registry = sorted(actual - expected)
                extra_in_registry = sorted(expected - actual)
                mismatches.extend(
                    [
                        f"{type_name} structural deps mismatch",
                        f"  missing from registry: {missing_from_registry}",
                        f"  extra in registry: {extra_in_registry}",
                    ]
                )

            continue

        # ---------------------------------------------------------------------
        # Versioned types
        # ---------------------------------------------------------------------

        versions = entry["versions"]

        for version, v_entry in versions.items():

            schema_path = schema_path_for("types", type_name, version)
            assert schema_path.exists(), f"Missing schema file for {type_name}:{version}"

            try:
                schema = load_yaml(schema_path)
            except YAMLError as e:
                mismatches.extend(
                    [
                        f"{type_name}:{version} schema could not be parsed",
                        f"  path: {schema_path}",
                        f"  error: {e}",
                    ]
                )
                continue
            refs = extract_refs(schema)

            expected = set(
                v_entry["direct_dependencies"]["structural"]
            )

            actual = set(refs)

            if expected != actual:
                missing_from_registry = sorted(actual - expected)
                extra_in_registry = sorted(expected - actual)
                mismatches.extend(
                    [
                        f"{type_name}:{version} structural deps mismatch",
                        f"  missing from registry: {missing_from_registry}",
                        f"  extra in registry: {extra_in_registry}",
                    ]
                )

    if mismatches:
        raise AssertionError("\n".join(mismatches))
