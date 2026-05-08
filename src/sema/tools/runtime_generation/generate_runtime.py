from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, StrictUndefined

from sema.tools.build_seed_dag import build_seed_dag_from_data
from sema.tools.runtime_generation.enums import generate_enums
from sema.tools.runtime_generation.formats import generate_formats
from sema.tools.runtime_generation.helpers import load_local_names_yaml
from sema.tools.runtime_generation.types import generate_types


TEMPLATE_ROOT = Path(__file__).parent / "templates"


def _ensure_package_layout(target_root) -> None:
    (target_root / "enums" / "old_versions").mkdir(parents=True, exist_ok=True)
    (target_root / "types" / "old_versions").mkdir(parents=True, exist_ok=True)


def _render_template(template_name: str, **context) -> str:
    template_text = (TEMPLATE_ROOT / template_name).read_text()
    env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    return env.from_string(template_text).render(**context)


def _write_package_init(target_root, import_root: str) -> None:
    (target_root / "__init__.py").write_text(
        _render_template("__init__.py.jinja2", import_root=import_root)
    )


def _write_base(target_root) -> None:
    (target_root / "base.py").write_text(_render_template("base.py.jinja2"))


def _write_codec(target_root, import_root: str) -> None:
    (target_root / "codec.py").write_text(
        _render_template("codec.py.jinja2", import_root=import_root)
    )


def generate_runtime_from_dag(
    target_root,
    seed,
    registry,
    import_root: str,
    local_names=None,
    write_tests: bool = False,
):
    """Generate a sema runtime package.

    target_root: filesystem directory where the package is laid out (e.g.
        ``src/sema/runtime`` for the runtime itself, or ``<pkg>/sema`` for a
        snapshot).
    import_root: dotted Python path where the generated package will live
        (e.g. ``"sema.runtime"`` for the runtime, ``"gjk.sema"`` for a
        snapshot).
    """
    dag = build_seed_dag_from_data(seed, registry)
    dag_max = dag.dag_max()
    if isinstance(local_names, str | Path):
        local_names = load_local_names_yaml(Path(local_names))

    _ensure_package_layout(target_root)
    _write_package_init(target_root, import_root)
    _write_base(target_root)

    generate_formats(target_root, dag, seed, import_root, write_tests=write_tests)
    generate_enums(
        target_root,
        dag,
        dag_max,
        seed,
        import_root,
        local_names,
    )
    _write_codec(target_root, import_root)
    generate_types(
        target_root,
        dag,
        dag_max,
        seed,
        registry,
        import_root,
        local_names,
    )
