from pathlib import Path

from sema.interfaces.cli import snapshot


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

    # layout.lite include_all_versions pulls staging versions (013+), so this
    # is a dev snapshot; the lint guard's coverage is what matters here.
    snapshot.prepare_snapshot(
        ROOT / "tests" / "fixtures" / "strict_lint_seed.yaml", allow_staged=True
    )
    # strict_lint=True turns any ruff/mypy violation into a LintGateError; no
    # assertion is needed, the call raises on a dirty generated tree.
    snapshot.build_snapshot_runtime("gjk", strict_lint=True)
