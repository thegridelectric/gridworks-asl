from pathlib import Path

from sema.tools.build_seed_expanded import expand_seed
from sema.tools.build_seed_snapshot import (
    build_restricted_registry,
    copy_seed_definitions,
    load_registry,
    load_seed,
    write_restricted_indexes,
    write_restricted_registry,
    write_snapshot_readme,
)


ROOT = Path(__file__).resolve().parents[1]


def run_snapshot(target_root: Path) -> None:
    seed_request = ROOT / "seed_request.yaml"
    expanded_seed = target_root / "seed_expanded.yaml"
    expand_seed(seed_request, expanded_seed)
    seed = load_seed(expanded_seed)

    target_root.mkdir(parents=True, exist_ok=True)
    copy_seed_definitions(target_root, seed)
    restricted_registry = build_restricted_registry(seed, load_registry())
    write_restricted_registry(target_root, restricted_registry)
    write_restricted_indexes(target_root, restricted_registry)
    write_snapshot_readme(target_root, seed)


def test_snapshot_contains_no_runtime(tmp_path: Path) -> None:
    run_snapshot(tmp_path)

    forbidden = ["enums", "types", "base.py", "codec.py", "property_format.py"]

    for name in forbidden:
        assert not (tmp_path / name).exists()
