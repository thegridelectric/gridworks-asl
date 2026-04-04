import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)


def test_i2c_multichannel_dt_relay_component_gt_latest_version_is_004() -> None:
    assert I2cMultichannelDtRelayComponentGt.version_value() == "004"


def test_default_v002_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, I2cMultichannelDtRelayComponentGt)
    assert decoded.type_name == "i2c.multichannel.dt.relay.component.gt"
    assert decoded.version == "004"


def test_default_v003_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v003" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, I2cMultichannelDtRelayComponentGt)
    assert decoded.type_name == "i2c.multichannel.dt.relay.component.gt"
    assert decoded.version == "004"
