import json
import re
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec
from sema.runtime.types.g_node_gt import GNodeGt


def _axiom_match(n: int) -> re.Pattern[str]:
    return re.compile(rf"axiom {n}", re.IGNORECASE)


def _load_fixture(name: str) -> dict:
    fixture = Path(__file__).parent / "fixtures" / "v005" / name
    return json.loads(fixture.read_text())


def test_g_node_gt_latest_version_is_005() -> None:
    assert GNodeGt.version_value() == "005"


def test_default_v005_loads_as_g_node_gt() -> None:
    decoded = default_codec.from_dict(_load_fixture("default.json"))

    assert isinstance(decoded, GNodeGt)
    assert decoded.type_name == "g.node.gt"
    assert decoded.version == "005"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "axiom_1_a.json",
        "axiom_1_b.json",
    ],
)
def test_axiom_1(fixture_name: str) -> None:
    """
    a. If BaseClass is not Logical, GNodeClass SHALL equal the string value of BaseClass.
    b. If BaseClass is Logical, GNodeClass SHALL NOT equal any value of base.g.node.class other than Logical.
    """
    with pytest.raises(SemaError, match=_axiom_match(1)):
        default_codec.from_dict(_load_fixture(fixture_name))


def test_axiom_2() -> None:
    """
    If BaseClass != Logical, PositionPointId SHALL NOT be null.
    """
    with pytest.raises(SemaError, match=_axiom_match(2)):
        default_codec.from_dict(_load_fixture("axiom_2.json"))


def test_axiom_3() -> None:
    """
    If PrevAlias is not null, it SHALL differ from Alias. If PrevAlias
    is null, no alias transition is represented in this snapshot.
    """
    with pytest.raises(SemaError, match=_axiom_match(3)):
        default_codec.from_dict(_load_fixture("axiom_3.json"))


def test_axiom_4() -> None:
    """
    GNodeClass SHALL be a non-empty string. It SHALL NOT contain whitespace.
    """
    with pytest.raises(SemaError, match=_axiom_match(4)):
        default_codec.from_dict(_load_fixture("axiom_4.json"))


@pytest.mark.parametrize(
    "fixture_name",
    [
        "axiom_5_a.json",
        "axiom_5_b.json",
    ],
)
def test_axiom_5(fixture_name: str) -> None:
    """
    a. Alias SHALL end with ".ta" if and only if GNodeClass is "TerminalAsset".
    b. Alias SHALL end with ".scada" if and only if GNodeClass is "Scada".
    """
    with pytest.raises(SemaError, match=_axiom_match(5)):
        default_codec.from_dict(_load_fixture(fixture_name))


@pytest.mark.parametrize(
    "fixture_name",
    [
        "axiom_6_a.json",
        "axiom_6_b.json",
    ],
)
def test_axiom_6(fixture_name: str) -> None:
    """
    a. Alias SHALL have at least two dotted words.
    b. If PrevAlias is present, it SHALL likewise have at least two dotted words.
    """
    with pytest.raises(SemaError, match=_axiom_match(6)):
        default_codec.from_dict(_load_fixture(fixture_name))
