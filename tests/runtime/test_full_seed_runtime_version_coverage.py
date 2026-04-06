import ast
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
FULL_SEED_PATH = REPO_ROOT / "full_seed.yaml"
REGISTRY_PATH = REPO_ROOT / "definitions" / "registry.yaml"
RUNTIME_TYPES_DIR = REPO_ROOT / "src" / "sema" / "runtime" / "types"
RUNTIME_ENUMS_DIR = REPO_ROOT / "src" / "sema" / "runtime" / "enums"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def sema_name_to_module(word_name: str) -> str:
    return word_name.replace(".", "_")


def sema_name_to_class(word_name: str) -> str:
    return "".join(part.capitalize() for part in word_name.split("."))


def parse_python(path: Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def find_classes(module: ast.Module, class_name: str) -> list[ast.ClassDef]:
    return [
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    ]


def extract_type_version(class_def: ast.ClassDef) -> str | None:
    for node in class_def.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "version":
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "version":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return None


def extract_enum_version(class_def: ast.ClassDef) -> str | None:
    for node in class_def.body:
        if isinstance(node, ast.FunctionDef) and node.name == "enum_version":
            for stmt in node.body:
                if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                    return stmt.value.value
    return None


def selected_type_versions(seed: dict) -> dict[str, list[str]]:
    selected: dict[str, list[str]] = {}
    for word_name, entry in seed["worklist"]["types"].items():
        if not isinstance(entry, dict):
            continue
        versions = sorted(
            [version for version in entry.keys() if isinstance(version, str) and version.isdigit()],
            key=int,
        )
        if versions:
            selected[word_name] = versions
    return selected


def selected_versionless_types(seed: dict) -> list[str]:
    selected: list[str] = []
    for word_name, entry in seed["worklist"]["types"].items():
        if not isinstance(entry, dict):
            continue
        if entry.get("versioning_strategy") == "none":
            selected.append(word_name)
    return sorted(selected)


def selected_versioned_enum_versions(seed: dict, registry: dict) -> dict[str, list[str]]:
    selected: dict[str, list[str]] = {}
    for word_name, entry in seed["worklist"]["enums"].items():
        if registry["enums"][word_name]["enum_type"] != "versioned":
            continue
        versions = sorted(
            [version for version in entry.keys() if isinstance(version, str) and version.isdigit()],
            key=int,
        )
        if versions:
            selected[word_name] = versions
    return selected


def test_full_seed_runtime_version_coverage() -> None:
    seed = load_yaml(FULL_SEED_PATH)
    registry = load_yaml(REGISTRY_PATH)
    findings: list[str] = []

    for word_name in selected_versionless_types(seed):
        module_name = sema_name_to_module(word_name)
        class_name = sema_name_to_class(word_name)
        current_path = RUNTIME_TYPES_DIR / f"{module_name}.py"
        if not current_path.exists():
            findings.append(f"{word_name} missing current runtime type module: {current_path}")
            continue
        current_module = parse_python(current_path)
        current_classes = find_classes(current_module, class_name)
        if not current_classes:
            findings.append(f"{word_name} missing current runtime type class: {class_name}")
            continue
        if len(current_classes) != 1:
            findings.append(f"{word_name} current runtime type has {len(current_classes)} matching classes named {class_name}")
            continue
        current_class = current_classes[0]
        actual_version = extract_type_version(current_class)
        if actual_version is not None:
            findings.append(f"{word_name} is versionless but current runtime type defines version {actual_version}")

    for word_name, versions in selected_type_versions(seed).items():
        registry_entry = registry["types"][word_name]
        latest_version = registry_entry["latest_version"]
        module_name = sema_name_to_module(word_name)
        class_name = sema_name_to_class(word_name)

        current_path = RUNTIME_TYPES_DIR / f"{module_name}.py"
        if not current_path.exists():
            findings.append(f"{word_name} missing current runtime type module: {current_path}")
        else:
            current_module = parse_python(current_path)
            current_classes = find_classes(current_module, class_name)
            if not current_classes:
                findings.append(f"{word_name} missing current runtime type class: {class_name}")
            elif len(current_classes) != 1:
                findings.append(f"{word_name} current runtime type has {len(current_classes)} matching classes named {class_name}")
            else:
                actual_version = extract_type_version(current_classes[0])
                if actual_version != latest_version:
                    findings.append(
                        f"{word_name} current runtime type version mismatch: expected {latest_version}, got {actual_version}"
                    )

        for version in versions:
            if version == latest_version:
                continue
            top_level_old_path = RUNTIME_TYPES_DIR / f"{module_name}_{version}.py"
            if top_level_old_path.exists():
                findings.append(
                    f"{word_name}:{version} old runtime type module exists at top level: {top_level_old_path}"
                )

        for version in versions:
            if version == latest_version:
                continue
            old_module_name = f"{module_name}_{version}"
            old_class_name = f"{class_name}{version}"
            old_path = RUNTIME_TYPES_DIR / "old_versions" / f"{old_module_name}.py"
            if not old_path.exists():
                findings.append(f"{word_name}:{version} missing old runtime type module: {old_path}")
                continue
            old_module = parse_python(old_path)
            old_classes = find_classes(old_module, old_class_name)
            if not old_classes:
                findings.append(f"{word_name}:{version} missing old runtime type class: {old_class_name}")
                continue
            if len(old_classes) != 1:
                findings.append(f"{word_name}:{version} old runtime type has {len(old_classes)} matching classes named {old_class_name}")
                continue
            actual_version = extract_type_version(old_classes[0])
            if actual_version != version:
                findings.append(
                    f"{word_name}:{version} old runtime type version mismatch: expected {version}, got {actual_version}"
                )

    for word_name, versions in selected_versioned_enum_versions(seed, registry).items():
        registry_entry = registry["enums"][word_name]
        latest_version = registry_entry["latest_version"]
        module_name = sema_name_to_module(word_name)
        class_name = sema_name_to_class(word_name)

        current_path = RUNTIME_ENUMS_DIR / f"{module_name}.py"
        if not current_path.exists():
            findings.append(f"{word_name} missing current runtime enum module: {current_path}")
        else:
            current_module = parse_python(current_path)
            current_classes = find_classes(current_module, class_name)
            if not current_classes:
                findings.append(f"{word_name} missing current runtime enum class: {class_name}")
            elif len(current_classes) != 1:
                findings.append(f"{word_name} current runtime enum has {len(current_classes)} matching classes named {class_name}")
            else:
                actual_version = extract_enum_version(current_classes[0])
                if actual_version != latest_version:
                    findings.append(
                        f"{word_name} current runtime enum version mismatch: expected {latest_version}, got {actual_version}"
                    )

        for version in versions:
            if version == latest_version:
                continue
            top_level_old_path = RUNTIME_ENUMS_DIR / f"{module_name}_{version}.py"
            if top_level_old_path.exists():
                findings.append(
                    f"{word_name}:{version} old runtime enum module exists at top level: {top_level_old_path}"
                )

        for version in versions:
            if version == latest_version:
                continue
            old_module_name = f"{module_name}_{version}"
            old_class_name = f"{class_name}{version}"
            old_path = RUNTIME_ENUMS_DIR / "old_versions" / f"{old_module_name}.py"
            if not old_path.exists():
                findings.append(f"{word_name}:{version} missing old runtime enum module: {old_path}")
                continue
            old_module = parse_python(old_path)
            old_classes = find_classes(old_module, old_class_name)
            if not old_classes:
                findings.append(f"{word_name}:{version} missing old runtime enum class: {old_class_name}")
                continue
            if len(old_classes) != 1:
                findings.append(f"{word_name}:{version} old runtime enum has {len(old_classes)} matching classes named {old_class_name}")
                continue
            actual_version = extract_enum_version(old_classes[0])
            if actual_version != version:
                findings.append(
                    f"{word_name}:{version} old runtime enum version mismatch: expected {version}, got {actual_version}"
                )

    if findings:
        raise AssertionError("\n".join(findings))
