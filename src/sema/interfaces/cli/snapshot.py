from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from sema.tools.build_public_registry import (
    OUTPUT_PATH as PUBLIC_REGISTRY_PATH,
)
from sema.tools.build_public_registry import (
    build_public_registry,
)
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
from sema.tools.runtime_generation.helpers import render_local_names_yaml
from sema.tools.snapshot_lint import lint_generated_tree

# Files and directories the runtime generator owns inside a snapshot. Cleared
# and rewritten on every build; the prepared `definitions/` and `indexes/` are
# left alone.
_RUNTIME_FILES = (
    "__init__.py",
    "base.py",
    "codec.py",
    "property_format.py",
    "roundtrip.py",
)
_RUNTIME_DIRS = ("enums", "types", "samples", "tests")


_REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_clean_checkout() -> None:
    """Snapshot commands read committed registry state and write only under
    output/ — a snapshot must be reproducible from a commit hash, so running
    over uncommitted edits is refused. Silently skipped when git is
    unavailable (e.g. an installed package outside a checkout)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(_REPO_ROOT), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return
    if result.returncode != 0:
        return
    if result.stdout.strip():
        raise SystemExit(
            "sema checkout has uncommitted changes — snapshot commands run only\n"
            "from a clean checkout so the result is reproducible from a commit\n"
            "hash. Commit or stash first.\n"
            f"{result.stdout.rstrip()}"
        )


def snapshot_root() -> Path:
    return resolve_target_path("snapshot", str(OUTPUT_DIR))


STAGING_README_BANNER = """\
# STAGING SNAPSHOT — PLEASE ONLY USE IN DEV

This snapshot contains STAGING vocabulary: mutable words that run on dev
brokers only. It MUST NOT be used against hybrid or production brokers.

Staging words in this snapshot:

{words}

