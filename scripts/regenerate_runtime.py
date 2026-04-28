from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import yaml

from sema.tools.build_public_registry import build as build_public_registry
from sema.tools.runtime_generation.generate_runtime import generate_runtime_from_dag
from sema.tools.runtime_generation.scaffold_axiom_template import (
    scaffold_axiom_templates_for_seed,
)
from sema.tools.runtime_generation.scaffold_upgrade_template import (
    scaffold_upgrade_templates_for_seed,
)
from sema.tools.seed_requests import expand_all_registry_seed


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "indexes" / "public_registry.yaml"
RUNTIME_ROOT = REPO_ROOT / "src" / "sema" / "runtime"
RUNTIME_IMPORT_ROOT = "sema.runtime"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def _delete_runtime_generated_artifacts() -> None:
    for name in ("enums", "types", "tests"):
        path = RUNTIME_ROOT / name
        if path.exists():
            shutil.rmtree(path)


def main() -> None:
    build_public_registry()
    registry = _load_yaml(REGISTRY_PATH)
    with tempfile.TemporaryDirectory() as tmp_name:
        seed = expand_all_registry_seed(Path(tmp_name), registry)
    axiom_templates = scaffold_axiom_templates_for_seed(seed)
    if axiom_templates:
        print(f"Ensured {len(axiom_templates)} axiom templates")
    upgrade_templates = scaffold_upgrade_templates_for_seed(seed)
    if upgrade_templates:
        print(f"Ensured {len(upgrade_templates)} upgrade templates")

    _delete_runtime_generated_artifacts()
    generate_runtime_from_dag(
        RUNTIME_ROOT,
        seed,
        registry,
        import_root=RUNTIME_IMPORT_ROOT,
    )
    print(f"Regenerated runtime at {RUNTIME_ROOT}")


if __name__ == "__main__":
    main()
