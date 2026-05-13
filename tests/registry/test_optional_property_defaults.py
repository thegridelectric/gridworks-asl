from typing import Any


def test_optional_properties_do_not_have_defaults(all_schemas: dict[str, Any]) -> None:
    for schema_name, schema in all_schemas.items():
        schema_id = schema.get("$id", "")
        if "/types/" not in schema_id:
            continue

        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        for property_name, property_schema in properties.items():
            if not isinstance(property_schema, dict):
                continue
            assert property_name in required or "default" not in property_schema, (
                f"{schema_name}.{property_name}: optional properties SHALL NOT have "
                "default values. Add the property to required or remove the default."
            )
