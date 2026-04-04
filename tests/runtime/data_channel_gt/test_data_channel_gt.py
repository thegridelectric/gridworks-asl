import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.data_channel_gt import DataChannelGt


def test_data_channel_gt_latest_version_is_002() -> None:
    assert DataChannelGt.version_value() == "002"


def test_default_v001_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v001" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, DataChannelGt)
    assert decoded.type_name == "data.channel.gt"
    assert decoded.version == "002"


def test_default_v002_loads_as_data_channel_gt() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, DataChannelGt)
    assert decoded.type_name == "data.channel.gt"
    assert decoded.version == "002"
