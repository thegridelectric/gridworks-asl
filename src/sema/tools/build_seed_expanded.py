# build_seed_expanded.py
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "indexes" / "public_registry.yaml"
LOOKUP_PATH = ROOT / "indexes" / "lookup.yaml"
CLOSURE_PATH = ROOT / "indexes" / "dependency_closure.yaml"
OUTPUT_DIR = ROOT / "output"
DEFAULT_OUTPUT_NAME = "seed_expanded.yaml"

OUTPUT_NAME_PATTERN = re.compile(r"^[a-z0-9._-]+\.yaml$")
VERSION_KEY_PATTERN = re.compile(r"^\d{3}$")


def load_yaml(path: Path) -> dict:
    with path.open() as handle:
        return yaml.safe_load(handle)


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


def add_intermediate_type_versions(types: dict[str, set[str]], registry: dict) -> list[tuple[str, str]]:
    # Intermediate versions are included to ensure upgrade chains are complete,
    # using only registry-declared versions (no inferred versions).
    added: list[tuple[str, str]] = []
    for name, selected in list(types.items()):
        if len(selected) < 2:
            continue
        available_versions = sorted(
            (int(v), v) for v in registry["types"][name].get("versions", {})
        )
        available_set = {version for _, version in available_versions}
        for version in selected:
            if version not in available_set:
                raise ValueError(f"Type {name}:{version} not declared in registry")
        low = min(int(version) for version in selected)
        high = max(int(version) for version in selected)
        for numeric_version, version in available_versions:
            if low <= numeric_version <= high and version not in selected:
                selected.add(version)
                added.append((name, version))
    return added


def available_versions(category: str, name: str, registry: dict) -> list[str | None]:
    if category == "types":
        if name not in registry["types"]:
            raise ValueError(f"Unknown type target: {name}")
        type_entry = registry["types"][name]
        if type_entry.get("versioning_strategy") == "none":
            return [None]
        return sorted(type_entry.get("versions", {}), key=int)

    if category == "enums":
        if name not in registry["enums"]:
            raise ValueError(f"Unknown enum target: {name}")
        enum_entry = registry["enums"][name]
        if enum_entry["enum_type"] == "literal":
            return ["000"]
        return sorted(enum_entry.get("versions", {}), key=int)

    raise ValueError(f"Unsupported initial_targets section: {category}")


def latest_version(category: str, name: str, registry: dict) -> str | None:
    if category == "types":
        type_entry = registry["types"][name]
        if type_entry.get("versioning_strategy") == "none":
            return None
        return type_entry["latest_version"]

    enum_entry = registry["enums"][name]
    if enum_entry["enum_type"] == "literal":
        return "000"
    return enum_entry["latest_version"]


def select_initial_versions(category: str, name: str, options: object, registry: dict) -> list[str | None]:
    if not isinstance(options, dict):
        raise ValueError(f"initial_targets.{category}.{name} must be a mapping.")

    unknown_keys = set(options) - {"include_all_versions", "versions"}
    if unknown_keys:
        unknown = ", ".join(sorted(unknown_keys))
        raise ValueError(f"Unknown initial target options for {category}.{name}: {unknown}")

    has_include_all = "include_all_versions" in options
    has_versions = "versions" in options
    if has_include_all and has_versions:
        raise ValueError(f"{category}.{name} cannot set both include_all_versions and versions.")

    available = available_versions(category, name, registry)
    if not options:
        return [latest_version(category, name, registry)]

    if has_include_all:
        if options["include_all_versions"] is not True:
            raise ValueError(f"{category}.{name}.include_all_versions must be true.")
        return available

    versions = options["versions"]
    if not isinstance(versions, list) or not versions:
        raise ValueError(f"{category}.{name}.versions must be a non-empty list.")

    selected: list[str] = []
    available_set = {version for version in available if version is not None}
    for version in versions:
        if not isinstance(version, str) or not VERSION_KEY_PATTERN.fullmatch(version):
            raise ValueError(f"{category}.{name}.versions entries must be 3-digit strings.")
        if version not in available_set:
            raise ValueError(f"Unknown {category[:-1]} target: {name}:{version}")
        if version not in selected:
            selected.append(version)
    return selected