When these words promote to published, rebuild without `--allow-staged` to
get a publication-grade snapshot (and this file disappears).
"""


def _collect_staging_words(seed: dict, public_registry: dict) -> list[str]:
    """Every word/version in the expanded worklist whose status is staging.

    Formats are skipped — they never stage. Drafts cannot appear here: the
    public registry (which the expansion works from) excludes them entirely.
    """
    staging: list[str] = []
    worklist = seed.get("worklist", {})

    for name, spec in (worklist.get("enums", {}) or {}).items():
        entry = public_registry["enums"][name]
        if entry.get("enum_type") == "literal":
            if entry["status"] == "staging":
                staging.append(f"enum {name}")
            continue
        for version in spec:
            if entry["versions"][version]["status"] == "staging":
                staging.append(f"enum {name}:{version}")

    for name, spec in (worklist.get("types", {}) or {}).items():
        entry = public_registry["types"][name]
        if "path" in spec:  # versionless type
            if entry["status"] == "staging":
                staging.append(f"type {name}")
            continue
        for version in spec:
            if entry["versions"][version]["status"] == "staging":
                staging.append(f"type {name}:{version}")

    return sorted(staging)


def _validate_staging_closure(
    seed: dict, public_registry: dict, *, allow_staged: bool
) -> list[str]:
    """Published-only is the default: a staging closure refuses the
    prepare — BEFORE ``output/`` is touched, so a refusal leaves the
    previous snapshot intact. Returns the staging words for the marker
    write."""
    staging = _collect_staging_words(seed, public_registry)
    if staging and not allow_staged:
        raise ValueError(
            "Snapshot closure contains STAGING words (published-only is the "
            "default; pass --allow-staged to build a dev-only snapshot):\n  "
            + "\n  ".join(staging)
        )
    return staging


def _write_staging_markers(target_root: Path, staging: list[str]) -> None:
    """A staged snapshot is marked twice — machine-readably
    (``indexes/staging.yaml``) and for humans (a README banner at the
    snapshot root)."""
    if not staging:
        return
    with (target_root / "indexes" / "staging.yaml").open("w") as handle:
        yaml.safe_dump({"staging": True, "staging_words": staging}, handle)
    (target_root / "README.md").write_text(
        STAGING_README_BANNER.format(words="\n".join(f"- {word}" for word in staging))
    )
    print(f"STAGING snapshot ({len(staging)} staging words) — PLEASE ONLY USE IN DEV")


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


def prepare_snapshot(seed_request: Path, *, allow_staged: bool = False) -> Path:
    # Compute the public registry in memory. This validates:
    #   - status placement (word-level only on versionless / literal /
    #     formats; otherwise version-level)
    #   - published-vs-draft dependency closure (published SHALL NOT depend on
    #     draft, transitively or directly)
    # and raises ValueError if the registry is in an inconsistent state.
    # Nothing is written into the repo tree — indexes/public_registry.yaml is
    # scripts/build_indexes.sh's to regenerate. Because expand_seed reads the
    # committed indexes, refuse when they are stale against definitions/.
    public_registry = build_public_registry(load_registry())
    committed = (
        yaml.safe_load(PUBLIC_REGISTRY_PATH.open())
        if PUBLIC_REGISTRY_PATH.exists()
        else None
    )
    if committed != public_registry:
        raise ValueError(
            "indexes/public_registry.yaml is stale against definitions/registry.yaml"
            " — run scripts/build_indexes.sh, commit, and retry."
        )

    seed_request_path = seed_request.resolve()
    with seed_request_path.open() as handle:
        seed_request_data = yaml.safe_load(handle)
    _reject_drafts_in_seed_request(seed_request_data, public_registry)

    # Expand and validate BEFORE touching output/: a refused prepare must
    # leave the previous snapshot intact — a cleared-then-refused output/
    # silently guts whatever a consumer mirrors next (rsync --delete).
    with tempfile.TemporaryDirectory() as tmp_dir:
        expanded_tmp = Path(tmp_dir) / "seed_expanded.yaml"
        expand_seed(seed_request_path, expanded_tmp)
        seed = load_seed(expanded_tmp)
        staging = _validate_staging_closure(
            seed, public_registry, allow_staged=allow_staged
        )

        ensure_clean_dir(OUTPUT_DIR)
        target_root = snapshot_root()
        indexes_root = target_root / "indexes"
        expanded_seed = indexes_root / "seed_expanded.yaml"
        local_names = indexes_root / "local_names.yaml"
        indexes_root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(expanded_tmp, expanded_seed)

    # Record the original seed request alongside the expansion so the snapshot is
    # self-describing and exactly replicable. (Previously only the expanded seed
    # was kept, so the request that built a snapshot had to be reconstructed.)
    shutil.copyfile(seed_request_path, indexes_root / "seed_request.yaml")

    _write_staging_markers(target_root, staging)

    registry = load_registry()
    copy_seed_definitions(target_root, seed)
    restricted_registry = build_restricted_registry(seed, registry)
    write_restricted_registry(target_root, restricted_registry)
    write_restricted_indexes(target_root, restricted_registry)

    dag = build_seed_dag_from_data(seed, restricted_registry)

    # Local class/module names are declared in the seed request, not hand-edited:
    # `local_names.strip_prefixes` (e.g. [gw1, gw]) + per-type `overrides`.
    # Materialize the effective file here for build to consume.
    local_names_cfg = seed_request_data.get("local_names", {}) or {}
    render_local_names_yaml(
        dag,
        local_names,
        strip_prefixes=tuple(local_names_cfg.get("strip_prefixes", []) or []),
        overrides=local_names_cfg.get("overrides", {}) or {},
    )
    return target_root


def _clear_runtime_outputs(target_root: Path) -> None:
    for name in _RUNTIME_DIRS:
        path = target_root / name
        if path.exists():
            shutil.rmtree(path)
    for name in _RUNTIME_FILES:
        path = target_root / name
        if path.exists():
            path.unlink()


def _run_samples_and_roundtrip(
    staged_parent: Path, definitions_root: Path, samples_dir: Path, import_root: str
) -> None:
    """Generate ``samples/`` and run the round-trip gate in a subprocess.

    The staged package's internal imports use ``import_root`` (e.g. ``gjk.sema``),
    so it is importable only when ``staged_parent`` is on ``sys.path``. Running in
    a subprocess gives that import a clean process and isolates pydantic model
    registration from the build. A non-zero exit (round-trip failure) raises, so
    the caller aborts before touching the previous snapshot.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(staged_parent), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sema.tools.snapshot_check",
            "--definitions",
            str(definitions_root),
            "--samples",
            str(samples_dir),
            "--import-root",
            import_root,
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        raise RuntimeError(
            "Snapshot round-trip gate failed (snapshot left unchanged):\n"
            + result.stdout
            + result.stderr
        )


