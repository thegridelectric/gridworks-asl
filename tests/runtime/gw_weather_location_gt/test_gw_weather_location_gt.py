"""gw.weather.location.gt axiom counterexamples — sema must reject what violates an axiom.

Each fixture is an otherwise-valid payload with one axiom-relevant field mutated
to a violating value. Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_a_catches_latitude_out_of_bounds() -> None:
    payload = json.loads((FIX / "axiom_1_a.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_1_b_catches_longitude_out_of_bounds() -> None:
    payload = json.loads((FIX / "axiom_1_b.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 1"):
        default_codec.from_dict(payload)
