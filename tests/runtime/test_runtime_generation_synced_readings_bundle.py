from pathlib import Path

import yaml

from sema.tools.build_seed_expanded import expand_seed
from sema.tools.build_seed_definitions import load_registry
from sema.tools.runtime_generation.generate_runtime import generate_runtime_from_dag


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def test_synced_readings_bundle_002_uses_channel_readings_list_item(
    tmp_path: Path,
) -> None:
    seed_request = tmp_path / "seed_request.yaml"
    expanded_seed = tmp_path / "seed_expanded.yaml"
    seed_request.write_text(
        "initial_targets:\n"
        "  types:\n"
        "    synced.readings.bundle:\n"
        "      versions: [\"001\", \"002\"]\n"
    )
    expand_seed(seed_request, expanded_seed)

    target_root = tmp_path / "gjk" / "sema"
    generate_runtime_from_dag(
        target_root,
        load_yaml(expanded_seed),
        load_registry(),
        import_root="gjk.sema",
    )

    item_text = (target_root / "types" / "channel_readings_list_item.py").read_text()
    bundle_text = (target_root / "types" / "synced_readings_bundle.py").read_text()
    old_bundle_text = (
        target_root / "types" / "old_versions" / "synced_readings_bundle_001.py"
    ).read_text()

    assert "class ChannelReadingsListItem(SemaType):" in item_text
    assert "value_list: list[StrictInt | None]" in item_text
    assert (
        "from gjk.sema.types.channel_readings_list_item import "
        "ChannelReadingsListItem"
    ) in bundle_text
    assert "channel_readings_list: list[ChannelReadingsListItem]" in bundle_text
    assert "def check_axiom_5(self) -> Self:" in bundle_text
    assert "def upgrade(self) -> SyncedReadingsBundle:" in old_bundle_text
    assert '"channel.readings.list.item"' in old_bundle_text
