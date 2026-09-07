"""gw.command.interface axiom counterexamples — sema must reject what violates an axiom.

Each fixture is the word's own example with one axiom-relevant field mutated to a
violating value. Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_empty_commands() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="Axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_event_outside_event_type_vocabulary() -> None:
    payload = json.loads((FIX / "axiom_2.json").read_text())
    with pytest.raises(SemaError, match="Axiom 2"):
        default_codec.from_dict(payload)


def test_axiom_3_catches_state_outside_state_type_vocabulary() -> None:
    payload = json.loads((FIX / "axiom_3.json").read_text())
    with pytest.raises(SemaError, match="Axiom 3"):
        default_codec.from_dict(payload)
