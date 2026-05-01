from pathlib import Path

from sema.interfaces.cli import snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_prepare_and_build_write_sema_at_output_root(monkeypatch, tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    monkeypatch.setattr(snapshot, "OUTPUT_DIR", output_root)

    target_root = snapshot.prepare_snapshot(ROOT / "template_seed_request.yaml")

    assert target_root == output_root / "sema"
    assert not (output_root / "gjk").exists()
    assert not (output_root / "seed_expanded.yaml").exists()
    assert (target_root / "indexes" / "seed_expanded.yaml").exists()
    assert (target_root / "indexes" / "local_names.yaml").exists()
    assert not (target_root / "base.py").exists()

    stale_file = output_root / "stale.txt"
    stale_file.write_text("remove me")
    local_names = target_root / "indexes" / "local_names.yaml"
    local_names.write_text(local_names.read_text().replace("LayoutLite", "LiteLayout"))

    assert snapshot.prepare_snapshot(ROOT / "template_seed_request.yaml") == target_root
    assert not stale_file.exists()
    assert "LiteLayout" not in local_names.read_text()
    local_names.write_text(
        local_names.read_text()
        .replace("LayoutLite", "LiteLayout")
        .replace("Gw1EmissionMethod", "EmissionMethod")
        .replace("Gw1SeasonalStorageMode", "SeasonalStorageMode")
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
    assert (target_root / "tests" / "test_property_format.py").exists()
    assert (target_root / "logic" / "axioms" / "lite_layout.py").exists()
    assert (target_root / "logic" / "upgrades" / "lite_layout_011_to_012.py").exists()
    assert "from gjk.sema.base import" in (target_root / "codec.py").read_text()
    assert (target_root / "enums" / "emission_method.py").exists()
    assert not (target_root / "enums" / "gw1_emission_method.py").exists()
    lite_layout = (target_root / "types" / "lite_layout.py").read_text()
    assert "class LiteLayout" in lite_layout
    assert "from gjk.sema.logic.axioms.lite_layout import check_axiom_1 as _check_axiom_1" in lite_layout
    assert "from gjk.sema.enums.seasonal_storage_mode import SeasonalStorageMode" in lite_layout

    axiom_logic = target_root / "logic" / "axioms" / "lite_layout.py"
    upgrade_logic = target_root / "logic" / "upgrades" / "lite_layout_011_to_012.py"
    axiom_logic.write_text("# stale axiom implementation\n")
    upgrade_logic.write_text("# stale upgrade implementation\n")

    assert snapshot.build_snapshot_runtime("gjk") == target_root
    assert "stale axiom" not in axiom_logic.read_text()
    assert "stale upgrade" not in upgrade_logic.read_text()
    assert "def check_axiom_1" in axiom_logic.read_text()
    assert "def upgrade" in upgrade_logic.read_text()
