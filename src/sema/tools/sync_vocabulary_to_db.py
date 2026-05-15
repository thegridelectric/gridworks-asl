"""
sync_vocabulary_to_db.py
========================
Read the legacy YAML SSoT under definitions/ and emit idempotent UPSERT SQL
into postgres/05c-install-vocabulary.sql so every word and version registered
in registry.yaml is present in the live database.

Tables synced (in FK-order):
  owners
  formats          (+ format_examples)
  enums            (+ enum_versions, enum_values)
  types            (+ type_versions, type_attributes, type_examples, type_axioms)

Conflict policy: INSERT ... ON CONFLICT (...) DO UPDATE SET ... — YAML wins.

Status: respects the explicit `status:` markers in registry.yaml. Versions
without a `status` are treated as 'published'.

Reference resolution: $ref URLs in per-version YAML files are parsed to fill
in FormatRef / EnumVersionRef / SubTypeVersionRef on TypeAttributes. The
"/draft/" segment in some schema URLs is stripped before parsing.

Usage:
    python -m sema.tools.sync_vocabulary_to_db
        --root /path/to/repo --out postgres/05c-install-vocabulary.sql
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sql_literal(v: Any) -> str:
    """Render a Python value as a PostgreSQL literal."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("'", "''")
    return f"'{s}'"


def upsert(table: str, pk_cols: list[str], row: dict[str, Any]) -> str:
    """Build an INSERT ... ON CONFLICT (natural_key) DO UPDATE statement.
    Columns and table names are emitted snake_case (no quoting); the surrogate
    `*_id` PK is omitted so the table's DEFAULT fills it."""
    # Quote every column name — some are SQL reserved words ("default", "value").
    cols = list(row.keys())
    vals = ", ".join(sql_literal(row[c]) for c in cols)
    col_list = ", ".join(f'"{c}"' for c in cols)
    pk_list = ", ".join(f'"{c}"' for c in pk_cols)
    non_pk = [c for c in cols if c not in pk_cols]
    if non_pk:
        set_clause = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in non_pk)
        return (f"INSERT INTO {table} ({col_list}) VALUES ({vals})\n"
                f"  ON CONFLICT ({pk_list}) DO UPDATE SET {set_clause};")
    return (f"INSERT INTO {table} ({col_list}) VALUES ({vals})\n"
            f"  ON CONFLICT ({pk_list}) DO NOTHING;")


# Map schema-url path → (Kind, NameAndVersion)
URL_RE = re.compile(
    r"https?://schemas\.electricity\.works/(?:draft/)?(formats|enums|types)/([^/]+)(?:/(\d+))?$"
)


def parse_ref(url: str) -> tuple[str | None, str | None]:
    """Parse a $ref schema URL → (kind, identifier). identifier is name for
    formats, name/version for enums and types."""
    if not isinstance(url, str):
        return None, None
    m = URL_RE.match(url.strip())
    if not m:
        return None, None
    kind, name, version = m.group(1), m.group(2), m.group(3)
    if kind == "formats":
        return "format", name
    return ("enum" if kind == "enums" else "type"), f"{name}/{version}"


# ---------------------------------------------------------------------------
# YAML loaders
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text()) or {}


def load_owners(root: Path) -> dict[str, dict]:
    return load_yaml(root / "definitions" / "owners.yaml")


def load_registry(root: Path) -> dict[str, Any]:
    return load_yaml(root / "definitions" / "registry.yaml")


def load_format_yaml(root: Path, name: str) -> dict[str, Any] | None:
    p = root / "definitions" / "formats" / f"{name}.yaml"
    return load_yaml(p) if p.exists() else None


def load_enum_version_yaml(root: Path, name: str, ver: str) -> dict[str, Any] | None:
    p = root / "definitions" / "enums" / name / f"{ver}.yaml"
    return load_yaml(p) if p.exists() else None


def load_type_version_yaml(root: Path, name: str, ver: str) -> dict[str, Any] | None:
    p = root / "definitions" / "types" / name / f"{ver}.yaml"
    return load_yaml(p) if p.exists() else None


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def build_owners(owners: dict) -> list[str]:
    out = []
    for name, info in owners.items():
        row = {
            "name": name,
            "owner_type": info.get("type"),
            "organization": info.get("organization"),
            "description": info.get("description"),
            "contact": info.get("contact"),
            "website": info.get("website"),
            "github": info.get("github"),
            "license": info.get("license"),
            "support_policy": info.get("support_policy"),
        }
        out.append(upsert("owners", ["name"], row))
    return out