def iter_initial_targets(initial_targets: object, registry: dict) -> list[tuple[str, str, str | None]]:
    if not isinstance(initial_targets, dict) or not initial_targets:
        raise ValueError("seed request must contain a non-empty initial_targets mapping.")

    unknown_sections = set(initial_targets) - {"types", "enums"}
    if unknown_sections:
        unknown = ", ".join(sorted(unknown_sections))
        raise ValueError(f"initial_targets may only contain types and enums; found: {unknown}")

    targets: list[tuple[str, str, str | None]] = []
    for category in ("types", "enums"):
        section = initial_targets.get(category, {})
        if section is None:
            continue
        if not isinstance(section, dict):
            raise ValueError(f"initial_targets.{category} must be a mapping.")
        for name, options in section.items():
            if not isinstance(name, str):
                raise ValueError(f"initial_targets.{category} names must be strings.")
            for version in select_initial_versions(category, name, options, registry):
                targets.append((category, name, version))

    if not targets:
        raise ValueError("seed request initial_targets must include at least one type or enum.")
    return targets


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
    requested_targets = iter_initial_targets(initial_targets, registry)

    formats: set[str] = set()
    enums: dict[str, set[str]] = {}
    types: dict[str, set[str]] = {}
    versionless_types: set[str] = set()
    normalized_targets: list[str] = []
    pending_type_versions: list[tuple[str, str]] = []
    expanded_type_versions: set[tuple[str, str]] = set()
    pending_versionless: list[str] = []
    expanded_versionless: set[str] = set()

    def add_enum(name: str, version: str) -> None:
        enums.setdefault(name, set()).add(version)

    def add_type(name: str, version: str) -> None:
        selected = types.setdefault(name, set())
        if version not in selected:
            selected.add(version)
            pending_type_versions.append((name, version))

    def add_versionless_type(name: str) -> None:
        if name not in versionless_types:
            versionless_types.add(name)
            pending_versionless.append(name)

    def absorb_closure(type_closure: dict) -> None:
        for dep in type_closure.get("formats", []):
            formats.add(dep)
        for dep in type_closure.get("enums", []):
            dep_name, dep_version = dep.rsplit(":", 1)
            add_enum(dep_name, dep_version)
        for dep in type_closure.get("types", []):
            dep_name, dep_version = dep.rsplit(":", 1)
            add_type(dep_name, dep_version)
        for dep in type_closure.get("versionless_types", []):
            add_versionless_type(dep)

    def expand_pending_type_versions() -> None:
        while pending_type_versions:
            name, version = pending_type_versions.pop(0)
            key = (name, version)
            if key in expanded_type_versions:
                continue
            expanded_type_versions.add(key)
            absorb_closure(closure["types"][name][version])

    def expand_pending_versionless() -> None:
        while pending_versionless:
            name = pending_versionless.pop(0)
            if name in expanded_versionless:
                continue
            expanded_versionless.add(name)
            absorb_closure(closure["versionless_types"][name])

    for category, name, version in requested_targets:
        normalized_targets.append(name if version is None else f"{name}:{version}")

        if category == "enums":
            if version is None:
                raise ValueError(f"Enum target missing version: {name}")
            add_enum(name, version)
            continue

        if version is None:
            add_versionless_type(name)
            continue

        add_type(name, version)

    while True:
        expand_pending_type_versions()
        expand_pending_versionless()
        if pending_type_versions or pending_versionless:
            continue
        added_intermediate_versions = add_intermediate_type_versions(types, registry)
        if not added_intermediate_versions:
            break
        pending_type_versions.extend(added_intermediate_versions)

    output: dict[str, object] = {
        "metadata": {
            "generated_from": "indexes/public_registry.yaml",
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
            "Expand a structured seed request into a generated seed/worklist by validating "
            "initial target types and enums, computing typed transitive closure, and "
            "resolving local paths."
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
