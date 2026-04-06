from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "definitions" / "registry.yaml"
LOOKUP_PATH = ROOT / "indexes" / "lookup.yaml"
CLOSURE_PATH = ROOT / "indexes" / "dependency_closure.yaml"
OUTPUT_DIR = ROOT / "output"
DEFAULT_OUTPUT_NAME = "seed_expanded.yaml"

VERSION_PATTERN = re.compile(r"^(?P<name>.+)[.:](?P<version>\d{3})$")
OUTPUT_NAME_PATTERN = re.compile(r"^[a-z0-9._-]+\.yaml$")


def load_yaml(path: Path) -> dict:
    with path.open() as handle:
        return yaml.safe_load(handle)


def normalize_target(target: str, registry: dict) -> tuple[str, str | None, str]:
    match = VERSION_PATTERN.match(target)
    if match:
        name = match.group("name")
        version = match.group("version")
        if name in registry["types"]:
            if version not in registry["types"][name].get("versions", {}):
                raise ValueError(f"Unknown type target: {name}:{version}")
            return name, version, "type"
        if name in registry["enums"]:
            enum_entry = registry["enums"][name]
            if enum_entry["enum_type"] == "literal":
                if version != "000":
                    raise ValueError(f"Unknown enum target: {name}:{version}")
            elif version not in enum_entry.get("versions", {}):
                raise ValueError(f"Unknown enum target: {name}:{version}")
            return name, version, "enum"
        raise ValueError(f"Unknown versioned target: {target}")

    if target in registry["formats"]:
        return target, None, "format"

    if target in registry["types"] and registry["types"][target].get("versioning_strategy") == "none":
        return target, None, "type"

    if target in registry["types"] or target in registry["enums"]:
        raise ValueError(f"{target} requires a 3-digit version.")

    raise ValueError(f"Unknown target: {target}")


def ensure_lookup_path(lookup: dict, category: str, name: str, version: str | None) -> str:
    if category == "format":
        return lookup["formats"][name]
    if category == "enum":
        enum_entry = lookup["enums"][name]
        if version is None:
            raise ValueError(f"Enum lookup requires version: {name}")
        if enum_entry.get("enum_type") == "literal":
            if version != "000":
                raise ValueError(f"Literal enum lookup only supports version 000: {name}:{version}")
            return enum_entry["schema"]
        return enum_entry["versions"][version]
    if version is None:
        return lookup["types"][name]["schema"]
    return lookup[f"{category}s"][name]["versions"][version]


def resolve_output_name(name: str) -> Path:
    if "/" in name or "\\" in name:
        raise ValueError("--out must be a single filename with no slashes.")
    if not OUTPUT_NAME_PATTERN.fullmatch(name):
        raise ValueError("--out must be a lowercase filename ending in .yaml")
    return OUTPUT_DIR / name


def expand_seed(seed_request_path: Path, output_path: Path) -> None:
    registry = load_yaml(REGISTRY_PATH)
    lookup = load_yaml(LOOKUP_PATH)
    closure = load_yaml(CLOSURE_PATH)
    request = load_yaml(seed_request_path)

    initial_targets = request.get("initial_targets")
    if not isinstance(initial_targets, list) or not initial_targets:
        raise ValueError("seed request must contain a non-empty initial_targets list.")

    formats: set[str] = set()
    enums: dict[str, set[str]] = {}
    types: dict[str, set[str]] = {}
    versionless_types: set[str] = set()
    normalized_targets: list[str] = []

    def add_enum(name: str, version: str) -> None:
        enums.setdefault(name, set()).add(version)

    def add_type(name: str, version: str) -> None:
        types.setdefault(name, set()).add(version)

    for raw_target in initial_targets:
        if not isinstance(raw_target, str):
            raise ValueError("initial_targets entries must be strings.")

        name, version, category = normalize_target(raw_target, registry)
        normalized_targets.append(name if version is None else f"{name}:{version}")

        if category == "format":
            formats.add(name)
            continue

        if category == "enum":
            if version is None:
                raise ValueError(f"Enum target missing version: {name}")
            add_enum(name, version)
            continue

        if version is None:
            versionless_types.add(name)
            continue

        add_type(name, version)
        type_closure = closure["types"][name][version]

        for dep in type_closure["formats"]:
            formats.add(dep)
        for dep in type_closure["enums"]:
            dep_name, dep_version = dep.rsplit(":", 1)
            add_enum(dep_name, dep_version)
        for dep in type_closure["types"]:
            dep_name, dep_version = dep.rsplit(":", 1)
            add_type(dep_name, dep_version)

    output: dict[str, object] = {
        "metadata": {
            "generated_from": "definitions/registry.yaml",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "note": "Transitive closure of initial_targets",
        },
        "initial_targets": normalized_targets,
        "worklist": {
            "formats": {},
            "enums": {},
            "types": {},
        },
    }

    worklist = output["worklist"]
    if not isinstance(worklist, dict):
        raise AssertionError("worklist shape corrupted")

    for name in sorted(formats):
        worklist["formats"][name] = {
            "path": ensure_lookup_path(lookup, "format", name, None),
        }

    for name in sorted(enums):
        worklist["enums"][name] = {}
        for version in sorted(enums[name], key=int):
            worklist["enums"][name][version] = {
                "path": ensure_lookup_path(lookup, "enum", name, version),
            }

    for name in sorted(types):
        worklist["types"][name] = {}
        for version in sorted(types[name], key=int):
            worklist["types"][name][version] = {
                "path": ensure_lookup_path(lookup, "type", name, version),
            }

    for name in sorted(versionless_types):
        worklist["types"][name] = {
            "versioning_strategy": "none",
            "path": ensure_lookup_path(lookup, "type", name, None),
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as handle:
        yaml.dump(output, handle, sort_keys=False, default_flow_style=False)

    print(f"Wrote expanded seed to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Expand a small seed request into a generated seed/worklist by validating "
            "initial_targets, computing typed transitive closure, and resolving local paths."
        )
    )
    parser.add_argument("seed_request", type=Path)
    parser.add_argument("--out", default=DEFAULT_OUTPUT_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    expand_seed(args.seed_request.resolve(), resolve_output_name(args.out))


if __name__ == "__main__":
    main()
