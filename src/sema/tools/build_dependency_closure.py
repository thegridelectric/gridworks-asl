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
        if name in registry["formats"]:
            return "format"
        if (
            name in registry["types"]
            and registry["types"][name].get("versioning_strategy") == "none"
        ):
            return "versionless_type"
        raise ValueError(f"Unknown bare dependency: {dep}")

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


def compute_closure(type_name: str, version: str | None, registry) -> dict:
    visited = set()
    stack: list[tuple[str, str | None]] = [(type_name, version)]

    closure = {
        "types": set(),
        "enums": set(),
        "formats": set(),
        "versionless_types": set(),
    }

    while stack:
        t_name, t_version = stack.pop()
        key = f"{t_name}:{t_version}" if t_version is not None else t_name

        if key in visited:
            continue

        visited.add(key)

        types = registry["types"]

        if t_name not in types:
            raise ValueError(f"Unknown type referenced: {t_name}")

        type_entry = types[t_name]

        if t_version is None:
            if type_entry.get("versioning_strategy") != "none":
                raise ValueError(f"Versioned type referenced without version: {t_name}")
            type_def = type_entry
        else:
            versions = type_entry["versions"]
            if t_version not in versions:
                raise ValueError(f"Unknown version: {t_name}:{t_version}")
            type_def = versions[t_version]

        direct_deps = get_direct_deps(type_def)

        for dep in direct_deps:
            category = classify(dep, registry)

            if category == "format":
                closure["formats"].add(dep)
            elif category == "enum":
                closure["enums"].add(dep)
            elif category == "type":
                closure["types"].add(dep)
                dep_name, dep_version = split_dep(dep)
                stack.append((dep_name, dep_version))
            elif category == "versionless_type":
                closure["versionless_types"].add(dep)
                stack.append((dep, None))

    return {
        "types": sorted(closure["types"]),
        "enums": sorted(closure["enums"]),
        "formats": sorted(closure["formats"]),
        "versionless_types": sorted(closure["versionless_types"]),
    }


def build():
    registry = load_registry()

    output = {"types": {}, "versionless_types": {}}

    for type_name, type_def in registry["types"].items():
        if type_def.get("versioning_strategy") == "none":
            output["versionless_types"][type_name] = compute_closure(
                type_name, None, registry
            )
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
