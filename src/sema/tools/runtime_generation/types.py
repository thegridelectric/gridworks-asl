from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sema.tools.build_seed_dag import normalize_ref, resolve_ref_to_node
from sema.tools.runtime_generation.helpers import (
    class_name_for_node,
    import_path_and_symbol_for_node,
    load_schema_for_node,
    module_name_for_node,
    pascal_to_snake,
    target_path_for_node,
)


@dataclass
class TypeContext:
    package_name: str
    latest_map: dict[tuple[str, str], str | None]
    type_registry: dict[str, Any]
    enum_registry: dict[str, Any]
    local_names: dict[str, Any] | None = None
    imports: set[str] = field(default_factory=set)
    needs_literal: bool = False
    needs_any: bool = False
    needs_model_validator: bool = False
    needs_strict_int: bool = False
    needs_strict_float: bool = False


def generate_types(
    target_root,
    dag,
    latest,
    seed=None,
    registry=None,
    definitions_root=None,
    package_name="gjk",
    local_names: dict[str, Any] | None = None,
):
    if seed is None or registry is None or definitions_root is None:
        return
    write_base(target_root)
    for node in dag.topo_sort():
        if node[0] != "type":
            continue
        schema = load_schema_for_node(node, seed, definitions_root)
        target_path = target_path_for_node(node, latest, target_root, local_names)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            render_type(node, schema, dag, latest, registry, package_name, local_names)
        )
        write_axiom_logic_artifact(target_root, node, schema, latest, package_name, local_names)
        write_upgrade_logic_artifact(target_root, node, dag, latest, package_name, local_names)
    (target_root / "types" / "__init__.py").write_text("")
    (target_root / "types" / "old_versions" / "__init__.py").write_text("")


def write_base(target_root) -> None:
    (target_root / "base.py").write_text(
        '''import json
import re
from typing import Any, Self, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError


snake_add_underscore_to_camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def is_pascal_case(s: str) -> bool:
    return re.match(r"^[A-Z][a-zA-Z0-9]*$", s) is not None


def recursively_pascal(d: dict) -> bool:
    if isinstance(d, dict):
        for key, value in d.items():
            if key and key[0].isalpha() and not is_pascal_case(key):
                return False
            if not recursively_pascal(value):
                return False
    elif isinstance(d, list):
        for item in d:
            if not recursively_pascal(item):
                return False
    return True


def snake_to_pascal(word: str) -> str:
    return "".join(x.capitalize() or "_" for x in word.split("_"))


class SemaError(Exception):
    """Base exception for Sema-related errors."""


T = TypeVar("T", bound="SemaType")


class SemaType(BaseModel):
    type_name: str
    version: str | None = None

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        frozen=True,
        populate_by_name=True,
        extra="forbid",
    )

    def to_bytes(self) -> bytes:
        return self.model_dump_json(exclude_none=True, by_alias=True).encode()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_bytes(cls, json_bytes: bytes) -> Self:
        try:
            d = json.loads(json_bytes)
        except TypeError as e:
            raise SemaError("Type must be string or bytes!") from e
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        if not recursively_pascal(d):
            raise SemaError("Dictionary must be recursively PascalCase")
        try:
            return cls.model_validate(d)
        except ValidationError as e:
            raise SemaError(f"Validation failed: {e}") from e

    @classmethod
    def type_name_value(cls) -> str:
        return cls.model_fields["type_name"].default

    @classmethod
    def version_value(cls) -> str | None:
        return cls.model_fields["version"].default

    def upgrade(self) -> "SemaType":
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement upgrade()"
        )
'''
    )


