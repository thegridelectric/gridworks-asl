from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import TypeAdapter, ValidationError

from sema.runtime import property_format


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMATS_DIR = REPO_ROOT / "definitions" / "formats"
RUNTIME_FORMAT_TYPES: dict[str, Any] = {
    "handle.name": property_format.HandleName,
    "hex.char": property_format.HexChar,
    "hh.mm": property_format.HhMm,
    "left.right.dot": property_format.LeftRightDot,
    "market.slot.name": property_format.MarketSlotName,
    "non.empty.string": property_format.NonEmptyString,
    "non.negative.int": property_format.NonNegativeInt,
    "pascal.case": property_format.PascalCase,
    "positive.float": property_format.PositiveFloat,
    "positive.int": property_format.PositiveInt,
    "positive.int.as.str": property_format.PositiveIntAsStr,
    "spaceheat.name": property_format.SpaceheatName,
    "utc.iso8601.millis": property_format.UtcIso8601Millis,
    "utc.iso8601.seconds": property_format.UtcIso8601Seconds,
    "utc.milliseconds": property_format.UTCMilliseconds,
    "utc.seconds": property_format.UTCSeconds,
    "uuid4.str": property_format.UUID4Str,
    "mac.address": property_format.MacAddress,
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def format_adapter(format_name: str) -> TypeAdapter:
    return TypeAdapter(RUNTIME_FORMAT_TYPES[format_name])


@pytest.mark.parametrize("schema_path", sorted(FORMATS_DIR.glob("*.yaml")))
def test_property_format_schema_examples_validate(schema_path: Path) -> None:
    schema = load_yaml(schema_path)
    adapter = format_adapter(schema["title"])

    for example in schema.get("examples", []):
        assert adapter.validate_python(example) == example


@pytest.mark.parametrize("schema_path", sorted(FORMATS_DIR.glob("*.yaml")))
def test_property_format_schema_counterexamples_fail(schema_path: Path) -> None:
    schema = load_yaml(schema_path)
    adapter = format_adapter(schema["title"])

    for counterexample in schema.get("counterexamples", []):
        with pytest.raises((TypeError, ValueError, ValidationError)):
            adapter.validate_python(counterexample)
