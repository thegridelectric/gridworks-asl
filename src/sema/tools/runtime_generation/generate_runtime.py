from __future__ import annotations

from sema.tools.build_seed_dag import build_seed_dag_from_data
from sema.tools.runtime_generation.enums import generate_enums
from sema.tools.runtime_generation.formats import generate_formats
from sema.tools.runtime_generation.types import generate_types


RUNTIME_INIT = '''"""
Generated snapshot runtime package.
"""
'''


def _ensure_package_layout(target_root) -> None:
    (target_root / "enums" / "old_versions").mkdir(parents=True, exist_ok=True)
    (target_root / "types" / "old_versions").mkdir(parents=True, exist_ok=True)
    (target_root / "__init__.py").write_text(RUNTIME_INIT)


def generate_runtime_from_dag(
    target_root,
    seed,
    registry,
    definitions_root=None,
    package_name="gjk",
):
    dag = build_seed_dag_from_data(seed, registry)
    latest = dag.latest_in_dag()

    _ensure_package_layout(target_root)

    generate_formats(target_root, dag, seed, definitions_root)
    generate_enums(target_root, dag, latest, seed, definitions_root, package_name)
    generate_types(target_root, dag, latest, seed, registry, definitions_root, package_name)
