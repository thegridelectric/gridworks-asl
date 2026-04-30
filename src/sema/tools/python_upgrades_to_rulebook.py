"""Extract version-upgrade chain from src/sema/runtime/{types,enums}/old_versions/*.py
into Module 2 of the rulebook.

Reads:
  src/sema/runtime/types/old_versions/*.py
  src/sema/runtime/enums/old_versions/*.py
  src/sema/runtime/types/*projection*.py

Writes:
  effortless-rulebook/effortless-rulebook.json — populates:
    Projections, ProjectionMappings,
    TypeUpgrades, TypeUpgradeOps,
    EnumUpgrades, EnumUpgradeMappings.

Op-classification follows the 12-op vocabulary from the migration plan.
Anything not matching falls back to a Custom op carrying the verbatim source as RawScript.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TYPES_OLD = ROOT / "src" / "sema" / "runtime" / "types" / "old_versions"
ENUMS_OLD = ROOT / "src" / "sema" / "runtime" / "enums" / "old_versions"
RUNTIME_TYPES = ROOT / "src" / "sema" / "runtime" / "types"
RULEBOOK_PATH = ROOT / "effortless-rulebook" / "effortless-rulebook.json"


CAMEL_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


def snake_to_pascal(snake: str) -> str:
    return "".join(p.capitalize() for p in snake.split("_"))


def filename_to_slugver(stem: str) -> tuple[str, str]:
    """e.g. 'ha1_params_004' -> ('ha1.params', '004')."""
    parts = stem.rsplit("_", 1)
    return parts[0].replace("_", "."), parts[1]


# ------------------------------------------------------------- AST helpers


def find_class_def(tree: ast.Module, name_endings: tuple[str, ...] = ()) -> ast.ClassDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if not name_endings or any(node.name.endswith(s) for s in name_endings):
                return node
    return None


def find_method(cls: ast.ClassDef, name: str) -> ast.FunctionDef | None:
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def get_docstring(node: ast.AST) -> str | None:
    return ast.get_docstring(node)


def to_source(node: ast.AST) -> str:
    return ast.unparse(node)


def returns_target_class(method: ast.FunctionDef) -> str | None:
    if isinstance(method.returns, ast.Name):
        return method.returns.id
    if isinstance(method.returns, ast.Constant) and isinstance(method.returns.value, str):
        return method.returns.value
    return None


def find_target_version_in_body(method: ast.FunctionDef) -> str | None:
    """Look for `data["version"] = "NNN"`."""
    for node in ast.walk(method):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Subscript)
            and isinstance(node.targets[0].value, ast.Name)
            and node.targets[0].value.id == "data"
            and isinstance(node.targets[0].slice, ast.Constant)
            and node.targets[0].slice.value == "version"
            and isinstance(node.value, ast.Constant)
        ):
            return node.value.value
    return None


# --------------------------------------------------- Per-statement op classifier


BOILERPLATE = object()  # sentinel: statement is boilerplate, not an op, and not unrecognized


def classify_statement(stmt: ast.AST) -> dict[str, Any] | object | None:
    """Return an op dict for a recognized pattern, BOILERPLATE if known-skip, or None if unrecognized."""
    if isinstance(stmt, ast.Assign):
        # data["version"] = "..."  → boilerplate
        # data = self.model_dump()  → boilerplate
        if (
            len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Subscript)
            and isinstance(stmt.targets[0].value, ast.Name)
            and stmt.targets[0].value.id == "data"
            and isinstance(stmt.targets[0].slice, ast.Constant)
            and stmt.targets[0].slice.value == "version"
        ):
            return BOILERPLATE
        if (
            len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and stmt.targets[0].id == "data"
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and stmt.value.func.attr == "model_dump"
        ):
            return BOILERPLATE
        # data["X"] = <something>  → real op
        if (
            len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Subscript)
            and isinstance(stmt.targets[0].value, ast.Name)
            and stmt.targets[0].value.id == "data"
            and isinstance(stmt.targets[0].slice, ast.Constant)
        ):
            field = stmt.targets[0].slice.value
            return _classify_assign_to_field(field, stmt.value)

    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        # data.pop("X", None) as a bare expression
        call = stmt.value
        if (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "data"
            and call.func.attr == "pop"
            and call.args
            and isinstance(call.args[0], ast.Constant)
        ):
            return {"OpKind": "Remove", "FieldName": call.args[0].value}

    if isinstance(stmt, ast.Return):
        # boilerplate `return X.model_validate(data)`
        if (
            isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and stmt.value.func.attr == "model_validate"
        ):
            return BOILERPLATE

    if isinstance(stmt, ast.If):
        return _classify_if(stmt)

    return None  # let caller decide if it's Custom-worthy


def _classify_assign_to_field(field: str, expr: ast.AST) -> dict[str, Any] | None:
    pascal_field = snake_to_pascal(field)

    # data["X"] = literal  → AddWithDefault
    if isinstance(expr, ast.Constant):
        return {"OpKind": "AddWithDefault", "FieldName": pascal_field,
                "LiteralValue": json.dumps(expr.value)}

    # data["X"] = self.X.upgrade()  → UpgradeChild
    if (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Attribute)
        and expr.func.attr == "upgrade"
        and isinstance(expr.func.value, ast.Attribute)
        and isinstance(expr.func.value.value, ast.Name)
        and expr.func.value.value.id == "self"
    ):
        return {"OpKind": "UpgradeChild", "FieldName": pascal_field}

    # data["X"] = [item.upgrade() for item in self.X]   → UpgradeListItems
    # data["X"] = [item.upgrade() if item.version == "V" else item for item in self.X]
    if isinstance(expr, ast.ListComp) and len(expr.generators) == 1:
        gen = expr.generators[0]
        if (
            isinstance(gen.iter, ast.Attribute)
            and isinstance(gen.iter.value, ast.Name)
            and gen.iter.value.id == "self"
        ):
            elt = expr.elt
            # plain item.upgrade()
            if (
                isinstance(elt, ast.Call)
                and isinstance(elt.func, ast.Attribute)
                and elt.func.attr == "upgrade"
            ):
                return {"OpKind": "UpgradeListItems", "FieldName": pascal_field}
            # conditional: item.upgrade() if item.version == "V" else item
            if isinstance(elt, ast.IfExp):
                v = _extract_version_compare(elt.test)
                if v is not None and isinstance(elt.body, ast.Call) and \
                   isinstance(elt.body.func, ast.Attribute) and elt.body.func.attr == "upgrade":
                    return {"OpKind": "UpgradeListItemsIf",
                            "FieldName": pascal_field, "FromVersion": v}

    # data["X"] = SomethingProjection.project(...)  → AddProjected
    if (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Attribute)
        and expr.func.attr == "project"
        and isinstance(expr.func.value, ast.Name)
        and "Projection" in expr.func.value.id
    ):
        return {"OpKind": "AddProjected", "FieldName": pascal_field,
                "ProjectionRef": expr.func.value.id}

    # data["X"] = SomeEnum[self.X.name].value  → CoerceToEnum (string → enum value)
    # data["X"] = SomeEnum[data["X"]] (etc.) — heuristic match by name pattern
    if (
        isinstance(expr, ast.Attribute)
        and expr.attr == "value"
        and isinstance(expr.value, ast.Subscript)
        and isinstance(expr.value.value, ast.Name)
    ):
        return {"OpKind": "CoerceToEnum", "FieldName": pascal_field,
                "EnumVersionRefName": expr.value.value.id}

    return None  # caller may emit Custom


def _classify_if(if_stmt: ast.If) -> dict[str, Any] | None:
    """if self.X.version == 'V': data['X'] = self.X.upgrade()  → UpgradeChildIf"""
    if (
        isinstance(if_stmt.test, ast.Compare)
        and len(if_stmt.test.ops) == 1
        and isinstance(if_stmt.test.ops[0], ast.Eq)
        and isinstance(if_stmt.test.left, ast.Attribute)
        and if_stmt.test.left.attr == "version"
        and isinstance(if_stmt.test.left.value, ast.Attribute)
        and isinstance(if_stmt.test.left.value.value, ast.Name)
        and if_stmt.test.left.value.value.id == "self"
        and len(if_stmt.test.comparators) == 1
        and isinstance(if_stmt.test.comparators[0], ast.Constant)
        and len(if_stmt.body) == 1
    ):
        version = if_stmt.test.comparators[0].value
        attr_name = if_stmt.test.left.value.attr
        body = if_stmt.body[0]
        if (
            isinstance(body, ast.Assign)
            and isinstance(body.value, ast.Call)
            and isinstance(body.value.func, ast.Attribute)
            and body.value.func.attr == "upgrade"
        ):
            return {"OpKind": "UpgradeChildIf",
                    "FieldName": snake_to_pascal(attr_name),
                    "FromVersion": version}
    return None


def _extract_version_compare(test: ast.AST) -> str | None:
    """Extract V from `item.version == 'V'`."""
    if (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and isinstance(test.left, ast.Attribute)
        and test.left.attr == "version"
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
    ):
        return test.comparators[0].value
    return None


# ------------------------------------------------------------- Per-file extract


def extract_type_upgrade(path: Path, warnings: list[str]) -> dict[str, Any] | None:
    src = path.read_text()
    tree = ast.parse(src)
    cls = find_class_def(tree)
    if cls is None:
        return None
    method = find_method(cls, "upgrade")
    if method is None:
        return None

    from_slug, from_ver = filename_to_slugver(path.stem)
    to_class = returns_target_class(method)
    to_ver = find_target_version_in_body(method) or ""
    to_slug = from_slug
    target_v_match = re.search(r"(\d{3})$", to_class or "")
    if to_class and target_v_match:
        target_v = target_v_match.group(1)
        # Strip "NNN" suffix → CamelCase class name → slug heuristic
        base = (to_class or "")[: -len(target_v)]
        to_ver = to_ver or target_v
    elif to_class:
        # current-version target (e.g. DataChannelGt)
        to_ver = to_ver or _next_version(from_ver)

    docstring = get_docstring(method) or ""

    ops: list[dict[str, Any]] = []
    custom_blocks: list[str] = []
    pending_custom: list[ast.AST] = []

    for stmt in method.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) \
           and isinstance(stmt.value.value, str):
            continue  # docstring
        op = classify_statement(stmt)
        if op is BOILERPLATE:
            continue
        if isinstance(op, dict):
            ops.append(op)
        else:
            pending_custom.append(stmt)

    if pending_custom:
        body_src = "\n".join(to_source(s) for s in pending_custom)
        ops.append({"OpKind": "Custom", "RawScript": body_src})
        warnings.append(f"CustomFallback: {path.name}")

    return {
        "FromTypeVersion": f"{from_slug}/{from_ver}",
        "ToTypeVersion": f"{to_slug}/{to_ver}",
        "Description": _first_line(docstring),
        "Ops": ops,
    }


def _next_version(v: str) -> str:
    try:
        return f"{int(v)+1:03d}"
    except ValueError:
        return ""


def _first_line(s: str) -> str:
    for line in s.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _is_pure_boilerplate(src: str) -> bool:
    stripped = re.sub(r"\s+", " ", src).strip()
    return stripped in {
        "data = self.model_dump()",
        "return data",
    }


# ------------------------------------------------------------- Projections


def extract_projection(path: Path) -> dict[str, Any] | None:
    src = path.read_text()
    tree = ast.parse(src)
    cls = find_class_def(tree)
    if cls is None or "Projection" not in cls.name:
        return None

    # Find the module-level dict (e.g. _PROJECTION = {...})
    mapping: dict[str, str] = {}
    from_enum_class: str | None = None
    to_enum_class: str | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Attribute) and isinstance(v, ast.Attribute):
                    from_enum_class = from_enum_class or _name_of(k.value)
                    to_enum_class = to_enum_class or _name_of(v.value)
                    mapping[k.attr] = v.attr
            if mapping:
                break

    return {
        "Name": cls.name,
        "FromEnumClass": from_enum_class,
        "ToEnumClass": to_enum_class,
        "Mappings": mapping,
        "Description": (get_docstring(cls) or _first_line(get_docstring(tree) or ""))[:200],
    }


def _name_of(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


# ------------------------------------------------------------- Driver


def populate_rulebook(
    type_upgrades: list[dict[str, Any]],
    projections: list[dict[str, Any]],
    enum_upgrades: list[dict[str, Any]],
) -> dict[str, Any]:
    rulebook = json.loads(RULEBOOK_PATH.read_text())

    # Projections
    proj_rows: list[dict[str, Any]] = []
    pmap_rows: list[dict[str, Any]] = []
    for p in projections:
        proj_rows.append({
            "Name": p["Name"],
            "Description": p["Description"],
            "FromEnumVersion": p.get("FromEnumVersion"),
            "ToEnumVersion": p.get("ToEnumVersion"),
            "RawScript": None if p["Mappings"] else p.get("RawScript"),
        })
        for k, v in p["Mappings"].items():
            pmap_rows.append({
                "Projection": p["Name"], "FromSymbol": k, "ToSymbol": v,
                "Description": None,
            })
    rulebook["Projections"]["data"] = proj_rows
    rulebook["ProjectionMappings"]["data"] = pmap_rows

    # TypeUpgrades / TypeUpgradeOps
    upgrade_rows: list[dict[str, Any]] = []
    op_rows: list[dict[str, Any]] = []
    for upgr in type_upgrades:
        from_tv = upgr["FromTypeVersion"]
        to_tv = upgr["ToTypeVersion"]
        upgrade_rows.append({
            "FromTypeVersion": from_tv, "ToTypeVersion": to_tv,
            "Description": upgr["Description"], "RawScript": None,
        })
        upgrade_key = f"{from_tv} -> {to_tv}"
        for idx, op in enumerate(upgr["Ops"]):
            row = {
                "TypeUpgrade": upgrade_key, "Idx": idx,
                "OpKind": op["OpKind"],
                "FieldName": op.get("FieldName"),
                "LiteralValue": op.get("LiteralValue"),
                "FromVersion": op.get("FromVersion"),
                "ToVersion": op.get("ToVersion"),
                "EnumVersionRef": None,
                "ProjectionRef": op.get("ProjectionRef"),
                "RawScript": op.get("RawScript"),
                "Description": None,
            }
            op_rows.append(row)
    rulebook["TypeUpgrades"]["data"] = upgrade_rows
    rulebook["TypeUpgradeOps"]["data"] = op_rows

    # EnumUpgrades stay empty for now
    rulebook["EnumUpgrades"]["data"] = []
    rulebook["EnumUpgradeMappings"]["data"] = []

    meta = rulebook.setdefault("_meta", {}).setdefault("_conversion_metadata", {})
    meta["module_2_row_counts"] = {
        "Projections": len(proj_rows),
        "ProjectionMappings": len(pmap_rows),
        "TypeUpgrades": len(upgrade_rows),
        "TypeUpgradeOps": len(op_rows),
    }
    return rulebook


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print summary; do not write the rulebook.")
    args = parser.parse_args(argv)

    warnings: list[str] = []

    type_upgrades: list[dict[str, Any]] = []
    for p in sorted(TYPES_OLD.glob("*.py")):
        if p.stem == "__init__":
            continue
        upgr = extract_type_upgrade(p, warnings)
        if upgr is not None:
            type_upgrades.append(upgr)

    enum_upgrades: list[dict[str, Any]] = []
    for p in sorted(ENUMS_OLD.glob("*.py")):
        if p.stem == "__init__":
            continue
        # enum upgrades typically don't have an upgrade() method body —
        # they're version-bumps without value renames. Capture the (from, to) shell.
        from_slug, from_ver = filename_to_slugver(p.stem)
        to_ver = _next_version(from_ver)
        enum_upgrades.append({
            "FromEnumVersion": f"{from_slug}/{from_ver}",
            "ToEnumVersion": f"{from_slug}/{to_ver}",
            "Description": f"Enum version bump from {from_ver} to {to_ver}",
        })

    projections: list[dict[str, Any]] = []
    for p in sorted(RUNTIME_TYPES.glob("*projection*.py")):
        proj = extract_projection(p)
        if proj is not None:
            projections.append(proj)

    op_kind_counts: dict[str, int] = {}
    total_ops = 0
    for upgr in type_upgrades:
        for op in upgr["Ops"]:
            op_kind_counts[op["OpKind"]] = op_kind_counts.get(op["OpKind"], 0) + 1
            total_ops += 1

    print("=== Module 2 extraction summary ===")
    print(f"TypeUpgrades:        {len(type_upgrades)}")
    print(f"  Total ops:          {total_ops}")
    print(f"  By OpKind:")
    for kind, count in sorted(op_kind_counts.items()):
        print(f"    {kind:20s} {count}")
    decl_count = total_ops - op_kind_counts.get("Custom", 0)
    if total_ops:
        pct = 100.0 * decl_count / total_ops
        print(f"  Declarative coverage: {decl_count}/{total_ops} ({pct:.1f}%)")
    print(f"EnumUpgrades:        {len(enum_upgrades)} (shells, no value renames)")
    print(f"Projections:         {len(projections)}")
    print(f"  Mappings total:     {sum(len(p['Mappings']) for p in projections)}")
    print()
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  - {w}")

    if args.dry_run:
        return 0

    rulebook = populate_rulebook(type_upgrades, projections, enum_upgrades)
    RULEBOOK_PATH.write_text(json.dumps(rulebook, indent=2) + "\n")
    print(f"\nWrote {RULEBOOK_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
