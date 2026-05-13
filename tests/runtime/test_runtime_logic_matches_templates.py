import ast
from pathlib import Path
import tempfile

import pytest
import yaml

from sema.tools.runtime_generation.generate_runtime import generate_runtime_from_dag
from sema.tools.seed_requests import expand_all_registry_seed


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "indexes" / "public_registry.yaml"
RUNTIME_TYPES_ROOT = ROOT / "src" / "sema" / "runtime" / "types"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def compact_python(source: str) -> str:
    return "".join(source.split())


def logic_methods(path: Path) -> dict[str, str]:
    text = path.read_text()
    module = ast.parse(text, filename=str(path))
    methods: dict[str, str] = {}
    for node in ast.walk(module):
        if not isinstance(node, ast.ClassDef):
            continue
        for child in node.body:
            if not isinstance(child, ast.FunctionDef):
                continue
            if child.name == "upgrade" or child.name.startswith("check_axiom"):
                segment = ast.get_source_segment(text, child)
                if segment is None:
                    raise AssertionError(f"Could not extract {child.name} from {path}")
                methods[child.name] = compact_python(segment)
    return methods


def generated_runtime_from_registry(tmp_path: Path) -> Path:
    registry = load_yaml(REGISTRY_PATH)
    generated_root = tmp_path / "runtime"
    generate_runtime_from_dag(
        generated_root,
        expand_all_registry_seed(tmp_path, registry),
        registry,
        import_root="sema.runtime",
    )
    return generated_root


@pytest.mark.xfail(
    reason=(
        "The checked-in runtime logic has not yet been regenerated from the "
        "Jinja axiom/upgrade templates."
    )
)
def test_runtime_axioms_and_upgrades_match_generated_templates() -> None:
    with tempfile.TemporaryDirectory() as tmp_name:
        generated_root = generated_runtime_from_registry(Path(tmp_name))

        findings: list[str] = []
        for generated_path in sorted((generated_root / "types").rglob("*.py")):
            generated_methods = logic_methods(generated_path)
            if not generated_methods:
                continue

            rel_path = generated_path.relative_to(generated_root / "types")
            runtime_path = RUNTIME_TYPES_ROOT / rel_path
            if not runtime_path.exists():
                findings.append(
                    f"{rel_path}: missing runtime file with generated logic methods "
                    f"{sorted(generated_methods)}"
                )
                continue

            runtime_methods = logic_methods(runtime_path)
            for method_name, generated_source in generated_methods.items():
                runtime_source = runtime_methods.get(method_name)
                if runtime_source is None:
                    findings.append(f"{rel_path}: missing {method_name}")
                elif runtime_source != generated_source:
                    findings.append(f"{rel_path}: {method_name} differs")

        assert not findings, "\n" + "\n".join(findings)
