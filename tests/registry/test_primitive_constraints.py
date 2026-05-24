from typing import Any


# Per authoring/types.md §"Primitive Constraint Rule":
# type and enum schemas SHALL NOT use these constraint keywords directly;
# all such constraints MUST be wrapped in a named Sema format. Formats
# themselves are exempt (formats are the canonical carriers of primitive
# constraints).
#
# `propertyNames.pattern` is a deferred spec question (it constrains the
# key-set of an object, not a primitive value); recursion stops at
# `propertyNames:` so its children are not checked.
#
# Array cardinality keywords (`minItems`, `maxItems`, `uniqueItems`) are
# NOT forbidden — they are structural keywords on arrays, not primitive
# value constraints. The `bid` worked example in the spec uses `minItems: 1`.
FORBIDDEN_CONSTRAINT_KEYWORDS = {
    # numeric
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    # string
    "pattern",
    "minLength",
    "maxLength",
}


def test_no_primitive_constraint_keywords(all_schemas):
    def walk(schema_name: str, obj: Any) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in FORBIDDEN_CONSTRAINT_KEYWORDS, (
                    f"{schema_name}: found forbidden JSON Schema constraint '{key}'. "
                    "Use a Sema format instead (see authoring/types.md §Primitive "
                    "Constraint Rule)."
                )
                if key == "propertyNames":
                    # Deferred spec question — do not recurse.
                    continue
                walk(schema_name, value)
        elif isinstance(obj, list):
            for item in obj:
                walk(schema_name, item)

    for name, schema in all_schemas.items():
        if "/formats/" in schema.get("$id", ""):
            continue
        walk(name, schema)
