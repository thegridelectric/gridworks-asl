import ast
import re
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
AXIOM_TEMPLATE_DIR = REPO_ROOT / "src" / "sema" / "tools" / "runtime_generation" / "templates" / "axioms"
DEFINITIONS_TYPES_DIR = REPO_ROOT / "definitions" / "types"
JINJA_VARIABLE_RE = re.compile(r"{{\s*[a-zA-Z_][a-zA-Z0-9_]*\s*}}")
AXIOM_METHOD_RE = re.compile(r"check_axiom_(\d+)$")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def normalize_words(text: str) -> str:
    return " ".join(text.split())


def type_name_and_version(template_path: Path) -> tuple[str, str]:
    stem = template_path.name.removesuffix(".py.jinja2")
    sema_name, version = stem.rsplit("_", 1)
    return sema_name.replace("_", "."), version


def template_ast(template_path: Path) -> ast.Module:
    source = template_path.read_text()
    source = JINJA_VARIABLE_RE.sub("TemplateSymbol", source)
    return ast.parse("class TemplateClass:\n" + source)


def axiom_methods(tree: ast.Module) -> dict[int, ast.FunctionDef]:
    class_def = tree.body[0]
    assert isinstance(class_def, ast.ClassDef)
    methods: dict[int, ast.FunctionDef] = {}
    for stmt in class_def.body:
        if not isinstance(stmt, ast.FunctionDef):
            continue
        match = AXIOM_METHOD_RE.fullmatch(stmt.name)
        if match:
            methods[int(match.group(1))] = stmt
    return methods


def expected_axiom_docstrings(sema_name: str, version: str) -> dict[int, str]:
    schema = load_yaml(DEFINITIONS_TYPES_DIR / sema_name / f"{version}.yaml")
    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    return {
        int(axiom["number"]): (
            f'Axiom {axiom["number"]}: {axiom["name"]} '
            f'{axiom.get("statement", axiom.get("description", ""))}'
        )
        for axiom in axioms
    }


def test_axiom_template_docstrings_match_definitions() -> None:
    for template_path in sorted(AXIOM_TEMPLATE_DIR.glob("*.py.jinja2")):
        sema_name, version = type_name_and_version(template_path)
        expected = expected_axiom_docstrings(sema_name, version)
        methods = axiom_methods(template_ast(template_path))

        assert set(methods) == set(expected), template_path
        for axiom_number, method in methods.items():
            docstring = ast.get_docstring(method)
            assert docstring is not None, f"{template_path}: check_axiom_{axiom_number}"
            assert normalize_words(docstring) == normalize_words(expected[axiom_number])
