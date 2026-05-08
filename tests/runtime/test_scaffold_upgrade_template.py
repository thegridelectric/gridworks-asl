from pathlib import Path
from types import SimpleNamespace
import ast
import re

import pytest
import yaml

from sema.tools.runtime_generation.scaffold_upgrade_template import (
    scaffold_upgrade_template,
    scaffold_upgrade_templates_for_seed,
)
from sema.tools.runtime_generation.types import _render_upgrade_method


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "definitions" / "registry.yaml"
UPGRADE_TEMPLATE_DIR = (
    REPO_ROOT / "src" / "sema" / "tools" / "runtime_generation" / "templates" / "upgrades"
)
JINJA_VARIABLE_RE = re.compile(r"{{\s*[a-zA-Z_][a-zA-Z0-9_]*\s*}}")


def _normalize_words(text: str) -> str:
    return " ".join(text.split())


def _type_name_and_versions(template_path: Path) -> tuple[str, str, str]:
    stem = template_path.name.removesuffix(".py.jinja2")
    source, next_version = stem.rsplit("_to_", 1)
    type_identifier, version = source.rsplit("_", 1)
    return type_identifier.replace("_", "."), version, next_version


def _upgrade_docstring(template_path: Path) -> str:
    source = JINJA_VARIABLE_RE.sub("TemplateSymbol", template_path.read_text())
    module = ast.parse("class TemplateClass:\n" + source, filename=str(template_path))
    class_def = module.body[0]
    assert isinstance(class_def, ast.ClassDef)
    for child in class_def.body:
        if isinstance(child, ast.FunctionDef) and child.name == "upgrade":
            docstring = ast.get_docstring(child)
            assert docstring is not None, template_path
            return docstring
    raise AssertionError(f"{template_path} has no upgrade method")


def test_upgrade_template_docstrings_match_registry_summaries() -> None:
    registry = yaml.safe_load(REGISTRY_PATH.read_text())

    findings: list[str] = []
    for template_path in sorted(UPGRADE_TEMPLATE_DIR.glob("*.py.jinja2")):
        type_name, _, next_version = _type_name_and_versions(template_path)
        expected = registry["types"][type_name]["versions"][next_version]["summary"]
        actual = _upgrade_docstring(template_path)
        if _normalize_words(actual) != _normalize_words(expected):
            findings.append(
                f"{template_path.name}: docstring {actual!r} != registry summary {expected!r}"
            )

    assert not findings, "\n".join(findings)


def test_scaffold_upgrade_template_creates_missing_template(tmp_path: Path) -> None:
    template_dir = tmp_path / "templates" / "upgrades"

    path = scaffold_upgrade_template(
        "example.type",
        "000",
        "001",
        upgrade_template_dir=template_dir,
    )

    text = path.read_text()
    assert path == template_dir / "example_type_000_to_001.py.jinja2"
    assert "def upgrade(self) -> {{ example_type_001_class_name }}:" in text
    assert '"""Upgrade example.type:000 -> 001."""' in text
    assert (
        'raise NotImplementedError(\n'
        '            "example.type:000 -> 001 upgrade not implemented"'
    ) in text


def test_scaffold_upgrade_template_is_idempotent(tmp_path: Path) -> None:
    template_dir = tmp_path / "templates" / "upgrades"
    first = scaffold_upgrade_template(
        "example.type", "000", "001", upgrade_template_dir=template_dir
    )
    first_mtime = first.stat().st_mtime_ns
    second = scaffold_upgrade_template(
        "example.type", "000", "001", upgrade_template_dir=template_dir
    )
    assert second == first
    assert second.stat().st_mtime_ns == first_mtime  # not rewritten


