from __future__ import annotations

import yaml
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple


# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "indexes" / "public_registry.yaml"
OUTPUT_PATH = ROOT / "indexes" / "reverse_dependencies.yaml"
HEADER = """# GENERATED FILE — DO NOT EDIT
# Generated from indexes/public_registry.yaml
"""


# -----------------------------------------------------------------------------
# LOAD
# -----------------------------------------------------------------------------

def load_registry() -> dict:
    with open(REGISTRY_PATH, "r") as f:
        return yaml.safe_load(f)


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def split_dep(dep: str) -> Tuple[str, str | None]:
    if ":" in dep:
        name, version = dep.rsplit(":", 1)
        return name, version
    return dep, None


def get_direct_deps(type_version_block: dict) -> List[str]:
    deps = type_version_block.get("direct_dependencies", {})
    structural = deps.get("structural", []) or []
    axiom = deps.get("axiom", []) or []
    return sorted(set(structural + axiom))


def classify(dep: str, registry: dict) -> str:
    name, version = split_dep(dep)

    if version is None:
        return "format"

    if name in registry.get("types", {}):
        return "type"

    if name in registry.get("enums", {}):
        return "enum"

    raise ValueError(f"Unknown dependency: {dep}")


# -----------------------------------------------------------------------------
# BUILD
# -----------------------------------------------------------------------------

def build() -> None:
    registry = load_registry()

    reverse = {
        "types": defaultdict(lambda: defaultdict(set)),
        "enums": defaultdict(lambda: defaultdict(set)),
        "formats": defaultdict(set),
    }

    types_registry = registry.get("types", {})

    for type_name, type_def in types_registry.items():
        for version, version_block in type_def.get("versions", {}).items():

            source = f"{type_name}:{version}"
            deps = get_direct_deps(version_block)

            for dep in deps:
                category = classify(dep, registry)
                name, dep_version = split_dep(dep)

                if category == "type":
                    if dep_version is None:
                        raise ValueError(f"Type dependency missing version: {dep}")
                    reverse["types"][name][dep_version].add(source)

                elif category == "enum":
                    if dep_version is None:
                        raise ValueError(f"Enum dependency missing version: {dep}")
                    reverse["enums"][name][dep_version].add(source)

                elif category == "format":
                    reverse["formats"][name].add(source)

    # -------------------------------------------------------------------------
    # Convert sets → sorted lists
    # -------------------------------------------------------------------------

    output = {
        "types": {},
        "enums": {},
        "formats": {},
    }

    for name in sorted(reverse["types"]):
        versions = reverse["types"][name]
        output["types"][name] = {}
        for version in sorted(versions, key=int):
            users = versions[version]
            output["types"][name][version] = {
                "used_by": sorted(users)
            }

    for name in sorted(reverse["enums"]):
        versions = reverse["enums"][name]
        output["enums"][name] = {}
        for version in sorted(versions, key=int):
            users = versions[version]
            output["enums"][name][version] = {
                "used_by": sorted(users)
            }

    for name in sorted(reverse["formats"]):
        users = reverse["formats"][name]
        output["formats"][name] = {
            "used_by": sorted(users)
        }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        f.write(HEADER + "\n")
        yaml.dump(
            output,
            f,
            sort_keys=False,
            default_flow_style=False,
        )

    print(f"✔ Reverse dependencies written to: {OUTPUT_PATH}")


# -----------------------------------------------------------------------------
# ENTRYPOINT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    build()
