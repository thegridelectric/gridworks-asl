from types import SimpleNamespace

import pytest

from sema.tools.runtime_generation.types import render_type


def _registry() -> dict:
    return {"types": {"example.type": {"versions": {"000": {}}}}, "enums": {}}


def _dag():
    return SimpleNamespace(upgrades={})


def test_runtime_generation_creates_depth_one_inline_object_classes() -> None:
    schema = {
        "$id": "https://schemas.electricity.works/types/example.type/000",
        "title": "example.type",
        "type": "object",
        "properties": {
            "Items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Count": {"type": "integer"},
                    },
                    "required": ["Name", "Count"],
                    "additionalProperties": False,
                },
            },
            "TypeName": {"const": "example.type"},
            "Version": {"const": "000"},
        },
        "required": ["Items", "TypeName", "Version"],
        "additionalProperties": False,
    }

    text = render_type(
        ("type", "example.type", "000"),
        schema,
        _dag(),
        {("type", "example.type"): "000"},
        _registry(),
        "sema.runtime",
    )

    assert "class ItemsItem(BaseModel):" in text
    assert "name: str" in text
    assert "count: StrictInt" in text
    assert "items: list[ItemsItem]" in text
    assert "class ExampleType(SemaType):" in text


def test_runtime_generation_rejects_nested_inline_objects() -> None:
    schema = {
        "$id": "https://schemas.electricity.works/types/example.type/000",
        "title": "example.type",
        "type": "object",
        "properties": {
            "Items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Nested": {
                            "type": "object",
                            "properties": {
                                "Name": {"type": "string"},
                            },
                            "required": ["Name"],
                            "additionalProperties": False,
                        }
                    },
                    "required": ["Nested"],
                    "additionalProperties": False,
                },
            },
            "TypeName": {"const": "example.type"},
            "Version": {"const": "000"},
        },
        "required": ["Items", "TypeName", "Version"],
        "additionalProperties": False,
    }

    with pytest.raises(ValueError, match="Nested inline object generation"):
        render_type(
            ("type", "example.type", "000"),
            schema,
            _dag(),
            {("type", "example.type"): "000"},
            _registry(),
            "sema.runtime",
        )
