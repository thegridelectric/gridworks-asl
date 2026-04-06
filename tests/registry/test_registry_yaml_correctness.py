import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


RFC3339_SECONDS_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
)
FORMAT_SCHEMA_URL_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/formats/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)$"
)
ENUM_SCHEMA_URL_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/enums/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)/(?P<version>\d{3})$"
)
VERSIONED_TYPE_SCHEMA_URL_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/types/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)/(?P<version>\d{3})$"
)
VERSIONLESS_TYPE_SCHEMA_URL_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/types/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)$"
)


def parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFINITIONS_DIR = REPO_ROOT / "definitions"


def load_registry(path: str) -> dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_created_for_dep(registry: dict[str, Any], dep: str) -> str:
    if ":" in dep:
        name, version = dep.rsplit(":", 1)

        if name in registry.get("types", {}):
            entry = registry["types"][name]
            if entry["versioning_strategy"] == "none":
                raise AssertionError(
                    f"{dep} is referenced with a version but {name} is a versionless type"
                )
            return entry["versions"][version]["created"]

        if name in registry.get("enums", {}):
            entry = registry["enums"][name]
            if entry["enum_type"] == "literal":
                if version != "000":
                    raise AssertionError(
                        f"{dep} references a non-000 version for literal enum {name}"
                    )
                return entry["created"]
            return entry["versions"][version]["created"]

        raise AssertionError(f"Unknown versioned dependency: {dep}")

    if dep in registry.get("formats", {}):
        return registry["formats"][dep]["created"]

    if dep in registry.get("types", {}):
        entry = registry["types"][dep]
        if entry["versioning_strategy"] != "none":
            raise AssertionError(
                f"{dep} is referenced without a version but is a versioned type"
            )
        return entry["created"]

    if dep in registry.get("enums", {}):
        raise AssertionError(
            f"{dep} is referenced without a version but is an enum"
        )

    raise AssertionError(f"Unknown dependency: {dep}")


# -----------------------------------------------------------------------------
# CORE TESTS
# -----------------------------------------------------------------------------
def test_registry_top_level_structure_and_sections():
    registry = load_registry(DEFINITIONS_DIR / "registry.yaml")

    # ---------------------------------------------------------------------
    # Required sections
    # ---------------------------------------------------------------------

    required_sections = ["metadata", "types", "enums", "formats"]

    for section in required_sections:
        assert section in registry, f"Missing top-level section: {section}"

    # ---------------------------------------------------------------------
    # Section types
    # ---------------------------------------------------------------------

    assert isinstance(registry["metadata"], dict)
    assert isinstance(registry["types"], dict)
    assert isinstance(registry["enums"], dict)
    assert isinstance(registry["formats"], dict)

    # ---------------------------------------------------------------------
    # No unexpected sections
    # ---------------------------------------------------------------------

    allowed_sections = set(required_sections)
    actual_sections = set(registry.keys())

    extra = actual_sections - allowed_sections
    if extra:
        raise AssertionError(f"Unexpected top-level sections: {sorted(extra)}")

    # ---------------------------------------------------------------------
    # Section ordering (strict)
    # ---------------------------------------------------------------------

    expected_order = ["metadata", "formats", "enums", "types"]
    actual_order = list(registry.keys())

    if actual_order != expected_order:
        raise AssertionError(
            f"Top-level sections must be ordered as {expected_order}, got {actual_order}"
        )

    # ---------------------------------------------------------------------
    # Metadata validation
    # ---------------------------------------------------------------------

    metadata = registry["metadata"]

    assert "registry_version" in metadata
    assert isinstance(metadata["registry_version"], str)

    assert "last_updated" in metadata
    assert is_valid_ts(metadata["last_updated"])

    assert "maintainer" in metadata
    assert isinstance(metadata["maintainer"], str)


