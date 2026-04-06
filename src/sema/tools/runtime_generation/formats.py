from __future__ import annotations

from dataclasses import dataclass, field

from sema.tools.runtime_generation.naming import class_name_for_node, sema_name_to_module
from sema.tools.runtime_generation.schema import load_schema_for_node


@dataclass
class FormatArtifact:
    imports: set[str] = field(default_factory=set)
    bodies: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)


def generate_formats(target_root, dag, seed=None, definitions_root=None):
    if seed is None or definitions_root is None:
        return
    artifact = FormatArtifact()
    for node in sorted(dag.nodes):
        if node[0] != "format":
            continue
        schema = load_schema_for_node(node, seed, definitions_root)
        merge_format_artifact(artifact, render_format(node, schema))
    (target_root / "property_format.py").write_text(build_property_format_text(artifact))


def build_property_format_text(artifact: FormatArtifact) -> str:
    lines = ['"""Generated snapshot property formats."""', ""]
    lines.extend(sorted(artifact.imports))
    if artifact.imports:
        lines.append("")
    lines.extend(artifact.bodies)
    if artifact.bodies:
        lines.append("")
    lines.extend(artifact.aliases)
    if artifact.aliases:
        lines.append("")
    lines.extend(artifact.classes)
    if artifact.classes:
        lines.append("")
    return "\n".join(lines)


def merge_format_artifact(target: FormatArtifact, source: FormatArtifact) -> None:
    target.imports.update(source.imports)
    _extend_unique(target.bodies, source.bodies)
    _extend_unique(target.aliases, source.aliases)
    _extend_unique(target.classes, source.classes)


def _extend_unique(target: list[str], source: list[str]) -> None:
    for item in source:
        if item not in target:
            target.append(item)


def render_format(node, schema: dict) -> FormatArtifact:
    _, name, version = node
    if version is not None:
        raise ValueError(f"Format nodes must not have version: {node}")

    artifact = FormatArtifact()
    alias_name = class_name_for_node(node, {})
    helper_name = f"is_{sema_name_to_module(name)}"
    format_class_name = f"{alias_name}Format"
    type_name = schema["type"]
    artifact.imports.update({"from typing import Annotated", "from pydantic import BeforeValidator"})

    if type_name == "string":
        artifact.imports.add("import re")
        pattern_name = f"_{sema_name_to_module(name).upper()}_PATTERN"
        body: list[str] = []
        if pattern := schema.get("pattern"):
            body.append(f'{pattern_name} = re.compile(r"{pattern}")')
            body.append("")
        body.extend(
            [
                f"def {helper_name}(v: str) -> str:",
                '    if not isinstance(v, str):',
                f'        raise ValueError("Expected string for {name}.")',
            ]
        )
        if min_length := schema.get("minLength"):
            body.append(f"    if len(v) < {min_length}:")
            body.append(f'        raise ValueError("{name} must have length >= {min_length}.")')
        if max_length := schema.get("maxLength"):
            body.append(f"    if len(v) > {max_length}:")
            body.append(f'        raise ValueError("{name} must have length <= {max_length}.")')
        if schema.get("pattern"):
            body.append(f"    if not {pattern_name}.fullmatch(v):")
            body.append(f'        raise ValueError("Fails {name} pattern.")')
        body.append("    return v")
        artifact.bodies.append("\n".join(body))
        artifact.aliases.append(f"{alias_name} = Annotated[str, BeforeValidator({helper_name})]")
        artifact.classes.append(
            f'''class {format_class_name}:
    @staticmethod
    def validate(v: str) -> str:
        return {helper_name}(v)
'''
        )
        return artifact

    if type_name == "integer":
        body = [
            f"def {helper_name}(v: int) -> int:",
            "    if isinstance(v, bool) or not isinstance(v, int):",
            f'        raise ValueError("Expected integer for {name}.")',
        ]
        if minimum := schema.get("minimum"):
            body.append(f"    if v < {minimum}:")
            body.append(f'        raise ValueError("{name} must be >= {minimum}.")')
        if maximum := schema.get("maximum"):
            body.append(f"    if v > {maximum}:")
            body.append(f'        raise ValueError("{name} must be <= {maximum}.")')
        body.append("    return v")
        artifact.bodies.append("\n".join(body))
        artifact.aliases.append(f"{alias_name} = Annotated[int, BeforeValidator({helper_name})]")
        artifact.classes.append(
            f'''class {format_class_name}:
    @staticmethod
    def validate(v: int) -> int:
        return {helper_name}(v)
'''
        )
        return artifact

    raise NotImplementedError(f"Unsupported format schema type for {name}: {type_name}")
