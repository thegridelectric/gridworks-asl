"""Serialized field names are PascalCase, recursively (spec Principle 2).

Every property key in a type schema — including nested inline objects and
array item objects — must match ``^[A-Z][A-Za-z0-9]*$``. The dotted-name
tests police vocabulary names; this one polices the wire field names those
schemas define.
"""

import re
from pathlib import Path

import yaml

TYPES_ROOT = Path(__file__).resolve().parents[2] / "definitions" / "types"
PASCAL_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def _check_properties(schema: object, location: str, findings: list[str]) -> None:
    if isinstance(schema, dict):
        for prop_name, prop_schema in schema.get("properties", {}).items():
            if not PASCAL_RE.match(prop_name):
                findings.append(f"{location}: property {prop_name!r} is not PascalCase")
            _check_properties(prop_schema, f"{location}.{prop_name}", findings)
        for key in ("items", "additionalProperties"):
            if key in schema:
                _check_properties(schema[key], f"{location}[{key}]", findings)
        for branch in schema.get("oneOf", []):
            _check_properties(branch, f"{location}[oneOf]", findings)


def test_type_property_names_are_pascal_case() -> None:
    findings: list[str] = []
    for path in sorted(TYPES_ROOT.rglob("*.yaml")):
        schema = yaml.safe_load(path.read_text())
        _check_properties(
            schema, str(path.relative_to(TYPES_ROOT.parents[1])), findings
        )
    assert not findings, "Non-PascalCase serialized field names:\n" + "\n".join(
        findings
    )
