from pathlib import Path

import yaml

from sema.tools.runtime_generation.enums import render_enum, write_enum_base


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def test_string_enum_uses_schema_values_as_member_names() -> None:
    schema = load_yaml(
        REPO_ROOT / "definitions" / "enums" / "change.relay.state" / "000.yaml"
    )
    code = render_enum(
        ("enum", "change.relay.state", "000"),
        schema,
        {("enum", "change.relay.state"): "000"},
        "sema.runtime",
    )

    assert "class ChangeRelayState(SemaEnum):" in code
    assert "    CloseRelay = auto()" in code
    assert "    OpenRelay = auto()" in code
    assert "        return cls.OpenRelay" in code


def test_integer_enum_uses_value_descriptions_as_member_names() -> None:
    schema = load_yaml(
        REPO_ROOT
        / "definitions"
        / "enums"
        / "relay.energization.state"
        / "000.yaml"
    )
    code = render_enum(
        ("enum", "relay.energization.state", "000"),
        schema,
        {("enum", "relay.energization.state"): "000"},
        "sema.runtime",
    )

    assert "class RelayEnergizationState(IntEnum):" in code
    assert "    DeEnergized = 0" in code
    assert "    Energized = 1" in code
    assert "        return cls.DeEnergized" in code


def test_structured_string_enum_renders_attrs_record_and_table() -> None:
    schema = load_yaml(
        REPO_ROOT / "definitions" / "enums" / "gw.market.product.name" / "000.yaml"
    )
    code = render_enum(
        ("enum", "gw.market.product.name", "000"),
        schema,
        {("enum", "gw.market.product.name"): "000"},
        "sema.runtime",
    )

    # Imports the structured base, not the plain SemaEnum.
    assert "from sema.runtime.enums.gw_str_enum import StructuredEnum" in code
    assert "class GwMarketProductName(StructuredEnum):" in code

    # Frozen attribute record with one typed, nullable field per column.
    assert "@dataclass(frozen=True)" in code
    assert "class GwMarketProductNameAttrs:" in code
    assert "    slot_minutes: int | None" in code
    assert "    timeframe: str | None" in code

    # .attrs accessor + deferred (module-level) attribute table, never a member.
    assert "    def attrs(self) -> \"GwMarketProductNameAttrs | None\":" in code
    assert "        return _ATTRS.get(self.value)" in code
    assert "_ATTRS: dict[str, GwMarketProductNameAttrs] = {" in code
    assert "GwMarketProductNameAttrs(timeframe='rt', slot_minutes=60, gate_minutes=5, quantity_unit='AvgkWh')" in code

    # The default sentinel ('unknown') carries no row -> absent from the table.
    assert "'unknown':" not in code


def test_structured_enum_round_trips_through_generated_runtime() -> None:
    from sema.runtime.enums import GwMarketProductName

    assert GwMarketProductName.rt60gate5.attrs.slot_minutes == 60
    assert GwMarketProductName.rt60gate5.attrs.gate_minutes == 5
    assert GwMarketProductName.da60.attrs.gate_minutes is None
    assert GwMarketProductName.rt60gate30b.attrs.quantity_unit == "AvgkW"
    assert GwMarketProductName.unknown.attrs is None
    assert GwMarketProductName.default() is GwMarketProductName.unknown


def test_generated_enum_base_matches_runtime_enum_base(tmp_path: Path) -> None:
    target_root = tmp_path / "sema" / "runtime"

    write_enum_base(target_root)

    generated = (target_root / "enums" / "gw_str_enum.py").read_text()
    checked_in = (
        REPO_ROOT / "src" / "sema" / "runtime" / "enums" / "gw_str_enum.py"
    ).read_text()
    assert generated == checked_in
