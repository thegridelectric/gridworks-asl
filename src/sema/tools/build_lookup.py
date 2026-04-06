from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "definitions" / "registry.yaml"
OUTPUT_PATH = ROOT / "indexes" / "lookup.yaml"

HEADER = """# GENERATED FILE — DO NOT EDIT
# Generated from definitions/registry.yaml
#
# ------------------------------------------------------------------
# LOCAL LOOKUP (NON-AUTHORITATIVE)
#
# This file provides local resolution from Sema vocabulary words
# to schema files within this repository.
#
# Authority for all Sema vocabulary definitions SHALL be the
# canonical schema_url (https://schemas.electricity.works/...).
#
# This file is a convenience index for navigation and tooling.
# It MUST NOT be treated as a source of truth for schema content,
# versioning, or dependencies.
# ------------------------------------------------------------------
"""


def load_registry() -> dict:
    with open(REGISTRY_PATH, "r") as f:
        return yaml.safe_load(f)


def build() -> None:
    registry = load_registry()

    output: dict[str, dict] = {
        "types": {},
        "enums": {},
        "formats": {},
    }

    for type_name, type_def in registry["types"].items():
        if type_def["versioning_strategy"] == "none":
            output["types"][type_name] = {
                "versioning_strategy": "none",
                "schema": f"definitions/types/{type_name}.yaml",
            }
        else:
            versions = type_def.get("versions", {})
            output["types"][type_name] = {
                "latest_version": type_def["latest_version"],
                "versioning_strategy": type_def["versioning_strategy"],
                "versions": {
                    version: f"definitions/types/{type_name}/{version}.yaml"
                    for version in versions
                },
            }

    for enum_name, enum_def in registry["enums"].items():
        if enum_def["enum_type"] == "literal":
            output["enums"][enum_name] = {
                "enum_type": "literal",
                "schema": f"definitions/enums/{enum_name}/000.yaml",
            }
        else:
            versions = enum_def.get("versions", {})
            output["enums"][enum_name] = {
                "enum_type": "versioned",
                "latest_version": enum_def["latest_version"],
                "versions": {
                    version: f"definitions/enums/{enum_name}/{version}.yaml"
                    for version in versions
                },
            }

    for format_name in registry["formats"]:
        output["formats"][format_name] = f"definitions/formats/{format_name}.yaml"

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        f.write(HEADER + "\n")
        yaml.dump(
            output,
            f,
            sort_keys=False,
            default_flow_style=False,
        )

    print(f"Wrote lookup to {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
