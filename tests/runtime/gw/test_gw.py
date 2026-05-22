import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.gw import Gw


def test_gw_is_versionless() -> None:
    assert Gw.version_value() is None


def test_scada_glitch_fixture_decodes() -> None:
    fixture = Path(__file__).parent / "fixtures" / "scada_glitch.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, Gw)
    assert decoded.type_name == "gw"
    assert decoded.header.type_name == "gridworks.header"
    assert decoded.header.version == "001"
    assert decoded.payload.type_name == "glitch"

