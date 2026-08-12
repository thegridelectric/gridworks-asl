"""gw.weather.forecast.channel.gt axiom counterexamples — sema must reject what violates an axiom.

Each fixture is an otherwise-valid payload with one axiom-relevant field mutated
to a violating value, chosen so no earlier axiom fires first (e.g. the Axiom 3
fixture keeps the slice sum consistent so only the quantum check trips).
Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_slice_count_mismatch() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_duration_inconsistency() -> None:
    payload = json.loads((FIX / "axiom_2.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 2"):
        default_codec.from_dict(payload)


def test_axiom_3_catches_slice_not_multiple_of_quantum() -> None:
    payload = json.loads((FIX / "axiom_3.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 3"):
        default_codec.from_dict(payload)


def test_axiom_4_catches_name_without_forecast_infix() -> None:
    payload = json.loads((FIX / "axiom_4.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 4"):
        default_codec.from_dict(payload)
