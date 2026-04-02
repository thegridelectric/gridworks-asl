from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import yaml


DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "runtime"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "output"
DEFAULT_SEED = OUTPUT_DIR / "seed_expanded.yaml"
PACKAGE_NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")

CORE_FILES = [
    "__init__.py",
    "base.py",
    "codec.py",
    "property_format.py",
]

CLASS_PATTERN = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\(", re.MULTILINE)
TYPE_HELPER_IMPORT_PATTERN = re.compile(
    r"from\s+sema\.runtime\.type_helpers(?:\.([A-Za-z0-9_]+))?\s+import"
)


def sema_name_to_module(word_name: str) -> str:
    return word_name.replace(".", "_")


def read_text(path: Path) -> str:
    return path.read_text()


def rewrite_imports(text: str, package_name: str) -> str:
    replacements = {
        "from sema.runtime import": f"from {package_name}.sema import",
        "from sema.runtime.base import": f"from {package_name}.sema.base import",
        "from sema.runtime.codec import": f"from {package_name}.sema.codec import",
        "from sema.runtime.property_format import": f"from {package_name}.sema.property_format import",
        "from sema.runtime.enums import": f"from {package_name}.sema.enums import",
        "from sema.runtime.enums.": f"from {package_name}.sema.enums.",
        "from sema.runtime.types import": f"from {package_name}.sema.types import",
        "from sema.runtime.types.": f"from {package_name}.sema.types.",
        "from sema.runtime.type_helpers import": f"from {package_name}.sema.type_helpers import",
        "from sema.runtime.type_helpers.": f"from {package_name}.sema.type_helpers.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def write_python_file(source: Path, target: Path, package_name: str) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    text = rewrite_imports(read_text(source), package_name)
    target.write_text(text)
    return text


def parse_primary_class_name(path: Path) -> str:
    matches = CLASS_PATTERN.findall(read_text(path))
    if not matches:
        raise ValueError(f"No class declaration found in {path}")
    return matches[-1]


def load_seed(seed_path: Path) -> dict:
    with seed_path.open() as handle:
        return yaml.safe_load(handle)


def validate_package_name(name: str) -> str:
    if not PACKAGE_NAME_PATTERN.fullmatch(name):
        raise ValueError("--package-name must be lowercase snake_case.")
    return name


def resolve_target_path(package_name: str, target_path: str | None) -> Path:
    if target_path:
        return Path(target_path).resolve()
    return OUTPUT_DIR / package_name


def selected_versions(seed: dict, section: str) -> dict[str, list[str]]:
    worklist = seed["worklist"][section]
    selected: dict[str, list[str]] = {}
    for word_name, word_entry in worklist.items():
        if not isinstance(word_entry, dict):
            continue
        versions = sorted(
            [version for version in word_entry.keys() if isinstance(version, str) and version.isdigit()],
            key=int,
        )
        if versions:
            selected[word_name] = versions
    return selected


def selected_versionless_types(seed: dict) -> list[str]:
    selected: list[str] = []
    for word_name, word_entry in seed["worklist"]["types"].items():
        if not isinstance(word_entry, dict):
            continue
        if word_entry.get("versioning_strategy") == "none":
            selected.append(word_name)
    return sorted(selected)


def latest_and_old_versions(versions: list[str]) -> tuple[str | None, list[str]]:
    if not versions:
        return None, []
    latest = max(versions, key=int)
    old_versions = [version for version in versions if version != latest]
    return latest, old_versions


def generate_package_init(
    init_path: Path,
    package_root: str,
    package: str,
    imports: list[tuple[str, str]],
) -> None:
    lines: list[str] = []
    for module_name, class_name in imports:
        lines.append(f"from {package_root}.sema.{package}.{module_name} import {class_name}")
    if lines:
        body = "\n".join(lines) + "\n\n"
    else:
        body = ""
    all_values = ",\n".join(f'    "{class_name}"' for _, class_name in imports)
    if all_values:
        all_block = "[\n" + all_values + ",\n]\n"
    else:
        all_block = "[]\n"
    init_path.write_text(body + "__all__ = " + all_block)


def discover_type_helpers(text: str) -> set[str]:
    helpers: set[str] = set()
    for match in TYPE_HELPER_IMPORT_PATTERN.finditer(text):
        module_name = match.group(1)
        if module_name:
            helpers.add(module_name)
    return helpers


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def mirror_vocab_package(source_root: Path, target_root: Path, seed: dict, package_name: str) -> None:
    target_root.mkdir(parents=True, exist_ok=True)

    for filename in CORE_FILES:
        write_python_file(source_root / filename, target_root / filename, package_name)

    enum_target = target_root / "enums"
    type_target = target_root / "types"
    enum_old_target = enum_target / "old_versions"
    type_old_target = type_target / "old_versions"
    type_helper_target = target_root / "type_helpers"

    ensure_clean_dir(enum_target)
    ensure_clean_dir(type_target)
    ensure_clean_dir(enum_old_target)
    ensure_clean_dir(type_old_target)

    helper_modules: set[str] = set()

    enum_imports: list[tuple[str, str]] = []
    enum_old_imports: list[tuple[str, str]] = []
    type_imports: list[tuple[str, str]] = []
    type_old_imports: list[tuple[str, str]] = []
    missing_sources: list[str] = []

    gw_str_enum_source = source_root / "enums" / "gw_str_enum.py"
    write_python_file(gw_str_enum_source, enum_target / "gw_str_enum.py", package_name)

    for word_name, versions in selected_versions(seed, "enums").items():
        module_name = sema_name_to_module(word_name)
        latest_version, old_versions = latest_and_old_versions(versions)
        if latest_version is None:
            continue

        current_source = source_root / "enums" / f"{module_name}.py"
        if not current_source.exists():
            missing_sources.append(str(current_source))
            continue
        current_target = enum_target / f"{module_name}.py"
        write_python_file(current_source, current_target, package_name)
        enum_imports.append((module_name, parse_primary_class_name(current_source)))

        for version in old_versions:
            old_module_name = f"{module_name}_{version}"
            old_source = source_root / "enums" / "old_versions" / f"{old_module_name}.py"
            if not old_source.exists():
                missing_sources.append(str(old_source))
                continue
            old_target = enum_old_target / f"{old_module_name}.py"
            write_python_file(old_source, old_target, package_name)
            enum_old_imports.append((old_module_name, parse_primary_class_name(old_source)))

    for word_name, versions in selected_versions(seed, "types").items():
        module_name = sema_name_to_module(word_name)
        latest_version, old_versions = latest_and_old_versions(versions)
        if latest_version is None:
            continue

        current_source = source_root / "types" / f"{module_name}.py"
        if not current_source.exists():
            missing_sources.append(str(current_source))
            continue
        current_target = type_target / f"{module_name}.py"
        current_text = write_python_file(current_source, current_target, package_name)
        type_imports.append((module_name, parse_primary_class_name(current_source)))
        helper_modules.update(discover_type_helpers(current_text))

        for version in old_versions:
            old_module_name = f"{module_name}_{version}"
            old_source = source_root / "types" / "old_versions" / f"{old_module_name}.py"
            if not old_source.exists():
                missing_sources.append(str(old_source))
                continue
            old_target = type_old_target / f"{old_module_name}.py"
            old_text = write_python_file(old_source, old_target, package_name)
            type_old_imports.append((old_module_name, parse_primary_class_name(old_source)))
            helper_modules.update(discover_type_helpers(old_text))

    for word_name in selected_versionless_types(seed):
        module_name = sema_name_to_module(word_name)
        current_source = source_root / "types" / f"{module_name}.py"
        if not current_source.exists():
            missing_sources.append(str(current_source))
            continue
        current_target = type_target / f"{module_name}.py"
        current_text = write_python_file(current_source, current_target, package_name)
        type_imports.append((module_name, parse_primary_class_name(current_source)))
        helper_modules.update(discover_type_helpers(current_text))

    generate_package_init(
        enum_target / "__init__.py",
        package_name,
        "enums",
        enum_imports + [("gw_str_enum", "GwStrEnum"), ("gw_str_enum", "SemaEnum"), ("gw_str_enum", "SymbolizedEnum")],
    )
    generate_package_init(enum_old_target / "__init__.py", package_name, "enums.old_versions", enum_old_imports)
    generate_package_init(type_target / "__init__.py", package_name, "types", type_imports)
    generate_package_init(type_old_target / "__init__.py", package_name, "types.old_versions", type_old_imports)

    if helper_modules:
        ensure_clean_dir(type_helper_target)
        helper_init_source = source_root / "type_helpers" / "__init__.py"
        if helper_init_source.exists():
            write_python_file(helper_init_source, type_helper_target / "__init__.py", package_name)
        else:
            (type_helper_target / "__init__.py").write_text("__all__ = []\n")
        for module_name in sorted(helper_modules):
            source = source_root / "type_helpers" / f"{module_name}.py"
            if not source.exists():
                missing_sources.append(str(source))
                continue
            target = type_helper_target / f"{module_name}.py"
            write_python_file(source, target, package_name)
        (type_helper_target / "__init__.py").write_text("__all__ = []\n")

    if missing_sources:
        missing_text = "\n".join(sorted(missing_sources))
        raise FileNotFoundError(
            "Seed-selected canonical modules are missing from src/sema/runtime:\n"
            f"{missing_text}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Mirror seed-selected canonical sema/src/sema/runtime Python into "
            "gridworks-data/src/gw_data/sema with import-path rewrites. "
            "Current versions are mirrored to enums/ and types/; older selected "
            "versions are mirrored to the corresponding old_versions/ folders."
        )
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--package-name", required=True)
    parser.add_argument("--target-path")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed = load_seed(args.seed.resolve())
    package_name = validate_package_name(args.package_name)
    target_path = resolve_target_path(package_name, args.target_path)
    mirror_vocab_package(args.source.resolve(), target_path, seed, package_name)
    print(f"Mirrored seed-selected vocabulary from {args.source} -> {target_path}")
    print(f"Selection source: {args.seed}")


if __name__ == "__main__":
    main()
