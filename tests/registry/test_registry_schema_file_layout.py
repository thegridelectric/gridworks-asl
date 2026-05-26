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


def _draft_segment(status: str) -> str:
    return "draft/" if status == "draft" else ""


def _registry_word_status(entry: dict) -> str:
    return entry.get("status", "published")


def _registry_version_status(entry: dict, version: str) -> str:
    # Versioned words carry status ONLY at the version level (per spec).
    # The placement rule itself is enforced separately.
    return entry["versions"][version].get("status", "published")


def expected_format_id_line(name: str, status: str = "published") -> str:
    return f'$id: "https://schemas.electricity.works/{_draft_segment(status)}formats/{name}"'


def expected_enum_id_line(name: str, version: str, status: str = "published") -> str:
    return (
        f'$id: "https://schemas.electricity.works/'
        f'{_draft_segment(status)}enums/{name}/{version}"'
    )


def expected_versioned_type_id_line(name: str, version: str, status: str = "published") -> str:
    return (
        f'$id: "https://schemas.electricity.works/'
        f'{_draft_segment(status)}types/{name}/{version}"'
    )


def expected_versionless_type_id_line(name: str, status: str = "published") -> str:
    return f'$id: "https://schemas.electricity.works/{_draft_segment(status)}types/{name}"'


def _path_to_status_lookup(registry: dict) -> dict[Path, str]:
    """Build a lookup from schema path → expected registry status."""
    statuses: dict[Path, str] = {}
    for name, entry in registry["formats"].items():
        statuses[expected_format_path(name)] = _registry_word_status(entry)
    for name, entry in registry["enums"].items():
        if entry["enum_type"] == "literal":
            statuses[expected_enum_path(name, "000")] = _registry_word_status(entry)
        else:
            for version in entry["versions"]:
                statuses[expected_enum_path(name, version)] = _registry_version_status(
                    entry, version
                )
    for name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            statuses[expected_versionless_type_path(name)] = _registry_word_status(entry)
        else:
            for version in entry["versions"]:
                statuses[expected_versioned_type_path(name, version)] = (
                    _registry_version_status(entry, version)
                )
    return statuses


def test_registry_entries_resolve_to_schema_files() -> None:
    registry = load_yaml(DEFINITIONS_DIR / "registry.yaml")

    for name, entry in registry["formats"].items():
        status = _registry_word_status(entry)
        path = expected_format_path(name)
        assert path.exists(), f"Missing format schema for {name}: {path}"
        assert id_line(path) == expected_format_id_line(name, status)

    for name, entry in registry["enums"].items():
        if entry["enum_type"] == "literal":
            status = _registry_word_status(entry)
            schema_url = str(entry.get("schema_url", ""))
            assert schema_url.endswith("/000"), (
                f"{name}: literal enums SHALL only be version 000; "
                f"registry schema_url is {schema_url}"
            )
            path = expected_enum_path(name, "000")
            assert path.exists(), (
                f"Missing enum schema for {name}:000: {path}. "
                "Literal enums SHALL only be version 000."
            )
            assert id_line(path) == expected_enum_id_line(name, "000", status)
            schema = load_yaml(path)
            expected_type = "integer" if entry.get("value_type") == "integer" else "string"
            assert schema.get("type") == expected_type, (
                f"{path} schema type must be {expected_type} to match registry value_type"
            )
        else:
            for version in entry["versions"]:
                status = _registry_version_status(entry, version)
                path = expected_enum_path(name, version)
                assert path.exists(), f"Missing enum schema for {name}:{version}: {path}"
                assert id_line(path) == expected_enum_id_line(name, version, status)
                schema = load_yaml(path)
                expected_type = "integer" if entry.get("value_type") == "integer" else "string"
                assert schema.get("type") == expected_type, (
                    f"{path} schema type must be {expected_type} to match registry value_type"
                )

    for name, entry in registry["types"].items():
        if entry["versioning_strategy"] == "none":
            status = _registry_word_status(entry)
            path = expected_versionless_type_path(name)
            assert path.exists(), f"Missing versionless type schema for {name}: {path}"
            assert id_line(path) == expected_versionless_type_id_line(name, status)
        else:
            for version in entry["versions"]:
                status = _registry_version_status(entry, version)
                path = expected_versioned_type_path(name, version)
                assert path.exists(), f"Missing type schema for {name}:{version}: {path}"
                assert id_line(path) == expected_versioned_type_id_line(name, version, status)


def test_schema_files_resolve_back_to_registry_entries() -> None:
    """File-system → registry direction.

    Walks every YAML file under definitions/{formats,enums,types}/ and asserts:

      1. The file corresponds to a registered word (no orphan schema files,
         except those listed in EXEMPTED_TYPE_FILES).
      2. Each registered word has a corresponding file (no missing schemas).
      3. The file's $id line matches the canonical URL for its kind, name,
         version, and registry-declared status (published vs draft, where draft
         schemas live at .../draft/<kind>s/...).
      4. For enums, the schema's declared ``type`` matches the registry's
         declared ``value_type``.
      5. For types, the file's location agrees with the registry's
         versioning_strategy (versionless types in types/<name>.yaml,
         versioned types in types/<name>/<version>.yaml).

    The complementary direction (registry entries → schema files) lives in
    ``test_registry_entries_resolve_to_schema_files``.
    """
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
        status = _registry_word_status(registry["formats"][path.stem])
        assert id_line(path) == expected_format_id_line(path.stem, status)

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
        name = path.parent.name
        version = path.stem
        entry = registry["enums"][name]
        status = (
            _registry_word_status(entry)
            if entry["enum_type"] == "literal"
            else _registry_version_status(entry, version)
        )
        assert id_line(path) == expected_enum_id_line(name, version, status)
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
        status = _registry_word_status(registry["types"][name])
        assert id_line(path) == expected_versionless_type_id_line(name, status)

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
        status = _registry_version_status(registry["types"][name], version)
        assert id_line(path) == expected_versioned_type_id_line(name, version, status)

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
