"""
Workaround for a transpiler bug: lookup-type fields generate SQL that matches by
`<target_table>_id` (UUID PK) when the FK in this rulebook is actually stored
as the human-readable Name string. We override every lookup function by
replacing the broken outer match with `name = ...` and emit the fixed bodies
to postgres/02b-customize-functions.sql.

Run after `effortless build`. The override file is committed; running this
script is only needed when a build regenerates broken bodies — i.e. after every
`effortless build`. The output is deterministic.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULEBOOK = ROOT / "effortless-rulebook" / "effortless-rulebook.json"
GENERATED = ROOT / "postgres" / "02-create-functions.sql"
OVERRIDE = ROOT / "postgres" / "02b-customize-functions.sql"


def to_snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def field_kind_index(rb):
    """Return {(table, field): kind} where kind is raw|calculated|aggregation|lookup|relationship."""
    idx = {}
    for table_name, table in rb.items():
        if not isinstance(table, dict) or "schema" not in table:
            continue
        for f in table["schema"]:
            idx[(table_name, f["name"])] = f.get("type", "raw")
    return idx


def collect_lookups():
    rb = json.loads(RULEBOOK.read_text())
    kinds = field_kind_index(rb)
    out = []
    for table_name, table in rb.items():
        if not isinstance(table, dict) or "schema" not in table:
            continue
        for f in table["schema"]:
            if f.get("type") != "lookup":
                continue
            formula = f.get("formula", "")
            m = re.search(
                r"INDEX\(\s*(\w+)!\{\{(\w+)\}\}\s*,\s*MATCH\(\s*\{\{(\w+)\}\}\s*,\s*(\w+)!\{\{(\w+)\}\}\s*,\s*0\s*\)\s*\)",
                formula,
            )
            if not m:
                print(f"  skip (formula didn't parse): {table_name}.{f['name']} → {formula}")
                continue
            target_table, target_field, local_fk, _match_table, match_field = m.groups()
            target_kind = kinds.get((target_table, target_field), "raw")
            out.append({
                "source_table": table_name,
                "field_name": f["name"],
                "datatype": f.get("datatype", "string"),
                "target_table": target_table,
                "target_field": target_field,
                "target_kind": target_kind,
                "local_fk": local_fk,
                "match_field": match_field,
            })
    return out


PG_TYPE = {
    "string": "TEXT",
    "boolean": "BOOLEAN",
    "integer": "INTEGER",
    "number": "NUMERIC",
    "datetime": "TIMESTAMPTZ",
}


def emit():
    lookups = collect_lookups()
    chunks = ["-- " + "=" * 76,
              "-- AUTO-GENERATED OVERRIDE — fixes lookup functions whose generated bodies",
              "-- match by `<target>_id` (UUID PK) instead of `<target>.<MatchField>`.",
              "-- Regenerate with scripts/fix_lookup_functions.py after every effortless build.",
              "-- " + "=" * 76,
              ""]
    rb = json.loads(RULEBOOK.read_text())
    kinds = field_kind_index(rb)

    for lk in lookups:
        src_t = to_snake(lk["source_table"])
        tgt_t = to_snake(lk["target_table"])
        target_field = to_snake(lk["target_field"])
        local_fk = to_snake(lk["local_fk"])
        match_field_snake = to_snake(lk["match_field"])
        ret = PG_TYPE[lk["datatype"]]
        cast = ret.lower() if ret != "TIMESTAMPTZ" else "timestamptz"
        fname = f"calc_{src_t}_{to_snake(lk['field_name'])}"

        # Target field side
        if lk["target_kind"] in ("raw", "relationship"):
            select_expr = f"{target_field}::{cast}"
        else:
            tgt_fn = f"calc_{tgt_t}_{target_field}"
            select_expr = f"{tgt_fn}({tgt_t}_id)::{cast}"

        # Match field side — if Name (or any calc) on target table, call calc fn
        match_kind = kinds.get((lk["target_table"], lk["match_field"]), "raw")
        if match_kind in ("raw", "relationship"):
            match_lhs = match_field_snake
        else:
            match_lhs = f"calc_{tgt_t}_{match_field_snake}({tgt_t}_id)"

        chunks.append(
            f"CREATE OR REPLACE FUNCTION {fname}(p_{src_t}_id TEXT)\n"
            f"RETURNS {ret} AS $$\n"
            f"  SELECT ({select_expr}) FROM {tgt_t}\n"
            f"   WHERE {match_lhs} = (SELECT {local_fk} FROM {src_t} WHERE {src_t}_id = p_{src_t}_id)\n"
            f"   LIMIT 1;\n"
            f"$$ LANGUAGE sql STABLE;\n"
        )
    OVERRIDE.write_text("\n".join(chunks))
    print(f"Wrote {len(lookups)} lookup function overrides to {OVERRIDE}.")


if __name__ == "__main__":
    emit()