def _write_minimal_schema(path: Path, type_name: str, version: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.electricity.works/types/{type_name}/{version}"
title: "{type_name}"
type: object
properties:
  TypeName:
    const: "{type_name}"
  Version:
    const: "{version}"
required:
  - TypeName
  - Version
additionalProperties: false
x-gridworks:
  owner: "gridworks-energy"
"""
    )


def test_scaffold_upgrade_templates_for_seed_creates_scada_v000(tmp_path: Path) -> None:
    """Confirms the seed-walker creates the upgrade template for
    ``scada.control.capabilities:000`` (which has 001 as its successor).
    """
    definitions_types = tmp_path / "definitions" / "types"
    _write_minimal_schema(
        definitions_types / "scada.control.capabilities" / "000.yaml",
        "scada.control.capabilities",
        "000",
    )
    _write_minimal_schema(
        definitions_types / "scada.control.capabilities" / "001.yaml",
        "scada.control.capabilities",
        "001",
    )

    seed = {
        "worklist": {
            "types": {
                "scada.control.capabilities": {
                    "000": {"path": "definitions/types/scada.control.capabilities/000.yaml"},
                    "001": {"path": "definitions/types/scada.control.capabilities/001.yaml"},
                }
            }
        }
    }

    template_dir = tmp_path / "templates" / "upgrades"
    expected = template_dir / "scada_control_capabilities_000_to_001.py.jinja2"

    paths = scaffold_upgrade_templates_for_seed(
        seed,
        definitions_types_dir=definitions_types,
        upgrade_template_dir=template_dir,
    )
    assert paths == [expected]
    assert expected.exists()
    text = expected.read_text()
    assert "def upgrade(self) -> {{ scada_control_capabilities_001_class_name }}:" in text
    assert '"""Upgrade scada.control.capabilities:000 -> 001."""' in text


def test_scaffold_upgrade_templates_for_seed_is_idempotent(tmp_path: Path) -> None:
    definitions_types = tmp_path / "definitions" / "types"
    _write_minimal_schema(
        definitions_types / "scada.control.capabilities" / "000.yaml",
        "scada.control.capabilities",
        "000",
    )
    _write_minimal_schema(
        definitions_types / "scada.control.capabilities" / "001.yaml",
        "scada.control.capabilities",
        "001",
    )
    seed = {
        "worklist": {
            "types": {
                "scada.control.capabilities": {
                    "000": {"path": "definitions/types/scada.control.capabilities/000.yaml"},
                    "001": {"path": "definitions/types/scada.control.capabilities/001.yaml"},
                }
            }
        }
    }
    template_dir = tmp_path / "templates" / "upgrades"
    expected = template_dir / "scada_control_capabilities_000_to_001.py.jinja2"

    first_run = scaffold_upgrade_templates_for_seed(
        seed,
        definitions_types_dir=definitions_types,
        upgrade_template_dir=template_dir,
    )
    second_run = scaffold_upgrade_templates_for_seed(
        seed,
        definitions_types_dir=definitions_types,
        upgrade_template_dir=template_dir,
    )
    assert first_run == [expected]
    assert second_run == [expected]


def test_scaffold_upgrade_templates_skips_single_version_types(tmp_path: Path) -> None:
    """A type with only one selected version has no upgrade chain — skip it."""
    definitions_types = tmp_path / "definitions" / "types"
    _write_minimal_schema(
        definitions_types / "lonely.type" / "000.yaml", "lonely.type", "000"
    )
    seed = {
        "worklist": {
            "types": {
                "lonely.type": {
                    "000": {"path": "definitions/types/lonely.type/000.yaml"}
                }
            }
        }
    }
    template_dir = tmp_path / "templates" / "upgrades"
    paths = scaffold_upgrade_templates_for_seed(
        seed,
        definitions_types_dir=definitions_types,
        upgrade_template_dir=template_dir,
    )
    assert paths == []
    assert list(template_dir.glob("*.py.jinja2")) == []


def test_render_upgrade_method_errors_when_template_missing() -> None:
    """Codegen MUST refuse to fall back to a hand-emitted stub. The
    upgrade-template scaffolder is the only producer of ``upgrade()`` bodies.
    """
    node = ("type", "example.type", "000")
    next_node = ("type", "example.type", "001")
    dag = SimpleNamespace(upgrades={node: next_node})
    dag_max = {("type", "example.type"): "001"}
    registry = {"types": {"example.type": {"versions": {"000": {}, "001": {}}}}, "enums": {}}

    ctx = SimpleNamespace(
        import_root="sema.runtime",
        dag_max=dag_max,
        local_names=None,
        imports=set(),
    )

    with pytest.raises(
        ValueError,
        match=r"example\.type:000 requires an upgrade to 001 but is missing upgrade template",
    ):
        _render_upgrade_method(node, dag, dag_max, registry, ctx)
