"""``sema promote <name> [version]`` — the human act that publishes a word.

Promotion flips a STAGING entry to PUBLISHED: it verifies the entry's full
dependency closure is already published, flips the one ``status`` line in
``registry.yaml`` (a text edit — ``created`` and everything else stay
byte-identical), records the schema file's content hash in
``definitions/published_hashes.yaml``, bumps ``metadata.last_updated``, and
regenerates ``indexes/public_registry.yaml``.

Draft entries are not promotable here: draft -> staging/published is authoring
work (the ``$id`` URL changes), not a status flip.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from typing import Any

import yaml

from sema.tools.build_public_registry import (
    REGISTRY_PATH,
    build as rebuild_public_registry,
    split_dep,
)
from sema.tools.published_hashes import (
    _schema_path,
    _sha256,
    load_pins,
    write_pins,
)


def _locate(registry: dict[str, Any], name: str) -> tuple[str, dict[str, Any], bool]:
    """(section, entry, word_level_status) for a vocabulary word."""
    for section in ("formats", "enums", "types"):
        entry = registry[section].get(name)
        if entry is None:
            continue
        if section == "formats":
            return section, entry, True
        if section == "enums":
            return section, entry, entry["enum_type"] == "literal"
        return section, entry, entry["versioning_strategy"] == "none"
    raise ValueError(f"{name}: not in the registry")


def _dep_status(registry: dict[str, Any], dep: str) -> str:
    dep_name, dep_version = split_dep(dep)
    section, entry, word_level = _locate(registry, dep_name)
    if word_level:
        return entry["status"]
    version_entry = entry.get("versions", {}).get(dep_version)
    if version_entry is None:
        raise ValueError(f"dependency {dep}: version not in the registry")
    return version_entry["status"]


def _rounded_utc_now() -> str:
    epoch = int(
        subprocess.run(["date", "-u", "+%s"], capture_output=True, text=True).stdout
    )
    rounded = round(epoch / 300) * 300
    return subprocess.run(
        ["date", "-u", "-r", str(rounded), "+%Y-%m-%dT%H:%M:00Z"],
        capture_output=True,
        text=True,
    ).stdout.strip()


def _flip_status_line(name: str, version: str | None) -> None:
    """Rewrite exactly one ``status: "staging"`` line to published, plus the
    metadata ``last_updated`` bump. Everything else stays byte-identical."""
    lines = REGISTRY_PATH.read_text().splitlines(keepends=True)
    word_re = re.compile(rf"^  {re.escape(name)}:\s*$")
    any_word_re = re.compile(r"^  [a-z0-9][a-z0-9.]*:\s*$")
    any_version_re = re.compile(r'^      "\d{3}":\s*$')

    in_word = in_version = False
    flipped = False
    for i, line in enumerate(lines):
        if line.startswith("  last_updated:"):
            lines[i] = f'  last_updated: "{_rounded_utc_now()}"\n'
            continue
        if any_word_re.match(line):
            in_word = bool(word_re.match(line))
            in_version = False
            continue
        if in_word and any_version_re.match(line):
            in_version = line.strip() == f'"{version}":'
            continue
        in_target = in_word and (in_version if version is not None else True)
        if in_target and line.strip() == 'status: "staging"':
            indent = line[: len(line) - len(line.lstrip())]
            lines[i] = f'{indent}status: "published"\n'
            flipped = True
            break
    if not flipped:
        raise ValueError(
            f"could not find the staging status line for "
            f"{name}{'/' + version if version else ''} in registry.yaml"
        )
    REGISTRY_PATH.write_text("".join(lines))


def promote(name: str, version: str | None) -> None:
    registry = yaml.safe_load(REGISTRY_PATH.read_text())
    section, entry, word_level = _locate(registry, name)

    if word_level:
        if version is not None:
            raise ValueError(f"{name} carries word-level status; omit the version")
        status = entry["status"]
        version_entry = entry
    else:
        if version is None:
            raise ValueError(f"{name} is versioned; a version is required")
        version_entry = entry.get("versions", {}).get(version)
        if version_entry is None:
            raise ValueError(f"{name}:{version} not in the registry")
        status = version_entry["status"]

    label = name if version is None else f"{name}:{version}"
    if status == "published":
        raise ValueError(f"{label} is already published")
    if status == "draft":
        raise ValueError(
            f"{label} is draft — promote handles staging -> published only; "
            "finishing a draft (canonical $id, examples, deps) is authoring work"
        )

    direct = version_entry.get("direct_dependencies", {})
    unpublished = [
        f"{dep} (status: {_dep_status(registry, dep)})"
        for dep in direct.get("structural", []) + direct.get("axiom", [])
        if _dep_status(registry, dep) != "published"
    ]
    if unpublished:
        raise ValueError(
            f"{label}: cannot promote — dependencies must be published first:\n  "
            + "\n  ".join(sorted(unpublished))
        )

    _flip_status_line(name, version)

    # record the immutability pin (literal enums carry word-level status but
    # their schema file lives at <name>/000.yaml)
    pin_version = version
    if section == "enums" and entry["enum_type"] == "literal":
        pin_version = "000"
    digest = _sha256(_schema_path(section, name, pin_version))
    pins = load_pins()
    if word_level:
        pins[section][name] = digest
    else:
        pins[section].setdefault(name, {})[version] = digest
        pins[section][name] = dict(sorted(pins[section][name].items()))
    write_pins(pins)

    rebuild_public_registry()
    print(f"promoted {label}: staging -> published (pin recorded)")


def _run_promote(args: argparse.Namespace) -> None:
    promote(args.name, args.version)


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "promote",
        help="Promote a staging word/version to published (records its hash pin).",
        description=(
            "Flip a STAGING entry to PUBLISHED after verifying its dependency "
            "closure is already published. Records the schema file's sha256 in "
            "definitions/published_hashes.yaml and regenerates "
            "indexes/public_registry.yaml. Promotion never touches `created`."
        ),
    )
    parser.add_argument("name", help="vocabulary word, e.g. layout.lite")
    parser.add_argument(
        "version",
        nargs="?",
        default=None,
        help="3-digit version for versioned words (omit for word-level status)",
    )
    parser.set_defaults(handler=_run_promote)
