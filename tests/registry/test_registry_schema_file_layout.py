from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFINITIONS_DIR = REPO_ROOT / "definitions"
EXEMPTED_TYPE_FILES = {
    "gw.nolan.layout:000",
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def id_line(path: Path) -> str:
    lines = path.read_text().splitlines()
    assert len(lines) >= 2, f"{path} must have at least two lines"
    return lines[1]


def expected_format_path(name: str) -> Path:
    return DEFINITIONS_DIR / "formats" / f"{name}.yaml"


def expected_enum_path(name: str, version: str) -> Path:
    return DEFINITIONS_DIR / "enums" / name / f"{version}.yaml"


def expected_versioned_type_path(name: str, version: str) -> Path:
    return DEFINITIONS_DIR / "types" / name / f"{version}.yaml"


def expected_versionless_type_path(name: str) -> Path:
    return DEFINITIONS_DIR / "types" / f"{name}.yaml"


def expected_format_id_line(name: str) -> str:
    return f'$id: "https://schemas.electricity.works/formats/{name}"'


def expected_enum_id_line(name: str, version: str) -> str:
    return f'$id: "https://schemas.electricity.works/enums/{name}/{version}"'


def expected_versioned_type_id_line(name: str, version: str) -> str:
    return f'$id: "https://schemas.electricity.works/types/{name}/{version}"'


def expected_versionless_type_id_line(name: str) -> str:
    return f'$id: "https://schemas.electricity.works/types/{name}"'


def test_registry_entries_resolve_to_schema_files() -> None:
    registry = load_yaml(DEFINITIONS_DIR / "registry.yaml")

    for name in registry["formats"]:
        path = expected_format_path(name)
        assert path.exists(), f"Missing format schema for {name}: {path}"
        assert id_line(path) == expected_format_id_line(name)

    for name, entry in registry["enums"].items():
        if entry["enum_type"] == "literal":
            path = expected_enum_path(name, "000")
            assert path.exists(), f"Missing enum schema for {name}:000: {path}"
            assert id_line(path) == expected_enum_id_line(name, "000")
            schema = load_yaml(path)
            expected_type = "integer" if entry.get("value_type") == "integer" else "string"
            assert schema.get("type") == expected_type, (
                f"{path} schema type must be {expected_type} to match registry value_type"
            )
        else:
            for version in entry["versions"]:
                path = expected_enum_path(name, version)
                assert path.exists(), f"Missing enum schema for {name}:{version}: {path}"
                assert id_line(path) == expected_enum_id_line(name, version)
                schema = load_yaml(path)
                expected_type = "integer" if entry.get("value_type") == "integer" else "string"
                assert schema.get("type") == expected_type, (
                    f"{path} schema type must be {expected_type} to match registry value_type"
                )

    for name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            path = expected_versionless_type_path(name)
            assert path.exists(), f"Missing versionless type schema for {name}: {path}"
            assert id_line(path) == expected_versionless_type_id_line(name)
        else:
            for version in entry["versions"]:
                path = expected_versioned_type_path(name, version)
                assert path.exists(), f"Missing type schema for {name}:{version}: {path}"
                assert id_line(path) == expected_versioned_type_id_line(name, version)


def test_schema_files_resolve_back_to_registry_entries() -> None:
    registry = load_yaml(DEFINITIONS_DIR / "registry.yaml")

    format_files = {path.stem for path in sorted((DEFINITIONS_DIR / "formats").glob("*.yaml"))}
    registry_formats = set(registry["formats"])
    extra_formats = sorted(format_files - registry_formats)
    missing_formats = sorted(registry_formats - format_files)
    assert not extra_formats and not missing_formats, "\n".join(
        [
            "Format files and registry formats differ",
            f"present in files but missing from registry.yaml: {extra_formats}",
            f"present in registry.yaml but missing from files: {missing_formats}",
        ]
    )
    for path in sorted((DEFINITIONS_DIR / "formats").glob("*.yaml")):
        assert id_line(path) == expected_format_id_line(path.stem)

    enum_files = set()
    for path in sorted((DEFINITIONS_DIR / "enums").glob("*/*.yaml")):
        name = path.parent.name
        version = path.stem
        assert version.isdigit() and len(version) == 3, (
            f"{path} must use enums/<name>/<version>.yaml with a 3-digit version"
        )
        enum_files.add(f"{name}:{version}")
    registry_enums = {
        f"{name}:000"
        if entry["enum_type"] == "literal"
        else f"{name}:{version}"
        for name, entry in registry["enums"].items()
        for version in (["000"] if entry["enum_type"] == "literal" else entry["versions"])
    }
    extra_enums = sorted(enum_files - registry_enums)
    missing_enums = sorted(registry_enums - enum_files)
    assert not extra_enums and not missing_enums, "\n".join(
        [
            "Enum files and registry enums differ",
            f"present in files but missing from registry.yaml: {extra_enums}",
            f"present in registry.yaml but missing from files: {missing_enums}",
        ]
    )
    for path in sorted((DEFINITIONS_DIR / "enums").glob("*/*.yaml")):
        assert id_line(path) == expected_enum_id_line(path.parent.name, path.stem)
        name = path.parent.name
        entry = registry["enums"][name]
        schema = load_yaml(path)
        expected_type = "integer" if entry.get("value_type") == "integer" else "string"
        assert schema.get("type") == expected_type, (
            f"{path} schema type must be {expected_type} to match registry value_type"
        )

    registry_types = set()
    for name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            registry_types.add(name)
        else:
            for version in entry["versions"]:
                registry_types.add(f"{name}:{version}")

    type_files = set()
    orphan_type_files = []
    for path in sorted((DEFINITIONS_DIR / "types").glob("*.yaml")):
        name = path.stem
        if name not in registry["types"]:
            orphan_type_files.append(name)
            continue
        assert registry["types"][name]["versioning_strategy"] == "none", (
            f"{path} must correspond to a versionless type"
        )
        type_files.add(name)
        assert id_line(path) == expected_versionless_type_id_line(name)

    for path in sorted((DEFINITIONS_DIR / "types").glob("*/*.yaml")):
        name = path.parent.name
        version = path.stem
        assert version.isdigit() and len(version) == 3, (
            f"{path} must use types/<name>/<version>.yaml with a 3-digit version"
        )
        if name not in registry["types"]:
            orphan_type_files.append(f"{name}:{version}")
            continue
        assert registry["types"][name]["versioning_strategy"] != "none", (
            f"{path} must correspond to a versioned type"
        )
        type_files.add(f"{name}:{version}")
        assert id_line(path) == expected_versioned_type_id_line(name, version)

    extra_types = sorted(type_files - registry_types)
    extra_types = sorted(set(extra_types).union(orphan_type_files))
    extra_types = sorted(set(extra_types) - EXEMPTED_TYPE_FILES)
    missing_types = sorted(registry_types - type_files)
    assert not extra_types and not missing_types, "\n".join(
        [
            "Type files and registry types differ",
            f"present in files but missing from registry.yaml: {extra_types}",
            f"present in registry.yaml but missing from files: {missing_types}",
        ]
    )
