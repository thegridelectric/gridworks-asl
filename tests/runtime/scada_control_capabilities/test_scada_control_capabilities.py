"""scada.control.capabilities axiom counterexamples — sema must reject what violates an axiom.

Each fixture is the word's own example with one axiom-relevant field mutated to a
violating value. Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v001"


def test_axiom_1_c_catches_relay_class_in_command_nodes() -> None:
    payload = json.loads((FIX / "axiom_1_c.json").read_text())
    with pytest.raises(SemaError, match="Axiom 1"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_command_node_handle_terminal_mismatch() -> None:
    payload = json.loads((FIX / "axiom_2.json").read_text())
    with pytest.raises(SemaError, match="Axiom 2"):
        default_codec.from_dict(payload)


def test_axiom_4_a_catches_directly_commanded_node_without_interface() -> None:
    payload = json.loads((FIX / "axiom_4_a.json").read_text())
    with pytest.raises(SemaError, match="Axiom 4"):
        default_codec.from_dict(payload)


def test_axiom_4_b_catches_duplicate_interface_actor_name() -> None:
    payload = json.loads((FIX / "axiom_4_b.json").read_text())
    with pytest.raises(SemaError, match="Axiom 4"):
        default_codec.from_dict(payload)
