"""gw.weather.forecast.bundle.gt axiom counterexamples — sema must reject
what violates an axiom.

Each fixture is an otherwise-valid payload with the fewest axiom-relevant
fields mutated (embedded channels stay valid against their own axioms, and
axioms other than the one under test stay satisfied, so exactly the right
axiom fires).
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def _rejects(fixture: str, axiom: str) -> None:
    payload = json.loads((FIX / fixture).read_text())
    with pytest.raises(SemaError, match=f"(?i)axiom {axiom}"):
        default_codec.from_dict(payload)


def test_axiom_1_catches_mismatched_slice_grids() -> None:
    _rejects("axiom_1.json", "1")


def test_axiom_2_catches_mismatched_emission_schedule() -> None:
    _rejects("axiom_2.json", "2")


def test_axiom_3_catches_identical_forecast_channel_names() -> None:
    _rejects("axiom_3.json", "3")


def test_axiom_4_catches_unbound_target() -> None:
    _rejects("axiom_4.json", "4")


def test_axiom_5_catches_wrong_quantity_target() -> None:
    _rejects("axiom_5.json", "5")


def test_axiom_6_catches_target_outside_location() -> None:
    _rejects("axiom_6.json", "6")


def test_axiom_7_catches_name_not_extending_location() -> None:
    _rejects("axiom_7.json", "7")
