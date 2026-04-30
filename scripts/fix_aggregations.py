"""
Workaround for a transpiler bug: COUNTIFS / MAXIFS / MINIFS / SUMIFS aggregations
silently DROP criteria-range arguments when those criteria are calc, lookup, or
aggregation fields (rather than raw columns). They also mangle column names
when joining on lookup fields. This script parses every aggregation formula in
the rulebook, detects whether any referenced field is non-raw, and if so
appends a corrected override to postgres/02b-customize-functions.sql.

Run AFTER scripts/fix_lookup_functions.py — this script appends, doesn't replace.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULEBOOK = ROOT / "effortless-rulebook" / "effortless-rulebook.json"
OVERRIDE = ROOT / "postgres" / "02b-customize-functions.sql"


def to_snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


PG_TYPE = {"string": "TEXT", "boolean": "BOOLEAN", "integer": "INTEGER",
           "number": "NUMERIC", "datetime": "TIMESTAMPTZ"}


def field_kind_index(rb):
    idx = {}
    for table_name, table in rb.items():
        if not isinstance(table, dict) or "schema" not in table:
            continue
        for f in table["schema"]:
            idx[(table_name, f["name"])] = f.get("type", "raw")
    return idx


def column_expr(table_pascal, field_pascal, kinds):
    """Return SQL expression for reading <table>.<field>, calling calc fn if needed.
    Uses table alias 't' for the foreign-side row."""
    kind = kinds.get((table_pascal, field_pascal), "raw")
    snake_t = to_snake(table_pascal)
    snake_f = to_snake(field_pascal)
    if kind in ("raw", "relationship"):
        return f"t.{snake_f}"
    return f"calc_{snake_t}_{snake_f}(t.{snake_t}_id)"


def local_col(local_table_pascal, local_field_pascal):
    """Local-side reference: this row's value for <field>, given p_<table>_id parameter."""
    snake_t = to_snake(local_table_pascal)
    snake_f = to_snake(local_field_pascal)
    return f"(SELECT {snake_f} FROM {snake_t} WHERE {snake_t}_id = p_{snake_t}_id)"


def parse_args(s):
    """Split top-level comma-separated args, respecting parens."""
    depth = 0
    out = []
    cur = []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return out


def parse_table_field(token):
    """Parse `Table!{{Field}}` -> ('Table', 'Field') or `{{Field}}` -> (None, 'Field') or literal."""
    m = re.match(r"^(\w+)!\{\{(\w+)\}\}$", token)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^\{\{(\w+)\}\}$", token)
    if m:
        return None, m.group(1)
    return None, None  # literal


def render_criterion(value_token):
    """Convert a literal criterion (`TRUE()`, `FALSE()`, `"x"`, `123`) to SQL."""
    t = value_token.strip()
    if t == "TRUE()" or t == "TRUE":
        return "TRUE"
    if t == "FALSE()" or t == "FALSE":
        return "FALSE"
    return t  # numbers and quoted strings pass through


def needs_override(formula, agg_func, args, kinds):
    """Return True if any referenced foreign field is calc/lookup/aggregation."""
    fields_to_check = []
    if agg_func in ("MAXIFS", "MINIFS", "SUMIFS"):
        fields_to_check.append(args[0])
        for i in range(1, len(args), 2):
            fields_to_check.append(args[i])
    elif agg_func == "COUNTIFS":
        for i in range(0, len(args), 2):
            fields_to_check.append(args[i])
    for tok in fields_to_check:
        tbl, fld = parse_table_field(tok)
        if tbl is None:
            continue
        kind = kinds.get((tbl, fld), "raw")
        if kind not in ("raw", "relationship"):
            return True
    return False


