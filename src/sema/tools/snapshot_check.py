"""Build-time samples generation + round-trip gate for a Sema snapshot.

Runs as a subprocess against a *staged* snapshot tree, so the generated package
(whose internal imports use the consumer's ``import_root``, e.g. ``gjk.sema``)
can be imported by name without polluting the build process. Invoked by
``sema.interfaces.cli.snapshot`` before the atomic swap:

    PYTHONPATH=<staged_parent>:<sema_src> python -m sema.tools.snapshot_check \
        --definitions <staged>/definitions \
        --samples     <staged>/samples \
        --import-root  gjk.sema

Two jobs, in order:

1. **Generate ``samples/``** — for every *type* version under ``definitions/``
   whose schema carries an ``examples:`` block, feed the first authored example
   through the snapshot codec (``from_dict -> to_dict``) and write the canonical
   serialized form. Filenames follow the Sema-typed-JSON convention with the
   version appended when the type is versioned (``<type.name>.<version>.json``;
   versionless ``<type.name>.json``). Old versions are included. A coverage
   report is written to ``samples/README.md``.

2. **Round-trip gate** — invoke the snapshot's own shipped ``roundtrip`` module
   over the freshly written samples. Exit non-zero on any failure so the caller
   leaves the previous snapshot untouched (a failed build is a no-op).

Samples are *types only*: only types are serialized between applications and
carry ``TypeName``/``Version``, so only a type has something to round-trip.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import yaml


def _iter_type_schemas(definitions_root: Path):
    """Yield (schema_dict, source_path) for every type schema file."""
    types_root = definitions_root / "types"
    for path in sorted(types_root.rglob("*.yaml")):
        yield yaml.safe_load(path.read_text()), path


def _sample_filename(type_name: str, version: str | None) -> str:
    if version is None:
        return f"{type_name}.json"
    return f"{type_name}.{version}.json"


def generate_samples(definitions_root: Path, samples_dir: Path, codec) -> dict:
    """Write one canonical sample per type version that has an example.

    Returns a coverage record: which type versions were seeded and which were
    skipped for lack of an example.
    """
    samples_dir.mkdir(parents=True, exist_ok=True)
    seeded: list[str] = []
    missing: list[str] = []

    for schema, _path in _iter_type_schemas(definitions_root):
        type_name = schema.get("title")
        examples = schema.get("examples") or []
        # Version is the const on the Version property (versioned types only).
        version = None
        version_prop = (schema.get("properties") or {}).get("Version")
        if isinstance(version_prop, dict) and "const" in version_prop:
            version = version_prop["const"]
        label = _sample_filename(type_name, version)

        if not examples:
            missing.append(label)
            continue

        example = json.loads(examples[0])
        # Canonicalize through the snapshot codec at the example's own version:
        # these are the exact bytes the runtime emits, so the sample doubles as
        # the round-trip's expected output and won't churn between regens.
        instance = codec.from_dict(example, mode="strict", auto_upgrade=False)
        canonical = instance.to_dict()
        out_path = samples_dir / label
        out_path.write_text(json.dumps(canonical, indent=2) + "\n")
        seeded.append(label)

    _write_readme(samples_dir, seeded, missing)
    return {"seeded": seeded, "missing": missing}


def _write_readme(samples_dir: Path, seeded: list[str], missing: list[str]) -> None:
    total = len(seeded) + len(missing)
    lines = [
        "# Samples",
        "",
        "Canonical JSON instances, one per seeded **type** version that carries",
        "an `examples:` block. Generated from the authored examples (never edited",
        "by hand) and consumed by `roundtrip.py`. A type version without a sample",
        "is silently untested by the round-trip, so its absence is recorded here.",
        "",
        f"Coverage: **{len(seeded)} of {total}** seeded type versions have a sample.",
        "",
    ]
    if missing:
        lines.append("Seeded type versions lacking a sample (no `examples:`):")
        lines.append("")
        for label in sorted(missing):
            lines.append(f"- `{label[:-5]}`")
        lines.append("")
    (samples_dir / "README.md").write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--definitions", required=True, type=Path)
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--import-root", required=True)
    args = parser.parse_args()

    codec_mod = importlib.import_module(f"{args.import_root}.codec")
    roundtrip_mod = importlib.import_module(f"{args.import_root}.roundtrip")

    coverage = generate_samples(args.definitions, args.samples, codec_mod.default_codec)
    print(
        f"Wrote {len(coverage['seeded'])} sample(s); "
        f"{len(coverage['missing'])} type version(s) lack an example."
    )

    failures = roundtrip_mod.run_roundtrip(args.samples)
    if failures:
        print(f"Round-trip FAILED for {len(failures)} sample(s):")
        for failure in failures:
            print(f"  - {failure.sample}: {failure.reason}")
        return 1
    print(f"Round-trip OK: {len(coverage['seeded'])} sample(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