def test_registry_format_structure():
    registry = load_registry(DEFINITIONS_DIR / "registry.yaml")
    owners = load_registry(DEFINITIONS_DIR / "owners.yaml")

    assert "formats" in registry
    formats = registry["formats"]

    assert isinstance(formats, dict)

    for format_name, entry in formats.items():

        # -----------------------------------------------------------------
        # Required fields
        # -----------------------------------------------------------------

        assert "owner" in entry, f"{format_name} missing owner"
        assert entry["owner"] in owners, f"{format_name} owner not in owners.yaml"

        assert "schema_url" in entry, f"{format_name} missing schema_url"
        assert "created" in entry, f"{format_name} missing created"

        # -----------------------------------------------------------------
        # No versioning allowed
        # -----------------------------------------------------------------

        assert "versions" not in entry, f"{format_name} must not have versions"
        assert "latest_version" not in entry, f"{format_name} must not have latest_version"

        # -----------------------------------------------------------------
        # No dependencies allowed (per spec)
        # -----------------------------------------------------------------

        assert "direct_dependencies" not in entry, (
            f"{format_name} must not declare direct_dependencies"
        )

        # -----------------------------------------------------------------
        # Timestamp validation
        # -----------------------------------------------------------------

        ts = entry["created"]
        assert is_valid_ts(ts), f"{format_name} invalid created timestamp"

        # -----------------------------------------------------------------
        # Schema URL validation
        # -----------------------------------------------------------------

        schema_url = entry["schema_url"]

        # Must include type name
        assert f"/{format_name}" in schema_url, (
            f"{format_name} schema_url does not contain its name"
        )

        # Must NOT include version suffix
        if re.search(r"/\d{3}$", schema_url):
            raise AssertionError(
                f"{format_name} schema_url must not include version segment"
            )

        # -----------------------------------------------------------------
        # Description (optional but recommended)
        # -----------------------------------------------------------------

        if "description" in entry:
            assert isinstance(entry["description"], str)


def test_registry_enum_structure():
    registry = load_registry(DEFINITIONS_DIR / "registry.yaml")
    owners = load_registry(DEFINITIONS_DIR / "owners.yaml")

    enums = registry.get("enums", {})

    for enum_name, entry in enums.items():

        # -----------------------------------------------------------------
        # Required fields
        # -----------------------------------------------------------------

        assert "owner" in entry
        assert entry["owner"] in owners

        assert "enum_type" in entry
        assert entry["enum_type"] in {"literal", "versioned"}

        if entry["enum_type"] == "literal":
            assert "versions" not in entry
            assert "latest_version" not in entry

            assert "schema_url" in entry
            assert "created" in entry

            assert is_valid_ts(entry["created"])
            assert_schema_url_matches_enum_name_and_version(
                enum_name, "000", entry["schema_url"]
            )

        else:
            assert "versions" in entry
            assert "latest_version" in entry

            versions = entry["versions"]
            version_keys = list(versions.keys())

            # -----------------------------------------------------------------
            # Version format and ordering
            # -----------------------------------------------------------------

            for v in version_keys:
                assert re.match(r"^\d{3}$", v), f"{enum_name}:{v} invalid version"

            assert version_keys == sorted(version_keys, reverse=True)
            assert entry["latest_version"] == version_keys[0]

            # -----------------------------------------------------------------
            # Created timestamps
            # -----------------------------------------------------------------

            timestamps = []

            for v in version_keys:
                v_entry = versions[v]

                assert "created" in v_entry
                assert is_valid_ts(v_entry["created"])

                timestamps.append((v, parse_ts(v_entry["created"])))

            ts_values = [t for _, t in timestamps]
            assert len(ts_values) == len(set(ts_values)), f"{enum_name} duplicate timestamps"

            for i in range(len(timestamps) - 1):
                v_new, t_new = timestamps[i]
                v_old, t_old = timestamps[i + 1]

                assert int(v_new) > int(v_old)
                assert t_new > t_old, f"{enum_name} timestamp ordering violated"

            # -----------------------------------------------------------------
            # Version entry structure
            # -----------------------------------------------------------------

            initial_version = version_keys[-1]

            for v, v_entry in versions.items():
                assert "schema_url" in v_entry
                assert "created" in v_entry
                assert_schema_url_matches_enum_name_and_version(
                    enum_name, v, v_entry["schema_url"]
                )

                if v == initial_version:
                    assert "added_values" not in v_entry
                else:
                    assert "added_values" in v_entry
                    assert isinstance(v_entry["added_values"], list)
                    assert len(v_entry["added_values"]) > 0


