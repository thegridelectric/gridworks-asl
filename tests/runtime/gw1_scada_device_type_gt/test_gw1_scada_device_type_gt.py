"""gw1.scada.device.type.gt axiom counterexamples — sema must reject what violates an axiom.

Each fixture is an otherwise-valid payload with one axiom-relevant field mutated to a
violating value (the payload a gwsproto producer would emit if its matching
check_axiom_n were removed). Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_bus_not_in_bus_list() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="BusMembership"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_expander_not_in_expanders() -> None:
    payload = json.loads((FIX / "axiom_2.json").read_text())
    with pytest.raises(SemaError, match="ExpanderMembership"):
        default_codec.from_dict(payload)


def test_axiom_4_a_catches_mux_not_in_muxes() -> None:
    payload = json.loads((FIX / "axiom_4_a.json").read_text())
    with pytest.raises(SemaError, match="MuxConsistency"):
        default_codec.from_dict(payload)


def test_axiom_4_b_catches_mux_channel_out_of_bounds() -> None:
    payload = json.loads((FIX / "axiom_4_b.json").read_text())
    with pytest.raises(SemaError, match="MuxConsistency"):
        default_codec.from_dict(payload)


def test_axiom_4_c_catches_dac_bus_mux_bus_mismatch() -> None:
    payload = json.loads((FIX / "axiom_4_c.json").read_text())
    with pytest.raises(SemaError, match="MuxConsistency"):
        default_codec.from_dict(payload)
