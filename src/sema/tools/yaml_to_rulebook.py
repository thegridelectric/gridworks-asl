"""Migrate the YAML registry under definitions/ into the hand-authored rulebook.

Reads:
  definitions/owners.yaml
  definitions/registry.yaml
  definitions/formats/*.yaml
  definitions/enums/<name>/<NNN>.yaml
  definitions/types/<name>/<NNN>.yaml

Writes:
  effortless-rulebook/effortless-rulebook.json
    - preserves the hand-authored schema[] arrays
    - populates the data[] arrays for Module 1 tables
    - leaves Module 2 tables (Projections / *Upgrades / *UpgradeMappings) empty;
      Phase 1.5 (python-upgrades-to-rulebook) populates those from
      src/sema/runtime/{types,enums}/old_versions/*.py.

oneOf bodies are parked in TypeAttributes.RawJson with a MIGRATION_WARNING note.
Inline nested objects (array items with type=object) are auto-promoted to
TypeHelpers using the deterministic name heuristic specified in the migration plan.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_DIR = ROOT / "definitions"
RULEBOOK_PATH = ROOT / "effortless-rulebook" / "effortless-rulebook.json"

REF_FORMAT = re.compile(r"^https://schemas\.electricity\.works/formats/([a-z0-9._-]+)$")
REF_ENUM = re.compile(r"^https://schemas\.electricity\.works/enums/([a-z0-9._-]+)/(\d{3})$")
REF_TYPE = re.compile(r"^https://schemas\.electricity\.works/types/([a-z0-9._-]+)/(\d{3})$")


class MigrationContext:
    """Accumulates rows + warnings while walking definitions/."""

    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, Any]]] = {
            "Owners": [],
            "Formats": [],
            "FormatExamples": [],
            "Enums": [],
            "EnumVersions": [],
            "EnumValues": [],
            "Types": [],
            "TypeVersions": [],
            "TypeAttributes": [],
            "TypeExamples": [],
            "TypeAxioms": [],
            "TypeHelpers": [],
            "TypeHelperAttributes": [],
        }
        self.warnings: list[str] = []
        self._helper_seen: set[str] = set()

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_yaml(path: Path) -> Any:
    with path.open() as f:
        return yaml.safe_load(f)


def load_yaml_safe(path: Path, ctx: MigrationContext, kind: str) -> Any | None:
    try:
        return load_yaml(path)
    except yaml.YAMLError as e:
        ctx.warn(f"YamlParseError: {kind} {path.relative_to(ROOT)} — {type(e).__name__}: {str(e).splitlines()[0]}")
        return None


def resolve_ref(url: str) -> tuple[str, str | None] | None:
    """Return (kind, key) for a $ref URL or None if unrecognized.

    kind ∈ {'format', 'enum', 'type'}; key is the resolved FK target:
        format → '<name>'              (no version)
        enum   → '<name>/<NNN>'        (compound EnumVersion key)
        type   → '<name>/<NNN>'        (compound TypeVersion key)
    """
    if m := REF_FORMAT.match(url):
        return ("format", m.group(1))
    if m := REF_ENUM.match(url):
        return ("enum", f"{m.group(1)}/{m.group(2)}")
    if m := REF_TYPE.match(url):
        return ("type", f"{m.group(1)}/{m.group(2)}")
    return None


def helper_name_for_array(parent_type_name: str, attr_name: str) -> str:
    """Deterministic helper-naming heuristic for array.items.object cases.

    Strip trailing 's' or 'List' from attribute name, fallback to <attr>Item.
    Examples (per plan):
      RelayNodes        -> RelayNode
      ChannelReadingsList -> ChannelReading
    """
    s = attr_name
    if s.endswith("List") and len(s) > 4:
        s = s[:-4]
    if s.endswith("s") and len(s) > 1:
        s = s[:-1]
    if s == attr_name:
        s = f"{attr_name}Item"
    return f"{parent_type_name}.{s}"


# ------------------------------------------------------------------ Module 1 builders


def import_owners(ctx: MigrationContext) -> None:
    data = load_yaml_safe(DEFINITIONS_DIR / "owners.yaml", ctx, "owners") or {}
    for slug, row in data.items():
        ctx.rows["Owners"].append({
            "Name": slug,
            "OwnerType": row.get("type"),
            "Contact": row.get("contact"),
            "Website": row.get("website"),
            "Github": row.get("github"),
            "Organization": row.get("organization"),
            "Description": row.get("description"),
            "SupportPolicy": row.get("support_policy"),
            "License": row.get("license"),
        })


def import_formats(ctx: MigrationContext, registry: dict[str, Any]) -> None:
    fmt_registry = (registry.get("formats") or {})
    for fmt_dir in sorted((DEFINITIONS_DIR / "formats").glob("*.yaml")):
        name = fmt_dir.stem
        fmt = load_yaml_safe(fmt_dir, ctx, "format") or {}
        reg = fmt_registry.get(name, {})
        modeled = {"$schema", "$id", "title", "description",
                   "pattern", "minLength", "maxLength", "format",
                   "examples", "counterexamples", "x-gridworks"}
        unmodeled = {k: v for k, v in fmt.items() if k not in modeled}
        if fmt.get("type") and fmt["type"] != "string":
            unmodeled["type"] = fmt["type"]
        ctx.rows["Formats"].append({
            "Name": name,
            "Owner": reg.get("owner") or (fmt.get("x-gridworks") or {}).get("owner"),
            "SchemaUrl": fmt.get("$id"),
            "Title": fmt.get("title"),
            "Description": fmt.get("description") or reg.get("description"),
            "Pattern": fmt.get("pattern"),
            "MinLength": fmt.get("minLength"),
            "MaxLength": fmt.get("maxLength"),
            "JsonSchemaFormat": fmt.get("format"),
            "Created": reg.get("created"),
            "RawJson": json.dumps(unmodeled) if unmodeled else None,
        })
        for idx, ex in enumerate(fmt.get("examples") or []):
            ctx.rows["FormatExamples"].append({
                "Format": name, "Idx": idx, "IsCounter": False,
                "Value": json.dumps(ex), "Description": None,
            })
        for idx, ex in enumerate(fmt.get("counterexamples") or []):
            ctx.rows["FormatExamples"].append({
                "Format": name, "Idx": idx, "IsCounter": True,
                "Value": json.dumps(ex), "Description": None,
            })


def import_enums(ctx: MigrationContext, registry: dict[str, Any]) -> None:
    enum_registry = (registry.get("enums") or {})
    yaml_owners: dict[str, str] = {}

    for enum_dir in sorted((DEFINITIONS_DIR / "enums").iterdir()):
        if not enum_dir.is_dir():
            continue
        enum_name = enum_dir.name
        for ver_path in sorted(enum_dir.glob("*.yaml")):
            version = ver_path.stem
            doc = load_yaml_safe(ver_path, ctx, "enum-version")
            if doc is None:
                continue
            reg = (enum_registry.get(enum_name) or {})
            reg_versions = reg.get("versions") or {}
            ver_meta = reg_versions.get(version) or reg
            xg = doc.get("x-gridworks") or {}
            yaml_owner = xg.get("owner")
            if yaml_owner:
                yaml_owners.setdefault(enum_name, yaml_owner)

            modeled = {"$schema", "$id", "title", "description", "type",
                       "enum", "default", "x-gridworks"}
            unmodeled = {k: v for k, v in doc.items() if k not in modeled}
            extended = xg.get("extended_description")
            if extended:
                unmodeled["x-gridworks-extended_description"] = extended

            ctx.rows["EnumVersions"].append({
                "Enum": enum_name,
                "Version": version,
                "SchemaUrl": doc.get("$id"),
                "Title": doc.get("title"),
                "Description": doc.get("description"),
                "DefaultSymbol": str(doc["default"]) if doc.get("default") is not None else None,
                "Status": ver_meta.get("status"),
                "Created": ver_meta.get("created"),
                "RawJson": json.dumps(unmodeled) if unmodeled else None,
            })
            value_descriptions = xg.get("value_descriptions") or {}
            ev_key = f"{enum_name}/{version}"
            for idx, sym in enumerate(doc.get("enum") or []):
                ctx.rows["EnumValues"].append({
                    "EnumVersion": ev_key,
                    "Symbol": str(sym),
                    "Idx": idx,
                    "Description": value_descriptions.get(sym),
                })

    for enum_name, reg in enum_registry.items():
        ctx.rows["Enums"].append({
            "Name": enum_name,
            "Owner": yaml_owners.get(enum_name) or reg.get("owner"),
            "EnumType": reg.get("enum_type"),
            "ValueType": reg.get("value_type"),
            "Description": reg.get("description"),
            "RawJson": None,
        })


def import_types(ctx: MigrationContext, registry: dict[str, Any]) -> None:
    type_registry = (registry.get("types") or {})
    yaml_owners: dict[str, str] = {}
    types_root = DEFINITIONS_DIR / "types"
    for entry in types_root.iterdir():
        if entry.is_dir():
            for ver_path in entry.glob("*.yaml"):
                try:
                    doc = yaml.safe_load(ver_path.read_text())
                except yaml.YAMLError:
                    continue
                xg = (doc or {}).get("x-gridworks") or {}
                if xg.get("owner"):
                    yaml_owners.setdefault(entry.name, xg["owner"])
        elif entry.suffix == ".yaml":
            try:
                doc = yaml.safe_load(entry.read_text())
            except yaml.YAMLError:
                continue
            xg = (doc or {}).get("x-gridworks") or {}
            if xg.get("owner"):
                yaml_owners.setdefault(entry.stem, xg["owner"])

    for type_name, reg in type_registry.items():
        ctx.rows["Types"].append({
            "Name": type_name,
            "Owner": yaml_owners.get(type_name) or reg.get("owner"),
            "Title": reg.get("title"),
            "Description": reg.get("description"),
            "PythonClassName": None,
            "MakeDataClass": None,
            "IsCac": None,
            "IsComponent": None,
        })

    types_root = DEFINITIONS_DIR / "types"
    for entry in sorted(types_root.iterdir()):
        if entry.is_dir():
            type_name = entry.name
            if type_name not in type_registry:
                ctx.rows["Types"].append({
                    "Name": type_name, "Owner": None, "Title": None,
                    "Description": None, "PythonClassName": None,
                    "MakeDataClass": None, "IsCac": None, "IsComponent": None,
                })
            for ver_path in sorted(entry.glob("*.yaml")):
                version = ver_path.stem
                _import_type_version(ctx, type_registry, type_name, version, ver_path)
        elif entry.suffix == ".yaml":
            type_name = entry.stem
            if type_name not in type_registry:
                ctx.rows["Types"].append({
                    "Name": type_name, "Owner": None, "Title": None,
                    "Description": None, "PythonClassName": None,
                    "MakeDataClass": None, "IsCac": None, "IsComponent": None,
                })
            _import_type_version(
                ctx, type_registry, type_name, "000", entry, versionless=True
            )


def _import_type_version(
    ctx: MigrationContext,
    type_registry: dict[str, Any],
    type_name: str,
    version: str,
    ver_path: Path,
    versionless: bool = False,
) -> None:
    doc = load_yaml_safe(ver_path, ctx, "type-version")
    if doc is None:
        return
    reg = (type_registry.get(type_name) or {})
    reg_versions = reg.get("versions") or {}
    ver_meta = reg_versions.get(version) or {}

    modeled = {"$schema", "$id", "title", "description", "type",
               "properties", "required", "additionalProperties",
               "examples", "x-gridworks"}
    unmodeled = {k: v for k, v in doc.items() if k not in modeled}
    extended = (doc.get("x-gridworks") or {}).get("extended_description")
    if extended:
        unmodeled["x-gridworks-extended_description"] = extended
    if versionless:
        unmodeled["IsVersionless"] = True

    ctx.rows["TypeVersions"].append({
        "Type": type_name,
        "Version": version,
        "SchemaUrl": doc.get("$id"),
        "Title": doc.get("title"),
        "Description": doc.get("description"),
        "ExtraAllowed": doc.get("additionalProperties"),
        "Status": ver_meta.get("status"),
        "Created": ver_meta.get("created"),
        "RawJson": json.dumps(unmodeled) if unmodeled else None,
    })

    tv_key = f"{type_name}/{version}"
    required = set(doc.get("required") or [])
    properties = doc.get("properties") or {}

    for idx, attr_name in enumerate(properties.keys()):
        prop = properties[attr_name] or {}
        # Skip ONLY const-form TypeName/Version (identity markers per plan §6).
        # If a YAML declares Version as non-const (e.g., ha1.params), keep it as a real attribute.
        if "const" in prop and attr_name in ("TypeName", "Version"):
            continue
        attr_row = _build_attribute_row(
            ctx,
            owner_table="TypeAttributes",
            parent_key=tv_key,
            parent_type_name=type_name,
            attr_name=attr_name,
            prop=prop,
            idx=idx,
            is_required=attr_name in required,
            origin_type_version=tv_key,
            origin_path_prefix=f"/properties/{attr_name}",
        )
        attr_row["TypeVersion"] = tv_key
        ctx.rows["TypeAttributes"].append(attr_row)

    for idx, ex in enumerate(doc.get("examples") or []):
        if isinstance(ex, str):
            example_json = ex.strip()
        else:
            example_json = json.dumps(ex)
        ctx.rows["TypeExamples"].append({
            "TypeVersion": tv_key, "Idx": idx, "ExampleJson": example_json,
        })

    axioms = (doc.get("x-gridworks") or {}).get("axioms") or []
    for ax in axioms:
        ctx.rows["TypeAxioms"].append({
            "TypeVersion": tv_key,
            "Number": ax.get("number"),
            "AxiomName": ax.get("name"),
            "Statement": ax.get("statement"),
            "AxiomDescription": ax.get("description"),
        })


_MODELED_PER_ATTR = {"description", "type", "$ref", "items", "oneOf", "anyOf",
                     "properties", "required", "additionalProperties", "const"}


def _extract_extras(prop: dict[str, Any]) -> dict[str, Any]:
    """Collect attribute-level JSON-Schema keys not covered by the structured columns.

    Examples: minimum, maximum, minLength, maxLength, minItems, maxItems, default,
    pattern, multipleOf, etc. These round-trip via TypeAttributes.RawJson.extras.
    """
    return {k: v for k, v in prop.items() if k not in _MODELED_PER_ATTR}


def _build_attribute_row(
    ctx: MigrationContext,
    owner_table: str,
    parent_key: str,
    parent_type_name: str,
    attr_name: str,
    prop: dict[str, Any],
    idx: int,
    is_required: bool,
    origin_type_version: str,
    origin_path_prefix: str,
) -> dict[str, Any]:
    """Build a TypeAttributes (or TypeHelperAttributes) row from a JSON-Schema property.

    Returns a row dict missing the TypeVersion / TypeHelper FK column —
    callers fill that in.
    """
    extras = _extract_extras(prop)
    row = {
        "AttributeName": attr_name,
        "Idx": idx,
        "Description": prop.get("description"),
        "IsRequired": is_required,
        "IsList": False,
        "PrimitiveType": None,
        "FormatRef": None,
        "EnumVersionRef": None,
        "SubTypeVersionRef": None,
        "HelperRef": None,
        "RawJson": json.dumps({"extras": extras}) if extras else None,
    }

    if "const" in prop:
        const_value = prop["const"]
        if isinstance(const_value, str):
            row["PrimitiveType"] = "string"
        elif isinstance(const_value, bool):
            row["PrimitiveType"] = "boolean"
        elif isinstance(const_value, int):
            row["PrimitiveType"] = "integer"
        elif isinstance(const_value, float):
            row["PrimitiveType"] = "number"
        row["RawJson"] = json.dumps({"const": const_value})
        return row

    if "oneOf" in prop:
        ctx.warn(
            f"OneOfDeferredToRawJson: {parent_key}.{attr_name} — oneOf body parked in RawJson"
        )
        row["RawJson"] = json.dumps({"MIGRATION_WARNING": "OneOfDeferredToRawJson",
                                      "oneOf": prop["oneOf"]})
        return row

    if "anyOf" in prop:
        branches = [b for b in prop["anyOf"] if not (isinstance(b, dict) and b.get("type") == "null")]
        has_null = len(branches) != len(prop["anyOf"])
        if len(branches) == 1 and has_null:
            single = branches[0]
            if "$ref" in single:
                ref = resolve_ref(single["$ref"])
                if ref is not None:
                    kind, key = ref
                    if kind == "format":
                        row["FormatRef"] = key
                    elif kind == "enum":
                        row["EnumVersionRef"] = key
                    elif kind == "type":
                        row["SubTypeVersionRef"] = key
                    return row
            elif single.get("type") in ("string", "integer", "number", "boolean"):
                row["PrimitiveType"] = single["type"]
                return row
        ctx.warn(f"AnyOfDeferredToRawJson: {parent_key}.{attr_name} — anyOf body parked in RawJson")
        row["RawJson"] = json.dumps({"MIGRATION_WARNING": "AnyOfDeferredToRawJson",
                                      "anyOf": prop["anyOf"]})
        return row

    if "$ref" in prop:
        ref = resolve_ref(prop["$ref"])
        if ref is None:
            ctx.warn(f"UnresolvedRef: {parent_key}.{attr_name} ref={prop['$ref']}")
            row["RawJson"] = json.dumps(prop)
        else:
            kind, key = ref
            if kind == "format":
                row["FormatRef"] = key
            elif kind == "enum":
                row["EnumVersionRef"] = key
            elif kind == "type":
                row["SubTypeVersionRef"] = key
        return row

    if prop.get("type") == "array":
        row["IsList"] = True
        items = prop.get("items") or {}
        if "$ref" in items:
            ref = resolve_ref(items["$ref"])
            if ref is None:
                ctx.warn(f"UnresolvedRef: {parent_key}.{attr_name}.items ref={items['$ref']}")
                row["RawJson"] = json.dumps(prop)
            else:
                kind, key = ref
                if kind == "format":
                    row["FormatRef"] = key
                elif kind == "enum":
                    row["EnumVersionRef"] = key
                elif kind == "type":
                    row["SubTypeVersionRef"] = key
        elif "oneOf" in items:
            ctx.warn(f"OneOfInArrayItemsDeferredToRawJson: {parent_key}.{attr_name} — oneOf in items parked in RawJson")
            row["RawJson"] = json.dumps({"MIGRATION_WARNING": "OneOfInArrayItemsDeferredToRawJson",
                                          "items": items})
        elif items.get("type") == "object" and "properties" in items:
            helper_name = helper_name_for_array(parent_type_name, attr_name)
            row["HelperRef"] = helper_name
            _ensure_type_helper(
                ctx, helper_name, items, origin_type_version,
                f"{origin_path_prefix}/items",
            )
        elif items.get("type") in ("string", "integer", "number", "boolean", "null"):
            row["PrimitiveType"] = items["type"]
        else:
            ctx.warn(f"UnsupportedArrayItems: {parent_key}.{attr_name} items={items}")
            row["RawJson"] = json.dumps(prop)
        return row

    if prop.get("type") == "object":
        if "properties" in prop:
            helper_name = helper_name_for_array(parent_type_name, attr_name)
            row["HelperRef"] = helper_name
            _ensure_type_helper(
                ctx, helper_name, prop, origin_type_version, origin_path_prefix,
            )
            return row
        ctx.warn(f"OpenObjectDeferredToRawJson: {parent_key}.{attr_name} — object without properties parked in RawJson")
        row["RawJson"] = json.dumps({"MIGRATION_WARNING": "OpenObjectDeferredToRawJson",
                                      "schema": prop})
        return row

    primitive = prop.get("type")
    if primitive in ("string", "integer", "number", "boolean", "null"):
        row["PrimitiveType"] = primitive
        return row

    ctx.warn(f"UnknownAttributeShape: {parent_key}.{attr_name} prop={prop}")
    row["RawJson"] = json.dumps(prop)
    return row


def _ensure_type_helper(
    ctx: MigrationContext,
    helper_name: str,
    obj_schema: dict[str, Any],
    origin_type_version: str,
    origin_path: str,
) -> None:
    if helper_name in ctx._helper_seen:
        return
    ctx._helper_seen.add(helper_name)

    ctx.rows["TypeHelpers"].append({
        "Name": helper_name,
        "Title": obj_schema.get("title"),
        "Description": obj_schema.get("description"),
        "ExtraAllowed": obj_schema.get("additionalProperties"),
        "OriginTypeVersion": origin_type_version,
        "OriginPath": origin_path,
    })

    helper_required = set(obj_schema.get("required") or [])
    helper_props = obj_schema.get("properties") or {}
    for idx, hattr_name in enumerate(helper_props.keys()):
        hprop = helper_props[hattr_name] or {}
        attr_row = _build_attribute_row(
            ctx,
            owner_table="TypeHelperAttributes",
            parent_key=helper_name,
            parent_type_name=helper_name,
            attr_name=hattr_name,
            prop=hprop,
            idx=idx,
            is_required=hattr_name in helper_required,
            origin_type_version=origin_type_version,
            origin_path_prefix=f"{origin_path}/properties/{hattr_name}",
        )
        attr_row["TypeHelper"] = helper_name
        ctx.rows["TypeHelperAttributes"].append(attr_row)


# ------------------------------------------------------------------ Driver


def build_rulebook(ctx: MigrationContext) -> dict[str, Any]:
    rulebook = json.loads(RULEBOOK_PATH.read_text())
    for table_name, rows in ctx.rows.items():
        if table_name in rulebook and isinstance(rulebook[table_name], dict):
            rulebook[table_name]["data"] = rows
    meta = rulebook.setdefault("_meta", {}).setdefault("_conversion_metadata", {})
    meta["source"] = "yaml-to-rulebook (Phase 1 importer)"
    meta["definitions_path"] = "definitions/"
    meta["module_1_row_counts"] = {k: len(v) for k, v in ctx.rows.items()}
    meta["migration_warnings"] = ctx.warnings[:50]
    meta["migration_warning_count"] = len(ctx.warnings)
    return rulebook


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print row counts and warnings; do not write the rulebook.")
    args = parser.parse_args(argv)

    ctx = MigrationContext()
    registry = load_yaml_safe(DEFINITIONS_DIR / "registry.yaml", ctx, "registry") or {}

    import_owners(ctx)
    import_formats(ctx, registry)
    import_enums(ctx, registry)
    import_types(ctx, registry)

    print("Module 1 row counts:")
    for table, rows in ctx.rows.items():
        print(f"  {table:25s} {len(rows):5d}")
    print(f"Warnings: {len(ctx.warnings)}")
    for w in ctx.warnings[:20]:
        print(f"  - {w}")
    if len(ctx.warnings) > 20:
        print(f"  ... ({len(ctx.warnings) - 20} more)")

    if args.dry_run:
        return 0

    rulebook = build_rulebook(ctx)
    RULEBOOK_PATH.write_text(json.dumps(rulebook, indent=2) + "\n")
    print(f"\nWrote {RULEBOOK_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
