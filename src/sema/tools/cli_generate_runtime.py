from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from sema.tools.generate_runtime_from_dag import generate_runtime_from_dag


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SEED = ROOT / "output" / "seed_expanded.yaml"
DEFAULT_REGISTRY = ROOT / "definitions" / "registry.yaml"
DEFAULT_DEFINITIONS = ROOT / "definitions"


def load_yaml(path: Path) -> dict:
    with path.open() as handle:
        return yaml.safe_load(handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate snapshot runtime files from an expanded seed worklist and registry."
        )
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=DEFAULT_SEED,
        help="Path to expanded seed YAML",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help="Path to registry.yaml",
    )
    parser.add_argument(
        "--definitions-root",
        type=Path,
        default=DEFAULT_DEFINITIONS,
        help="Path to definitions/ root",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Target snapshot sema package directory",
    )
    parser.add_argument(
        "--package-name",
        help="Owning package name for absolute generated imports; defaults to target directory name",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed = load_yaml(args.seed.resolve())
    registry = load_yaml(args.registry.resolve())
    target = args.target.resolve()
    package_name = args.package_name if args.package_name else target.name
    generate_runtime_from_dag(
        target,
        seed,
        registry,
        args.definitions_root.resolve(),
        package_name,
    )
    print(f"Generated runtime from DAG at {target}")
    print(f"Seed source: {args.seed}")
    print(f"Registry source: {args.registry}")


if __name__ == "__main__":
    main()
