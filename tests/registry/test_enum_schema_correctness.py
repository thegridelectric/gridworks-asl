import re
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ENUMS_DIR = REPO_ROOT / "definitions" / "enums"
ENUM_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
ENUM_ID_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/enums/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)/(?P<version>\d{3})$"
)
ALLOWED_TOP_LEVEL_KEYS = {
    "$schema",
    "$id",
    "title",
    "type",
    "description",
    "enum",
    "default",
    "x-gridworks",
}
ALLOWED_X_GRIDWORKS_KEYS = {
    "owner",
    "version",
    "value_descriptions",
    "extended_description",
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def enum_item_lines(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    in_enum = False
    items: list[str] = []
    for line in lines:
        if not in_enum:
            if line.strip() == "enum:":
                in_enum = True
            continue
        if not line.startswith("  - "):
            if line.strip() == "":
                continue
            break
        items.append(line.strip())
    return items


def test_enum_schema_correctness() -> None:
    findings: list[str] = []

    for path in sorted(ENUMS_DIR.glob("*/*.yaml")):
        enum_name = path.parent.name
        version = path.stem
        schema = load_yaml(path)

        extra_keys = sorted(set(schema) - ALLOWED_TOP_LEVEL_KEYS)
        if extra_keys:
            findings.append(f"{path} has unsupported top-level keys: {extra_keys}")

        if not ENUM_NAME_PATTERN.match(enum_name):
            findings.append(f"{path} has invalid enum name {enum_name}")

        if not re.match(r"^\d{3}$", version):
            findings.append(f"{path} must use a 3-digit version filename")

        schema_id = schema.get("$id")
        if not isinstance(schema_id, str):
            findings.append(f"{path} missing string $id")
        else:
            match = ENUM_ID_PATTERN.match(schema_id)
            if not match:
                findings.append(f"{path} has non-canonical $id: {schema_id}")
            else:
                id_name = match.group("name")
                id_version = match.group("version")
                if id_name != enum_name:
                    findings.append(
                        f"{path} $id name mismatch: file has {enum_name}, $id has {id_name}"
                    )
                if id_version != version:
                    findings.append(
                        f"{path} $id version mismatch: file has {version}, $id has {id_version}"
                    )

        title = schema.get("title")
        if title != enum_name:
            findings.append(f"{path} title mismatch: expected {enum_name}, got {title}")

        if schema.get("type") not in {"string", "integer"}:
            findings.append(f"{path} must have type: string or integer")

        enum_values = schema.get("enum")
        if not isinstance(enum_values, list) or not enum_values:
            findings.append(f"{path} must define a non-empty enum list")
        elif schema.get("type") == "string":
            for item_line in enum_item_lines(path):
                if not re.match(r'^-\s+["\'].*["\']$', item_line):
                    findings.append(
                        f"{path} string enum values must be quoted; found unquoted item line: {item_line}"
                    )

        default_value = schema.get("default")
        if default_value is None:
            findings.append(f"{path} missing default")
        elif isinstance(enum_values, list) and default_value not in enum_values:
            findings.append(f"{path} default must be one of the enum values")

        xg = schema.get("x-gridworks")
        if not isinstance(xg, dict):
            findings.append(f"{path} missing x-gridworks block")
            continue

        extra_xg_keys = sorted(set(xg) - ALLOWED_X_GRIDWORKS_KEYS)
        if extra_xg_keys:
            findings.append(f"{path} x-gridworks has unsupported keys: {extra_xg_keys}")

        schema_version = xg.get("version")
        if schema_version != version:
            findings.append(
                f"{path} x-gridworks.version mismatch: file has {version}, schema has {schema_version}"
            )

        if "owner" not in xg or not isinstance(xg["owner"], str):
            findings.append(f"{path} missing string x-gridworks.owner")

    if findings:
        raise AssertionError("\n".join(findings))
