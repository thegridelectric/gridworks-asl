from __future__ import annotations

import yaml
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "indexes" / "public_registry.yaml"
OUTPUT_PATH = ROOT / "indexes" / "dependency_closure.yaml"
HEADER = """# GENERATED FILE — DO NOT EDIT
# Generated from indexes/public_registry.yaml
"""


def load_registry():
    with open(REGISTRY_PATH, "r") as f:
        return yaml.safe_load(f)


def split_dep(dep: str):
    if ":" in dep:
        name, version = dep.rsplit(":", 1)
        return name, version
    return dep, None


def classify(dep: str, registry) -> str:
    name, version = split_dep(dep)

    if version is None:
        if name not in registry["formats"]:
            raise ValueError(f"Unknown format dependency: {dep}")
        return "format"

    if name in registry["types"]:
        return "type"

    if name in registry["enums"]:
        return "enum"

    raise ValueError(f"Unknown versioned dependency: {dep}")


def get_direct_deps(type_def: dict) -> list[str]:
    deps = type_def.get("direct_dependencies", {})
    return list(set(
        deps.get("structural", []) +
        deps.get("axiom", [])
    ))


def compute_closure(type_name: str, version: str, registry) -> dict:
    visited = set()
    stack = [(type_name, version)]

    closure = {
        "types": set(),
        "enums": set(),
        "formats": set(),
    }

    while stack:
        t_name, t_version = stack.pop()
        key = f"{t_name}:{t_version}"

        if key in visited:
            continue

        visited.add(key)

        types = registry["types"]

        if t_name not in types:
            raise ValueError(f"Unknown type referenced: {t_name}")

        versions = types[t_name]["versions"]

        if t_version not in versions:
            raise ValueError(f"Unknown version: {t_name}:{t_version}")

        type_def = versions[t_version]
        direct_deps = get_direct_deps(type_def)

        for dep in direct_deps:
            category = classify(dep, registry)

            closure[category + "s"].add(dep)

            if category == "type":
                dep_name, dep_version = split_dep(dep)

                if dep_version is None:
                    raise ValueError(f"Type dependency missing version: {dep}")

                stack.append((dep_name, dep_version))

    return {
        "types": sorted(closure["types"]),
        "enums": sorted(closure["enums"]),
        "formats": sorted(closure["formats"]),
    }


def build():
    registry = load_registry()

    output = {"types": {}}

    for type_name, type_def in registry["types"].items():
        if type_def.get("versioning_strategy") == "none":
            continue

        output["types"][type_name] = {}

        for version in type_def["versions"].keys():
            closure = compute_closure(type_name, version, registry)
            output["types"][type_name][version] = closure

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        f.write(HEADER + "\n")
        yaml.dump(
            output,
            f,
            sort_keys=True,
        )

    print(f"Wrote dependency closure to {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
