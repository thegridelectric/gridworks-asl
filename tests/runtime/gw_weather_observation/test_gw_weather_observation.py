"""gw.weather.observation axiom counterexamples — sema must reject what violates an axiom.

Each fixture is an otherwise-valid payload with one axiom-relevant field mutated
to a violating value. Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_identical_channel_names() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_2_a_catches_temp_channel_outside_location() -> None:
    payload = json.loads((FIX / "axiom_2_a.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 2"):
        default_codec.from_dict(payload)


def test_axiom_2_b_catches_windspeed_channel_outside_location() -> None:
    payload = json.loads((FIX / "axiom_2_b.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 2"):
        default_codec.from_dict(payload)
