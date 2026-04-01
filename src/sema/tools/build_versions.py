from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "definitions" / "registry.yaml"
OUTPUT_PATH = ROOT / "indexes" / "versions.yaml"
HEADER = """# GENERATED FILE — DO NOT EDIT
# Generated from definitions/registry.yaml
"""


def load_registry() -> dict:
    with open(REGISTRY_PATH, "r") as f:
        return yaml.safe_load(f)


def enum_note(enum_type: str) -> str:
    if enum_type == "literal":
        return "This enum is literal; version 000 is immutable and exclusive."
    return "This enum is versioned; new versions are additive only."


def fallback_summary(version: str, version_info: dict, latest_version: str) -> str:
    if "summary" in version_info:
        return version_info["summary"]
    if version == "000" and latest_version == "000":
        return "Initial and only version."
    if version == "000":
        return "Initial version."
    return f"Version {version}."


def quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def normalize_summary(summary: str) -> str:
    summary = summary.strip()
    if not summary.startswith("- "):
        return summary

    parts = summary.split(" - ")
    lines: list[str] = []
    for idx, part in enumerate(parts):
        text = part.strip()
        if not text:
            continue
        if idx == 0 and text.startswith("- "):
            lines.append(text)
        else:
            lines.append(f"- {text}")
    return "\n".join(lines)


def append_summary(lines: list[str], indent: str, summary: str) -> None:
    normalized = normalize_summary(summary)
    summary_lines = normalized.splitlines()
    if len(summary_lines) <= 1:
        lines.append(f"{indent}summary: {quote(normalized)}")
        return

    lines.append(f"{indent}summary: >")
    for part in summary_lines:
        lines.append(f"{indent}  {part}")


def build() -> None:
    registry = load_registry()
    lines: list[str] = [HEADER, "", "types:"]

    for type_name, type_def in registry["types"].items():
        lines.append(f"  {type_name}:")
        strategy = type_def["versioning_strategy"]

        if strategy == "none":
            lines.append(f'    versioning_strategy: "{strategy}"')
            lines.append(f"    summary: {quote(type_def['summary'])}")
            lines.append("")
            continue

        lines.append(f'    latest_version: "{type_def["latest_version"]}"')
        lines.append(f'    versioning_strategy: "{strategy}"')
        lines.append("    versions:")

        for version, version_info in type_def.get("versions", {}).items():
            lines.append(f'      "{version}":')
            append_summary(
                lines,
                "        ",
                fallback_summary(version, version_info, type_def["latest_version"]),
            )

        lines.append("")

    if lines[-1] == "":
        lines.pop()

    lines.append("")
    lines.append("enums:")

    for enum_name, enum_def in registry["enums"].items():
        latest_version = enum_def["latest_version"]
        latest_info = enum_def["versions"][latest_version]
        top_enum_type = latest_info["enum_type"]

        lines.append(f"  {enum_name}:")
        lines.append(f'    enum_type: "{top_enum_type}"')
        lines.append(f"    note: {quote(enum_note(top_enum_type))}")
        lines.append("    versions:")

        for version, version_info in enum_def.get("versions", {}).items():
            lines.append(f'      "{version}":')
            append_summary(
                lines,
                "        ",
                fallback_summary(version, version_info, latest_version),
            )

        lines.append("")

    if lines[-1] == "":
        lines.pop()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote versions to {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