def render_type(
    node,
    schema: dict,
    dag,
    latest_map,
    registry: dict,
    package_name: str,
    local_names: dict[str, Any] | None = None,
) -> str:
    class_name = class_name_for_node(node, latest_map, local_names)
    schema_url = schema["$id"]
    ctx = TypeContext(
        package_name=package_name,
        latest_map=latest_map,
        type_registry=registry["types"],
        enum_registry=registry["enums"],
        local_names=local_names,
    )

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    field_lines: list[str] = []
    for prop_name, prop_schema in properties.items():
        field_lines.append(_render_field(prop_name, prop_schema, required, ctx))

    axiom_methods: list[str] = []
    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    if axioms:
        ctx.needs_model_validator = True
        for axiom in axioms:
            axiom_number = axiom["number"]
            type_module_name = module_name_for_node(node, latest_map, local_names)
            ctx.imports.add(
                f"from {package_name}.sema.logic.axioms.{type_module_name} "
                f"import check_axiom_{axiom_number} as _check_axiom_{axiom_number}"
            )
            axiom_methods.append(
                f'''    @model_validator(mode="after")
    def check_axiom_{axiom_number}(self) -> "{class_name}":
        """
        Axiom {axiom_number}: {axiom["name"]}
        {" ".join(str(axiom["statement"]).split())}
        """
        return _check_axiom_{axiom_number}(self)
'''
            )

    upgrade_method = _render_upgrade_method(node, dag, latest_map, package_name, ctx)
    import_lines = _render_type_imports(ctx)

    lines: list[str] = import_lines
    if import_lines:
        lines.append("")
    lines.extend([f"class {class_name}(SemaType):", f'    """Sema: {schema_url}"""', ""])
    lines.extend(f"    {line}" for line in field_lines)
    if axiom_methods:
        lines.append("")
        lines.append("\n\n".join(ax.strip("\n") for ax in axiom_methods))
    if upgrade_method:
        lines.append("")
        lines.append(upgrade_method.strip("\n"))
    lines.append("")
    return "\n".join(lines)


def _render_type_imports(ctx: TypeContext) -> list[str]:
    lines: list[str] = []
    typing_names: list[str] = []
    pydantic_names: list[str] = []

    if ctx.needs_any:
        typing_names.append("Any")
    if ctx.needs_literal:
        typing_names.append("Literal")
    if typing_names:
        lines.append(f'from typing import {", ".join(sorted(set(typing_names)))}')

    if ctx.needs_model_validator:
        pydantic_names.append("model_validator")
    if ctx.needs_strict_float:
        pydantic_names.append("StrictFloat")
    if ctx.needs_strict_int:
        pydantic_names.append("StrictInt")
    if pydantic_names:
        lines.append(f'from pydantic import {", ".join(sorted(set(pydantic_names)))}')

    lines.append(f"from {ctx.package_name}.sema.base import SemaType")
    lines.extend(sorted(ctx.imports))
    return lines


def _render_field(prop_name: str, prop_schema: dict, required: set[str], ctx: TypeContext) -> str:
    field_name = pascal_to_snake(prop_name)
    if "const" in prop_schema:
        ctx.needs_literal = True
        const_value = prop_schema["const"]
        return f'{field_name}: Literal["{const_value}"] = "{const_value}"'

    annotation = _annotation_for_schema(prop_schema, ctx)
    default_suffix = ""
    if prop_name not in required:
        if "default" in prop_schema:
            default_suffix = f" = {repr(prop_schema['default'])}"
        else:
            annotation = f"{annotation} | None"
            default_suffix = " = None"
    elif "default" in prop_schema:
        default_suffix = f" = {repr(prop_schema['default'])}"
    return f"{field_name}: {annotation}{default_suffix}"


def _annotation_for_schema(prop_schema: dict, ctx: TypeContext) -> str:
    if "$ref" in prop_schema:
        node = resolve_ref_to_node(
            normalize_ref(prop_schema["$ref"]),
            ctx.type_registry,
            ctx.enum_registry,
        )
        if node is None:
            ctx.needs_any = True
            return "Any"
        module_path, symbol_name = import_path_and_symbol_for_node(
            node,
            ctx.latest_map,
            ctx.package_name,
            ctx.local_names,
        )
        ctx.imports.add(f"from {module_path} import {symbol_name}")
        return symbol_name

    schema_type = prop_schema.get("type")
    if schema_type == "string":
        return "str"
    if schema_type == "integer":
        ctx.needs_strict_int = True
        return "StrictInt"
    if schema_type == "number":
        ctx.needs_strict_float = True
        return "StrictFloat"
    if schema_type == "boolean":
        return "bool"
    if schema_type == "array":
        item_annotation = _annotation_for_schema(prop_schema.get("items", {}), ctx)
        return f"list[{item_annotation}]"
    if schema_type == "object":
        additional = prop_schema.get("additionalProperties")
        if isinstance(additional, dict):
            ctx.needs_any = True
            value_annotation = _annotation_for_schema(additional, ctx)
            return f"dict[str, {value_annotation}]"
        ctx.needs_any = True
        return "dict[str, Any]"

    ctx.needs_any = True
    return "Any"


