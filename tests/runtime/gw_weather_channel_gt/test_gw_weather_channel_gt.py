"""gw.weather.channel.gt axiom counterexamples — sema must reject what violates an axiom.

Each fixture is an otherwise-valid payload with one axiom-relevant field mutated
to a violating value. Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_name_not_derived_from_alias_and_quantity() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_offset_not_below_period() -> None:
    payload = json.loads((FIX / "axiom_2.json").read_text())
    with pytest.raises(SemaError, match="(?i)axiom 2"):
        default_codec.from_dict(payload)
