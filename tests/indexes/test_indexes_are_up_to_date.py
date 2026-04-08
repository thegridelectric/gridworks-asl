from __future__ import annotations

from pathlib import Path

from sema.tools import (
    build_dependency_closure,
    build_lookup,
    build_reverse_dependencies,
    build_versions,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEXES_DIR = REPO_ROOT / "indexes"


def _generated_text(module, tmp_path: Path, filename: str) -> str:
    original_output_path = module.OUTPUT_PATH
    try:
        module.OUTPUT_PATH = tmp_path / filename
        module.build()
        return module.OUTPUT_PATH.read_text()
    finally:
        module.OUTPUT_PATH = original_output_path


def _committed_text(filename: str) -> str:
    return (INDEXES_DIR / filename).read_text()


def test_dependency_closure_is_up_to_date(tmp_path: Path) -> None:
    generated = _generated_text(
        build_dependency_closure, tmp_path, "dependency_closure.yaml"
    )
    committed = _committed_text("dependency_closure.yaml")

    assert generated == committed, (
        "Indexes are out of date.\n"
        "Run: uv run sema build-indexes"
    )


def test_lookup_is_up_to_date(tmp_path: Path) -> None:
    generated = _generated_text(build_lookup, tmp_path, "lookup.yaml")
    committed = _committed_text("lookup.yaml")

    assert generated == committed, (
        "Indexes are out of date.\n"
        "Run: uv run sema build-indexes"
    )


def test_reverse_dependencies_are_up_to_date(tmp_path: Path) -> None:
    generated = _generated_text(
        build_reverse_dependencies, tmp_path, "reverse_dependencies.yaml"
    )
    committed = _committed_text("reverse_dependencies.yaml")

    assert generated == committed, (
        "Indexes are out of date.\n"
        "Run: uv run sema build-indexes"
    )


def test_versions_are_up_to_date(tmp_path: Path) -> None:
    generated = _generated_text(build_versions, tmp_path, "versions.yaml")
    committed = _committed_text("versions.yaml")

    assert generated == committed, (
        "Indexes are out of date.\n"
        "Run: uv run sema build-indexes"
    )
