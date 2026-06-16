from __future__ import annotations
import re
from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import BeforeValidator

from sema.tools.runtime_generation.templates.format import FORMAT_TEMPLATES


REPO_ROOT = Path(__file__).resolve().parents[4]


# ============================================================
# --- format primitives (copied from sema.runtime.property_format
#     and sema.runtime.base to keep tools/ free of runtime imports) ---
# ============================================================

LEFT_RIGHT_DOT_PATTERN = re.compile(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)*$")
PASCAL_CASE_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9]*$")
SNAKE_FROM_CAMEL_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def is_left_right_dot(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: LeftRightDot must be a string.")
    if not LEFT_RIGHT_DOT_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails LeftRightDot format.")
    return v


def is_pascal_case(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: PascalCase must be a string.")
    if not PASCAL_CASE_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails PascalCase format.")
    return v


def pascal_to_snake(name: str) -> str:
    return SNAKE_FROM_CAMEL_PATTERN.sub("_", name).lower()


LeftRightDot = Annotated[str, BeforeValidator(is_left_right_dot)]
PascalCase = Annotated[str, BeforeValidator(is_pascal_case)]


EMPTY_LOCAL_NAMES: dict[LeftRightDot, LeftRightDot] = {}


# ============================================================
# --- naming helpers ---
# ============================================================

def pattern_const_name(format_name: str) -> str:
    """
    "utc.iso8601.seconds" -> "UTC_ISO8601_SECONDS_PATTERN"
    """
    return format_name.upper().replace(".", "_") + "_PATTERN"


def local_name_to_class(local_name: LeftRightDot) -> PascalCase:
    parts = re.split(r"\.", local_name)
    return is_pascal_case("".join(p.capitalize() for p in parts if p))


def local_name_to_module(local_name: LeftRightDot) -> str:
    return local_name.replace(".", "_")


# ============================================================
# --- local names yaml ---
# ============================================================

def apply_local_name_rules(
    name: str,
    *,
    strip_prefixes: set[str],
    overrides: dict[str, str],
) -> str:
    """The local (class/module) name for a sema ``name`` under the rules.

    An explicit override wins. Otherwise drop a single leading dotted segment
    iff it is one of ``strip_prefixes`` (so ``gw1.unit`` -> ``unit`` but
    ``gw108.gpio.sensor.component.gt`` is untouched — its head is ``gw108``,
    not ``gw1``). Otherwise the name is unchanged.
    """
    if name in overrides:
        return overrides[name]
    head, sep, rest = name.partition(".")
    if sep and head in strip_prefixes:
        return rest
    return name


def render_local_names_yaml(
    dag,
    path: Path,
    *,
    strip_prefixes: tuple[str, ...] = (),
    overrides: dict[str, str] | None = None,
) -> None:
    """Materialize local_names.yaml from declarative rules (no hand-editing).

    The snapshot's class/module names derive from local names via
    ``local_name_to_class`` / ``local_name_to_module``. Rather than hand-edit a
    flat file, the seed request declares the intent — ``strip_prefixes`` (e.g.
    ``[gw1, gw]``) plus per-type ``overrides`` — and this renders the effective
    file. Local names must be unique within the snapshot and valid
    ``LeftRightDot``; a collision raises naming both sema types so the human adds
    an override.
    """
    strip = set(strip_prefixes)
    overrides = dict(overrides or {})

    data: dict[str, dict[str, LeftRightDot]] = {"types": {}, "enums": {}}
    seen: dict[str, str] = {}  # local name -> sema name (across both sections)
    for kind, name, _version in sorted(dag.nodes):
        if kind == "format":
            continue
        local = apply_local_name_rules(name, strip_prefixes=strip, overrides=overrides)
        is_left_right_dot(local)
        if local in seen and seen[local] != name:
            raise ValueError(
                f"local name collision: {name!r} and {seen[local]!r} both map to "
                f"{local!r}. Add an override in the seed request's `local_names`."
            )
        seen[local] = name
        data[f"{kind}s"][name] = local

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=True)


def load_local_names_yaml(path: Path) -> dict[LeftRightDot, LeftRightDot]:
    if not path.exists():
        return dict(EMPTY_LOCAL_NAMES)

    with path.open() as f:
        data = yaml.safe_load(f) or {}

    local_names: dict[LeftRightDot, LeftRightDot] = {}
    local_names.update(data.get("types", {}))
    local_names.update(data.get("enums", {}))

    for sema_name, local_name in local_names.items():
        is_left_right_dot(sema_name)
        is_left_right_dot(local_name)

    # all local class names must be unique
    assert len(local_names.values()) == len(set(local_names.values()))
    # TODO: make sure these class names are not in a set of protected
    # python classes
    return local_names


def get_local_class_name(
    section: str,
    sema_name: LeftRightDot,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> PascalCase:
    """
    section: "types" | "enums" | "formats"
    """
    if section == "formats":
        try:
            class_name = FORMAT_TEMPLATES[sema_name]["class_name"]
        except KeyError as e:
            raise ValueError(
                f"Missing format class_name template for: {sema_name}"
            ) from e
        return class_name

    local_names = local_names or EMPTY_LOCAL_NAMES
    local_name: LeftRightDot = local_names.get(sema_name, sema_name)
    return local_name_to_class(local_name)


def format_class_name(name: str) -> str:
    try:
        return FORMAT_TEMPLATES[name]["class_name"]
    except KeyError as e:
        raise ValueError(f"Missing format class_name template for: {name}") from e


def sema_name_to_template_identifier(name: LeftRightDot) -> str:
    return name.replace(".", "_")


def module_name_for_node(
    node: tuple[str, str, str | None],
    dag_max: dict[tuple[str, str], str | None],
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> str:
    kind, sema_name, version = node
    if kind == "format":
        raise ValueError("Formats are written into property_format.py")
    local_names = local_names or EMPTY_LOCAL_NAMES
    local_name: LeftRightDot = local_names.get(sema_name, sema_name)
    module_name = local_name_to_module(local_name)
    if version is not None and dag_max[(kind, sema_name)] != version:
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
    node: tuple[str, LeftRightDot, str | None],
    dag_max: dict[tuple[str, str], str | None],
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> str:
    kind, sema_name, version = node
    if kind not in {"format", "enum", "type"}:
        raise Exception(f"kind must be format, enum, or type .. not {kind}")
    section = f"{kind}s"
    base = get_local_class_name(section, sema_name, local_names)
    if version is None:
        return base
    latest_version = dag_max.get((kind, sema_name))
    if latest_version == version:
        return base
    return f"{base}{version}"


def import_path_and_symbol_for_node(
    node: tuple[str, str, str | None],
    dag_max: dict[tuple[str, str], str | None],
    import_root: str,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> tuple[str, str]:
    """import_root is the dotted path where the sema package lives.

    For a snapshot package "gjk", pass "gjk.sema". For the runtime itself,
    pass "sema.runtime".
    """
    kind, sema_name, version = node
    if kind == "format":
        return (
            f"{import_root}.property_format",
            format_class_name(sema_name),
        )

    module_name = module_name_for_node(node, dag_max, local_names)
    symbol_name = class_name_for_node(node, dag_max, local_names)
    is_old_version = version is not None and dag_max[(kind, sema_name)] != version
    if is_old_version:
        return (f"{import_root}.{kind}s.old_versions.{module_name}", symbol_name)
    # DAG-max enums: import from the package init (which eagerly re-exports
    # every latest enum), so generated code reads `from <root>.enums import
    # GNodeStatus` instead of `from <root>.enums.g_node_status import …`.
    # DAG-max types still use the per-module path to avoid circular-import
    # risk inside types/__init__.py.
    if kind == "enum":
        return (f"{import_root}.{kind}s", symbol_name)
    return (f"{import_root}.{kind}s.{module_name}", symbol_name)


def target_path_for_node(
    node: tuple[str, str, str | None],
    dag_max: dict[tuple[str, str], str | None],
    output_root,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
):
    kind, sema_name, version = node
    if kind == "format":
        raise ValueError("Formats are written into property_format.py")
    module_name = module_name_for_node(node, dag_max, local_names)
    if version is not None and dag_max[(kind, sema_name)] != version:
        return output_root / f"{kind}s" / "old_versions" / f"{module_name}.py"
    return output_root / f"{kind}s" / f"{module_name}.py"


def render_init_module(
    kind: str,
    dag,
    dag_max: dict[tuple[str, str], str | None],
    import_root: str,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> str:
    """Render the parent ``__init__.py`` for the latest types or enums in the DAG.

    Emits eager imports + ``__all__`` so downstream callers can do
    ``from <import_root>.<kind>s import <Class>``. The codec relies on this.

    The companion ``old_versions/__init__.py`` is intentionally written empty
    (NOT generated by this helper). Eager imports there would deadlock —
    old-version modules reference latest classes and vice-versa, so loading
    the package while a latest type is mid-init triggers a circular import.
    The codec discovers old versions via filesystem glob, so an empty init
    is sufficient.

    import_root: dotted path where the sema package lives (e.g. "gjk.sema"
    for a snapshot, "sema.runtime" for the runtime itself).
    """
    if kind not in {"type", "enum"}:
        raise ValueError(f"render_init_module only supports type/enum kinds, got {kind}")

    entries: list[tuple[str, str]] = []  # (module_name, class_name)
    for node in dag.topo_sort():
        node_kind, sema_name, version = node
        if node_kind != kind:
            continue
        is_latest = version is None or dag_max.get((kind, sema_name)) == version
        if not is_latest:
            continue
        module_name = module_name_for_node(node, dag_max, local_names)
        class_name = class_name_for_node(node, dag_max, local_names)
        entries.append((module_name, class_name))

    entries.sort(key=lambda entry: entry[1])

    lines: list[str] = []
    for module_name, class_name in entries:
        lines.append(
            f"from {import_root}.{kind}s.{module_name} import {class_name}"
        )
    lines.append("")
    lines.append("__all__ = [")
    for _, class_name in entries:
        lines.append(f'    "{class_name}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def load_schema_for_node(
    node: tuple[str, str, str | None],
    seed: dict,
) -> dict:
    """Load the schema named by the seed from the core repository definitions."""
    kind, sema_name, version = node
    if kind == "format":
        relative_path = seed["worklist"]["formats"][sema_name]["path"]
    elif kind == "enum":
        relative_path = seed["worklist"]["enums"][sema_name][version]["path"]
    elif kind == "type":
        type_entry = seed["worklist"]["types"][sema_name]
        if version is None:
            relative_path = type_entry["path"]
        else:
            relative_path = type_entry[version]["path"]
    else:
        raise ValueError(f"Schema loading not supported for node: {node}")
    definition_path = REPO_ROOT / relative_path
    return yaml.safe_load(definition_path.read_text())
