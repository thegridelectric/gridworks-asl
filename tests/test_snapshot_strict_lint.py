from pathlib import Path

from sema.interfaces.cli import snapshot
from sema.tools.build_public_registry import build_public_registry, load_registry


ROOT = Path(__file__).resolve().parents[1]


def test_strict_lint_build_is_clean(monkeypatch, tmp_path: Path) -> None:
    """The generated snapshot runtime must pass ruff + mypy under the strict
    lint gate, for the full production seed.

    Regression guard for the gjk-snapshot lint failures: the scada.params
    004->005 nested-upgrade loop (untyped loop var), the legacy GwStrEnum index
    API (mypy-invisible dynamic attrs + a `_missing_` LSP override), and the
    unused ``Any`` import on typed-map types. Verified against the committed
    fixtures/strict_lint_seed.yaml production seed: before those generator fixes
    a strict build raised LintGateError with 7 errors. A non-strict build (the
    default) only *prints* violations, so this strict gate is what actually
    fails on a dirty generator.
    """
    output_root = tmp_path / "output"
    monkeypatch.setattr(snapshot, "OUTPUT_DIR", output_root)
    monkeypatch.setattr(
        snapshot,
        "build_public_registry_index",
        lambda: build_public_registry(load_registry()),
    )

    snapshot.prepare_snapshot(ROOT / "tests" / "fixtures" / "strict_lint_seed.yaml")
    # strict_lint=True turns any ruff/mypy violation into a LintGateError; no
    # assertion is needed, the call raises on a dirty generated tree.
    snapshot.build_snapshot_runtime("gjk", strict_lint=True)