def _swap_runtime_into(target_root: Path, staged: Path) -> None:
    """Replace the runtime portion of ``target_root`` with the staged tree.

    Runs only after every gate is green, so a failed build never reaches here —
    the previous snapshot is left byte-for-byte unchanged on any gate failure.
    """
    _clear_runtime_outputs(target_root)
    for name in _RUNTIME_FILES:
        source = staged / name
        if source.exists():
            shutil.copy2(source, target_root / name)
    for name in _RUNTIME_DIRS:
        source = staged / name
        if source.exists():
            shutil.copytree(source, target_root / name)


def build_snapshot_runtime(package_name: str, *, strict_lint: bool = False) -> Path:
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

    # Generate into a staged tree, gate it there, and swap into place only on
    # green. The staged package lives at ``<tmp>/<package_name>/sema`` so its
    # ``import_root`` resolves for the round-trip subprocess. A failed gate is a
    # no-op: ``target_root`` is untouched until every gate passes.
    with tempfile.TemporaryDirectory() as tmp:
        staged_parent = Path(tmp)
        (staged_parent / package_name).mkdir(parents=True, exist_ok=True)
        (staged_parent / package_name / "__init__.py").write_text("")
        staged = staged_parent / package_name / "sema"
        staged.mkdir(parents=True, exist_ok=True)

        generate_runtime_from_dag(
            staged,
            seed,
            restricted_registry,
            import_root=import_root,
            local_names=local_names,
        )

        # ruff format (in place) + ruff check / mypy report. Format makes a
        # re-build a zero diff; check/mypy surface generator bugs.
        violations = lint_generated_tree(staged, strict=strict_lint)
        for violation in violations:
            print(f"[lint] {violation}")

        # Generate samples/ and run the per-type round-trip gate (the atn.bid
        # guard). Raises on failure, leaving the previous snapshot untouched.
        _run_samples_and_roundtrip(
            staged_parent,
            target_root / "definitions",
            staged / "samples",
            import_root,
        )

        _swap_runtime_into(target_root, staged)

    return target_root


def _run_prepare(args: argparse.Namespace) -> None:
    _ensure_clean_checkout()
    target_root = prepare_snapshot(
        Path(args.seed_request), allow_staged=args.allow_staged
    )
    print(f"Prepared snapshot at {target_root}")
    print(f"Expanded seed: {target_root / 'indexes' / 'seed_expanded.yaml'}")
    print(f"Local names: {target_root / 'indexes' / 'local_names.yaml'}")


def _run_build(args: argparse.Namespace) -> None:
    _ensure_clean_checkout()
    target_root = build_snapshot_runtime(
        args.package_name, strict_lint=args.strict_lint
    )
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
    prepare_parser.add_argument(
        "--allow-staged",
        action="store_true",
        help=(
            "Permit STAGING words in the closure (default: published-only). "
            "The result is a dev-only snapshot, marked in indexes/staging.yaml "
            "and by a README banner."
        ),
    )
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
    build_parser.add_argument(
        "--strict-lint",
        action="store_true",
        help=(
            "Treat ruff check / mypy findings on generated code as build "
            "failures (default: report only). ruff format always runs."
        ),
    )
    build_parser.set_defaults(handler=_run_build)
