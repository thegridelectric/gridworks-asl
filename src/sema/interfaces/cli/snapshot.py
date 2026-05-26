from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml

from sema.tools.build_public_registry import build as build_public_registry_index
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


def snapshot_root() -> Path:
    return resolve_target_path("snapshot", str(OUTPUT_DIR))


def _write_local_names_yaml(dag, path: Path) -> None:
    data: dict[str, dict[str, str]] = {
        "types": {},
        "enums": {},
    }

    for kind, name, _version in sorted(dag.nodes):
        if kind == "format":
            continue
        section = f"{kind}s"
        data[section][name] = name

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        yaml.safe_dump(data, handle, sort_keys=True)


def _reject_drafts_in_seed_request(seed_request: dict, public_registry: dict) -> None:
    """Fail if the seed REQUEST directly names a draft (or unknown) word.

    Active words are closed under dependency by registry-side validation, so
    drafts can only enter a snapshot via direct selection in the request.
    Catching that here gives a clear error before ``expand_seed`` runs.
    """
    missing: list[str] = []
    targets = seed_request.get("initial_targets", {}) or {}

    for name in targets.get("formats", {}) or {}:
        if name not in public_registry["formats"]:
            missing.append(f"format {name}")

    for name, spec in (targets.get("enums", {}) or {}).items():
        public_enum = public_registry["enums"].get(name)
        if public_enum is None:
            missing.append(f"enum {name}")
            continue
        if public_enum.get("enum_type") == "literal":
            continue
        requested_versions = (spec or {}).get("versions") or []
        for version in requested_versions:
            if version not in public_enum.get("versions", {}):
                missing.append(f"enum {name}:{version}")

    for name, spec in (targets.get("types", {}) or {}).items():
        public_type = public_registry["types"].get(name)
        if public_type is None:
            missing.append(f"type {name}")
            continue
        if public_type.get("versioning_strategy") == "none":
            continue
        requested_versions = (spec or {}).get("versions") or []
        for version in requested_versions:
            if version not in public_type.get("versions", {}):
                missing.append(f"type {name}:{version}")

    if missing:
        raise ValueError(
            "Snapshot seed_request references draft (or unknown) words/versions:\n  "
            + "\n  ".join(sorted(missing))
        )


def prepare_snapshot(seed_request: Path) -> Path:
    # Regenerate indexes/public_registry.yaml first. This validates:
    #   - status placement (word-level only on versionless / literal /
    #     formats; otherwise version-level)
    #   - published-vs-draft dependency closure (published SHALL NOT depend on
    #     draft, transitively or directly)
    # and raises ValueError if the registry is in an inconsistent state.
    public_registry = build_public_registry_index()

    seed_request_path = seed_request.resolve()
    with seed_request_path.open() as handle:
        seed_request_data = yaml.safe_load(handle)
    _reject_drafts_in_seed_request(seed_request_data, public_registry)

    ensure_clean_dir(OUTPUT_DIR)
    target_root = snapshot_root()
    indexes_root = target_root / "indexes"
    expanded_seed = indexes_root / "seed_expanded.yaml"
    local_names = indexes_root / "local_names.yaml"

    expand_seed(seed_request_path, expanded_seed)

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
    for name in ("enums", "types", "tests"):
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
    import_root = f"{package_name}.sema"
    _clear_runtime_outputs(target_root)
    generate_runtime_from_dag(
        target_root,
        seed,
        restricted_registry,
        import_root=import_root,
        local_names=local_names,
        write_tests=True,
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
