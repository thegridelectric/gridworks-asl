from __future__ import annotations

from sema.tools.runtime_generation.imports import target_path_for_node
from sema.tools.runtime_generation.naming import class_name_for_node, to_enum_member
from sema.tools.runtime_generation.schema import load_schema_for_node


def generate_enums(target_root, dag, latest, seed=None, definitions_root=None, package_name="gjk"):
    if seed is None or definitions_root is None:
        return
    write_enum_base(target_root)
    for node in dag.topo_sort():
        if node[0] != "enum":
            continue
        schema = load_schema_for_node(node, seed, definitions_root)
        target_path = target_path_for_node(node, latest, target_root)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(render_enum(node, schema, latest, package_name))
    (target_root / "enums" / "__init__.py").write_text("")
    (target_root / "enums" / "old_versions" / "__init__.py").write_text("")


def write_enum_base(target_root) -> None:
    (target_root / "enums" / "gw_str_enum.py").write_text(
        '''from enum import StrEnum
from typing import Any, Self


class GwStrEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> str:
        return name

    @classmethod
    def values(cls) -> list[str]:
        return [str(elt) for elt in cls]

    @classmethod
    def default(cls) -> Self | None:
        return None

    @classmethod
    def _missing_(cls, value: str) -> Self:
        default = cls.default()
        if default is None:
            raise ValueError(f"'{value}' is not valid {cls.__name__}")
        return default


class SemaEnum(GwStrEnum):
    @classmethod
    def enum_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def enum_version(cls) -> str:
        raise NotImplementedError
'''
    )


def render_enum(node, schema: dict, latest_map, package_name: str) -> str:
    _, name, version = node
    class_name = class_name_for_node(node, latest_map)
    schema_url = schema["$id"]
    values = schema["enum"]
    default_value = schema.get("default")
    x_gridworks = schema.get("x-gridworks", {})

    if schema["type"] == "string":
        lines = [
            "from enum import auto",
            "",
            f"from {package_name}.sema.enums.gw_str_enum import SemaEnum",
            "",
            "",
            f"class {class_name}(SemaEnum):",
            f'    """Sema: {schema_url}"""',
            "",
        ]
        for value in values:
            lines.append(f"    {to_enum_member(str(value))} = auto()")
        lines.extend(
            [
                "",
                "    @classmethod",
                (
                    f'    def default(cls) -> "{class_name}":'
                    if default_value is not None
                    else f'    def default(cls) -> "{class_name}" | None:'
                ),
                (
                    f"        return cls.{to_enum_member(str(default_value))}"
                    if default_value is not None
                    else "        return None"
                ),
                "",
                "    @classmethod",
                "    def values(cls) -> list[str]:",
                "        return [elt.value for elt in cls]",
                "",
                "    @classmethod",
                "    def enum_name(cls) -> str:",
                f'        return "{name}"',
                "",
                "    @classmethod",
                "    def enum_version(cls) -> str:",
                f'        return "{version}"',
                "",
            ]
        )
        return "\n".join(lines)

    value_descriptions = x_gridworks.get("value_descriptions", {})
    lines = [
        "from enum import IntEnum",
        "",
        "",
        f"class {class_name}(IntEnum):",
        f'    """Sema: {schema_url}"""',
        "",
    ]
    for value in values:
        member_name = value_descriptions.get(value, value_descriptions.get(str(value), f"Value{value}"))
        lines.append(f"    {to_enum_member(str(member_name))} = {value}")
    default_member = None
    if default_value is not None:
        default_member = value_descriptions.get(
            default_value,
            value_descriptions.get(str(default_value), f"Value{default_value}"),
        )
    lines.extend(
        [
            "",
            "    @classmethod",
            (
                f'    def default(cls) -> "{class_name}":'
                if default_member is not None
                else f'    def default(cls) -> "{class_name}" | None:'
            ),
            (
                f"        return cls.{to_enum_member(str(default_member))}"
                if default_member is not None
                else "        return None"
            ),
            "",
            "    @classmethod",
            "    def values(cls) -> list[int]:",
            "        return [int(elt.value) for elt in cls]",
            "",
            "    @classmethod",
            "    def enum_name(cls) -> str:",
            f'        return "{name}"',
            "",
            "    @classmethod",
            "    def enum_version(cls) -> str:",
            f'        return "{version}"',
            "",
        ]
    )
    return "\n".join(lines)
