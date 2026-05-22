from __future__ import annotations

import argparse
import copy
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "output"
DEFAULT_SEED = OUTPUT_DIR / "seed_expanded.yaml"
REGISTRY_PATH = ROOT / "definitions" / "registry.yaml"
PACKAGE_NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")
INDEX_HEADER = """# GENERATED FILE - DO NOT EDIT
# Generated from definitions/registry.yaml
"""
LOOKUP_HEADER = """# GENERATED FILE - DO NOT EDIT
# Generated from definitions/registry.yaml
#
# ------------------------------------------------------------------
# LOCAL LOOKUP (NON-AUTHORITATIVE)
#
# This file provides local resolution from Sema vocabulary words
# to schema files within this snapshot.
# ------------------------------------------------------------------
"""


def load_seed(seed_path: Path) -> dict:
    with seed_path.open() as handle:
        return yaml.safe_load(handle)


def load_registry() -> dict:
    with REGISTRY_PATH.open() as handle:
        return yaml.safe_load(handle)


def validate_package_name(name: str) -> str:
    if not PACKAGE_NAME_PATTERN.fullmatch(name):
        raise ValueError("--package-name must be lowercase snake_case.")
    return name


def resolve_target_path(package_name: str, target_path: str | None) -> Path:
    if target_path:
        base = Path(target_path).resolve()
    else:
        base = OUTPUT_DIR / package_name
    if base.name == "sema":
        return base
    return base / "sema"


def _is_version_key(value: object) -> bool:
    if isinstance(value, int):
        return True
    return isinstance(value, str) and value.isdigit()


def _normalize_version_key(value: object) -> str:
    if isinstance(value, int):
        return f"{value:03d}"
    if isinstance(value, str) and value.isdigit():
        return value.zfill(3)
    raise ValueError(f"Invalid version key: {value!r}")


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _worklist_versions(word_entry: dict) -> list[str]:
    return sorted({_normalize_version_key(version) for version in word_entry.keys() if _is_version_key(version)}, key=int)


def copy_seed_definitions(target_root: Path, seed: dict) -> None:
    definitions_root = target_root / "definitions"
    ensure_clean_dir(definitions_root)
    (definitions_root / "formats").mkdir(parents=True, exist_ok=True)
    (definitions_root / "enums").mkdir(parents=True, exist_ok=True)
    (definitions_root / "types").mkdir(parents=True, exist_ok=True)

    for section_name in ("formats", "enums", "types"):
        section = seed["worklist"][section_name]
        for _, entry in section.items():
            if not isinstance(entry, dict):
                continue
            if "path" in entry:
                _copy_definition_path(definitions_root, entry["path"])
                continue
            for version_entry in entry.values():
                if isinstance(version_entry, dict) and "path" in version_entry:
                    _copy_definition_path(definitions_root, version_entry["path"])


def _copy_definition_path(definitions_root: Path, relative_path: str) -> None:
    source = ROOT / relative_path
    target = definitions_root / Path(relative_path).relative_to("definitions")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def build_restricted_registry(seed: dict, registry: dict) -> dict:
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    restricted: dict[str, object] = {
        "metadata": copy.deepcopy(registry["metadata"]),
        "snapshot": {
            "built_at": built_at,
        },
        "formats": {},
        "enums": {},
        "types": {},
    }

    for format_name in sorted(seed["worklist"]["formats"]):
        restricted["formats"][format_name] = copy.deepcopy(registry["formats"][format_name])

    for enum_name, enum_entry in seed["worklist"]["enums"].items():
        registry_entry = registry["enums"][enum_name]
        if registry_entry["enum_type"] == "literal":
            restricted["enums"][enum_name] = copy.deepcopy(registry_entry)
            continue

        selected = set(_worklist_versions(enum_entry))
        restricted["enums"][enum_name] = _restrict_versioned_entry(registry_entry, selected)

    for type_name, type_entry in seed["worklist"]["types"].items():
        registry_entry = registry["types"][type_name]
        if registry_entry["versioning_strategy"] == "none":
            restricted["types"][type_name] = copy.deepcopy(registry_entry)
            continue

        selected = set(_worklist_versions(type_entry))
        restricted["types"][type_name] = _restrict_versioned_entry(registry_entry, selected)

    return restricted


def _restrict_versioned_entry(registry_entry: dict, selected_versions: set[str]) -> dict:
    restricted: dict[str, object] = {}
    restricted_versions = {
        version: copy.deepcopy(version_entry)
        for version, version_entry in registry_entry["versions"].items()
        if version in selected_versions
    }
    latest_version = max(selected_versions, key=int)
    for key, value in registry_entry.items():
        if key == "latest_version":
            restricted[key] = latest_version
        elif key == "versions":
            restricted[key] = restricted_versions
        else:
            restricted[key] = copy.deepcopy(value)
    return restricted


