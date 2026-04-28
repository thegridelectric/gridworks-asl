from pathlib import Path
from types import SimpleNamespace

import pytest

from sema.tools.runtime_generation.scaffold_axiom_template import (
    scaffold_axiom_template,
    scaffold_axiom_templates_for_seed,
)
from sema.tools.runtime_generation.types import render_type


def test_scaffold_axiom_template_creates_missing_template(tmp_path: Path) -> None:
    definitions_types = tmp_path / "definitions" / "types"
    schema_dir = definitions_types / "example.type"
    schema_dir.mkdir(parents=True)
    (schema_dir / "000.yaml").write_text(
        """
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.electricity.works/types/example.type/000"
title: "example.type"
type: object
properties:
  TypeName:
    const: "example.type"
  Version:
    const: "000"
required:
  - TypeName
  - Version
additionalProperties: false
x-gridworks:
  owner: "gridworks-energy"
  axioms:
    - number: 1
      name: "StructuredAxiom"
      statement: >
        Example SHALL preserve prose and bullets:

          - First condition SHALL hold.
          - Second condition SHALL hold.
""".lstrip()
    )

    template_dir = tmp_path / "templates" / "axioms"
    path = scaffold_axiom_template(
        "example.type",
        "000",
        definitions_types_dir=definitions_types,
        axiom_template_dir=template_dir,
    )

    text = path.read_text()
    assert path == template_dir / "example_type_000.py.jinja2"
    assert 'def check_axiom_1(self) -> "{{ example_type_000_class_name }}":' in text
    assert "Axiom 1: StructuredAxiom" in text
    assert "Example SHALL preserve prose and bullets:" in text
    assert "\n\n          - First condition SHALL hold." in text
    assert 'raise NotImplementedError("Axiom 1 validation is not implemented.")' in text

    assert scaffold_axiom_template(
        "example.type",
        "000",
        definitions_types_dir=definitions_types,
        axiom_template_dir=template_dir,
    ) == path


def test_runtime_generation_fails_when_axiom_template_is_missing() -> None:
    schema = {
        "$id": "https://schemas.electricity.works/types/example.type/000",
        "title": "example.type",
        "type": "object",
        "properties": {
            "TypeName": {"const": "example.type"},
            "Version": {"const": "000"},
        },
        "required": ["TypeName", "Version"],
        "additionalProperties": False,
        "x-gridworks": {
            "owner": "gridworks-energy",
            "axioms": [
                {
                    "number": 1,
                    "name": "StructuredAxiom",
                    "statement": "Example SHALL be validated.",
                }
            ],
        },
    }

    with pytest.raises(
        ValueError,
        match=(
            "example\\.type:000 declares x-gridworks\\.axioms but is missing "
            "axiom template"
        ),
    ):
        render_type(
            ("type", "example.type", "000"),
            schema,
            SimpleNamespace(upgrades={}),
            {("type", "example.type"): "000"},
            {"types": {"example.type": {"versions": {"000": {}}}}, "enums": {}},
            "sema.runtime",
        )


def test_scaffold_axiom_templates_for_seed_is_idempotent(tmp_path: Path) -> None:
    definitions_types = tmp_path / "definitions" / "types"
    schema_dir = definitions_types / "example.type"
    schema_dir.mkdir(parents=True)
    (schema_dir / "000.yaml").write_text(
        """
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.electricity.works/types/example.type/000"
title: "example.type"
type: object
properties:
  TypeName:
    const: "example.type"
  Version:
    const: "000"
required:
  - TypeName
  - Version
additionalProperties: false
x-gridworks:
  owner: "gridworks-energy"
  axioms:
    - number: 1
      name: "StructuredAxiom"
      statement: >
        Example SHALL be validated.
""".lstrip()
    )
    seed = {
        "worklist": {
            "types": {
                "example.type": {
                    "000": {"path": "definitions/types/example.type/000.yaml"}
                }
            }
        }
    }
    template_dir = tmp_path / "templates" / "axioms"
    expected_path = template_dir / "example_type_000.py.jinja2"

    assert scaffold_axiom_templates_for_seed(
        seed,
        definitions_types_dir=definitions_types,
        axiom_template_dir=template_dir,
    ) == [expected_path]
    assert scaffold_axiom_templates_for_seed(
        seed,
        definitions_types_dir=definitions_types,
        axiom_template_dir=template_dir,
    ) == [expected_path]
