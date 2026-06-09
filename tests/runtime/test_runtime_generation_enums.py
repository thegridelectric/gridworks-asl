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


def test_generated_enum_base_matches_runtime_enum_base(tmp_path: Path) -> None:
    target_root = tmp_path / "sema" / "runtime"

    write_enum_base(target_root)

    generated = (target_root / "enums" / "gw_str_enum.py").read_text()
    checked_in = (
        REPO_ROOT / "src" / "sema" / "runtime" / "enums" / "gw_str_enum.py"
    ).read_text()
    assert generated == checked_in