def test_registry_type_structure():
    registry = load_registry(DEFINITIONS_DIR / "registry.yaml")
    owners = load_registry(DEFINITIONS_DIR / "owners.yaml")

    assert isinstance(registry, dict)
    assert "types" in registry
    assert isinstance(registry["types"], dict)

    for type_name, entry in registry["types"].items():

        # ---------------------------------------------------------------------
        # Required top-level fields
        # ---------------------------------------------------------------------

        assert "owner" in entry
        assert "versioning_strategy" in entry
        assert entry["versioning_strategy"] in {"none", "string", "literal"}

        # ---------------------------------------------------------------------
        # Owner must exist
        # ---------------------------------------------------------------------

        assert entry["owner"] in owners

        strategy = entry["versioning_strategy"]

        # ---------------------------------------------------------------------
        # VERSIONLESS TYPES
        # ---------------------------------------------------------------------

        if strategy == "none":
            assert "versions" not in entry

            assert "schema_url" in entry
            assert "created" in entry
            assert "direct_dependencies" in entry

            assert is_valid_ts(entry["created"])
            assert_schema_url_matches_versionless_type_name(
                type_name, entry["schema_url"]
            )

            deps = entry["direct_dependencies"]
            assert "structural" in deps
            if "axiom" in deps:
                assert isinstance(deps["axiom"], list)
            assert isinstance(deps["structural"], list)
            assert len(deps["structural"]) == len(set(deps["structural"]))
            if "axiom" in deps:
                assert len(deps["axiom"]) == len(set(deps["axiom"]))
                overlap = sorted(set(deps["structural"]) & set(deps["axiom"]))
                if overlap:
                    raise AssertionError(
                        f"{type_name} has dependencies duplicated across structural and axiom: {', '.join(overlap)}"
                    )
            if deps["structural"] != sorted(deps["structural"]):
                raise AssertionError(
                    f"{type_name} structural dependencies are out of order"
                )
            if "axiom" in deps:
                assert deps["axiom"] == sorted(deps["axiom"])
            for dep in deps["structural"] + deps.get("axiom", []):
                assert is_valid_dep(dep)

        # ---------------------------------------------------------------------
        # VERSIONED TYPES
        # ---------------------------------------------------------------------

        else:
            assert "versions" in entry
            assert "latest_version" in entry

            versions = entry["versions"]

            assert isinstance(versions, dict)
            assert len(versions) > 0

            # -----------------------------------------------------------------
            # Version format + ordering
            # -----------------------------------------------------------------

            version_keys = list(versions.keys())

            for v in version_keys:
                assert re.match(r"^\d{3}$", v), f"{type_name}:{v} not 3-digit"

            # must be strictly decreasing
            sorted_versions = sorted(version_keys, reverse=True)
            assert version_keys == sorted_versions, f"{type_name} not sorted"

            # latest_version must match highest
            assert entry["latest_version"] == version_keys[0]

            # -----------------------------------------------------------------
            # Created timestamps
            # -----------------------------------------------------------------

            timestamps = []

            for v in version_keys:
                v_entry = versions[v]

                assert "created" in v_entry
                ts = v_entry["created"]

                assert is_valid_ts(ts)
                timestamps.append((v, parse_ts(ts)))

            # uniqueness
            ts_values = [t for _, t in timestamps]
            assert len(ts_values) == len(set(ts_values)), f"{type_name} duplicate timestamps"

            # ordering consistency
            for i in range(len(timestamps) - 1):
                v_new, t_new = timestamps[i]
                v_old, t_old = timestamps[i + 1]

                assert int(v_new) > int(v_old)
                if not t_new > t_old:
                    raise AssertionError(
                        "\n".join(
                            [
                                f"- sema/definitions/registry.yaml has timestamps out of order for {type_name} versions",
                                f"- {v_new} is {versions[v_new]['created']}",
                                f"- {v_old} is {versions[v_old]['created']}",
                            ]
                        )
                    )

            # -----------------------------------------------------------------
            # Version entry structure
            # -----------------------------------------------------------------

            for v, v_entry in versions.items():

                assert "schema_url" in v_entry
                assert "created" in v_entry
                assert "summary" in v_entry
                assert "direct_dependencies" in v_entry

                # schema_url must match
                assert_schema_url_matches_versioned_type_name_and_version(
                    type_name, v, v_entry["schema_url"]
                )

                # dependencies structure
                deps = v_entry["direct_dependencies"]
                assert "structural" in deps

                if "axiom" in deps:
                    assert isinstance(deps["axiom"], list)

                # structural always list
                assert isinstance(deps["structural"], list)

                # no duplicates
                assert len(deps["structural"]) == len(set(deps["structural"]))

                if "axiom" in deps:
                    assert len(deps["axiom"]) == len(set(deps["axiom"]))
                    overlap = sorted(set(deps["structural"]) & set(deps["axiom"]))
                    if overlap:
                        raise AssertionError(
                            f"{type_name}:{v} has dependencies duplicated across structural and axiom: {', '.join(overlap)}"
                        )

                # sorted
                if deps["structural"] != sorted(deps["structural"]):
                    raise AssertionError(
                        f"{type_name}:{v} structural dependencies are out of order"
                    )
                if "axiom" in deps:
                    assert deps["axiom"] == sorted(deps["axiom"])

                # identifier format
                for dep in deps["structural"] + deps.get("axiom", []):
                    assert is_valid_dep(dep)

                    current_created = parse_ts(v_entry["created"])
                    for dep in deps["structural"] + deps.get("axiom", []):
                        dep_created_raw = get_created_for_dep(registry, dep)
                        dep_created = parse_ts(dep_created_raw)
                        if not current_created >= dep_created:
                            raise AssertionError(
                                "\n".join(
                                    [
                                    f"- sema/definitions/registry.yaml has dependency timestamps out of order for {type_name}:{v}",
                                    f"- {type_name}:{v} is {v_entry['created']}",
                                    f"- dependency {dep} is {dep_created_raw}",
                                ]
                            )
                            )


