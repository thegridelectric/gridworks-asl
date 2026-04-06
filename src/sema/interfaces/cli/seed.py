from __future__ import annotations

import argparse
from pathlib import Path

from sema.tools.build_seed_expanded import expand_seed, resolve_output_name
from sema.tools.build_seed_snapshot import (
    build_restricted_registry,
    copy_seed_definitions,
    load_seed,
    load_registry,
    resolve_target_path,
    validate_package_name,
    write_restricted_indexes,
    write_restricted_registry,
    write_snapshot_readme,
)


def _run_expand(args: argparse.Namespace) -> None:
    expand_seed(Path(args.seed_request).resolve(), resolve_output_name(args.out))


def _run_mirror(args: argparse.Namespace) -> None:
    seed = load_seed(Path(args.seed_expanded).resolve())
    package_name = validate_package_name(args.package_name)
    target_path = resolve_target_path(package_name, args.target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    copy_seed_definitions(target_path, seed)
    restricted_registry = build_restricted_registry(seed, load_registry())
    write_restricted_registry(target_path, restricted_registry)
    write_restricted_indexes(target_path, restricted_registry)
    write_snapshot_readme(target_path, seed)
    print(f"Built seed snapshot at {target_path}")
    print(f"Selection source: {args.seed_expanded}")


def _run_sync(args: argparse.Namespace) -> None:
    seed_request = Path(args.seed_request).resolve()
    out_path = resolve_output_name(args.out if args.out else "seed_expanded.yaml")
    expand_seed(seed_request, out_path)
    seed = load_seed(out_path)
    package_name = validate_package_name(args.package_name)
    target_path = resolve_target_path(package_name, args.target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    copy_seed_definitions(target_path, seed)
    restricted_registry = build_restricted_registry(seed, load_registry())
    write_restricted_registry(target_path, restricted_registry)
    write_restricted_indexes(target_path, restricted_registry)
    write_snapshot_readme(target_path, seed)
    print(f"Built seed snapshot at {target_path}")
    print(f"Selection source: {out_path}")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    seed_parser = subparsers.add_parser(
        "seed",
        help="Expand seed requests and build seed-scoped definition snapshots.",
        description=(
            "Seed tooling for building a generated seed/worklist from a small request file "
            "and writing a seed-scoped definitions snapshot into another package."
        ),
    )
    seed_subparsers = seed_parser.add_subparsers(dest="seed_command", required=True)

    expand_parser = seed_subparsers.add_parser(
        "expand",
        help="Expand a small seed request into a generated seed/worklist YAML.",
        description=(
            "Read a small YAML request containing initial_targets, validate each target "
            "against definitions/registry.yaml, compute typed transitive closure using "
            "indexes/dependency_closure.yaml, include any registry-declared intermediate "
            "type versions needed to keep upgrade chains complete, resolve local schema "
            "paths using indexes/lookup.yaml, and write a generated seed/worklist YAML."
        ),
        epilog=(
            "Example:\n"
            "  sema seed expand src/sema/tools/templates/seed_request_template.yaml "
            "--out seed_expanded.yaml\n\n"
            "The output is written under output/.\n\n"
            "Then mirror it with:\n"
            "  sema seed mirror output/seed_expanded.yaml "
            "--package-name gw_data"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    expand_parser.add_argument("seed_request")
    expand_parser.add_argument("--out", required=True)
    expand_parser.set_defaults(handler=_run_expand)

    mirror_parser = seed_subparsers.add_parser(
        "mirror",
        help="Mirror a generated seed/worklist into a target snapshot package.",
        description=(
            "Read a generated seed/worklist YAML and build a seed-scoped snapshot package "
            "containing restricted definitions/, registry.yaml, indexes/, and README.md. "
            "If --target-path is omitted, the snapshot "
            "is written to output/<package-name>/."
        ),
        epilog=(
            "Example:\n"
            "  sema seed mirror output/seed_expanded.yaml "
            "--package-name gw_data "
            "--target-path ../gridworks-data/src/gw_data/sema\n\n"
            "If --target-path is omitted, the mirror is written under output/<package-name>/.\n\n"
            "Generate that file first with:\n"
            "  sema seed expand src/sema/tools/templates/seed_request_template.yaml "
            "--out seed_expanded.yaml"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mirror_parser.add_argument("seed_expanded")
    mirror_parser.add_argument("--package-name", required=True)
    mirror_parser.add_argument("--target-path")
    mirror_parser.add_argument(
        "--source",
        default=str(Path(__file__).resolve().parents[2] / "runtime"),
    )
    mirror_parser.set_defaults(handler=_run_mirror)

    sync_parser = seed_subparsers.add_parser(
        "sync",
        help="Expand a seed request and then mirror it in one step.",
        description=(
            "Run seed expand and then seed mirror in one command. This reads a small "
            "seed request, writes a generated seed/worklist YAML, and then builds a "
            "seed-scoped snapshot package containing restricted definitions/, registry.yaml, "
            "indexes/, and README.md. If --target-path "
            "is omitted, the snapshot is written to output/<package-name>/."
        ),
        epilog=(
            "Example:\n"
            "  sema seed sync src/sema/tools/templates/seed_request_template.yaml "
            "--package-name gw_data "
            "--target-path ../gridworks-data/src/gw_data/sema\n\n"
            "If --target-path is omitted, this writes output/seed_expanded.yaml and "
            "mirrors into output/<package-name>/."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sync_parser.add_argument("seed_request")
    sync_parser.add_argument("--package-name", required=True)
    sync_parser.add_argument("--target-path")
    sync_parser.add_argument("--out")
    sync_parser.add_argument(
        "--source",
        default=str(Path(__file__).resolve().parents[2] / "runtime"),
    )
    sync_parser.set_defaults(handler=_run_sync)
