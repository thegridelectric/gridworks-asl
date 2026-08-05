"""Every definitions schema file must be valid JSON Schema 2020-12.

The same check gates runtime regeneration (scripts/regenerate_runtime.py);
this test makes CI enforce it independently of any build.
"""

from pathlib import Path

from sema.tools.schema_validation import validate_definitions

DEFINITIONS_ROOT = Path(__file__).resolve().parents[2] / "definitions"


def test_schema_files_valid_jsonschema() -> None:
    findings = validate_definitions(DEFINITIONS_ROOT)
    assert not findings, (
        "Schema files violate the JSON Schema 2020-12 metaschema:\n"
        + "\n".join(findings)
    )
