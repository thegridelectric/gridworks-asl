#!/usr/bin/env python3
"""Idempotent schema-injection helper for adding inference fields to the rulebook.

Used iteratively to layer in calculated/lookup/aggregation fields. Each invocation
is parameterized by a `BATCH` dict mapping table name -> list of field defs.

Transpiler idiom notes (rulebook-to-postgres v2026.04.30.0131):
  Supported:
    =IF({{Field}}, TRUE(), FALSE())            -> IS NOT NULL test
    =IF({{Field}}="literal", TRUE(), FALSE())  -> CASE WHEN NULLIF(field,'')='literal'...
    =IF(LEN({{Field}})>0, TRUE(), FALSE())     -> LENGTH(NULLIF(field,''))>0 (NULL-safe)
    =NOT({{Field}}="literal")
    =AND(...), =OR(...)
    ={{Field}}                                  -> passthrough copy
    aggregation: =COUNTIFS(Child!{{FK}}, Parent!{{Name}})
    aggregation: =COUNTIFS(Child!{{FK}}, Parent!{{Name}}, Child!{{Bool}}, TRUE())

  Unsupported (compile to NULL with warning comment):
    COALESCE, ISBLANK, IFERROR

  Lookups via INDEX/MATCH compile, but the join uses <parent>_id (synthesized UUID),
  not the parent's name. Since FK columns in this rulebook store the parent's Name
  slug directly, simple passthrough lookups are redundant; skip them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RULEBOOK = Path(__file__).resolve().parents[1] / "effortless-rulebook" / "effortless-rulebook.json"


def field(
    name: str,
    type_: str,
    datatype: str,
    description: str,
    formula: str | None = None,
    related_to: str | None = None,
    nullable: bool = True,
) -> dict:
    f = {
        "name": name,
        "datatype": datatype,
        "type": type_,
        "nullable": nullable,
        "Description": description,
    }
    if formula is not None:
        f["formula"] = formula
    if related_to is not None:
        f["RelatedTo"] = related_to
    return f


def apply_batch(batch: dict[str, list[dict]]) -> tuple[int, int]:
    with open(RULEBOOK) as fp:
        raw = fp.read()
    data = json.loads(raw)

    added = 0
    skipped = 0
    for table, new_fields in batch.items():
        if table not in data:
            print(f"!! table missing: {table}", file=sys.stderr)
            sys.exit(1)
        schema = data[table]["schema"]
        existing = {f["name"] for f in schema}
        for nf in new_fields:
            if nf["name"] in existing:
                skipped += 1
                continue
            schema.append(nf)
            added += 1
            print(f"  + {table}.{nf['name']} ({nf['type']})")

    out = json.dumps(data, indent=2, ensure_ascii=True)
    if not out.endswith("\n"):
        out += "\n"
    if out != raw:
        with open(RULEBOOK, "w") as fp:
            fp.write(out)
        print(f"\nWrote rulebook ({added} added, {skipped} skipped)")
    else:
        print(f"\nNo changes ({skipped} fields already present)")
    return added, skipped


# ----------------------------------------------------------------------------
# BATCH — edited per invocation
# ----------------------------------------------------------------------------
_PREVIOUS_BATCHES_BATCH2: dict[str, list[dict]] = {
    "Enums": [
        field(
            "IsRetired", "calculated", "boolean",
            "True when this enum has been replaced by another (ReplacedBy is set).",
            formula='=IF({{ReplacedBy}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsVersioned", "calculated", "boolean",
            "True when EnumType is 'versioned' (additive-only multi-version enum).",
            formula='=IF({{EnumType}}="versioned", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsLiteral", "calculated", "boolean",
            "True when EnumType is 'literal' (single immutable version, frozen vocabulary).",
            formula='=IF({{EnumType}}="literal", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsIntegerValued", "calculated", "boolean",
            "True when ValueType is 'integer' (otherwise the enum's symbols are strings).",
            formula='=IF({{ValueType}}="integer", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "VersionCount", "aggregation", "integer",
            "Number of EnumVersions for this enum.",
            formula="=COUNTIFS(EnumVersions!{{Enum}}, Enums!{{Name}})",
            nullable=False,
        ),
    ],
    "EnumVersions": [
        field(
            "IsActive", "calculated", "boolean",
            "True when Status is 'active'.",
            formula='=IF({{Status}}="active", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsDeprecated", "calculated", "boolean",
            "True when Status is 'deprecated'.",
            formula='=IF({{Status}}="deprecated", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "HasDefaultSymbol", "calculated", "boolean",
            "True when DefaultSymbol is set on this version.",
            formula='=IF({{DefaultSymbol}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "ValueCount", "aggregation", "integer",
            "Number of EnumValues (symbols) declared in this version.",
            formula="=COUNTIFS(EnumValues!{{EnumVersion}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
    ],
    "EnumValues": [
        field(
            "HasDescription", "calculated", "boolean",
            "True when a per-symbol Description is present.",
            formula='=IF({{Description}}, TRUE(), FALSE())',
            nullable=False,
        ),
    ],
}


_PREVIOUS_BATCHES_BATCH3: dict[str, list[dict]] = {
    "Types": [
        field(
            "IsRetired", "calculated", "boolean",
            "True when this type has been replaced by another (ReplacedBy is set).",
            formula='=IF({{ReplacedBy}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "VersionCount", "aggregation", "integer",
            "Number of TypeVersions for this type.",
            formula="=COUNTIFS(TypeVersions!{{Type}}, Types!{{Name}})",
            nullable=False,
        ),
    ],
    "TypeVersions": [
        field(
            "IsActive", "calculated", "boolean",
            "True when Status is 'active'.",
            formula='=IF({{Status}}="active", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsDeprecated", "calculated", "boolean",
            "True when Status is 'deprecated'.",
            formula='=IF({{Status}}="deprecated", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsClosed", "calculated", "boolean",
            "True when ExtraAllowed is FALSE (additionalProperties: false in JSON-Schema).",
            formula='=IF({{ExtraAllowed}}, FALSE(), TRUE())',
            nullable=False,
        ),
        field(
            "AttributeCount", "aggregation", "integer",
            "Number of TypeAttributes declared on this version.",
            formula="=COUNTIFS(TypeAttributes!{{TypeVersion}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "RequiredAttributeCount", "aggregation", "integer",
            "Number of TypeAttributes on this version where IsRequired=true.",
            formula="=COUNTIFS(TypeAttributes!{{TypeVersion}}, TypeVersions!{{Name}}, TypeAttributes!{{IsRequired}}, TRUE())",
            nullable=False,
        ),
        field(
            "AxiomCount", "aggregation", "integer",
            "Number of natural-language axioms declared on this version.",
            formula="=COUNTIFS(TypeAxioms!{{TypeVersion}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "ExampleCount", "aggregation", "integer",
            "Number of TypeExamples attached to this version.",
            formula="=COUNTIFS(TypeExamples!{{TypeVersion}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
    ],
    "TypeAttributes": [
        field(
            "IsOptional", "calculated", "boolean",
            "True when this attribute is NOT required (inverse of IsRequired). Convenience predicate.",
            formula='=IF({{IsRequired}}, FALSE(), TRUE())',
            nullable=False,
        ),
        field(
            "HasDefault", "calculated", "boolean",
            "True when a JSON-encoded Default value is present for this attribute.",
            formula='=IF({{Default}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "RefKind", "calculated", "string",
            "Which $ref family this attribute uses: 'format', 'enum', 'subtype', 'helper', or 'primitive' when only PrimitiveType is set.",
            formula=(
                '=IF({{FormatRef}}, "format", '
                'IF({{EnumVersionRef}}, "enum", '
                'IF({{SubTypeVersionRef}}, "subtype", '
                'IF({{HelperRef}}, "helper", "primitive"))))'
            ),
            nullable=False,
        ),
    ],
    # TypeExamples: no useful first-layer inference beyond Name — ExampleJson is opaque
    # text. Revisit at higher-order if we want JSON-parsing scalars.
    "TypeAxioms": [
        field(
            "HasStatement", "calculated", "boolean",
            "True when the axiom carries a non-empty Statement.",
            formula='=IF({{Statement}}, TRUE(), FALSE())',
            nullable=False,
        ),
    ],
}


_PREVIOUS_BATCHES_BATCH4: dict[str, list[dict]] = {
    "TypeHelpers": [
        field(
            "AttributeCount", "aggregation", "integer",
            "Number of TypeHelperAttributes declared on this helper.",
            formula="=COUNTIFS(TypeHelperAttributes!{{TypeHelper}}, TypeHelpers!{{Name}})",
            nullable=False,
        ),
        field(
            "RequiredAttributeCount", "aggregation", "integer",
            "Number of TypeHelperAttributes on this helper where IsRequired=true.",
            formula="=COUNTIFS(TypeHelperAttributes!{{TypeHelper}}, TypeHelpers!{{Name}}, TypeHelperAttributes!{{IsRequired}}, TRUE())",
            nullable=False,
        ),
        field(
            "IsClosed", "calculated", "boolean",
            "True when ExtraAllowed is FALSE (the helper rejects unknown properties).",
            formula='=IF({{ExtraAllowed}}, FALSE(), TRUE())',
            nullable=False,
        ),
    ],
    "TypeHelperAttributes": [
        field(
            "IsOptional", "calculated", "boolean",
            "True when this attribute is NOT required (inverse of IsRequired). Convenience predicate.",
            formula='=IF({{IsRequired}}, FALSE(), TRUE())',
            nullable=False,
        ),
        field(
            "RefKind", "calculated", "string",
            "Which $ref family this attribute uses: 'format', 'enum', 'subtype', 'helper', or 'primitive'.",
            formula=(
                '=IF({{FormatRef}}, "format", '
                'IF({{EnumVersionRef}}, "enum", '
                'IF({{SubTypeVersionRef}}, "subtype", '
                'IF({{HelperRef}}, "helper", "primitive"))))'
            ),
            nullable=False,
        ),
    ],
}


_PREVIOUS_BATCHES_BATCH5: dict[str, list[dict]] = {
    "Projections": [
        field(
            "MappingCount", "aggregation", "integer",
            "Number of ProjectionMappings (FromSymbol -> ToSymbol pairs) declared on this projection.",
            formula="=COUNTIFS(ProjectionMappings!{{Projection}}, Projections!{{Name}})",
            nullable=False,
        ),
        field(
            "IsScripted", "calculated", "boolean",
            "True when RawScript is set — projection isn't a flat lookup and falls back to a script.",
            formula='=IF({{RawScript}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsFlatLookup", "calculated", "boolean",
            "True when this projection is a pure flat lookup (no RawScript). The common, well-behaved case.",
            formula='=IF({{RawScript}}, FALSE(), TRUE())',
            nullable=False,
        ),
    ],
    "ProjectionMappings": [
        field(
            "IsRemoval", "calculated", "boolean",
            "True when ToSymbol is empty/null — the source symbol is dropped during projection.",
            formula='=IF({{ToSymbol}}, FALSE(), TRUE())',
            nullable=False,
        ),
        field(
            "IsIdentity", "calculated", "boolean",
            "True when FromSymbol equals ToSymbol — the projection passes the symbol through unchanged.",
            formula='=IF({{FromSymbol}}={{ToSymbol}}, TRUE(), FALSE())',
            nullable=False,
        ),
    ],
}


_PREVIOUS_BATCHES_BATCH6: dict[str, list[dict]] = {
    "TypeUpgrades": [
        field(
            "OpCount", "aggregation", "integer",
            "Number of TypeUpgradeOps that compose this upgrade.",
            formula="=COUNTIFS(TypeUpgradeOps!{{TypeUpgrade}}, TypeUpgrades!{{Name}})",
            nullable=False,
        ),
        field(
            "IsScripted", "calculated", "boolean",
            "True when RawScript is set — the upgrade is a whole-method escape hatch instead of a clean op decomposition.",
            formula='=IF({{RawScript}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsDecomposed", "calculated", "boolean",
            "True when RawScript is empty — the upgrade is composed of structured TypeUpgradeOps. The desired form.",
            formula='=IF({{RawScript}}, FALSE(), TRUE())',
            nullable=False,
        ),
    ],
    "TypeUpgradeOps": [
        field(
            "IsCustom", "calculated", "boolean",
            "True when OpKind is 'Custom' — falls back to per-op RawScript, the escape hatch.",
            formula='=IF({{OpKind}}="Custom", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "HasRawScript", "calculated", "boolean",
            "True when this op carries an inline RawScript snippet (typically only Custom ops).",
            formula='=IF({{RawScript}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "ReferenceKind", "calculated", "string",
            "Which cross-table reference this op carries: 'enum' (EnumVersionRef), 'projection' (ProjectionRef), or 'none'.",
            formula=(
                '=IF({{EnumVersionRef}}, "enum", '
                'IF({{ProjectionRef}}, "projection", "none"))'
            ),
            nullable=False,
        ),
    ],
    "EnumUpgrades": [
        field(
            "MappingCount", "aggregation", "integer",
            "Number of EnumUpgradeMappings that compose this upgrade.",
            formula="=COUNTIFS(EnumUpgradeMappings!{{EnumUpgrade}}, EnumUpgrades!{{Name}})",
            nullable=False,
        ),
        field(
            "IsScripted", "calculated", "boolean",
            "True when RawScript is set (whole-upgrade escape hatch).",
            formula='=IF({{RawScript}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "IsDecomposed", "calculated", "boolean",
            "True when RawScript is empty — upgrade is composed of structured mappings.",
            formula='=IF({{RawScript}}, FALSE(), TRUE())',
            nullable=False,
        ),
    ],
    "EnumUpgradeMappings": [
        field(
            "IsRemoval", "calculated", "boolean",
            "True when ToSymbol is empty/null — the source symbol is dropped in this upgrade.",
            formula='=IF({{ToSymbol}}, FALSE(), TRUE())',
            nullable=False,
        ),
        field(
            "IsIdentity", "calculated", "boolean",
            "True when FromSymbol equals ToSymbol — the symbol passes through unchanged.",
            formula='=IF({{FromSymbol}}={{ToSymbol}}, TRUE(), FALSE())',
            nullable=False,
        ),
    ],
}


# ----------------------------------------------------------------------------
# BATCH 7 — higher-order inferences: cross-FK usage counts, lifecycle reach
# ----------------------------------------------------------------------------
BATCH: dict[str, list[dict]] = {
    "Formats": [
        field(
            "TypeAttributeUsageCount", "aggregation", "integer",
            "Number of TypeAttributes that point at this Format via FormatRef.",
            formula="=COUNTIFS(TypeAttributes!{{FormatRef}}, Formats!{{Name}})",
            nullable=False,
        ),
        field(
            "TypeHelperAttributeUsageCount", "aggregation", "integer",
            "Number of TypeHelperAttributes that point at this Format via FormatRef.",
            formula="=COUNTIFS(TypeHelperAttributes!{{FormatRef}}, Formats!{{Name}})",
            nullable=False,
        ),
    ],
    "EnumVersions": [
        field(
            "TypeAttributeUsageCount", "aggregation", "integer",
            "Number of TypeAttributes that point at this EnumVersion via EnumVersionRef.",
            formula="=COUNTIFS(TypeAttributes!{{EnumVersionRef}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "TypeHelperAttributeUsageCount", "aggregation", "integer",
            "Number of TypeHelperAttributes that point at this EnumVersion via EnumVersionRef.",
            formula="=COUNTIFS(TypeHelperAttributes!{{EnumVersionRef}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "OutgoingProjectionCount", "aggregation", "integer",
            "Number of Projections starting from this version (i.e. where this is FromEnumVersion).",
            formula="=COUNTIFS(Projections!{{FromEnumVersion}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "IncomingProjectionCount", "aggregation", "integer",
            "Number of Projections landing on this version (i.e. where this is ToEnumVersion).",
            formula="=COUNTIFS(Projections!{{ToEnumVersion}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "OutgoingUpgradeCount", "aggregation", "integer",
            "Number of EnumUpgrades that bump from this version.",
            formula="=COUNTIFS(EnumUpgrades!{{FromEnumVersion}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "IncomingUpgradeCount", "aggregation", "integer",
            "Number of EnumUpgrades that bump to this version.",
            formula="=COUNTIFS(EnumUpgrades!{{ToEnumVersion}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "TypeUpgradeOpUsageCount", "aggregation", "integer",
            "Number of TypeUpgradeOps referencing this version (via EnumVersionRef on EnumVersionBump / CoerceToEnum ops).",
            formula="=COUNTIFS(TypeUpgradeOps!{{EnumVersionRef}}, EnumVersions!{{Name}})",
            nullable=False,
        ),
    ],
    "TypeVersions": [
        field(
            "TypeAttributeAsSubtypeCount", "aggregation", "integer",
            "Number of TypeAttributes that nest this version as a sub-type via SubTypeVersionRef.",
            formula="=COUNTIFS(TypeAttributes!{{SubTypeVersionRef}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "TypeHelperAttributeAsSubtypeCount", "aggregation", "integer",
            "Number of TypeHelperAttributes that nest this version as a sub-type via SubTypeVersionRef.",
            formula="=COUNTIFS(TypeHelperAttributes!{{SubTypeVersionRef}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "OutgoingUpgradeCount", "aggregation", "integer",
            "Number of TypeUpgrades that bump from this version (this version has a successor).",
            formula="=COUNTIFS(TypeUpgrades!{{FromTypeVersion}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "IncomingUpgradeCount", "aggregation", "integer",
            "Number of TypeUpgrades that bump to this version (this version was reached from a predecessor).",
            formula="=COUNTIFS(TypeUpgrades!{{ToTypeVersion}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
        field(
            "OriginatedHelperCount", "aggregation", "integer",
            "Number of TypeHelpers whose YAML body originally introduced them in this version.",
            formula="=COUNTIFS(TypeHelpers!{{OriginTypeVersion}}, TypeVersions!{{Name}})",
            nullable=False,
        ),
    ],
    "TypeHelpers": [
        field(
            "TypeAttributeUsageCount", "aggregation", "integer",
            "Number of TypeAttributes that point at this helper via HelperRef.",
            formula="=COUNTIFS(TypeAttributes!{{HelperRef}}, TypeHelpers!{{Name}})",
            nullable=False,
        ),
        field(
            "TypeHelperAttributeUsageCount", "aggregation", "integer",
            "Number of TypeHelperAttributes that point at this helper via HelperRef (nested helpers).",
            formula="=COUNTIFS(TypeHelperAttributes!{{HelperRef}}, TypeHelpers!{{Name}})",
            nullable=False,
        ),
    ],
    "Projections": [
        field(
            "TypeUpgradeOpUsageCount", "aggregation", "integer",
            "Number of TypeUpgradeOps referencing this projection via ProjectionRef (typically AddProjected ops).",
            formula="=COUNTIFS(TypeUpgradeOps!{{ProjectionRef}}, Projections!{{Name}})",
            nullable=False,
        ),
    ],
}


if __name__ == "__main__":
    apply_batch(BATCH)
