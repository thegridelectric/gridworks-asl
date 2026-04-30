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
BATCH: dict[str, list[dict]] = {
    "Owners": [
        field(
            "IsOrganization", "calculated", "boolean",
            "True when OwnerType is 'organization' (vs 'individual'). Cheap classifier for grouping owners.",
            formula='=IF({{OwnerType}}="organization", TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "HasGithub", "calculated", "boolean",
            "True when this owner has a Github URL on file.",
            formula='=IF({{Github}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "FormatCount", "aggregation", "integer",
            "Number of Formats owned by this owner.",
            formula="=COUNTIFS(Formats!{{Owner}}, Owners!{{Name}})",
            nullable=False,
        ),
        field(
            "EnumCount", "aggregation", "integer",
            "Number of Enums owned by this owner.",
            formula="=COUNTIFS(Enums!{{Owner}}, Owners!{{Name}})",
            nullable=False,
        ),
        field(
            "TypeCount", "aggregation", "integer",
            "Number of Types owned by this owner.",
            formula="=COUNTIFS(Types!{{Owner}}, Owners!{{Name}})",
            nullable=False,
        ),
    ],
    "Formats": [
        field(
            "IsRetired", "calculated", "boolean",
            "True when this format has been replaced by another (ReplacedBy is set).",
            formula='=IF({{ReplacedBy}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "HasPattern", "calculated", "boolean",
            "True when a regex Pattern constraint is defined.",
            formula='=IF({{Pattern}}, TRUE(), FALSE())',
            nullable=False,
        ),
        field(
            "HasLengthBounds", "calculated", "boolean",
            "True when at least one of MinLength / MaxLength is defined.",
            formula="=IF(OR({{MinLength}}>0, {{MaxLength}}>0), TRUE(), FALSE())",
            nullable=False,
        ),
        field(
            "ExampleCount", "aggregation", "integer",
            "Number of positive examples on this format (FormatExamples where IsCounter=false).",
            formula="=COUNTIFS(FormatExamples!{{Format}}, Formats!{{Name}}, FormatExamples!{{IsCounter}}, FALSE())",
            nullable=False,
        ),
        field(
            "CounterExampleCount", "aggregation", "integer",
            "Number of counterexamples on this format (FormatExamples where IsCounter=true).",
            formula="=COUNTIFS(FormatExamples!{{Format}}, Formats!{{Name}}, FormatExamples!{{IsCounter}}, TRUE())",
            nullable=False,
        ),
    ],
    "FormatExamples": [
        field(
            "ExampleKind", "calculated", "string",
            "'counter' when IsCounter is true, else 'positive'. Convenience label.",
            formula='=IF({{IsCounter}}, "counter", "positive")',
            nullable=False,
        ),
    ],
}


if __name__ == "__main__":
    apply_batch(BATCH)
