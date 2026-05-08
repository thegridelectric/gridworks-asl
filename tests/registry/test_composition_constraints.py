from typing import Any


def path_str(path: list[Any]) -> str:
    return ".".join(str(part) for part in path)


def walk_schema(node: Any, path: list[Any] | None = None) -> list[tuple[list[Any], Any]]:
    if path is None:
        path = []

    results = [(path, node)]
    if isinstance(node, dict):
        for key, value in node.items():
            results.extend(walk_schema(value, path + [key]))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            results.extend(walk_schema(item, path + [index]))
    return results


def test_type_one_of_is_only_vocabulary_ref_union(all_schemas: dict[str, Any]) -> None:
    for schema_name, schema in all_schemas.items():
        schema_id = schema.get("$id", "")
        if "/types/" not in schema_id:
            continue

        for path, node in walk_schema(schema):
            if not isinstance(node, dict) or "oneOf" not in node:
                continue

            one_of = node["oneOf"]
            assert isinstance(one_of, list) and one_of, (
                f"{schema_name} at {path_str(path)}: oneOf SHALL be a non-empty list."
            )
            for index, branch in enumerate(one_of):
                branch_path = path + ["oneOf", index]
                assert isinstance(branch, dict), (
                    f"{schema_name} at {path_str(branch_path)}: oneOf branch SHALL be an object."
                )
                assert set(branch) == {"$ref"}, (
                    f"{schema_name} at {path_str(branch_path)}: oneOf branch SHALL contain "
                    "only a direct $ref."
                )
                ref = branch["$ref"]
                assert "/types/" in ref or "/enums/" in ref, (
                    f"{schema_name} at {path_str(branch_path)}: oneOf branch SHALL reference "
                    f"a Sema type or enum, got {ref!r}."
                )
                assert "/formats/" not in ref, (
                    f"{schema_name} at {path_str(branch_path)}: oneOf SHALL NOT reference formats."
                )


def test_type_schemas_do_not_define_inline_enums(all_schemas: dict[str, Any]) -> None:
    for schema_name, schema in all_schemas.items():
        schema_id = schema.get("$id", "")
        if "/types/" not in schema_id:
            continue

        for path, node in walk_schema(schema):
            if isinstance(node, dict):
                assert "enum" not in node, (
                    f"{schema_name} at {path_str(path)}: type schemas SHALL NOT define "
                    "inline enums. Promote the values to a Sema enum and reference it."
                )