def _render_upgrade_method(node, dag, latest_map, package_name: str, ctx: TypeContext) -> str | None:
    if node not in dag.upgrades:
        return None
    next_node = dag.upgrades[node]
    module_path, symbol_name = import_path_and_symbol_for_node(
        next_node,
        latest_map,
        package_name,
        ctx.local_names,
    )
    ctx.imports.add(f"from {module_path} import {symbol_name}")
    upgrade_module_name = upgrade_logic_module_name(node, next_node, latest_map, ctx.local_names)
    ctx.imports.add(
        f"from {package_name}.sema.logic.upgrades.{upgrade_module_name} "
        "import upgrade as _upgrade"
    )
    class_name = class_name_for_node(node, latest_map, ctx.local_names)
    _, name, version = node
    _, _, next_version = next_node
    return (
        f'    def upgrade(self) -> {symbol_name}:\n'
        f'        """Upgrade {name}:{version} -> {next_version}."""\n'
        "        return _upgrade(self)\n"
    )


def upgrade_logic_module_name(node, next_node, latest_map, local_names: dict[str, Any] | None = None) -> str:
    source_module = module_name_for_node(node, latest_map, local_names)
    _, _, next_version = next_node
    return f"{source_module}_to_{next_version}"


def type_import_path_for_node(
    node,
    latest_map,
    package_name: str,
    local_names: dict[str, Any] | None = None,
) -> tuple[str, str]:
    module_path, symbol_name = import_path_and_symbol_for_node(
        node,
        latest_map,
        package_name,
        local_names,
    )
    return module_path, symbol_name


def write_axiom_logic_artifact(
    target_root,
    node,
    schema: dict,
    latest_map,
    package_name: str,
    local_names: dict[str, Any] | None = None,
) -> None:
    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    if not axioms:
        return

    module_name = module_name_for_node(node, latest_map, local_names)
    module_path, class_name = type_import_path_for_node(node, latest_map, package_name, local_names)
    target_path = target_root / "logic" / "axioms" / f"{module_name}.py"

    lines = [
        "from __future__ import annotations",
        "",
        "from typing import TYPE_CHECKING",
        "",
        "if TYPE_CHECKING:",
        f"    from {module_path} import {class_name}",
        "",
    ]
    for index, axiom in enumerate(axioms):
        if index:
            lines.append("")
        axiom_number = axiom["number"]
        lines.extend(
            [
                f'def check_axiom_{axiom_number}(self: "{class_name}") -> "{class_name}":',
                "    return self",
            ]
        )
    lines.append("")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("\n".join(lines))


def write_upgrade_logic_artifact(
    target_root,
    node,
    dag,
    latest_map,
    package_name: str,
    local_names: dict[str, Any] | None = None,
) -> None:
    if node not in dag.upgrades:
        return

    next_node = dag.upgrades[node]
    module_name = upgrade_logic_module_name(node, next_node, latest_map, local_names)
    target_path = target_root / "logic" / "upgrades" / f"{module_name}.py"

    source_module_path, source_class_name = type_import_path_for_node(
        node,
        latest_map,
        package_name,
        local_names,
    )
    target_module_path, target_class_name = type_import_path_for_node(
        next_node,
        latest_map,
        package_name,
        local_names,
    )
    _, source_name, source_version = node
    _, _, target_version = next_node
    lines = [
        "from __future__ import annotations",
        "",
        "from typing import TYPE_CHECKING",
        "",
        "if TYPE_CHECKING:",
        f"    from {source_module_path} import {source_class_name}",
        f"    from {target_module_path} import {target_class_name}",
        "",
        f'def upgrade(self: "{source_class_name}") -> "{target_class_name}":',
        "    raise NotImplementedError(",
        f'        "{source_name}:{source_version} -> {target_version} upgrade not implemented"',
        "    )",
        "",
    ]
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("\n".join(lines))
