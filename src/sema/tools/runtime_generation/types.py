from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

from jinja2 import Environment, StrictUndefined

from sema.tools.build_seed_dag import normalize_ref, resolve_ref_to_node
from sema.tools.runtime_generation.helpers import (
    LeftRightDot,
    class_name_for_node,
    get_local_class_name,
    import_path_and_symbol_for_node,
    load_schema_for_node,
    module_name_for_node,
    pascal_to_snake,
    render_init_module,
    sema_name_to_template_identifier,
    target_path_for_node,
)


TEMPLATE_ROOT = Path(__file__).parent / "templates"
TEMPLATE_VARIABLE_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


@dataclass
class TypeContext:
    import_root: str
    dag_max: dict[tuple[str, str], str | None]
    type_registry: dict[str, Any]
    enum_registry: dict[str, Any]
    local_names: dict[LeftRightDot, LeftRightDot] | None = None
    imports: set[str] = field(default_factory=set)
    needs_literal: bool = False
    needs_any: bool = False
    needs_model_validator: bool = False
    needs_base_model: bool = False
    needs_config_dict: bool = False
    needs_strict_int: bool = False
    needs_strict_float: bool = False
    inline_classes: list[str] = field(default_factory=list)


def generate_types(
    target_root,
    dag,
    dag_max,
    seed=None,
    registry=None,
    import_root: str = "sema.runtime",
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
):
    if seed is None or registry is None:
        return
    for node in dag.topo_sort():
        if node[0] != "type":
            continue
        schema = load_schema_for_node(node, seed)
        target_path = target_path_for_node(node, dag_max, target_root, local_names)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            render_type(node, schema, dag, dag_max, registry, import_root, local_names)
        )
    (target_root / "types" / "__init__.py").write_text(
        render_init_module("type", dag, dag_max, import_root, local_names)
    )
    # Intentionally empty: eager imports here would deadlock with latest types.
    (target_root / "types" / "old_versions" / "__init__.py").write_text("")


