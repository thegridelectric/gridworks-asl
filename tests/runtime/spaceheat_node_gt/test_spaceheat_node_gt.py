import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.enums.gw1_actor_class import Gw1ActorClass
from sema.runtime.enums.old_versions.gw1_actor_class_009 import Gw1ActorClass009
from sema.runtime.types.old_versions.spaceheat_node_gt_300 import SpaceheatNodeGt300
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt


def test_spaceheat_node_gt_latest_version_is_302() -> None:
    assert SpaceheatNodeGt.version_value() == "302"


def test_default_v300_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v300" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, SpaceheatNodeGt)
    assert decoded.type_name == "spaceheat.node.gt"
    assert decoded.version == "302"


def test_default_v301_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v301" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, SpaceheatNodeGt)
    assert decoded.type_name == "spaceheat.node.gt"
    assert decoded.version == "302"


def test_default_v302_loads_as_spaceheat_node_gt() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v302" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, SpaceheatNodeGt)
    assert decoded.type_name == "spaceheat.node.gt"
    assert decoded.version == "302"
