"""Identity-field consistency for type schemas.

Per `sema/spec/authoring/types.md` §Identity Fields and §Schema Header
Requirements, plus `sema/spec/registry/types.md` §Strategy Semantics:

  - `title` MUST match the vocabulary name registered in `registry.yaml`
    (which equals the name segment of `$id`).
  - `TypeName` MUST be declared using `const` whose value equals the
    registered vocabulary name.
  - For versioned types, the schema-side `Version` field's shape
    depends on the current `versioning_strategy`:
      - `literal` enforces exact version matching, so the **latest**
        version's schema MUST use `const`. Older versions of a type
        whose strategy evolved `string -> literal` may retain their
        original `type: string` shape (the spec allows the
        monotonic strategy evolution); only the latest is checked here.
      - `string` allows a schema to validate multiple versions; all
        versions' schemas use `type: string` (typically with a
        `default:` of the version).
  - Versionless types (`versioning_strategy: "none"`) SHALL NOT have a
    `Version` property at all.

`tests/registry/test_registry_schema_file_layout.py` already checks the
`$id` line against the expected canonical URL. This test checks the
inner identity fields (`title`, `TypeName.const`, `Version` shape)
against the same canonical name/version derived from `$id` and the
type's strategy in the registry.
"""
from pathlib import Path
from typing import Any

import yaml


DEFINITIONS_DIR = Path("definitions")


def _load_registry() -> dict:
    return yaml.safe_load((DEFINITIONS_DIR / "registry.yaml").read_text())


def _name_and_version_from_id(sid: str) -> tuple[str, str | None]:
    """Parse `.../types/<name>` or `.../types/<name>/<version>` out of $id."""
    if "/types/" not in sid:
        return "", None
    tail = sid.split("/types/", 1)[1]
    parts = tail.split("/")
    if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 3:
        return parts[0], parts[1]
    if len(parts) == 1:
        return parts[0], None
    # Unexpected shape; let other tests flag the $id directly.
    return tail, None


def test_title_matches_id_name_for_types(all_schemas: dict[str, Any]) -> None:
    for name, schema in all_schemas.items():
        sid = schema.get("$id", "")
        if "/types/" not in sid:
            continue
        expected_name, _ = _name_and_version_from_id(sid)
        title = schema.get("title")
        assert title == expected_name, (
            f"{name}: title={title!r} does not match name {expected_name!r} "
            f"derived from $id={sid!r}."
        )


def test_typename_const_matches_id_name_for_types(all_schemas: dict[str, Any]) -> None:
    for name, schema in all_schemas.items():
        sid = schema.get("$id", "")
        if "/types/" not in sid:
            continue
        expected_name, _ = _name_and_version_from_id(sid)
        tn = schema.get("properties", {}).get("TypeName")
        assert isinstance(tn, dict), (
            f"{name}: TypeName property is missing or not an object."
        )
        assert "const" in tn, (
            f"{name}: TypeName SHALL be declared using `const` (see "
            f"authoring/types.md §Identity Fields and §Const Usage Rule). "
            f"Got keys: {sorted(tn.keys())!r}."
        )
        assert tn["const"] == expected_name, (
            f"{name}: TypeName.const={tn['const']!r} does not match name "
            f"{expected_name!r} derived from $id={sid!r}."
        )


def test_versionless_types_have_no_version_property(
    all_schemas: dict[str, Any],
) -> None:
    """Versionless types (`versioning_strategy: "none"`) SHALL NOT declare
    a `Version` property in the schema."""
    for name, schema in all_schemas.items():
        sid = schema.get("$id", "")
        if "/types/" not in sid:
            continue
        _, expected_version = _name_and_version_from_id(sid)
        if expected_version is not None:
            continue
        props = schema.get("properties", {}) or {}
        assert "Version" not in props, (
            f"{name}: versionless type (no version segment in $id) SHALL NOT "
            f"declare a `Version` property."
        )


def test_latest_literal_versions_use_version_const(
    all_schemas: dict[str, Any],
) -> None:
    """For versioned types currently at `versioning_strategy: "literal"`,
    the **latest** version's schema MUST declare `Version` as
    `const: "<latest_version>"`.

    Older versions of a type whose strategy evolved `string -> literal`
    may retain their original `type: string` shape per the spec's
    monotonic strategy-evolution rule (none -> string -> literal), so
    they are out of scope for this assertion.
    """
    registry = _load_registry()
    for type_name, entry in registry.get("types", {}).items():
        strategy = entry.get("versioning_strategy")
        if strategy != "literal":
            continue
        latest_version = entry.get("latest_version")
        if latest_version is None:
            continue
        # Skip if the latest version is a draft (drafts are excluded from
        # public surface and may be incomplete).
        latest_status = (
            entry.get("versions", {}).get(latest_version, {}).get("status", "active")
        )
        if latest_status == "draft":
            continue

        key = f"{type_name}:{latest_version}"
        schema = all_schemas.get(key)
        if schema is None:
            # Type isn't reachable via the fixture; covered elsewhere.
            continue
        ver = schema.get("properties", {}).get("Version")
        assert isinstance(ver, dict), (
            f"{key}: Version property is missing or not an object on a "
            f"versioned (literal-strategy) type."
        )
        assert "const" in ver, (
            f"{key}: Version SHALL be declared using `const` for the latest "
            f"version of a literal-strategy type (not `type` + `default`). "
            f"See authoring/types.md §Identity Fields and §Const Usage Rule. "
            f"Got keys: {sorted(ver.keys())!r}."
        )
        assert ver["const"] == latest_version, (
            f"{key}: Version.const={ver['const']!r} does not match "
            f"latest_version {latest_version!r}."
        )


def test_string_strategy_versions_use_type_string(
    all_schemas: dict[str, Any],
) -> None:
    """For versioned types currently at `versioning_strategy: "string"`,
    every version's schema MUST declare `Version` as `type: string` (so
    that the schema can validate multiple versions per the spec's
    Strategy Semantics)."""
    registry = _load_registry()
    for type_name, entry in registry.get("types", {}).items():
        strategy = entry.get("versioning_strategy")
        if strategy != "string":
            continue
        for version in (entry.get("versions") or {}):
            key = f"{type_name}:{version}"
            schema = all_schemas.get(key)
            if schema is None:
                continue
            ver = schema.get("properties", {}).get("Version")
            assert isinstance(ver, dict), (
                f"{key}: Version property is missing or not an object on a "
                f"string-strategy versioned type."
            )
            assert ver.get("type") == "string", (
                f"{key}: Version SHALL be declared as `type: string` for "
                f"string-strategy types (literal validation requires a "
                f"strategy bump to `literal`). Got: {ver!r}."
            )
