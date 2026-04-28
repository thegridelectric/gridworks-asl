from __future__ import annotations
import re
from pathlib import Path
from typing import Any

import yaml

from sema.tools.runtime_generation.templates.format import FORMAT_TEMPLATES


EMPTY_LOCAL_NAMES: dict[str, dict[str, dict[str, str]]] = {
    "types": {},
    "enums": {},
    "formats": {},
}


def pascal_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

# ============================================================
# --- naming helpers ---
# ============================================================

def pattern_const_name(format_name: str) -> str:
    """
    "utc.iso8601.seconds" -> "UTC_ISO8601_SECONDS_PATTERN"
    """
    return format_name.upper().replace(".", "_") + "_PATTERN"


def default_local_class_name(name: str) -> str:
    parts = re.split(r"\.", name)
    return "".join(p.capitalize() for p in parts if p)


# ============================================================
# --- local names yaml ---
# ============================================================

def generate_local_names_yaml(dag, path: Path) -> None:
    """
    Creates a local_names.yaml file if it does not exist.

    Does NOT overwrite existing file.
    """
    if path.exists():
        return

    data: dict[str, dict[str, dict[str, str]]] = {
        "types": {},
        "enums": {},
    }

    for kind, name, _version in sorted(dag.nodes):
        if kind == "format":
            continue
        section = f"{kind}s"
        if name not in data[section]:
            data[section][name] = {
                "local_class_name": default_local_class_name(name)
            }

    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=True)


def load_local_names_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return dict(EMPTY_LOCAL_NAMES)

    with path.open() as f:
        data = yaml.safe_load(f) or {}

    # ensure structure exists
    return {
        "types": data.get("types", {}),
        "enums": data.get("enums", {}),
        "formats": data.get("formats", {}),
    }


def format_class_name(name: str) -> str:
    try:
        class_name = FORMAT_TEMPLATES[name]["class_name"]
    except KeyError as e:
        raise ValueError(f"Missing format class_name template for: {name}") from e
    return class_name


def get_local_class_name(
    section: str,
    name: str,
    local_names: dict[str, Any] | None = None,
) -> str:
    """
    section: "types" | "enums" | "formats"
    """
    if section == "formats":
        return format_class_name(name)

    local_names = local_names or EMPTY_LOCAL_NAMES
    try:
        return local_names[section][name]["local_class_name"]
    except KeyError:
        return default_local_class_name(name)


def sema_name_to_module(name: str) -> str:
    return name.replace(".", "_")


def module_name_for_node(
    node: tuple[str, str, str | None],
    latest_map: dict[tuple[str, str], str | None],
    local_names: dict[str, Any] | None = None,
) -> str:
    kind, name, version = node
    if kind == "format":
        raise ValueError("Formats are written into property_format.py")
    module_name = pascal_to_snake(
        class_name_for_node((kind, name, None), latest_map, local_names)
    )
    if version is not None and latest_map[(kind, name)] != version:
        return f"{module_name}_{version}"
    return module_name


def string_enum_member_name(value: str) -> str:
    if not value.isidentifier():
        raise ValueError(f"String enum value is not a Python identifier: {value}")
    return value


def integer_enum_member_name(value: int, value_descriptions: dict[Any, Any]) -> str:
    if value in value_descriptions:
        member_name = str(value_descriptions[value])
    elif str(value) in value_descriptions:
        member_name = str(value_descriptions[str(value)])
    else:
        raise ValueError(
            f"Integer enum value {value} is missing x-gridworks.value_descriptions"
        )
    if not member_name.isidentifier():
        raise ValueError(
            f"Integer enum value {value} has invalid member name: {member_name}"
        )
    return member_name


def class_name_for_node(
    node: tuple[str, str, str | None],
    latest_map: dict[tuple[str, str], str | None],
    local_names: dict[str, Any] | None = None,
) -> str:
    kind, name, version = node
    section = f"{kind}s"
    base = get_local_class_name(section, name, local_names)
    if version is None:
        return base
    latest_version = latest_map.get((kind, name))
    if latest_version == version:
        return base
    return f"{base}{version}"




def import_path_and_symbol_for_node(
    node: tuple[str, str, str | None],
    latest_map: dict[tuple[str, str], str | None],
    package_name: str,
    local_names: dict[str, Any] | None = None,
) -> tuple[str, str]:
    kind, name, version = node
    if kind == "format":
        return (f"{package_name}.sema.property_format", format_class_name(name))

    module_name = module_name_for_node(node, latest_map, local_names)
    symbol_name = class_name_for_node(node, latest_map, local_names)
    if version is not None and latest_map[(kind, name)] != version:
        return (f"{package_name}.sema.{kind}s.old_versions.{module_name}", symbol_name)
    return (f"{package_name}.sema.{kind}s.{module_name}", symbol_name)


def target_path_for_node(
    node: tuple[str, str, str | None],
    latest_map: dict[tuple[str, str], str | None],
    output_root,
    local_names: dict[str, Any] | None = None,
):
    kind, name, version = node
    if kind == "format":
        raise ValueError("Formats are written into property_format.py")
    module_name = module_name_for_node(node, latest_map, local_names)
    if version is not None and latest_map[(kind, name)] != version:
        return output_root / f"{kind}s" / "old_versions" / f"{module_name}.py"
    return output_root / f"{kind}s" / f"{module_name}.py"


def load_schema_for_node(
    node: tuple[str, str, str | None],
    seed: dict,
    definitions_root: Path,
) -> dict:
    kind, name, version = node
    if kind == "format":
        relative_path = seed["worklist"]["formats"][name]["path"]
    elif kind == "enum":
        relative_path = seed["worklist"]["enums"][name][version]["path"]
    elif kind == "type":
        type_entry = seed["worklist"]["types"][name]
        if version is None:
            relative_path = type_entry["path"]
        else:
            relative_path = type_entry[version]["path"]
    else:
        raise ValueError(f"Schema loading not supported for node: {node}")
    definition_path = definitions_root / Path(relative_path).relative_to("definitions")
    return yaml.safe_load(definition_path.read_text())
