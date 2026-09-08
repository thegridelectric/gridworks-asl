import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.new_command_tree import NewCommandTree


def test_new_command_tree_latest_version_is_003() -> None:
    assert NewCommandTree.version_value() == "003"


def test_real_maple_v000_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v000" / "real_maple.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, NewCommandTree)
    assert decoded.type_name == "new.command.tree"
    assert decoded.version == "003"
    # the 000->003 upgrade lifted every ShNode to spaceheat.node.gt/303
    assert all(node.version == "303" for node in decoded.sh_nodes)