def render_type(
    node,
    schema: dict,
    dag,
    dag_max,
    registry: dict,
    import_root: str,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> str:
    class_name = class_name_for_node(node, dag_max, local_names)
    schema_url = schema["$id"]
    ctx = TypeContext(
        import_root=import_root,
        dag_max=dag_max,
        type_registry=registry["types"],
        enum_registry=registry["enums"],
        local_names=local_names,
    )

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    field_lines: list[str] = []
    for prop_name, prop_schema in properties.items():
        field_lines.append(
            _render_field(
                prop_name,
                prop_schema,
                required,
                ctx,
                inline_path=[prop_name],
                inline_depth=0,
            )
        )

    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    axiom_methods = _render_axiom_methods(schema, node, dag_max, registry, ctx)

    projection_prelude, projection_classmethod, projection_axioms = (
        _render_projection_artifacts(schema, class_name, ctx)
    )
    if projection_axioms and not axiom_methods and not axioms:
        axiom_methods = projection_axioms

    if axioms or axiom_methods:
        ctx.needs_model_validator = True
    if schema.get("additionalProperties") is True:
        ctx.needs_config_dict = True

    upgrade_method = _render_upgrade_method(node, dag, dag_max, registry, ctx)
    import_lines = _render_type_imports(ctx)

    class_lines = [f"class {class_name}(SemaType):", f'    """Sema: {schema_url}"""', ""]
    sections: list[str] = []
    if import_lines:
        sections.append("\n".join(import_lines))
    if projection_prelude:
        sections.append(projection_prelude)
    sections.extend(ctx.inline_classes)
    sections.append("\n".join(class_lines))

    lines: list[str] = ["\n\n\n".join(sections)]
    lines.extend(f"    {line}" for line in field_lines)
    if schema.get("additionalProperties") is True:
        lines.append("")
        lines.append(
            '    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))'
        )
    if projection_classmethod:
        lines.append("")
        lines.append(projection_classmethod)
    if axiom_methods:
        lines.append("")
        lines.append("\n\n".join(ax.strip("\n") for ax in axiom_methods))
    if upgrade_method:
        lines.append("")
        lines.append(upgrade_method.strip("\n"))
    lines.append("")
    return "\n".join(lines)


def _render_projection_artifacts(
    schema: dict,
    class_name: str,
    ctx: TypeContext,
) -> tuple[str | None, str | None, list[str]]:
    """Emit projection codegen for a type with x-gridworks.projection.

    Returns (module_prelude, classmethod_text, axiom_methods). Each is None /
    empty when the schema declares no projection.

    - module_prelude: ``_PROJECTION = { ... }`` placed above the class.
    - classmethod_text: ``project()`` classmethod for the class body.
    - axiom_methods: synthesized axiom bodies that compare ``self.project(...)``
      to the target field. Emitted only when no per-type axiom Jinja file
      exists; otherwise the Jinja file wins (axiom_methods returned here is
      ignored by the caller in that case).
    """
    projection = schema.get("x-gridworks", {}).get("projection")
    if not projection:
        return None, None, []

    from_prop = projection["from"]
    to_prop = projection["to"]
    table = projection["table"]
    properties = schema["properties"]

    from_class = _annotation_for_schema(properties[from_prop], ctx)
    to_class = _annotation_for_schema(properties[to_prop], ctx)
    from_snake = pascal_to_snake(from_prop)
    to_snake = pascal_to_snake(to_prop)

    dict_lines = ["_PROJECTION = {"]
    for source_value, target_value in table.items():
        dict_lines.append(
            f"    {from_class}.{source_value}: {to_class}.{target_value},"
        )
    dict_lines.append("}")
    module_prelude = "\n".join(dict_lines)

    classmethod_text = "\n".join(
        [
            "    @classmethod",
            f"    def project(cls, {from_snake}: {from_class}) -> {to_class}:",
            f"        expected = _PROJECTION.get({from_snake})",
            "        if expected is None:",
            "            raise ValueError(",
            f'                f"No projection defined for {from_snake} {{{from_snake}!r}}."',
            "            )",
            "        return expected",
        ]
    )

    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    axiom_methods: list[str] = []
    for axiom in axioms:
        axiom_number = axiom["number"]
        statement_block = _format_axiom_statement(axiom["statement"])
        axiom_methods.append(
            f'    @model_validator(mode="after")\n'
            f'    def check_axiom_{axiom_number}(self) -> "{class_name}":\n'
            f'        """\n'
            f'        Axiom {axiom_number}: {axiom["name"]}\n'
            f"{statement_block}\n"
            f'        """\n'
            f"        expected = self.project(self.{from_snake})\n"
            f"        if expected != self.{to_snake}:\n"
            f"            raise ValueError(\n"
            f'                "Axiom {axiom_number} failed: '
            f'{from_snake} and {to_snake} do not match the enumerated projection."\n'
            f"            )\n"
            f"        return self"
        )
    return module_prelude, classmethod_text, axiom_methods


def _format_axiom_statement(statement: str, indent_spaces: int = 8) -> str:
    """Format an axiom statement for a generated docstring.

    Preserve blank lines, bullets, and indented blocks. Wrap ordinary prose
    lines to the generated docstring width.
    """
    indent = " " * indent_spaces
    width = 92
    text = textwrap.dedent(str(statement)).strip("\n")

    formatted_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            formatted_lines.append("")
        elif line.startswith((" ", "\t")) or stripped.startswith(("-", "*")):
            formatted_lines.append(indent + line.rstrip())
        else:
            formatted_lines.append(
                textwrap.fill(
                    stripped,
                    width=width,
                    initial_indent=indent,
                    subsequent_indent=indent,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
    return "\n".join(formatted_lines)


def _render_type_imports(ctx: TypeContext) -> list[str]:
    lines: list[str] = []
    typing_names: list[str] = []
    pydantic_names: list[str] = []

    if ctx.needs_any:
        typing_names.append("Any")
    if ctx.needs_literal:
        typing_names.append("Literal")
    if any("Self" in import_line for import_line in ctx.imports):
        typing_names.append("Self")
    if typing_names:
        lines.append(f'from typing import {", ".join(sorted(set(typing_names)))}')

    if ctx.needs_config_dict:
        pydantic_names.append("ConfigDict")
    if ctx.needs_base_model:
        pydantic_names.append("BaseModel")
    if ctx.needs_model_validator:
        pydantic_names.append("model_validator")
    if any("ValidationError" in import_line for import_line in ctx.imports):
        pydantic_names.append("ValidationError")
    if ctx.needs_strict_float:
        pydantic_names.append("StrictFloat")
    if ctx.needs_strict_int:
        pydantic_names.append("StrictInt")
    if pydantic_names:
        lines.append(f'from pydantic import {", ".join(sorted(set(pydantic_names)))}')

    lines.append(f"from {ctx.import_root}.base import SemaType")
    lines.extend(
        sorted(
            line
            for line in ctx.imports
            if line not in {"Self", "ValidationError"}
        )
    )
    return lines


def _render_field(
    prop_name: str,
    prop_schema: dict,
    required: set[str],
    ctx: TypeContext,
    *,
    inline_path: list[str] | None = None,
    inline_depth: int = 0,
) -> str:
    field_name = pascal_to_snake(prop_name)
    if "const" in prop_schema:
        ctx.needs_literal = True
        const_value = prop_schema["const"]
        return f'{field_name}: Literal["{const_value}"] = "{const_value}"'

    annotation = _annotation_for_schema(
        prop_schema,
        ctx,
        inline_path=inline_path or [prop_name],
        inline_depth=inline_depth,
    )
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


def _annotation_for_schema(
    prop_schema: dict,
    ctx: TypeContext,
    *,
    inline_path: list[str] | None = None,
    inline_depth: int = 0,
) -> str:
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
            ctx.dag_max,
            ctx.import_root,
            ctx.local_names,
        )
        ctx.imports.add(f"from {module_path} import {symbol_name}")
        return symbol_name

    if "oneOf" in prop_schema:
        members = [
            _annotation_for_schema(
                member,
                ctx,
                inline_path=inline_path,
                inline_depth=inline_depth,
            )
            for member in prop_schema["oneOf"]
        ]
        return " | ".join(members)

    schema_type = prop_schema.get("type")
    if isinstance(schema_type, list):
        non_null_types = [item for item in schema_type if item != "null"]
        if len(non_null_types) == 1 and len(non_null_types) != len(schema_type):
            narrowed_schema = dict(prop_schema)
            narrowed_schema["type"] = non_null_types[0]
            return (
                f"{_annotation_for_schema(narrowed_schema, ctx, inline_path=inline_path, inline_depth=inline_depth)}"
                " | None"
            )
        ctx.needs_any = True
        return "Any"
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
        item_annotation = _annotation_for_schema(
            prop_schema.get("items", {}),
            ctx,
            inline_path=[*(inline_path or []), "Item"],
            inline_depth=inline_depth,
        )
        return f"list[{item_annotation}]"
    if schema_type == "object":
        if "properties" in prop_schema:
            return _render_inline_object_class(
                prop_schema,
                ctx,
                inline_path=inline_path or ["InlineObject"],
                inline_depth=inline_depth,
            )
        additional = prop_schema.get("additionalProperties")
        if isinstance(additional, dict):
            ctx.needs_any = True
            value_annotation = _annotation_for_schema(
                additional,
                ctx,
                inline_path=[*(inline_path or []), "Value"],
                inline_depth=inline_depth,
            )
            return f"dict[str, {value_annotation}]"
        ctx.needs_any = True
        return "dict[str, Any]"

    ctx.needs_any = True
    return "Any"


def _inline_class_name(inline_path: list[str]) -> str:
    return "".join(inline_path)


def _render_inline_object_class(
    prop_schema: dict,
    ctx: TypeContext,
    *,
    inline_path: list[str],
    inline_depth: int,
) -> str:
    if inline_depth >= 1:
        path = ".".join(inline_path)
        raise ValueError(
            f"Nested inline object generation is not yet supported at {path}. "
            "Inline objects are currently supported only at depth one."
        )

    ctx.needs_base_model = True
    ctx.needs_config_dict = True
    class_name = _inline_class_name(inline_path)
    required = set(prop_schema.get("required", []))
    properties = prop_schema.get("properties", {})
    field_lines = [
        _render_field(
            prop_name,
            field_schema,
            required,
            ctx,
            inline_path=[*inline_path, prop_name],
            inline_depth=inline_depth + 1,
        )
        for prop_name, field_schema in properties.items()
    ]

    extra = "allow" if prop_schema.get("additionalProperties") is True else "forbid"
    lines = [
        f"class {class_name}(BaseModel):",
        '    model_config = ConfigDict(',
        '        alias_generator=SemaType.model_config.get("alias_generator"),',
        "        populate_by_name=True,",
        f'        extra="{extra}",',
        "    )",
        "",
    ]
    lines.extend(f"    {line}" for line in field_lines)
    ctx.inline_classes.append("\n".join(lines))
    return class_name


def _render_upgrade_method(
    node,
    dag,
    dag_max,
    registry: dict,
    ctx: TypeContext,
) -> str | None:
    if node not in dag.upgrades:
        return None
    next_node = dag.upgrades[node]
    module_path, symbol_name = import_path_and_symbol_for_node(
        next_node,
        dag_max,
        ctx.import_root,
        ctx.local_names,
    )
    ctx.imports.add(f"from {module_path} import {symbol_name}")

    template_path = _upgrade_template_path(node, next_node)
    if not template_path.exists():
        _, name, version = node
        _, _, next_version = next_node
        raise ValueError(
            f"{name}:{version} requires an upgrade to {next_version} but is missing "
            f"upgrade template {template_path}. Create it with: "
            f"uv run sema runtime scaffold-upgrade-template {name} {version} {next_version}"
        )
    return _render_logic_template(
        template_path,
        node,
        dag_max,
        registry,
        ctx,
    )


def upgrade_logic_module_name(
    node,
    next_node,
    dag_max,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> str:
    source_module = module_name_for_node(node, dag_max, local_names)
    _, _, next_version = next_node
    return f"{source_module}_to_{next_version}"


def type_import_path_for_node(
    node,
    dag_max,
    import_root: str,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> tuple[str, str]:
    module_path, symbol_name = import_path_and_symbol_for_node(
        node,
        dag_max,
        import_root,
        local_names,
    )
    return module_path, symbol_name


def _render_axiom_methods(
    schema: dict,
    node,
    dag_max,
    registry: dict,
    ctx: TypeContext,
) -> list[str]:
    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    if not axioms:
        return []
    template_path = _axiom_template_path(node)
    if not template_path.exists():
        _, sema_name, version = node
        raise ValueError(
            f"{sema_name}:{version} declares x-gridworks.axioms but is missing "
            f"axiom template {template_path}. Create it with: "
            f"uv run sema runtime scaffold-axiom-template {sema_name} {version}"
        )
    rendered = _render_logic_template(
        template_path,
        node,
        dag_max,
        registry,
        ctx,
    )
    return [rendered]


def _axiom_template_path(node) -> Path:
    _, sema_name, version = node
    return (
        TEMPLATE_ROOT
        / "axioms"
        / f"{sema_name_to_template_identifier(sema_name)}_{version}.py.jinja2"
    )


def _upgrade_template_path(node, next_node) -> Path:
    _, sema_name, version = node
    _, _, next_version = next_node
    return (
        TEMPLATE_ROOT
        / "upgrades"
        / f"{sema_name_to_template_identifier(sema_name)}_{version}_to_{next_version}.py.jinja2"
    )


def _render_logic_template(
    template_path: Path,
    current_node,
    dag_max,
    registry: dict,
    ctx: TypeContext,
) -> str:
    template_text = template_path.read_text()
    variables = set(TEMPLATE_VARIABLE_RE.findall(template_text))
    context = _logic_template_context(registry, dag_max, ctx.local_names)
    missing = sorted(variable for variable in variables if variable not in context)
    if missing:
        raise ValueError(
            f"{template_path} uses unknown logic template variables: {', '.join(missing)}"
        )

    for variable in variables:
        node = context[variable + "__node"]
        if node == current_node:
            continue
        module_path, symbol_name = import_path_and_symbol_for_node(
            node,
            dag_max,
            ctx.import_root,
            ctx.local_names,
        )
        ctx.imports.add(f"from {module_path} import {symbol_name}")

    if "ValidationError" in template_text:
        ctx.imports.add("ValidationError")
    if "Self" in template_text:
        ctx.imports.add("Self")

    env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    rendered = env.from_string(template_text).render(context).rstrip()
    return rendered


def _logic_template_context(
    registry: dict,
    dag_max,
    local_names: dict[LeftRightDot, LeftRightDot] | None = None,
) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for kind in ("enum", "type"):
        registry_section = registry[f"{kind}s"]
        for sema_name, entry in registry_section.items():
            for version in _registry_versions(entry):
                variable = (
                    f"{sema_name_to_template_identifier(sema_name)}_"
                    f"{version}_class_name"
                )
                node = (kind, sema_name, version)
                context[variable] = _registered_class_name(
                    kind,
                    sema_name,
                    version,
                    entry,
                    dag_max,
                    local_names,
                )
                context[variable + "__node"] = node
    return context


def _registry_versions(entry: dict) -> list[str]:
    if "versions" in entry:
        return list(entry["versions"].keys())
    schema_url = str(entry.get("schema_url", ""))
    version = schema_url.rstrip("/").split("/")[-1]
    return [version] if version else []


def _registered_class_name(
    kind: str,
    sema_name: LeftRightDot,
    version: str,
    registry_entry: dict,
    dag_max,
    local_names: dict[LeftRightDot, LeftRightDot] | None,
) -> str:
    base = get_local_class_name(f"{kind}s", sema_name, local_names)
    latest_version = dag_max.get(
        (kind, sema_name),
        registry_entry.get("latest_version"),
    )
    if latest_version is None:
        latest_version = _registry_versions(registry_entry)[0]
    if latest_version == version:
        return base
    return f"{base}{version}"
