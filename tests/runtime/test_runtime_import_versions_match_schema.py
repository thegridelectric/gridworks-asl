import ast
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "indexes" / "public_registry.yaml"
RUNTIME_TYPES_DIR = REPO_ROOT / "src" / "sema" / "runtime" / "types"


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def sema_name_to_module(word_name: str) -> str:
    return word_name.replace(".", "_")


def sema_name_to_class(word_name: str) -> str:
    return "".join(part.capitalize() for part in word_name.split("."))


def parse_python(path: Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def import_targets(module: ast.Module) -> set[tuple[str, str]]:
    targets: set[tuple[str, str]] = set()
    for node in ast.walk(module):
        if not isinstance(node, ast.ImportFrom) or node.module is None:
            continue
        for alias in node.names:
            imported_name = alias.asname or alias.name
            targets.add((node.module, imported_name))
    return targets


def expected_type_import(
    registry: dict[str, Any], dep_name: str, dep_version: str
) -> tuple[str, str]:
    latest_version = registry["types"][dep_name]["latest_version"]
    module_name = sema_name_to_module(dep_name)
    class_name = sema_name_to_class(dep_name)
    if dep_version == latest_version:
        return (f"sema.runtime.types.{module_name}", class_name)
    return (
        f"sema.runtime.types.old_versions.{module_name}_{dep_version}",
        f"{class_name}{dep_version}",
    )


def expected_enum_import(
    registry: dict[str, Any], dep_name: str, dep_version: str
) -> tuple[str, str]:
    entry = registry["enums"][dep_name]
    module_name = sema_name_to_module(dep_name)
    class_name = sema_name_to_class(dep_name)
    if entry["enum_type"] == "literal":
        return (f"sema.runtime.enums.{module_name}", class_name)
    latest_version = entry["latest_version"]
    if dep_version == latest_version:
        return (f"sema.runtime.enums.{module_name}", class_name)
    return (
        f"sema.runtime.enums.old_versions.{module_name}_{dep_version}",
        f"{class_name}{dep_version}",
    )


def runtime_type_file(registry_entry: dict[str, Any], type_name: str, version: str) -> Path:
    module_name = sema_name_to_module(type_name)
    if version == registry_entry["latest_version"]:
        return RUNTIME_TYPES_DIR / f"{module_name}.py"
    return RUNTIME_TYPES_DIR / "old_versions" / f"{module_name}_{version}.py"


def candidate_type_imports(dep_name: str, imports: set[tuple[str, str]]) -> set[tuple[str, str]]:
    module_name = sema_name_to_module(dep_name)
    class_name = sema_name_to_class(dep_name)
    return {
        target
        for target in imports
        if (
            target[0] == f"sema.runtime.types.{module_name}"
            and target[1] == class_name
        )
        or (
            target[0].startswith(f"sema.runtime.types.old_versions.{module_name}_")
            and target[1].startswith(class_name)
        )
    }


def candidate_enum_imports(dep_name: str, imports: set[tuple[str, str]]) -> set[tuple[str, str]]:
    module_name = sema_name_to_module(dep_name)
    class_name = sema_name_to_class(dep_name)
    return {
        target
        for target in imports
        if (
            target[0] == f"sema.runtime.enums.{module_name}"
            and target[1] == class_name
        )
        or (
            target[0] == "sema.runtime.enums"
            and target[1] == class_name
        )
        or (
            target[0].startswith(f"sema.runtime.enums.old_versions.{module_name}_")
            and target[1].startswith(class_name)
        )
    }


def test_runtime_import_versions_match_schema() -> None:
    registry = load_yaml(REGISTRY_PATH)
    findings: list[str] = []

    for type_name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            continue

        for version, version_entry in entry["versions"].items():
            path = runtime_type_file(entry, type_name, version)
            if not path.exists():
                continue

            imports = import_targets(parse_python(path))
            structural = version_entry["direct_dependencies"]["structural"]

            for dep in structural:
                if ":" not in dep:
                    continue
                dep_name, dep_version = dep.rsplit(":", 1)

                if dep_name in registry["types"]:
                    dep_entry = registry["types"][dep_name]
                    if dep_entry["versioning_strategy"] == "none":
                        continue
                    expected = expected_type_import(registry, dep_name, dep_version)
                    candidates = candidate_type_imports(dep_name, imports)
                    if expected not in candidates:
                        findings.append(
                            f"{type_name}:{version} imports wrong runtime type version for {dep}; "
                            f"expected {expected[0]} import {expected[1]}, found {sorted(candidates) or 'none'}"
                        )
                elif dep_name in registry["enums"]:
                    expected = expected_enum_import(registry, dep_name, dep_version)
                    candidates = candidate_enum_imports(dep_name, imports)
                    acceptable = {expected}
                    if expected[0].startswith("sema.runtime.enums.") and ".old_versions." not in expected[0]:
                        acceptable.add(("sema.runtime.enums", expected[1]))
                    if not (acceptable & candidates):
                        findings.append(
                            f"{type_name}:{version} imports wrong runtime enum version for {dep}; "
                            f"expected {expected[0]} import {expected[1]}, found {sorted(candidates) or 'none'}"
                        )

    if findings:
        raise AssertionError("\n".join(findings))
