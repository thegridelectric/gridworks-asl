"""Metaschema gate for vocabulary definitions.

Every schema file under ``definitions/{formats,enums,types}`` must itself be
valid JSON Schema 2020-12. A schema that violates the metaschema has
undefined validation behavior, and the runtime generator would otherwise
degrade silently (e.g. an illegal ``type: [{$ref: ...}, "null"]`` once
generated ``list[Any | None]``, masking a format mismatch). Shared by the
registry test suite and the runtime-regeneration build gate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import yaml
from jsonschema.exceptions import SchemaError
from jsonschema.validators import Draft202012Validator

SCHEMA_KINDS = ("formats", "enums", "types")


def iter_schema_files(definitions_root: Path) -> Iterator[Path]:
    for kind in SCHEMA_KINDS:
        kind_root = definitions_root / kind
        if kind_root.exists():
            yield from sorted(kind_root.rglob("*.yaml"))


def validate_definitions(definitions_root: Path) -> list[str]:
    """Return one finding per schema file that fails the 2020-12 metaschema."""
    findings: list[str] = []
    for path in iter_schema_files(definitions_root):
        schema = yaml.safe_load(path.read_text())
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as e:
            keyword_path = "/".join(str(p) for p in e.absolute_path) or "(top level)"
            findings.append(
                f"{path.relative_to(definitions_root.parent)}: at {keyword_path}: {e.message}"
            )
    return findings
