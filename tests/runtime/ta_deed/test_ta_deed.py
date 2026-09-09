"""ta.deed axiom counterexamples — sema must reject what violates an axiom.

Each fixture is the word's own example with one axiom-relevant field mutated to a
violating value. Decoding through the sema runtime must catch it.
"""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_simulated_asset_in_world_universe() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="Axiom 1"):
        default_codec.from_dict(payload)
