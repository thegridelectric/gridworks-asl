from pathlib import Path

from sema.tools.build_seed_expanded import expand_seed
from sema.tools.build_seed_definitions import (
    build_restricted_registry,
    copy_seed_definitions,
    load_registry,
    load_seed,
    resolve_target_path,
    write_restricted_registry,
)


ROOT = Path(__file__).resolve().parents[1]


def run_definitions_build(target_root: Path) -> None:
    seed_request = ROOT / "template_seed_request.yaml"
    expanded_seed = target_root / "seed_expanded.yaml"
    expand_seed(seed_request, expanded_seed)
    seed = load_seed(expanded_seed)

    target_root.mkdir(parents=True, exist_ok=True)
    copy_seed_definitions(target_root, seed)
    restricted_registry = build_restricted_registry(seed, load_registry())
    write_restricted_registry(target_root, restricted_registry)


def test_seed_definitions_contains_no_runtime(tmp_path: Path) -> None:
    target_root = tmp_path / "sema"
    run_definitions_build(target_root)

    forbidden = ["enums", "types", "base.py", "codec.py", "property_format.py"]

    for name in forbidden:
        assert not (target_root / name).exists()
    assert (target_root / "definitions" / "registry.yaml").exists()


def test_resolve_target_path_always_uses_sema_directory(tmp_path: Path) -> None:
    assert resolve_target_path("gjk", str(tmp_path / "out")) == tmp_path / "out" / "sema"
    assert resolve_target_path("gjk", str(tmp_path / "out" / "sema")) == tmp_path / "out" / "sema"