def build_formats(root: Path, registry: dict) -> list[str]:
    out = []
    for name, info in (registry.get("formats") or {}).items():
        fyaml = load_format_yaml(root, name) or {}
        row = {
            "name": name,
            "owner": info.get("owner"),
            "schema_url": info.get("schema_url"),
            "title": fyaml.get("title"),
            "description": info.get("description") or fyaml.get("description"),
            "pattern": fyaml.get("pattern"),
            "min_length": fyaml.get("minLength"),
            "max_length": fyaml.get("maxLength"),
            "json_schema_format": fyaml.get("format"),
            "created": info.get("created"),
        }
        out.append(upsert("formats", ["name"], row))
        # Examples
        examples = fyaml.get("examples") or []
        counterexamples = fyaml.get("counterexamples") or []
        for idx, ex in enumerate(examples):
            out.append(upsert("format_examples", ["format", "value", "is_counter"], {
                "format": name, "idx": idx, "is_counter": False,
                "value": str(ex), "description": None,
            }))
        for idx, ex in enumerate(counterexamples):
            out.append(upsert("format_examples", ["format", "value", "is_counter"], {
                "format": name, "idx": idx, "is_counter": True,
                "value": str(ex), "description": None,
            }))
    return out


def build_enums(root: Path, registry: dict) -> list[str]:
    out = []
    for name, info in (registry.get("enums") or {}).items():
        is_literal = info.get("enum_type") == "literal"
        row = {
            "name": name,
            "owner": info.get("owner"),
            "enum_type": info.get("enum_type"),
            "value_type": "string",
            "description": info.get("description"),
        }
        out.append(upsert("enums", ["name"], row))

        if is_literal:
            ver = "000"
            vinfo = {"schema_url": info.get("schema_url"), "created": info.get("created")}
            _emit_enum_version(out, root, name, ver, vinfo)
            continue

        for ver_key, vinfo in (info.get("versions") or {}).items():
            _emit_enum_version(out, root, name, str(ver_key), vinfo)
    return out


def _emit_enum_version(out: list[str], root: Path, name: str, ver: str, vinfo: dict) -> None:
    eyaml = load_enum_version_yaml(root, name, ver) or {}
    status = vinfo.get("status") or "published"
    if status == "active":
        status = "published"
    row = {
        "enum": name,
        "version": ver,
        "schema_url": vinfo.get("schema_url"),
        "title": eyaml.get("title"),
        "description": vinfo.get("summary") or eyaml.get("description"),
        "default_symbol": eyaml.get("default"),
        "status": status,
        "created": vinfo.get("created"),
    }
    out.append(upsert("enum_versions", ["enum", "version"], row))

    values = eyaml.get("enum") or []
    descriptions = ((eyaml.get("x-gridworks") or {}).get("value_descriptions") or {})
    for idx, symbol in enumerate(values):
        out.append(upsert("enum_values", ["enum_version", "symbol"], {
            "enum_version": f"{name}/{ver}",
            "symbol": str(symbol),
            "idx": idx,
            "description": descriptions.get(symbol),
        }))


def build_types(root: Path, registry: dict) -> list[str]:
    out = []
    for name, info in (registry.get("types") or {}).items():
        row = {
            "name": name,
            "owner": info.get("owner"),
            "description": info.get("description"),
        }
        out.append(upsert("types", ["name"], row))

        for ver_key, vinfo in (info.get("versions") or {}).items():
            _emit_type_version(out, root, name, str(ver_key), vinfo)
    return out