def write_restricted_registry(target_root: Path, restricted: dict) -> None:
    registry_target = target_root / "definitions" / "registry.yaml"
    registry_target.parent.mkdir(parents=True, exist_ok=True)
    registry_target.write_text(render_registry_yaml(restricted))


def render_registry_yaml(data: dict) -> str:
    return _render_node(data, indent=0) + "\n"


def _render_node(node: object, indent: int) -> str:
    if isinstance(node, dict):
        return _render_mapping(node, indent)
    if isinstance(node, list):
        return _render_sequence(node, indent)
    return " " * indent + _render_scalar(node)


def _render_mapping(mapping: dict, indent: int) -> str:
    lines: list[str] = []
    items = list(mapping.items())
    for index, (key, value) in enumerate(items):
        prefix = " " * indent + f"{_render_key(key)}:"
        if _needs_entry_spacing(indent, mapping, index):
            lines.append("")
        if _needs_section_spacing(indent, mapping, index):
            lines.append("")
        if key == "versions" and index > 0:
            lines.append("")
        if isinstance(value, dict):
            if value:
                lines.append(prefix)
                lines.append(_render_mapping(value, indent + 2))
            else:
                lines.append(prefix + " {}")
        elif isinstance(value, list):
            if value:
                lines.append(prefix)
                lines.append(_render_sequence(value, indent + 2))
            else:
                lines.append(prefix + " []")
        else:
            lines.append(prefix + f" {_render_scalar(value, key=key, parent=mapping)}")
    return "\n".join(lines)


def _render_sequence(values: list, indent: int) -> str:
    lines: list[str] = []
    for value in values:
        prefix = " " * indent + "-"
        if isinstance(value, dict):
            if value:
                lines.append(prefix)
                lines.append(_render_mapping(value, indent + 2))
            else:
                lines.append(prefix + " {}")
        elif isinstance(value, list):
            if value:
                lines.append(prefix)
                lines.append(_render_sequence(value, indent + 2))
            else:
                lines.append(prefix + " []")
        else:
            lines.append(prefix + f" {_render_scalar(value)}")
    return "\n".join(lines)


def _render_scalar(value: object, key: object | None = None, parent: dict | None = None) -> str:
    if isinstance(value, str):
        if _should_render_plain_string(value, key=key, parent=parent):
            return value
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def _render_key(value: object) -> str:
    if isinstance(value, str) and re.fullmatch(r"\d{3}", value):
        return f'"{value}"'
    return str(value)


def _should_render_plain_string(value: str, key: object | None = None, parent: dict | None = None) -> bool:
    if key == "owner" and parent is not None and not _is_metadata_mapping(parent):
        return bool(re.fullmatch(r"[a-z_][a-z0-9_-]*", value))
    return False


def _needs_entry_spacing(indent: int, mapping: dict, index: int) -> bool:
    if index == 0:
        return False
    return indent == 2 and not _is_top_level_sections_mapping(mapping) and not _is_metadata_mapping(mapping)


def _needs_section_spacing(indent: int, mapping: dict, index: int) -> bool:
    if index == 0:
        return False
    return indent == 0 and _is_top_level_sections_mapping(mapping)


def _is_top_level_sections_mapping(mapping: dict) -> bool:
    return list(mapping.keys()) == ["metadata", "snapshot", "formats", "enums", "types"]


def _is_metadata_mapping(mapping: dict) -> bool:
    return list(mapping.keys()) == ["registry_version", "last_updated", "maintainer"]


def write_restricted_indexes(target_root: Path, restricted: dict) -> None:
    indexes_root = target_root / "indexes"
    indexes_root.mkdir(parents=True, exist_ok=True)
    _write_yaml_with_header(
        indexes_root / "lookup.yaml",
        LOOKUP_HEADER,
        build_restricted_lookup(restricted),
    )
    _write_yaml_with_header(
        indexes_root / "dependency_closure.yaml",
        INDEX_HEADER,
        build_restricted_dependency_closure(restricted),
        sort_keys=True,
    )
    _write_yaml_with_header(
        indexes_root / "reverse_dependencies.yaml",
        INDEX_HEADER,
        build_restricted_reverse_dependencies(restricted),
    )
    (indexes_root / "versions.yaml").write_text(build_restricted_versions_text(restricted))


