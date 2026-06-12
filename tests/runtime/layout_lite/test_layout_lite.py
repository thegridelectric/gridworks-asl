import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.layout_lite import LayoutLite


def test_layout_lite_latest_version_is_014() -> None:
    assert LayoutLite.version_value() == "014"


def test_real_beech_v011_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v011" / "real_beech.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, LayoutLite)
    assert decoded.type_name == "layout.lite"
    assert decoded.version == "014"


def test_real_spruce_v012_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v012" / "real_spruce.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, LayoutLite)
    assert decoded.type_name == "layout.lite"
    assert decoded.version == "014"