def emit_override(source_table, field_name, datatype, agg_func, args, kinds):
    """Generate a corrected aggregation function body."""
    src_t = to_snake(source_table)
    fname = f"calc_{src_t}_{to_snake(field_name)}"
    ret = PG_TYPE[datatype]
    cast = ret.lower() if ret != "TIMESTAMPTZ" else "timestamptz"

    if agg_func in ("MAXIFS", "MINIFS", "SUMIFS"):
        agg_map = {"MAXIFS": "MAX", "MINIFS": "MIN", "SUMIFS": "SUM"}
        sql_agg = agg_map[agg_func]
        value_tok = args[0]
        v_tbl, v_fld = parse_table_field(value_tok)
        foreign_table = v_tbl
        snake_foreign = to_snake(foreign_table)
        value_expr = column_expr(v_tbl, v_fld, kinds)
        criteria = []
        for i in range(1, len(args), 2):
            r_tbl, r_fld = parse_table_field(args[i])
            crit_tok = args[i + 1]
            c_tbl, c_fld = parse_table_field(crit_tok)
            left = column_expr(r_tbl, r_fld, kinds)
            if c_tbl is not None:
                # Comparison against a local-side field
                right = local_col(c_tbl, c_fld)
            else:
                right = render_criterion(crit_tok)
            criteria.append(f"{left} = {right}")
        where = " AND ".join(criteria) if criteria else "TRUE"
        body = (
            f"  SELECT ({sql_agg}({value_expr}))::{cast}\n"
            f"    FROM {snake_foreign} t\n"
            f"   WHERE {where};"
        )
    elif agg_func == "COUNTIFS":
        # First foreign-side range determines the FROM table
        first_tbl, _ = parse_table_field(args[0])
        snake_foreign = to_snake(first_tbl)
        criteria = []
        for i in range(0, len(args), 2):
            r_tbl, r_fld = parse_table_field(args[i])
            crit_tok = args[i + 1]
            c_tbl, c_fld = parse_table_field(crit_tok)
            left = column_expr(r_tbl, r_fld, kinds)
            if c_tbl is not None:
                right = local_col(c_tbl, c_fld)
            else:
                right = render_criterion(crit_tok)
            criteria.append(f"{left} = {right}")
        where = " AND ".join(criteria) if criteria else "TRUE"
        body = (
            f"  SELECT (COUNT(*))::{cast}\n"
            f"    FROM {snake_foreign} t\n"
            f"   WHERE {where};"
        )
    else:
        return None

    return (
        f"CREATE OR REPLACE FUNCTION {fname}(p_{src_t}_id TEXT)\n"
        f"RETURNS {ret} AS $$\n"
        f"{body}\n"
        f"$$ LANGUAGE sql STABLE;\n"
    )


FUNC_RE = re.compile(r"^=\s*(COUNTIFS|MAXIFS|MINIFS|SUMIFS)\s*\((.*)\)\s*$", re.DOTALL)


def main():
    rb = json.loads(RULEBOOK.read_text())
    kinds = field_kind_index(rb)

    overrides = []
    skipped_ok = 0
    for table_name, table in rb.items():
        if not isinstance(table, dict) or "schema" not in table:
            continue
        for f in table["schema"]:
            if f.get("type") != "aggregation":
                continue
            formula = f.get("formula", "").strip()
            m = FUNC_RE.match(formula)
            if not m:
                continue
            agg_func, inner = m.group(1), m.group(2)
            args = parse_args(inner)
            if not needs_override(formula, agg_func, args, kinds):
                skipped_ok += 1
                continue
            sql = emit_override(table_name, f["name"], f.get("datatype", "string"),
                                agg_func, args, kinds)
            if sql:
                overrides.append(sql)

    existing = OVERRIDE.read_text()
    marker = "-- BEGIN aggregation overrides --"
    end_marker = "-- END aggregation overrides --"
    new_block = (
        f"\n{marker}\n"
        f"-- {len(overrides)} aggregation overrides for fields whose criteria_range\n"
        f"-- references calc/lookup/aggregation columns. The transpiler silently\n"
        f"-- drops those criteria; we restore them here. Auto-generated by\n"
        f"-- scripts/fix_aggregations.py.\n\n"
        + "\n".join(overrides)
        + f"\n{end_marker}\n"
    )
    # Replace any existing aggregation-overrides block
    if marker in existing and end_marker in existing:
        before = existing.split(marker)[0]
        after = existing.split(end_marker, 1)[1]
        OVERRIDE.write_text(before + marker + new_block.split(marker, 1)[1] + after)
    else:
        OVERRIDE.write_text(existing + new_block)
    print(f"Appended {len(overrides)} aggregation overrides ({skipped_ok} OK as-is).")


if __name__ == "__main__":
    main()
