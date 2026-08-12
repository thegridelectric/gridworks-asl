from pathlib import Path

import pytest

from sema.interfaces.cli import snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_prepare_rejects_staging_by_default(
    monkeypatch, tmp_path: Path
) -> None:
    # The template seed pulls layout.lite:013, which is staging — so the
    # published-only default must fail and name the staging offenders.
    monkeypatch.setattr(snapshot, "OUTPUT_DIR", tmp_path / "output")
    with pytest.raises(ValueError, match="STAGING") as excinfo:
        snapshot.prepare_snapshot(ROOT / "template_seed_request.yaml")
    assert "layout.lite:013" in str(excinfo.value)


def test_refused_prepare_leaves_previous_output_intact(
    monkeypatch, tmp_path: Path
) -> None:
    # A refusal must fire BEFORE output/ is cleared: a cleared-then-refused
    # output/ silently guts whatever a consumer mirrors next (rsync --delete).
    output_root = tmp_path / "output"
    monkeypatch.setattr(snapshot, "OUTPUT_DIR", output_root)
    target_root = snapshot.prepare_snapshot(
        ROOT / "template_seed_request.yaml", allow_staged=True
    )
    before = sorted(p.relative_to(target_root) for p in target_root.rglob("*"))
    assert before

    with pytest.raises(ValueError, match="STAGING"):
        snapshot.prepare_snapshot(ROOT / "template_seed_request.yaml")

    after = sorted(p.relative_to(target_root) for p in target_root.rglob("*"))
    assert after == before


def test_snapshot_prepare_and_build_write_sema_at_output_root(
    monkeypatch, tmp_path: Path
) -> None:
    output_root = tmp_path / "output"
    monkeypatch.setattr(snapshot, "OUTPUT_DIR", output_root)

    target_root = snapshot.prepare_snapshot(
        ROOT / "template_seed_request.yaml", allow_staged=True
    )

    assert target_root == output_root / "sema"
    assert not (output_root / "gjk").exists()
    assert not (output_root / "seed_expanded.yaml").exists()
    assert (target_root / "indexes" / "seed_expanded.yaml").exists()
    assert (target_root / "indexes" / "local_names.yaml").exists()
    assert not (target_root / "base.py").exists()
    # staging closure + --allow-staged => the dev-only markers, both machine
    # (indexes/staging.yaml) and human (README banner)
    assert (target_root / "indexes" / "staging.yaml").exists()
    readme = (target_root / "README.md").read_text()
    assert "PLEASE ONLY USE IN DEV" in readme
    assert "layout.lite:013" in readme

    stale_file = output_root / "stale.txt"
    stale_file.write_text("remove me")
    local_names = target_root / "indexes" / "local_names.yaml"
    local_names.write_text(
        local_names.read_text().replace(
            "layout.lite: layout.lite", "layout.lite: lite.layout"
        )
    )

    assert (
        snapshot.prepare_snapshot(
            ROOT / "template_seed_request.yaml", allow_staged=True
        )
        == target_root
    )
    assert not stale_file.exists()
    assert "lite.layout" not in local_names.read_text()
    local_names.write_text(
        local_names.read_text()
        .replace("layout.lite: layout.lite", "layout.lite: lite.layout")
        .replace(
            "gw1.emission.method: gw1.emission.method",
            "gw1.emission.method: emission.method",
        )
        .replace(
            "gw1.seasonal.storage.mode: gw1.seasonal.storage.mode",
            "gw1.seasonal.storage.mode: seasonal.storage.mode",
        )
    )

    assert snapshot.build_snapshot_runtime("gjk") == target_root
    assert (target_root / "base.py").exists()
    assert (target_root / "codec.py").exists()
    assert (target_root / "property_format.py").exists()
    assert (target_root / "definitions" / "registry.yaml").exists()
    assert (target_root / "indexes" / "dependency_closure.yaml").exists()
    assert (target_root / "indexes" / "lookup.yaml").exists()
    assert (target_root / "indexes" / "reverse_dependencies.yaml").exists()
    assert (target_root / "indexes" / "versions.yaml").exists()
    # Snapshots ship data, not test code: no vendored tests/ directory.
    assert not (target_root / "tests").exists()
    # Round-trip harness + generated samples ship instead.
    assert (target_root / "roundtrip.py").exists()
    assert (target_root / "samples" / "README.md").exists()
    sample_files = list((target_root / "samples").glob("*.json"))
    assert sample_files, "expected at least one generated sample"
    assert any("channel.readings.list.item" in p.name for p in sample_files)
    assert "from gjk.sema.base import" in (target_root / "codec.py").read_text()
    assert (target_root / "enums" / "emission_method.py").exists()
    assert not (target_root / "enums" / "gw1_emission_method.py").exists()
    enum_init = (target_root / "enums" / "__init__.py").read_text()
    lite_layout = (target_root / "types" / "lite_layout.py").read_text()
    assert "class LiteLayout" in lite_layout
    assert "from gjk.sema.logic" not in lite_layout
    assert "def check_axiom_1" in lite_layout
    assert (
        "from gjk.sema.enums.seasonal_storage_mode import SeasonalStorageMode"
        in enum_init
    )
    assert "from gjk.sema.enums import SeasonalStorageMode" in lite_layout

    assert snapshot.build_snapshot_runtime("gjk") == target_root
    assert "def check_axiom_1" in (target_root / "types" / "lite_layout.py").read_text()
    assert (
        "def upgrade"
        in (target_root / "types" / "old_versions" / "lite_layout_011.py").read_text()
    )
