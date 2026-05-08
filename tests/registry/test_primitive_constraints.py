from typing import Any


def test_no_numeric_constraints(all_schemas):
    forbidden = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"}

    def walk(schema_name: str, obj: Any) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in forbidden, (
                    f"{schema_name}: found forbidden JSON Schema constraint '{key}'. "
                    "Use a Sema format instead."
                )
                walk(schema_name, value)
        elif isinstance(obj, list):
            for item in obj:
                walk(schema_name, item)

    for name, schema in all_schemas.items():
        if "/formats/" in schema.get("$id", ""):
            continue
        walk(name, schema)
