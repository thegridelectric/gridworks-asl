"""Every `$ref` value in a type or enum schema SHALL be a canonical
Sema schema URL.

Per `sema/spec/authoring/types.md` §Referencing Other Vocabulary:

  Every `$ref` value in a type or enum schema SHALL be a canonical Sema
  schema URL of one of the following shapes:

    https://schemas.electricity.works/formats/<format-name>
    https://schemas.electricity.works/enums/<enum-name>/<3-digit-version>
    https://schemas.electricity.works/types/<type-name>
    https://schemas.electricity.works/types/<type-name>/<3-digit-version>

  Draft schemas use the parallel `…/draft/{formats,enums,types}/…` prefix.
  A `$ref` value SHALL NOT be a bare JSON Schema primitive name
  (`"string"`, `"integer"`, etc.), a relative path, a fragment, or any
  other non-canonical string.

This test catches mistakes like a stray `$ref: string` left in a schema
during authoring.
"""
import re
from typing import Any


CANONICAL_REF = re.compile(
    r"^https://schemas\.electricity\.works/"
    r"(?:draft/)?"
    r"(?:"
    r"formats/[a-z0-9.]+"
    r"|enums/[a-z0-9.]+/\d{3}"
    r"|types/[a-z0-9.]+(?:/\d{3})?"
    r")$"
)


def _walk_refs(node: Any, path: list[Any] | None = None):
    """Yield (path, ref_value) for every `$ref` key found in the tree."""
    if path is None:
        path = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref":
                yield (path, value)
            else:
                yield from _walk_refs(value, path + [key])
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from _walk_refs(item, path + [i])


def test_ref_values_are_canonical_sema_urls(all_schemas: dict[str, Any]) -> None:
    for name, schema in all_schemas.items():
        sid = schema.get("$id", "")
        # Formats SHALL NOT use $ref at all (enforced elsewhere); this
        # test applies to type and enum schemas, where $ref is permitted.
        if "/formats/" in sid:
            continue
        for path, ref in _walk_refs(schema):
            assert isinstance(ref, str), (
                f"{name} at {'.'.join(str(p) for p in path)}.$ref: "
                f"value SHALL be a string, got {type(ref).__name__}: {ref!r}."
            )
            assert CANONICAL_REF.match(ref), (
                f"{name} at {'.'.join(str(p) for p in path)}.$ref: "
                f"value {ref!r} is not a canonical Sema schema URL. "
                f"Expected `https://schemas.electricity.works/"
                f"{{formats,enums,types}}/<name>[/<3-digit-version>]`."
            )