def _write_yaml_with_header(
    path: Path,
    header: str,
    payload: dict,
    *,
    sort_keys: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        handle.write(header + "\n")
        yaml.dump(payload, handle, sort_keys=sort_keys, default_flow_style=False)


def build_restricted_lookup(registry: dict) -> dict:
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
            continue
        output["types"][type_name] = {
            "latest_version": type_def["latest_version"],
            "versioning_strategy": type_def["versioning_strategy"],
            "versions": {
                version: f"definitions/types/{type_name}/{version}.yaml"
                for version in type_def["versions"]
            },
        }

    for enum_name, enum_def in registry["enums"].items():
        if enum_def["enum_type"] == "literal":
            output["enums"][enum_name] = {
                "enum_type": "literal",
                "schema": f"definitions/enums/{enum_name}/000.yaml",
            }
            continue
        output["enums"][enum_name] = {
            "enum_type": "versioned",
            "latest_version": enum_def["latest_version"],
            "versions": {
                version: f"definitions/enums/{enum_name}/{version}.yaml"
                for version in enum_def["versions"]
            },
        }

    for format_name in registry["formats"]:
        output["formats"][format_name] = f"definitions/formats/{format_name}.yaml"

    return output


def build_restricted_dependency_closure(registry: dict) -> dict:
    output = {"types": {}, "versionless_types": {}}

    for type_name, type_def in registry["types"].items():
        if type_def.get("versioning_strategy") == "none":
            output["versionless_types"][type_name] = _compute_closure(
                type_name, None, registry
            )
            continue
        output["types"][type_name] = {}
        for version in type_def["versions"]:
            output["types"][type_name][version] = _compute_closure(type_name, version, registry)

    return output


def _compute_closure(type_name: str, version: str | None, registry: dict) -> dict:
    visited: set[str] = set()
    stack: list[tuple[str, str | None]] = [(type_name, version)]
    closure = {
        "types": set(),
        "enums": set(),
        "formats": set(),
        "versionless_types": set(),
    }

    while stack:
        current_name, current_version = stack.pop()
        key = f"{current_name}:{current_version}" if current_version is not None else current_name
        if key in visited:
            continue
        visited.add(key)

        type_entry = registry["types"][current_name]
        if current_version is None:
            if type_entry.get("versioning_strategy") != "none":
                raise ValueError(
                    f"Versioned type referenced without version: {current_name}"
                )
            version_block = type_entry
        else:
            version_block = type_entry["versions"][current_version]

        for dep in _get_direct_deps(version_block):
            category = _classify_dep(dep, registry)
            if category == "format":
                closure["formats"].add(dep)
            elif category == "enum":
                closure["enums"].add(dep)
            elif category == "type":
                closure["types"].add(dep)
                dep_name, dep_version = _split_dep(dep)
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


def build_restricted_reverse_dependencies(registry: dict) -> dict:
    type_reverse: dict[str, dict[str, set[str]]] = {}
    enum_reverse: dict[str, dict[str, set[str]]] = {}
    format_reverse: dict[str, set[str]] = {}

    for type_name, type_def in registry["types"].items():
        for version, version_block in type_def.get("versions", {}).items():
            source = f"{type_name}:{version}"
            for dep in _get_direct_deps(version_block):
                category = _classify_dep(dep, registry)
                dep_name, dep_version = _split_dep(dep)
                if category == "type":
                    if dep_version is None:
                        raise ValueError(f"Type dependency missing version: {dep}")
                    type_reverse.setdefault(dep_name, {}).setdefault(dep_version, set()).add(source)
                elif category == "enum":
                    if dep_version is None:
                        raise ValueError(f"Enum dependency missing version: {dep}")
                    enum_reverse.setdefault(dep_name, {}).setdefault(dep_version, set()).add(source)
                else:
                    format_reverse.setdefault(dep_name, set()).add(source)

    reverse: dict[str, dict] = {
        "types": {},
        "enums": {},
        "formats": {},
    }
    for name in sorted(type_reverse):
        reverse["types"][name] = {}
        for version in sorted(type_reverse[name], key=int):
            reverse["types"][name][version] = {"used_by": sorted(type_reverse[name][version])}
    for name in sorted(enum_reverse):
        reverse["enums"][name] = {}
        for version in sorted(enum_reverse[name], key=int):
            reverse["enums"][name][version] = {"used_by": sorted(enum_reverse[name][version])}
    for name in sorted(format_reverse):
        reverse["formats"][name] = {"used_by": sorted(format_reverse[name])}
    return reverse


def build_restricted_versions_text(registry: dict) -> str:
    lines: list[str] = [INDEX_HEADER, "", "types:"]

    for type_name, type_def in registry["types"].items():
        lines.append(f"  {type_name}:")
        strategy = type_def["versioning_strategy"]

        if strategy == "none":
            lines.append(f'    versioning_strategy: "{strategy}"')
            lines.append(f"    summary: {quote(type_def['summary'])}")
            lines.append("")
            continue

        lines.append(f'    latest_version: "{type_def["latest_version"]}"')
        lines.append(f'    versioning_strategy: "{strategy}"')
        lines.append("    versions:")
        for version, version_info in type_def.get("versions", {}).items():
            lines.append(f'      "{version}":')
            append_summary(
                lines,
                "        ",
                fallback_summary(version, version_info, type_def["latest_version"]),
            )
        lines.append("")

    if lines[-1] == "":
        lines.pop()

    lines.append("")
    lines.append("enums:")

    for enum_name, enum_def in registry["enums"].items():
        enum_type = enum_def["enum_type"]
        lines.append(f"  {enum_name}:")
        lines.append(f'    enum_type: "{enum_type}"')
        lines.append(f"    note: {quote(enum_note(enum_type))}")
        lines.append("    versions:")

        if enum_type == "literal":
            lines.append('      "000": {}')
            lines.append("")
            continue

        version_keys = list(enum_def.get("versions", {}).keys())
        initial_version = version_keys[-1] if version_keys else "000"
        for version, version_info in enum_def.get("versions", {}).items():
            if version == initial_version and "added_values" not in version_info:
                lines.append(f'      "{version}": {{}}')
                continue
            lines.append(f'      "{version}":')
            if "added_values" in version_info:
                append_added_values(lines, "        ", version_info["added_values"])
        lines.append("")

    if lines[-1] == "":
        lines.pop()

    return "\n".join(lines) + "\n"


def _split_dep(dep: str) -> tuple[str, str | None]:
    if ":" in dep:
        return dep.rsplit(":", 1)
    return dep, None


def _classify_dep(dep: str, registry: dict) -> str:
    name, version = _split_dep(dep)
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
    raise ValueError(f"Unknown dependency: {dep}")


def _get_direct_deps(type_version_block: dict) -> list[str]:
    deps = type_version_block.get("direct_dependencies", {})
    structural = deps.get("structural", []) or []
    axiom = deps.get("axiom", []) or []
    return sorted(set(structural + axiom))


def enum_note(enum_type: str) -> str:
    if enum_type == "literal":
        return "This enum is literal; version 000 is immutable and exclusive."
    return "This enum is versioned; new versions are additive only."


def fallback_summary(version: str, version_info: dict, latest_version: str) -> str:
    if "summary" in version_info:
        return version_info["summary"]
    if version == "000" and latest_version == "000":
        return "Initial and only version."
    if version == "000":
        return "Initial version."
    return f"Version {version}."


def append_added_values(lines: list[str], indent: str, values: list[str]) -> None:
    lines.append(f"{indent}added_values:")
    for value in values:
        lines.append(f"{indent}  - {quote(value)}")


def quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def normalize_summary(summary: str) -> str:
    summary = summary.strip()
    if not summary.startswith("- "):
        return summary

    parts = summary.split(" - ")
    lines: list[str] = []
    for idx, part in enumerate(parts):
        text = part.strip()
        if not text:
            continue
        if idx == 0 and text.startswith("- "):
            lines.append(text)
        else:
            lines.append(f"- {text}")
    return "\n".join(lines)


def append_summary(lines: list[str], indent: str, summary: str) -> None:
    normalized = normalize_summary(summary)
    summary_lines = normalized.splitlines()
    if len(summary_lines) <= 1:
        lines.append(f"{indent}summary: {quote(normalized)}")
        return

    lines.append(f"{indent}summary: >")
    for part in summary_lines:
        lines.append(f"{indent}  {part}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build seed-scoped Sema definitions under a sema/ directory."
    )
    parser.add_argument("--source", type=Path, default=Path("."))
    parser.add_argument("--package-name", required=True)
    parser.add_argument("--target-path")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed = load_seed(args.seed.resolve())
    package_name = validate_package_name(args.package_name)
    target_path = resolve_target_path(package_name, args.target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    copy_seed_definitions(target_path, seed)
    restricted_registry = build_restricted_registry(seed, load_registry())
    write_restricted_registry(target_path, restricted_registry)
    print(f"Built seed definitions at {target_path / 'definitions'}")
    print(f"Selection source: {args.seed}")


if __name__ == "__main__":
    main()
