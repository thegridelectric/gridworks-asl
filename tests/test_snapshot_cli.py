from pathlib import Path

from sema.interfaces.cli import snapshot
from sema.tools.build_public_registry import build_public_registry, load_registry


ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_prepare_and_build_write_sema_at_output_root(monkeypatch, tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    monkeypatch.setattr(snapshot, "OUTPUT_DIR", output_root)
    monkeypatch.setattr(
        snapshot,
        "build_public_registry_index",
        lambda: build_public_registry(load_registry()),
    )

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
    local_names.write_text(
        local_names.read_text().replace("layout.lite: layout.lite", "layout.lite: lite.layout")
    )

    assert snapshot.prepare_snapshot(ROOT / "template_seed_request.yaml") == target_root
    assert not stale_file.exists()
    assert "lite.layout" not in local_names.read_text()
    local_names.write_text(
        local_names.read_text()
        .replace("layout.lite: layout.lite", "layout.lite: lite.layout")
        .replace("gw1.emission.method: gw1.emission.method", "gw1.emission.method: emission.method")
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
    assert (target_root / "tests" / "test_property_format.py").exists()
    assert "from gjk.sema.base import" in (target_root / "codec.py").read_text()
    assert (target_root / "enums" / "emission_method.py").exists()
    assert not (target_root / "enums" / "gw1_emission_method.py").exists()
    enum_init = (target_root / "enums" / "__init__.py").read_text()
    lite_layout = (target_root / "types" / "lite_layout.py").read_text()
    assert "class LiteLayout" in lite_layout
    assert "from gjk.sema.logic" not in lite_layout
    assert "def check_axiom_1" in lite_layout
    assert "from gjk.sema.enums.seasonal_storage_mode import SeasonalStorageMode" in enum_init
    assert "from gjk.sema.enums import SeasonalStorageMode" in lite_layout

    assert snapshot.build_snapshot_runtime("gjk") == target_root
    assert "def check_axiom_1" in (target_root / "types" / "lite_layout.py").read_text()
    assert "def upgrade" in (target_root / "types" / "old_versions" / "lite_layout_011.py").read_text()