def _emit_type_version(out: list[str], root: Path, name: str, ver: str, vinfo: dict) -> None:
    tyaml = load_type_version_yaml(root, name, ver) or {}
    status = vinfo.get("status") or "published"
    if status == "active":
        status = "published"
    extra_allowed = tyaml.get("additionalProperties", True) is not False
    row = {
        "type": name,
        "version": ver,
        "schema_url": vinfo.get("schema_url"),
        "title": tyaml.get("title"),
        "description": vinfo.get("summary") or tyaml.get("description"),
        "extra_allowed": extra_allowed,
        "status": status,
        "created": vinfo.get("created"),
    }
    out.append(upsert("type_versions", ["type", "version"], row))

    properties = tyaml.get("properties") or {}
    required = set(tyaml.get("required") or [])
    tv_id = f"{name}/{ver}"
    idx = 0
    for attr_name, attr_spec in properties.items():
        # Skip TypeName/Version constants — implicit in the rulebook.
        if attr_name in ("TypeName", "Version") and "const" in (attr_spec or {}):
            continue
        prim, fmt_ref, enum_ref, sub_ref, is_list = _classify_attribute(attr_spec or {})
        out.append(upsert("type_attributes", ["type_version", "attribute_name"], {
            "type_version": tv_id,
            "attribute_name": attr_name,
            "idx": idx,
            "description": _scalar_description(attr_spec),
            "default": attr_spec.get("default") if isinstance(attr_spec, dict) else None,
            "is_required": attr_name in required,
            "is_list": is_list,
            "primitive_type": prim,
            "format_ref": fmt_ref,
            "enum_version_ref": enum_ref,
            "sub_type_version_ref": sub_ref,
        }))
        idx += 1

    # Examples
    for ex_idx, ex in enumerate(tyaml.get("examples") or []):
        out.append(upsert("type_examples", ["type_version", "idx"], {
            "type_version": tv_id,
            "idx": ex_idx,
            "example_json": ex if isinstance(ex, str) else str(ex),
        }))

    # Axioms
    for ax_idx, axiom in enumerate((tyaml.get("x-gridworks") or {}).get("axioms") or [], start=1):
        if isinstance(axiom, dict):
            name_ax = axiom.get("name") or f"Axiom{ax_idx}"
            stmt = axiom.get("statement") or axiom.get("description")
        else:
            name_ax = f"Axiom{ax_idx}"
            stmt = str(axiom)
        out.append(upsert("type_axioms", ["type_version", "axiom_name"], {
            "type_version": tv_id,
            "number": ax_idx,
            "axiom_name": name_ax,
            "statement": stmt,
        }))


def _classify_attribute(spec: dict) -> tuple[str | None, str | None, str | None, str | None, bool]:
    """Return (PrimitiveType, FormatRef, EnumVersionRef, SubTypeVersionRef, IsList)."""
    is_list = False
    if spec.get("type") == "array":
        is_list = True
        spec = spec.get("items") or {}

    if "$ref" in spec:
        kind, ident = parse_ref(spec["$ref"])
        if kind == "format":
            return None, ident, None, None, is_list
        if kind == "enum":
            return None, None, ident, None, is_list
        if kind == "type":
            return None, None, None, ident, is_list
        return None, None, None, None, is_list

    t = spec.get("type")
    if t in ("string", "integer", "number", "boolean"):
        return t, None, None, None, is_list
    return None, None, None, None, is_list


def _scalar_description(spec: Any) -> str | None:
    if isinstance(spec, dict):
        d = spec.get("description")
        if isinstance(d, str):
            return d.strip()
    return None


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

HEADER = """-- ============================================================================
-- 05c-install-vocabulary.sql
-- ============================================================================
-- AUTO-GENERATED by src/sema/tools/sync_vocabulary_to_db.py from definitions/.
-- DO NOT EDIT BY HAND. Re-run the sync tool to regenerate.
--
-- This file upserts every Owner / Format / Enum (+versions, values) /
-- Type (+versions, attributes, examples, axioms) declared in the legacy YAML
-- SSoT into the rulebook tables. Conflict policy: YAML wins (DO UPDATE).
-- ============================================================================

BEGIN;
"""

FOOTER = """
COMMIT;
"""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    root: Path = args.root
    out: Path = args.out or root / "postgres" / "05c-install-vocabulary.sql"

    owners = load_owners(root)
    registry = load_registry(root)

    statements: list[str] = []
    statements.append("-- === Owners ===")
    statements.extend(build_owners(owners))
    statements.append("\n-- === Formats (+examples) ===")
    statements.extend(build_formats(root, registry))
    statements.append("\n-- === Enums (+versions, values) ===")
    statements.extend(build_enums(root, registry))
    statements.append("\n-- === Types (+versions, attributes, examples, axioms) ===")
    statements.extend(build_types(root, registry))

    out.write_text(HEADER + "\n" + "\n".join(statements) + FOOTER)
    print(f"wrote {out} ({len(statements)} statements)")


if __name__ == "__main__":
    main()
