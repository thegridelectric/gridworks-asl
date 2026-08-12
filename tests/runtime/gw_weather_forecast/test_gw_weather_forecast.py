"""gw.weather.forecast axiom counterexamples — sema must reject what violates an axiom.

Each fixture is an otherwise-valid payload with one axiom-relevant field mutated
to a violating value. Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_empty_value_lists() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_unequal_value_lengths() -> None:
    payload = json.loads((FIX / "axiom_2.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 2"):
        default_codec.from_dict(payload)


def test_axiom_3_catches_identical_channel_names() -> None:
    payload = json.loads((FIX / "axiom_3.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 3"):
        default_codec.from_dict(payload)


def test_axiom_4_a_catches_bundle_name_without_forecast_segment() -> None:
    payload = json.loads((FIX / "axiom_4_a.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 4"):
        default_codec.from_dict(payload)


def test_axiom_4_b_catches_temp_channel_without_forecast_segment() -> None:
    payload = json.loads((FIX / "axiom_4_b.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 4"):
        default_codec.from_dict(payload)


def test_axiom_4_c_catches_windspeed_channel_without_forecast_segment() -> None:
    payload = json.loads((FIX / "axiom_4_c.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 4"):
        default_codec.from_dict(payload)
