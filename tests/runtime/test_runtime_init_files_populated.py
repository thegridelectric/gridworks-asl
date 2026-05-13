"""
Regression guard: the parent ``__init__.py`` files for sema/runtime/types/
and sema/runtime/enums/ MUST be populated by the runtime generator with
eager imports + ``__all__``. The codec relies on these eager imports.

The companion ``old_versions/__init__.py`` files are intentionally written
empty by the generator. Eager imports there would deadlock — old-version
modules reference latest classes for their upgrade-target annotations, and
latest modules in turn import old versions for old-version-typed fields.
The codec discovers old versions via filesystem glob, so an empty init is
sufficient and is the safer choice.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "src" / "sema" / "runtime"

PARENT_INITS = [
    RUNTIME_ROOT / "types" / "__init__.py",
    RUNTIME_ROOT / "enums" / "__init__.py",
]


def test_runtime_parent_init_files_populated() -> None:
    failures: list[str] = []
    for path in PARENT_INITS:
        text = path.read_text() if path.exists() else ""
        if "import" not in text or "__all__ = [" not in text:
            failures.append(f"{path} (expected imports + __all__)")
    assert not failures, (
        "Runtime parent __init__.py files are not populated:\n  "
        + "\n  ".join(failures)
    )
