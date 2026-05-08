# test_inline_object_constraints.py

from typing import Any, Dict, List, Tuple


# ----------------------------
# Helpers
# ----------------------------

def find_inline_objects(schema: Any, path: List[Any] | None = None) -> List[Tuple[List[Any], Dict]]:
    if path is None:
        path = []

    results: List[Tuple[List[Any], Dict]] = []

    if isinstance(schema, dict):
        if schema.get("type") == "object" and "properties" in schema:
            # Inline object = object with properties, not a $ref, and not top-level
            if "$ref" not in schema and path:
                results.append((path, schema))

        for k, v in schema.items():
            results.extend(find_inline_objects(v, path + [k]))

    elif isinstance(schema, list):
        for i, item in enumerate(schema):
            results.extend(find_inline_objects(item, path + [i]))

    return results


def extract_axiom_texts(schema: Dict) -> List[str]:
    axioms = schema.get("x-gridworks", {}).get("axioms", [])
    return [a.get("statement", "").lower() for a in axioms]


def is_type_ref(ref: str) -> bool:
    return "/types/" in ref


def path_str(path: List[Any]) -> str:
    return ".".join(str(p) for p in path)


def walk_schema(node: Any, path: List[Any] | None = None) -> List[Tuple[List[Any], Dict]]:
    if path is None:
        path = []

    results: List[Tuple[List[Any], Dict]] = []
    if isinstance(node, dict):
        results.append((path, node))
        for key, value in node.items():
            results.extend(walk_schema(value, path + [key]))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            results.extend(walk_schema(item, path + [index]))
    return results


# ----------------------------
# Tests
# ----------------------------

def test_inline_objects_are_structural_only(all_schemas):
    """
    Inline objects are allowed but must be semantically inert.

    They MUST NOT:
    - contain semantic constraint keywords
    - reference Sema types
    - be referenced by axioms
    - include semantic language like 'shall'
    """

    forbidden_keys = {"const", "enum", "allOf", "anyOf", "oneOf"}
    forbidden_words = ["shall", "must", "only", "exactly"]

    for schema_name, schema in all_schemas.items():
        axiom_texts = extract_axiom_texts(schema)

        for path, obj in find_inline_objects(schema):
            p = path_str(path)

            # 1. No semantic JSON Schema constructs
            for inner_path, inner_obj in walk_schema(obj):
                inner_p = path_str(path + inner_path)
                for key in forbidden_keys:
                    assert key not in inner_obj, (
                        f"{schema_name} at {inner_p}: inline object uses forbidden key "
                        f"'{key}'. Promote to a Sema type."
                    )

            # 2. No references to Sema types
            for prop_name, prop in obj.get("properties", {}).items():
                if isinstance(prop, dict) and "$ref" in prop:
                    ref = prop["$ref"]
                    assert not is_type_ref(ref), (
                        f"{schema_name} at {p}.{prop_name}: inline object references "
                        f"Sema type '{ref}'. Promote to a Sema type."
                    )

            # 3. No axiom references to inline fields
            field_names = obj.get("properties", {}).keys()
            for axiom in axiom_texts:
                for field in field_names:
                    assert field.lower() not in axiom, (
                        f"{schema_name}: axiom references inline field '{field}' at {p}. "
                        f"Promote to a Sema type."
                    )

            # 4. No semantic language in descriptions anywhere inside the inline object
            for inner_path, inner_obj in walk_schema(obj):
                inner_p = path_str(path + inner_path)
                desc = inner_obj.get("description", "").lower()
                for word in forbidden_words:
                    assert word not in desc, (
                        f"{schema_name} at {inner_p}: inline object description "
                        f"contains semantic word '{word}'. Promote to a Sema type."
                    )


def test_inline_objects_do_not_nest_composition(all_schemas):
    """
    Inline objects should remain simple structural groupings.
    Disallow nested composition like oneOf inside properties.
    """

    for schema_name, schema in all_schemas.items():
        for path, obj in find_inline_objects(schema):
            p = path_str(path)

            for inner_path, inner_obj in walk_schema(obj):
                inner_p = path_str(path + inner_path)
                assert "oneOf" not in inner_obj, (
                    f"{schema_name} at {inner_p}: inline object contains oneOf. "
                    f"Promote to a Sema type."
                )
                assert "anyOf" not in inner_obj, (
                    f"{schema_name} at {inner_p}: inline object contains anyOf. "
                    f"Promote to a Sema type."
                )
                assert "allOf" not in inner_obj, (
                    f"{schema_name} at {inner_p}: inline object contains allOf. "
                    f"Promote to a Sema type."
                )
