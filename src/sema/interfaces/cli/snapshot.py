from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml

from sema.tools.build_seed_dag import build_seed_dag_from_data
from sema.tools.build_seed_definitions import (
    OUTPUT_DIR,
    build_restricted_registry,
    copy_seed_definitions,
    ensure_clean_dir,
    load_registry,
    load_seed,
    resolve_target_path,
    validate_package_name,
    write_restricted_indexes,
    write_restricted_registry,
)
from sema.tools.build_seed_expanded import expand_seed
from sema.tools.runtime_generation.generate_runtime import generate_runtime_from_dag
from sema.tools.runtime_generation.helpers import default_local_class_name


def snapshot_root() -> Path:
    return resolve_target_path("snapshot", str(OUTPUT_DIR))


def _write_local_names_yaml(dag, path: Path) -> None:
    data: dict[str, dict[str, dict[str, str]]] = {
        "types": {},
        "enums": {},
    }

    for kind, name, _version in sorted(dag.nodes):
        if kind == "format":
            continue
        section = f"{kind}s"
        data[section][name] = {
            "local_class_name": default_local_class_name(name)
        }

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        yaml.safe_dump(data, handle, sort_keys=True)


def prepare_snapshot(seed_request: Path) -> Path:
    ensure_clean_dir(OUTPUT_DIR)
    target_root = snapshot_root()
    indexes_root = target_root / "indexes"
    expanded_seed = indexes_root / "seed_expanded.yaml"
    local_names = indexes_root / "local_names.yaml"

    expand_seed(seed_request.resolve(), expanded_seed)

    seed = load_seed(expanded_seed)
    registry = load_registry()
    copy_seed_definitions(target_root, seed)
    restricted_registry = build_restricted_registry(seed, registry)
    write_restricted_registry(target_root, restricted_registry)
    write_restricted_indexes(target_root, restricted_registry)

    dag = build_seed_dag_from_data(seed, restricted_registry)
    _write_local_names_yaml(dag, local_names)
    return target_root


def _clear_runtime_outputs(target_root: Path) -> None:
    for name in ("enums", "types", "tests", "logic"):
        path = target_root / name
        if path.exists():
            shutil.rmtree(path)
    for name in ("__init__.py", "base.py", "codec.py", "property_format.py"):
        path = target_root / name
        if path.exists():
            path.unlink()


def build_snapshot_runtime(package_name: str) -> Path:
    package_name = validate_package_name(package_name)
    target_root = snapshot_root()
    expanded_seed = target_root / "indexes" / "seed_expanded.yaml"
    local_names = target_root / "indexes" / "local_names.yaml"
    if not expanded_seed.exists():
        raise ValueError(
            "Missing output/sema/indexes/seed_expanded.yaml. "
            "Run `uv run sema snapshot prepare <seed.yaml>` first."
        )

    seed = load_seed(expanded_seed)
    restricted_registry = load_seed(target_root / "definitions" / "registry.yaml")
    _clear_runtime_outputs(target_root)
    generate_runtime_from_dag(
        target_root,
        seed,
        restricted_registry,
        target_root / "definitions",
        package_name,
        local_names,
    )
    return target_root


def _run_prepare(args: argparse.Namespace) -> None:
    target_root = prepare_snapshot(Path(args.seed_request))
    print(f"Prepared snapshot at {target_root}")
    print(f"Expanded seed: {target_root / 'indexes' / 'seed_expanded.yaml'}")
    print(f"Local names: {target_root / 'indexes' / 'local_names.yaml'}")


def _run_build(args: argparse.Namespace) -> None:
    target_root = build_snapshot_runtime(args.package_name)
    print(f"Built snapshot runtime at {target_root}")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "snapshot",
        help="Prepare and build a complete Sema snapshot runtime.",
        description=(
            "Use `prepare` with a structured seed request YAML, then edit "
            "output/sema/indexes/local_names.yaml if needed, then use `build` "
            "with --package-name to generate runtime imports. Use "
            "template_seed_request.yaml at the repository root as a starting point."
        ),
    )
    snapshot_subparsers = parser.add_subparsers(dest="snapshot_command", required=True)

    prepare_parser = snapshot_subparsers.add_parser(
        "prepare",
        help="Expand a seed request and write definitions, indexes, and local names.",
        description=(
            "Read a structured seed request YAML, expand the transitive closure, "
            "clear output/, mirror seed-scoped definitions under "
            "output/sema/definitions, write restricted indexes under "
            "output/sema/indexes, and create output/sema/indexes/local_names.yaml. "
            "Use template_seed_request.yaml at the repository root as a starting point."
        ),
    )
    prepare_parser.add_argument("seed_request")
    prepare_parser.set_defaults(handler=_run_prepare)

    build_parser = snapshot_subparsers.add_parser(
        "build",
        help="Generate runtime files from a prepared snapshot.",
        description=(
            "Read output/sema/indexes/seed_expanded.yaml and "
            "output/sema/indexes/local_names.yaml, then generate runtime files under "
            "output/sema. The package name is used for generated imports."
        ),
    )
    build_parser.add_argument("--package-name", required=True)
    build_parser.set_defaults(handler=_run_build)
