"""Negative tests: the schema guardrails actually fire.

The corpus-level tests prove today's definitions are clean; these prove the
guards detect the illegal constructs they exist for (the api-types review
found `type: [{$ref: ...}, "null"]` silently generating `list[Any | None]`).
"""

import pytest
import yaml

from sema.tools.runtime_generation.types import (
    SchemaMappingError,
    TypeContext,
    _annotation_for_schema,
)
from sema.tools.schema_validation import validate_definitions

ILLEGAL_REF_IN_TYPE = {
    "type": "array",
    "items": {
        "type": [
            {"$ref": "https://schemas.electricity.works/formats/spaceheat.name"},
            "null",
        ]
    },
}


def _ctx() -> TypeContext:
    return TypeContext(
        import_root="sema.runtime",
        dag_max={},
        type_registry={},
        enum_registry={},
        type_label="test.type/000",
    )


def test_metaschema_gate_rejects_ref_in_type(tmp_path) -> None:
    schema_dir = tmp_path / "definitions" / "types" / "bad.type"
    schema_dir.mkdir(parents=True)
    (schema_dir / "000.yaml").write_text(
        yaml.safe_dump({"properties": {"ValueList": ILLEGAL_REF_IN_TYPE}})
    )
    findings = validate_definitions(tmp_path / "definitions")
    assert len(findings) == 1
    assert "bad.type" in findings[0]


def test_metaschema_gate_accepts_valid_schema(tmp_path) -> None:
    schema_dir = tmp_path / "definitions" / "types" / "good.type"
    schema_dir.mkdir(parents=True)
    (schema_dir / "000.yaml").write_text(
        yaml.safe_dump(
            {"type": "object", "properties": {"Values": {"type": ["integer", "null"]}}}
        )
    )
    assert validate_definitions(tmp_path / "definitions") == []


def test_generator_raises_on_unmappable_type_list() -> None:
    with pytest.raises(SchemaMappingError, match="cannot map type list"):
        _annotation_for_schema(
            ILLEGAL_REF_IN_TYPE["items"], _ctx(), inline_path=["ValueList", "Item"]
        )


def test_generator_raises_on_non_canonical_ref() -> None:
    # normalize_ref rejects non-canonical URLs before node resolution; the
    # SchemaMappingError in _annotation_for_schema is defense-in-depth behind
    # it. (A well-formed ref to an unregistered word is caught upstream: DAG
    # construction and tests/registry/test_ref_values.py.)
    with pytest.raises(ValueError, match="non-canonical"):
        _annotation_for_schema(
            {"$ref": "https://example.com/not-a-sema-ref"},
            _ctx(),
            inline_path=["Field"],
        )


def test_generator_raises_on_unknown_construct() -> None:
    with pytest.raises(SchemaMappingError, match="cannot map schema construct"):
        _annotation_for_schema({"nonsense": True}, _ctx(), inline_path=["Field"])