def test_type_versioning_strategy_matches_schema_version_field():
    registry = load_registry(DEFINITIONS_DIR / "registry.yaml")

    for type_name, entry in registry["types"].items():
        strategy = entry["versioning_strategy"]

        if strategy == "none":
            schema_path = DEFINITIONS_DIR / "types" / f"{type_name}.yaml"
            schema = load_registry(schema_path)
            properties = schema.get("properties", {})
            assert "Version" not in properties, (
                f"{type_name} has versioning_strategy 'none' but schema defines Version"
            )
            continue

        latest_version = entry["latest_version"]
        schema_path = DEFINITIONS_DIR / "types" / type_name / f"{latest_version}.yaml"
        schema = load_registry(schema_path)
        properties = schema.get("properties", {})

        assert "Version" in properties, (
            f"{type_name}:{latest_version} has versioning_strategy '{strategy}' but schema omits Version"
        )

        version_prop = properties["Version"]

        if strategy == "literal":
            assert version_prop == {"const": latest_version}, (
                f"{type_name}:{latest_version} has versioning_strategy 'literal' but Version is not "
                f'{{"const": "{latest_version}"}}'
            )

        elif strategy == "string":
            assert version_prop == {"type": "string", "default": latest_version}, (
                f"{type_name}:{latest_version} has versioning_strategy 'string' but Version is not "
                f'{{"type": "string", "default": "{latest_version}"}}'
            )

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def is_valid_ts(ts: str) -> bool:
    if not RFC3339_SECONDS_PATTERN.match(ts):
        return False
    try:
        parse_ts(ts)
        return True
    except Exception:
        return False


def is_valid_dep(dep: str) -> bool:
    if ":" in dep:
        name, version = dep.split(":")
        return re.match(r"^\d{3}$", version) is not None
    return True


def assert_schema_url_matches_format_name(format_name: str, schema_url: str) -> None:
    match = FORMAT_SCHEMA_URL_PATTERN.match(schema_url)
    if not match:
        raise AssertionError(
            f"{format_name} has invalid format schema_url: {schema_url}"
        )
    if match.group("name") != format_name:
        raise AssertionError(
            f"{format_name} schema_url name mismatch: {schema_url}"
        )


def assert_schema_url_matches_enum_name_and_version(
    enum_name: str, version: str, schema_url: str
) -> None:
    match = ENUM_SCHEMA_URL_PATTERN.match(schema_url)
    if not match:
        raise AssertionError(
            f"{enum_name}:{version} has invalid enum schema_url: {schema_url}"
        )
    if match.group("name") != enum_name:
        raise AssertionError(
            f"{enum_name}:{version} schema_url name mismatch: {schema_url}"
        )
    if match.group("version") != version:
        raise AssertionError(
            f"{enum_name}:{version} schema_url version mismatch: {schema_url}"
        )


def assert_schema_url_matches_versioned_type_name_and_version(
    type_name: str, version: str, schema_url: str
) -> None:
    match = VERSIONED_TYPE_SCHEMA_URL_PATTERN.match(schema_url)
    if not match:
        raise AssertionError(
            f"{type_name}:{version} has invalid versioned type schema_url: {schema_url}"
        )
    if match.group("name") != type_name:
        raise AssertionError(
            f"{type_name}:{version} schema_url name mismatch: {schema_url}"
        )
    if match.group("version") != version:
        raise AssertionError(
            f"{type_name}:{version} schema_url version mismatch: {schema_url}"
        )


def assert_schema_url_matches_versionless_type_name(
    type_name: str, schema_url: str
) -> None:
    match = VERSIONLESS_TYPE_SCHEMA_URL_PATTERN.match(schema_url)
    if not match:
        raise AssertionError(
            f"{type_name} has invalid versionless type schema_url: {schema_url}"
        )
    if match.group("name") != type_name:
        raise AssertionError(
            f"{type_name} schema_url name mismatch: {schema_url}"
        )
