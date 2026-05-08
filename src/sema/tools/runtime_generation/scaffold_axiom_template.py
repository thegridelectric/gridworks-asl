from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from sema.tools.runtime_generation.helpers import (
    REPO_ROOT,
    sema_name_to_template_identifier,
)
from sema.tools.runtime_generation.types import _format_axiom_statement


DEFINITIONS_TYPES_DIR = REPO_ROOT / "definitions" / "types"
AXIOM_TEMPLATE_DIR = (
    REPO_ROOT / "src" / "sema" / "tools" / "runtime_generation" / "templates" / "axioms"
)


def scaffold_axiom_template(
    type_name: str,
    version: str,
    *,
    definitions_types_dir: Path = DEFINITIONS_TYPES_DIR,
    axiom_template_dir: Path = AXIOM_TEMPLATE_DIR,
) -> Path:
    schema_path = definitions_types_dir / type_name / f"{version}.yaml"
    if not schema_path.exists():
        raise ValueError(f"Missing type schema: {schema_path}")

    template_path = (
        axiom_template_dir
        / f"{sema_name_to_template_identifier(type_name)}_{version}.py.jinja2"
    )
    if template_path.exists():
        return template_path

    with schema_path.open() as handle:
        schema = yaml.safe_load(handle)

    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    if not axioms:
        raise ValueError(f"{type_name}:{version} has no x-gridworks.axioms")

    class_name_variable = f"{sema_name_to_template_identifier(type_name)}_{version}_class_name"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(
        "\n\n".join(
            _render_axiom_stub(axiom, class_name_variable)
            for axiom in axioms
        )
        + "\n"
    )
    return template_path


def scaffold_axiom_templates_for_seed(
    seed: dict,
    *,
    definitions_types_dir: Path = DEFINITIONS_TYPES_DIR,
    axiom_template_dir: Path = AXIOM_TEMPLATE_DIR,
) -> list[Path]:
    """Ensure axiom templates exist for every axiom-bearing type in ``seed``.

    Existing templates are returned unchanged. Newly created templates contain
    ``NotImplementedError`` stubs, making missing hand-written logic explicit.
    """
    paths: list[Path] = []
    for type_name, entry in sorted(seed.get("worklist", {}).get("types", {}).items()):
        if entry.get("versioning_strategy") == "none":
            schema_path = definitions_types_dir / f"{type_name}.yaml"
            if not schema_path.exists():
                continue
            schema = yaml.safe_load(schema_path.read_text())
            if schema.get("x-gridworks", {}).get("axioms"):
                raise ValueError(
                    f"{type_name} is versionless and declares x-gridworks.axioms; "
                    "versionless axiom template scaffolding is not supported"
                )
            continue

        for version in sorted(entry, key=int):
            schema_path = definitions_types_dir / type_name / f"{version}.yaml"
            schema = yaml.safe_load(schema_path.read_text())
            if not schema.get("x-gridworks", {}).get("axioms"):
                continue
            paths.append(
                scaffold_axiom_template(
                    type_name,
                    version,
                    definitions_types_dir=definitions_types_dir,
                    axiom_template_dir=axiom_template_dir,
                )
            )
    return paths


def _render_axiom_stub(axiom: dict[str, Any], class_name_variable: str) -> str:
    axiom_number = int(axiom["number"])
    statement = axiom.get("statement", axiom.get("description", ""))
    statement_block = _format_axiom_statement(statement)
    return (
        '    @model_validator(mode="after")\n'
        f"    def check_axiom_{axiom_number}(self) -> \"{{{{ {class_name_variable} }}}}\":\n"
        '        """\n'
        f'        Axiom {axiom_number}: {axiom["name"]}\n'
        f"{statement_block}\n"
        '        """\n'
        f'        raise NotImplementedError("Axiom {axiom_number} validation is not implemented.")'
    )
