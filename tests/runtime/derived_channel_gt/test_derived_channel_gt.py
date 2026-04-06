import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec
from sema.runtime.types.derived_channel_gt import DerivedChannelGt


def test_derived_channel_gt_latest_version_is_002() -> None:
    assert DerivedChannelGt.version_value() == "002"


def test_default_v000_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v000" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, DerivedChannelGt)
    assert decoded.type_name == "derived.channel.gt"
    assert decoded.version == "002"


def test_default_v001_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v001" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, DerivedChannelGt)
    assert decoded.type_name == "derived.channel.gt"
    assert decoded.version == "002"


def test_default_v002_loads_as_derived_channel_gt() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, DerivedChannelGt)
    assert decoded.type_name == "derived.channel.gt"
    assert decoded.version == "002"


def test_axiom_2_catches_output_unit_quantity_mismatch() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "axiom_2.json"
    payload = json.loads(fixture.read_text())

    with pytest.raises(SemaError, match="Axiom 2 failed"):
        default_codec.from_dict(payload)


def test_axiom_1_catches_missing_emit_period_for_periodic() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "axiom_1.json"
    payload = json.loads(fixture.read_text())

    with pytest.raises(SemaError, match="Axiom 1 failed"):
        default_codec.from_dict(payload)


def test_axiom_3_catches_missing_affine_calibration() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "axiom_3.json"
    payload = json.loads(fixture.read_text())

    with pytest.raises(SemaError, match="Axiom 3 failed"):
        default_codec.from_dict(payload)


def test_axiom_4_catches_missing_system_model_energy_model() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "axiom_4.json"
    payload = json.loads(fixture.read_text())

    with pytest.raises(SemaError, match="Axiom 4 failed"):
        default_codec.from_dict(payload)
