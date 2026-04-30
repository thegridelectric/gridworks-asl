"""Emit definitions/*.yaml from the rulebook (round-trip of yaml-to-rulebook).

Reads:
  effortless-rulebook/effortless-rulebook.json (the SSoT)

Writes (to --output-dir, default = a sibling of definitions/ called definitions-emitted/):
  <out>/owners.yaml
  <out>/registry.yaml
  <out>/formats/<name>.yaml
  <out>/enums/<name>/<NNN>.yaml
  <out>/types/<name>/<NNN>.yaml
  <out>/types/<versionless-name>.yaml          (for IsVersionless types)

The output is canonical-equivalent to the source: comments and exact whitespace are
not preserved, but the modeled content (schema + axioms + examples + descriptions)
is identical after normalization.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
RULEBOOK_PATH = ROOT / "effortless-rulebook" / "effortless-rulebook.json"
DEFAULT_OUTPUT_DIR = ROOT / "definitions-emitted"


SCHEMA_BASE = "https://schemas.electricity.works"


def _by(rulebook: dict[str, Any], table: str) -> list[dict[str, Any]]:
    return rulebook.get(table, {}).get("data") or []


def _index_by(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {r[key]: r for r in rows if key in r}


def _group_by(rows: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    out: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        out[r.get(key)].append(r)
    return out


# ---------------------------------------------------- $ref reconstruction


def ref_for_format(name: str) -> str:
    return f"{SCHEMA_BASE}/formats/{name}"


def ref_for_enum_version(key: str) -> str:
    # key already shaped as 'name/NNN'
    return f"{SCHEMA_BASE}/enums/{key}"


def ref_for_type_version(key: str) -> str:
    return f"{SCHEMA_BASE}/types/{key}"


def attr_to_property(attr: dict[str, Any]) -> dict[str, Any]:
    """Build a single JSON-Schema property dict from a TypeAttributes (or TypeHelperAttributes) row."""
    raw = attr.get("RawJson")
    parked: dict[str, Any] = {}
    if raw:
        try:
            parked = json.loads(raw)
        except json.JSONDecodeError:
            parked = {}
    if isinstance(parked, dict):
        if parked.get("MIGRATION_WARNING") == "OneOfDeferredToRawJson":
            prop = {"oneOf": parked["oneOf"]}
            if attr.get("Description"):
                prop.setdefault("description", attr["Description"])
            return prop
        if parked.get("MIGRATION_WARNING") == "OneOfInArrayItemsDeferredToRawJson":
            prop = {"type": "array", "items": parked["items"]}
            if attr.get("Description"):
                prop.setdefault("description", attr["Description"])
            return prop
        if parked.get("MIGRATION_WARNING") == "AnyOfDeferredToRawJson":
            prop = {"anyOf": parked["anyOf"]}
            if attr.get("Description"):
                prop.setdefault("description", attr["Description"])
            return prop
        if parked.get("MIGRATION_WARNING") == "OpenObjectDeferredToRawJson":
            prop = parked.get("schema") or {}
            if attr.get("Description"):
                prop.setdefault("description", attr["Description"])
            return prop
        if "const" in parked:
            prop = {"const": parked["const"]}
            if attr.get("Description"):
                prop.setdefault("description", attr["Description"])
            return prop

    extras = parked.get("extras", {}) if isinstance(parked, dict) else {}

    prop: dict[str, Any] = {}
    is_list = bool(attr.get("IsList"))
    item_or_root = {} if is_list else prop

    if attr.get("FormatRef"):
        item_or_root["$ref"] = ref_for_format(attr["FormatRef"])
    elif attr.get("EnumVersionRef"):
        item_or_root["$ref"] = ref_for_enum_version(attr["EnumVersionRef"])
    elif attr.get("SubTypeVersionRef"):
        item_or_root["$ref"] = ref_for_type_version(attr["SubTypeVersionRef"])
    elif attr.get("HelperRef"):
        # Helper bodies get re-inlined later in build_type_yaml — stash a sentinel.
        item_or_root["__HELPER_REF__"] = attr["HelperRef"]
    elif attr.get("PrimitiveType"):
        item_or_root["type"] = attr["PrimitiveType"]

    if is_list:
        prop["type"] = "array"
        prop["items"] = item_or_root

    if attr.get("Description"):
        prop["description"] = attr["Description"]

    if attr.get("Default") is not None:
        try:
            prop["default"] = json.loads(attr["Default"])
        except json.JSONDecodeError:
            prop["default"] = attr["Default"]

    for k, v in extras.items():
        prop.setdefault(k, v)
    return prop


# ---------------------------------------------------- helpers


def _strip_helper_sentinels(prop: Any, helpers_by_name: dict[str, dict[str, Any]],
                            helper_attrs_by_helper: dict[str, list[dict[str, Any]]]) -> Any:
    """Replace any __HELPER_REF__ sentinels with the inlined helper schema."""
    if isinstance(prop, dict):
        if "__HELPER_REF__" in prop:
            helper_name = prop["__HELPER_REF__"]
            helper = helpers_by_name.get(helper_name) or {}
            inlined = build_helper_inline(helper, helper_attrs_by_helper)
            return inlined
        return {k: _strip_helper_sentinels(v, helpers_by_name, helper_attrs_by_helper)
                for k, v in prop.items()}
    if isinstance(prop, list):
        return [_strip_helper_sentinels(x, helpers_by_name, helper_attrs_by_helper) for x in prop]
    return prop


def build_helper_inline(helper: dict[str, Any],
                        helper_attrs_by_helper: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    out: dict[str, Any] = {"type": "object"}
    if helper.get("Description"):
        out["description"] = helper["Description"]
    properties: dict[str, Any] = {}
    required: list[str] = []
    attrs = sorted(helper_attrs_by_helper.get(helper["Name"], []), key=lambda r: r.get("Idx", 0))
    for attr in attrs:
        properties[attr["AttributeName"]] = attr_to_property(attr)
        if attr.get("IsRequired"):
            required.append(attr["AttributeName"])
    if properties:
        out["properties"] = properties
    if required:
        out["required"] = required
    if helper.get("ExtraAllowed") is not None:
        out["additionalProperties"] = helper["ExtraAllowed"]
    return out


# ---------------------------------------------------- per-file builders


def _decode_value(s: Any) -> Any:
    """FormatExamples.Value / EnumValues.Symbol may be JSON-encoded; round-trip the original type if so."""
    if not isinstance(s, str):
        return s
    try:
        return json.loads(s)
    except (json.JSONDecodeError, ValueError):
        return s


def build_format_yaml(fmt: dict[str, Any], examples: list[dict[str, Any]]) -> dict[str, Any]:
    raw = {}
    if fmt.get("RawJson"):
        try:
            raw = json.loads(fmt["RawJson"])
        except json.JSONDecodeError:
            raw = {}
    fmt_type = raw.get("type", "string")

    out: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": fmt.get("SchemaUrl"),
        "title": fmt.get("Title"),
    }
    if fmt.get("Description"):
        out["description"] = fmt["Description"]
    out["type"] = fmt_type
    if fmt.get("Pattern"):
        out["pattern"] = fmt["Pattern"]
    if fmt.get("MinLength") is not None:
        out["minLength"] = fmt["MinLength"]
    if fmt.get("MaxLength") is not None:
        out["maxLength"] = fmt["MaxLength"]
    if fmt.get("JsonSchemaFormat"):
        out["format"] = fmt["JsonSchemaFormat"]

    pos = sorted([e for e in examples if not e.get("IsCounter")], key=lambda r: r.get("Idx", 0))
    neg = sorted([e for e in examples if e.get("IsCounter")], key=lambda r: r.get("Idx", 0))
    if pos:
        out["examples"] = [_decode_value(e["Value"]) for e in pos]
    if neg:
        out["counterexamples"] = [_decode_value(e["Value"]) for e in neg]

    if fmt.get("Owner"):
        out["x-gridworks"] = {"owner": fmt["Owner"]}

    for k, v in raw.items():
        if k != "type":
            out.setdefault(k, v)

    return _strip_nones(out)


def build_enum_yaml(enum: dict[str, Any], ev: dict[str, Any],
                    values: list[dict[str, Any]]) -> dict[str, Any]:
    raw = {}
    if ev.get("RawJson"):
        try:
            raw = json.loads(ev["RawJson"])
        except json.JSONDecodeError:
            raw = {}
    value_type = enum.get("ValueType") or "string"
    sorted_values = sorted(values, key=lambda r: r.get("Idx", 0))

    def _cast(v: str) -> Any:
        decoded = _decode_value(v)
        if value_type == "integer":
            try:
                return int(decoded)
            except (TypeError, ValueError):
                return decoded
        return decoded

    out: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": ev.get("SchemaUrl"),
        "title": ev.get("Title") or enum["Name"],
        "type": value_type,
    }
    if ev.get("Description"):
        out["description"] = ev["Description"]
    out["enum"] = [_cast(v["Symbol"]) for v in sorted_values]
    if ev.get("DefaultSymbol") is not None:
        out["default"] = _cast(ev["DefaultSymbol"])
    value_descriptions = {_cast(v["Symbol"]): v["Description"]
                          for v in sorted_values if v.get("Description")}
    xg: dict[str, Any] = {}
    if enum.get("Owner"):
        xg["owner"] = enum["Owner"]
    xg["version"] = ev["Version"]
    if value_descriptions:
        xg["value_descriptions"] = value_descriptions
    extended = raw.get("x-gridworks-extended_description")
    if extended:
        xg["extended_description"] = extended
    out["x-gridworks"] = xg

    for k, v in raw.items():
        if k in ("type", "x-gridworks-extended_description"):
            continue
        out.setdefault(k, v)

    return _strip_nones(out)


def build_type_yaml(
    type_row: dict[str, Any],
    tv: dict[str, Any],
    attrs: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    axioms: list[dict[str, Any]],
    helpers_by_name: dict[str, dict[str, Any]],
    helper_attrs_by_helper: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    is_versionless = False
    raw_json = tv.get("RawJson")
    if raw_json:
        try:
            parked = json.loads(raw_json)
            is_versionless = bool(parked.get("IsVersionless"))
        except json.JSONDecodeError:
            pass

    out: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": tv.get("SchemaUrl"),
        "title": tv.get("Title") or type_row["Name"],
        "type": "object",
    }
    if tv.get("Description"):
        out["description"] = tv["Description"]

    sorted_attrs = sorted(attrs, key=lambda r: r.get("Idx", 0))
    properties: dict[str, Any] = {}
    required: list[str] = []
    for attr in sorted_attrs:
        prop = attr_to_property(attr)
        prop = _strip_helper_sentinels(prop, helpers_by_name, helper_attrs_by_helper)
        properties[attr["AttributeName"]] = prop
        if attr.get("IsRequired"):
            required.append(attr["AttributeName"])

    # auto-emit TypeName / Version const properties unless the source already declared them
    if "TypeName" not in properties:
        properties["TypeName"] = {"const": type_row["Name"]}
    if not is_versionless and "Version" not in properties:
        properties["Version"] = {"const": tv["Version"]}

    # Always order [...real, TypeName, Version] in required; properties dict order
    # follows the same convention via dict-rebuild below.
    non_id_required = [r for r in required if r not in ("TypeName", "Version")]
    tail = ["TypeName"] + (["Version"] if not is_versionless else [])
    required = non_id_required + tail
    if "TypeName" in properties or "Version" in properties:
        ordered: dict[str, Any] = {k: v for k, v in properties.items()
                                    if k not in ("TypeName", "Version")}
        if "TypeName" in properties:
            ordered["TypeName"] = properties["TypeName"]
        if "Version" in properties and not is_versionless:
            ordered["Version"] = properties["Version"]
        properties = ordered

    out["properties"] = properties
    out["required"] = required
    if tv.get("ExtraAllowed") is not None:
        out["additionalProperties"] = tv["ExtraAllowed"]

    sorted_examples = sorted(examples, key=lambda r: r.get("Idx", 0))
    if sorted_examples:
        out["examples"] = []
        for ex in sorted_examples:
            try:
                out["examples"].append(json.loads(ex["ExampleJson"]))
            except (json.JSONDecodeError, TypeError):
                out["examples"].append(ex["ExampleJson"])

    xg: dict[str, Any] = {}
    if type_row.get("Owner"):
        xg["owner"] = type_row["Owner"]
    if axioms:
        xg["axioms"] = []
        for a in sorted(axioms, key=lambda r: r.get("Number") or 0):
            ax_row = {"number": a["Number"], "name": a["AxiomName"], "statement": a["Statement"]}
            if a.get("AxiomDescription"):
                ax_row["description"] = a["AxiomDescription"]
            xg["axioms"].append(ax_row)
    if raw_json:
        try:
            parked = json.loads(raw_json)
            for k, v in parked.items():
                if k == "IsVersionless":
                    continue
                if k == "x-gridworks-extended_description":
                    xg["extended_description"] = v
                else:
                    out.setdefault(k, v)
        except json.JSONDecodeError:
            pass
    if xg:
        out["x-gridworks"] = xg

    return _strip_nones(out)


def _strip_nones(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_nones(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nones(x) for x in obj]
    return obj


# ---------------------------------------------------- driver


def emit(rulebook: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    owners = _by(rulebook, "Owners")
    formats = _by(rulebook, "Formats")
    format_examples = _by(rulebook, "FormatExamples")
    enums = _by(rulebook, "Enums")
    enum_versions = _by(rulebook, "EnumVersions")
    enum_values = _by(rulebook, "EnumValues")
    types = _by(rulebook, "Types")
    type_versions = _by(rulebook, "TypeVersions")
    type_attributes = _by(rulebook, "TypeAttributes")
    type_examples = _by(rulebook, "TypeExamples")
    type_axioms = _by(rulebook, "TypeAxioms")
    type_helpers = _by(rulebook, "TypeHelpers")
    type_helper_attributes = _by(rulebook, "TypeHelperAttributes")

    enums_by_name = _index_by(enums, "Name")
    types_by_name = _index_by(types, "Name")
    helpers_by_name = _index_by(type_helpers, "Name")

    # --- owners.yaml
    owners_doc: dict[str, Any] = {}
    for o in owners:
        body: dict[str, Any] = {}
        if o.get("OwnerType"):
            body["type"] = o["OwnerType"]
        if o.get("Contact"):
            body["contact"] = o["Contact"]
        if o.get("Website"):
            body["website"] = o["Website"]
        if o.get("Github"):
            body["github"] = o["Github"]
        if o.get("Organization"):
            body["organization"] = o["Organization"]
        if o.get("Description"):
            body["description"] = o["Description"]
        if o.get("SupportPolicy"):
            body["support_policy"] = o["SupportPolicy"]
        if o.get("License"):
            body["license"] = o["License"]
        owners_doc[o["Name"]] = body
    _write_yaml(output_dir / "owners.yaml", owners_doc)

    # --- formats/<name>.yaml
    formats_dir = output_dir / "formats"
    formats_dir.mkdir(exist_ok=True)
    fe_by_format = _group_by(format_examples, "Format")
    for fmt in formats:
        doc = build_format_yaml(fmt, fe_by_format.get(fmt["Name"], []))
        _write_yaml(formats_dir / f"{fmt['Name']}.yaml", doc)

    # --- enums/<name>/<version>.yaml
    enums_dir = output_dir / "enums"
    enums_dir.mkdir(exist_ok=True)
    values_by_ev = _group_by(enum_values, "EnumVersion")
    for ev in enum_versions:
        enum = enums_by_name.get(ev["Enum"]) or {"Name": ev["Enum"]}
        ev_dir = enums_dir / ev["Enum"]
        ev_dir.mkdir(exist_ok=True)
        ev_key = f"{ev['Enum']}/{ev['Version']}"
        doc = build_enum_yaml(enum, ev, values_by_ev.get(ev_key, []))
        _write_yaml(ev_dir / f"{ev['Version']}.yaml", doc)

    # --- types/<name>/<version>.yaml
    types_dir = output_dir / "types"
    types_dir.mkdir(exist_ok=True)
    attrs_by_tv = _group_by(type_attributes, "TypeVersion")
    examples_by_tv = _group_by(type_examples, "TypeVersion")
    axioms_by_tv = _group_by(type_axioms, "TypeVersion")
    helper_attrs_by_helper = _group_by(type_helper_attributes, "TypeHelper")

    for tv in type_versions:
        type_row = types_by_name.get(tv["Type"]) or {"Name": tv["Type"]}
        tv_key = f"{tv['Type']}/{tv['Version']}"
        is_versionless = False
        if tv.get("RawJson"):
            try:
                parked = json.loads(tv["RawJson"])
                is_versionless = bool(parked.get("IsVersionless"))
            except json.JSONDecodeError:
                pass

        doc = build_type_yaml(
            type_row, tv,
            attrs_by_tv.get(tv_key, []),
            examples_by_tv.get(tv_key, []),
            axioms_by_tv.get(tv_key, []),
            helpers_by_name, helper_attrs_by_helper,
        )
        if is_versionless:
            _write_yaml(types_dir / f"{tv['Type']}.yaml", doc)
        else:
            t_dir = types_dir / tv["Type"]
            t_dir.mkdir(exist_ok=True)
            _write_yaml(t_dir / f"{tv['Version']}.yaml", doc)


def _write_yaml(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(
            doc, f,
            sort_keys=False, allow_unicode=True, default_flow_style=False,
            width=10**6,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    rulebook = json.loads(RULEBOOK_PATH.read_text())
    emit(rulebook, args.output_dir)

    counts = {
        "owners.yaml": 1,
        "formats/*.yaml": len(list((args.output_dir / "formats").glob("*.yaml"))),
        "enums/*/*.yaml": len(list((args.output_dir / "enums").glob("*/*.yaml"))),
        "types/*/*.yaml": len(list((args.output_dir / "types").glob("*/*.yaml"))),
        "types/*.yaml (versionless)": len(list((args.output_dir / "types").glob("*.yaml"))),
    }
    print(f"Emitted to {args.output_dir}")
    for k, v in counts.items():
        print(f"  {k:30s} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
