import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec
from sema.runtime.types.gw_readings import GwReadings


def test_gw_readings_latest_version_is_000() -> None:
    assert GwReadings.version_value() == "000"


def test_default_v000_loads_as_gw_readings() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v000" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, GwReadings)
    assert decoded.type_name == "gw.readings"
    assert decoded.version == "000"
    assert decoded.channels[0].name == "vdc-relay"
    assert decoded.channel_readings_list[0].channel_name == "vdc-relay"


def test_axiom_1_catches_window_order() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v000" / "axiom_1.json"
    payload = json.loads(fixture.read_text())

    with pytest.raises(SemaError, match="Axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_readings_without_matching_channel() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v000" / "axiom_2.json"
    payload = json.loads(fixture.read_text())

    with pytest.raises(SemaError, match="Axiom 2"):
        default_codec.from_dict(payload)
