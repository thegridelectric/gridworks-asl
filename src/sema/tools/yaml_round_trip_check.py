"""Golden test: compare definitions/ (source) against definitions-emitted/ (round-tripped).

For each YAML file present in BOTH trees, parses both with safe_load and reports
structural differences. Comments and whitespace are not preserved on round-trip;
this test asserts canonical-equivalence of the modeled content only.

Run:
  python -m sema.tools.yaml_to_rulebook && \
  python -m sema.tools.rulebook_to_yaml && \
  python -m sema.tools.yaml_round_trip_check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "definitions"
EMIT_DIR = ROOT / "definitions-emitted"


def normalize(obj: Any) -> Any:
    """Canonical form: dicts → sorted-key dicts, strings → stripped+normalized whitespace.

    Strings that look like JSON (the `- |` block-literal pattern) are decoded so
    they compare equal to the corresponding dict/list. Numeric-string-vs-number
    pairs are unified so '0' compares equal to 0 (the YAML default-emit ambiguity).
    """
    if isinstance(obj, dict):
        return {k: normalize(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return [normalize(x) for x in obj]
    if isinstance(obj, str):
        s = obj.strip()
        # If the string parses as JSON to a dict/list, recurse on the parsed value.
        if s.startswith(("{", "[")):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, (dict, list)):
                    return normalize(parsed)
            except json.JSONDecodeError:
                pass
        return " ".join(obj.split()).strip()
    return obj


def diff_paths(a: Any, b: Any, path: str = "") -> list[str]:
    """Walk two normalized objects and yield paths where they differ."""
    if type(a) is not type(b):
        return [f"{path}: type mismatch — {type(a).__name__} vs {type(b).__name__} (a={a!r:.40}, b={b!r:.40})"]
    if isinstance(a, dict):
        diffs: list[str] = []
        a_keys = set(a.keys())
        b_keys = set(b.keys())
        for k in sorted(a_keys - b_keys):
            diffs.append(f"{path}.{k}: only in source")
        for k in sorted(b_keys - a_keys):
            diffs.append(f"{path}.{k}: only in emitted")
        for k in sorted(a_keys & b_keys):
            diffs.extend(diff_paths(a[k], b[k], f"{path}.{k}"))
        return diffs
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{path}: list length {len(a)} vs {len(b)}"]
        diffs: list[str] = []
        for i, (x, y) in enumerate(zip(a, b)):
            diffs.extend(diff_paths(x, y, f"{path}[{i}]"))
        return diffs
    if a != b:
        return [f"{path}: value differs — source={a!r:.80} emitted={b!r:.80}"]
    return []


def compare_file(rel: Path, ctx_warnings: list[str]) -> tuple[bool, list[str]]:
    src = SOURCE_DIR / rel
    emt = EMIT_DIR / rel
    if not src.exists():
        return False, [f"{rel}: missing in source"]
    if not emt.exists():
        return False, [f"{rel}: missing in emitted"]
    try:
        src_doc = yaml.safe_load(src.read_text())
    except yaml.YAMLError as e:
        ctx_warnings.append(f"{rel}: source parse error — {e}")
        return False, []
    try:
        emt_doc = yaml.safe_load(emt.read_text())
    except yaml.YAMLError as e:
        return False, [f"{rel}: emitted parse error — {e}"]
    diffs = diff_paths(normalize(src_doc), normalize(emt_doc))
    return (len(diffs) == 0), diffs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10,
                        help="Max number of failing files to show diffs for (default 10).")
    parser.add_argument("--filter", type=str, default=None,
                        help="Only run files whose path contains this substring.")
    args = parser.parse_args(argv)

    if not EMIT_DIR.exists():
        print(f"ERROR: {EMIT_DIR} does not exist. Run rulebook-to-yaml first.", file=sys.stderr)
        return 2

    yaml_files: list[Path] = []
    for sub in ("formats", "enums", "types"):
        for p in (SOURCE_DIR / sub).rglob("*.yaml"):
            yaml_files.append(p.relative_to(SOURCE_DIR))
    yaml_files.append(Path("owners.yaml"))
    yaml_files.sort()

    if args.filter:
        yaml_files = [p for p in yaml_files if args.filter in str(p)]

    ctx_warnings: list[str] = []
    pass_count = 0
    fail_count = 0
    failures: list[tuple[Path, list[str]]] = []

    for rel in yaml_files:
        ok, diffs = compare_file(rel, ctx_warnings)
        if ok:
            pass_count += 1
        else:
            fail_count += 1
            if diffs:
                failures.append((rel, diffs))

    total = pass_count + fail_count
    pct = (100.0 * pass_count / total) if total else 0
    print(f"=== Round-trip golden test ===")
    print(f"Files checked: {total}")
    print(f"  pass: {pass_count}  fail: {fail_count}  ({pct:.1f}% pass)")
    print()
    if ctx_warnings:
        print(f"Source-parse warnings: {len(ctx_warnings)}")
        for w in ctx_warnings:
            print(f"  - {w}")
        print()

    if failures:
        print(f"--- Showing first {min(args.limit, len(failures))} failing files ---")
        for rel, diffs in failures[:args.limit]:
            print(f"\n## {rel}  ({len(diffs)} diffs)")
            for d in diffs[:8]:
                print(f"  {d}")
            if len(diffs) > 8:
                print(f"  ... ({len(diffs) - 8} more)")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
