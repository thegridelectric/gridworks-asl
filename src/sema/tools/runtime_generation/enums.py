from __future__ import annotations

from typing import Any

from sema.tools.runtime_generation.helpers import (
    LeftRightDot,
    class_name_for_node,
    integer_enum_member_name,
    load_schema_for_node,
    render_init_module,
    string_enum_member_name,
    target_path_for_node,
)


def generate_enums(
    target_root,
    dag,
    dag_max,
    seed=None,
    import_root: str = "sema.runtime",
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
):
    if seed is None:
        return
    write_enum_base(target_root)
    for node in dag.topo_sort():
        if node[0] != "enum":
            continue
        schema = load_schema_for_node(node, seed)
        target_path = target_path_for_node(node, dag_max, target_root, local_names)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(render_enum(node, schema, dag_max, import_root, local_names))
    (target_root / "enums" / "__init__.py").write_text(
        render_init_module("enum", dag, dag_max, import_root, local_names)
    )
    # Intentionally empty: eager imports here would deadlock with latest enums.
    (target_root / "enums" / "old_versions" / "__init__.py").write_text("")


def write_enum_base(target_root) -> None:
    (target_root / "enums").mkdir(parents=True, exist_ok=True)
    (target_root / "enums" / "gw_str_enum.py").write_text(
        '''from enum import StrEnum
from typing import Any, Self


class GwStrEnum(StrEnum):
    """
    Mimics fastapi-utils use of StrEnum, which diverges from the
    python-native StrEnum for python 3.11+.  Also, fills in with default
    value if a string does not exist in the enum.

    Specifically (re difference with python StrEnum) if

    class Foo(Enum):
        Bar = auto()

    then

    Foo.Bar.value is 'Bar' (instead of 'bar')

    """

    @staticmethod
    def _generate_next_value_(
        name: str,
        start: int,  # noqa: ARG004
        count: int,  # noqa: ARG004
        last_values: list[Any],  # noqa: ARG004
    ) -> str:
        return name

    @classmethod
    def values(cls) -> list[str]:
        return [str(elt) for elt in cls]

    @classmethod
    def default(cls) -> Self | None:
        return None

    @classmethod
    def _missing_(cls, value: object) -> Self:
        default = cls.default()
        if default is None:
            raise ValueError(f"'{value}' is not valid {cls.__name__}")
        return default

class SemaEnum(GwStrEnum):
    """
    Base for enums published in Sema.
    Requires enum_name(). Version is optional (return None for stable enums).
    """

    @classmethod
    def enum_name(cls) -> str:
        """Sema identifier (e.g., 'gw1.relay.state')"""
        raise NotImplementedError(
            f"{cls.__name__} must implement enum_name() for Sema"
        )

    @classmethod
    def enum_version(cls) -> str:
        """Sema identifier (e.g., '000')"""
        raise NotImplementedError(
            f"{cls.__name__} must implement enum_name() for Sema"
        )


class SymbolizedEnum(SemaEnum):
    @classmethod
    def symbol_to_value(cls, symbol: str) -> str:
        raise NotImplementedError

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        raise NotImplementedError

    @classmethod
    def symbols(cls) -> list[str]:
        raise NotImplementedError
'''
    )


def render_enum(
    node,
    schema: dict,
    dag_max,
    import_root: str,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> str:
    _, name, version = node
    class_name = class_name_for_node(node, dag_max, local_names)
    schema_url = schema["$id"]
    values = schema["enum"]
    default_value = schema.get("default")
    x_gridworks = schema.get("x-gridworks", {})

    if schema["type"] == "string":
        return _render_string_enum(
            class_name,
            schema_url,
            name,
            version,
            values,
            default_value,
            import_root,
        )

    if schema["type"] != "integer":
        raise ValueError(f"Unsupported enum schema type for {name}: {schema['type']}")

    value_descriptions = x_gridworks.get("value_descriptions")
    if not isinstance(value_descriptions, dict):
        raise ValueError(
            f"Integer enum {name}:{version} requires x-gridworks.value_descriptions"
        )
    return _render_integer_enum(
        class_name,
        schema_url,
        name,
        version,
        values,
        default_value,
        value_descriptions,
    )


def _render_string_enum(
    class_name: str,
    schema_url: str,
    name: str,
    version: str,
    values: list[str],
    default_value: str | None,
    import_root: str,
) -> str:
    lines = [
        "from enum import auto",
        "",
        f"from {import_root}.enums.gw_str_enum import SemaEnum",
        "",
        "",
        f"class {class_name}(SemaEnum):",
        f'    """Sema: {schema_url}"""',
        "",
    ]
    for value in values:
        member_name = string_enum_member_name(str(value))
        lines.append(f"    {member_name} = auto()")
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
                f"        return cls.{string_enum_member_name(str(default_value))}"
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


def _render_integer_enum(
    class_name: str,
    schema_url: str,
    name: str,
    version: str,
    values: list[int],
    default_value: int | None,
    value_descriptions: dict[Any, Any],
) -> str:
    lines = [
        "from enum import IntEnum",
        "",
        "",
        f"class {class_name}(IntEnum):",
        f'    """Sema: {schema_url}"""',
        "",
    ]
    for value in values:
        member_name = integer_enum_member_name(value, value_descriptions)
        lines.append(f"    {member_name} = {value}")
    default_member = None
    if default_value is not None:
        default_member = integer_enum_member_name(default_value, value_descriptions)
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
                f"        return cls.{default_member}"
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
