"""Examples in type schemas SHALL be serialized JSON document strings.

Per `sema/spec/authoring/types.md` §Examples:

    Examples SHALL be serialized JSON documents, not YAML object
    representations.
    Examples SHALL be structurally valid according to the schema.

In YAML terms, each example entry MUST be a string (typically `- |`
followed by a JSON literal), never a YAML mapping (`- ChannelName: "..."`).
And if it IS a string, it MUST parse as valid JSON.

This test enforces both halves. It applies to type schemas only — formats
and enums also have `examples` blocks, but those are scalar values, not
JSON documents.
"""
import json
from typing import Any


def test_type_examples_are_json_document_strings(all_schemas: dict[str, Any]) -> None:
    for name, schema in all_schemas.items():
        if "/types/" not in schema.get("$id", ""):
            continue
        examples = schema.get("examples")
        if not examples:
            continue
        for i, ex in enumerate(examples):
            assert isinstance(ex, str), (
                f"{name} examples[{i}]: example is a YAML mapping, not a JSON "
                f"document string. Use `examples:` with `- |` followed by a "
                f"JSON literal. Got type {type(ex).__name__}."
            )


def test_type_examples_parse_as_valid_json(all_schemas: dict[str, Any]) -> None:
    for name, schema in all_schemas.items():
        if "/types/" not in schema.get("$id", ""):
            continue
        examples = schema.get("examples")
        if not examples:
            continue
        for i, ex in enumerate(examples):
            if not isinstance(ex, str):
                # The structural check above already flagged this; skip.
                continue
            try:
                json.loads(ex)
            except json.JSONDecodeError as e:
                raise AssertionError(
                    f"{name} examples[{i}]: example string is not valid JSON: {e}. "
                    f"Check for missing commas, trailing commas, or unquoted keys."
                ) from None
