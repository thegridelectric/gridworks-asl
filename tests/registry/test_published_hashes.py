"""The published-immutability tripwire.

Every published schema file's sha256 must match its pin in
``definitions/published_hashes.yaml``. Three failure modes, three messages:

- **changed pin** — a published schema file was edited in place. The fix is a
  NEW version, never an in-place change.
- **missing pin** — a version was published (status flipped) without recording
  its hash. Run ``uv run python -m sema.tools.published_hashes`` (or promote
  via ``sema promote``, which records the pin).
- **orphan pin** — a pin exists for something no longer published. Statuses
  only move toward published, so this indicates a registry edit that needs a
  human look.
"""

import yaml

from sema.tools.published_hashes import (
    DEFINITIONS_DIR,
    PINS_PATH,
    compute_published_hashes,
    load_pins,
)


def _flatten(pins: dict) -> dict[str, str]:
    flat: dict[str, str] = {}
    for kind in ("formats", "enums", "types"):
        for name, value in pins.get(kind, {}).items():
            if isinstance(value, str):
                flat[f"{kind}/{name}"] = value
            else:
                for version, digest in value.items():
                    flat[f"{kind}/{name}:{version}"] = digest
    return flat


def test_published_schema_files_match_pins() -> None:
    assert PINS_PATH.exists(), (
        "definitions/published_hashes.yaml is missing. Create it with:\n"
        "  uv run python -m sema.tools.published_hashes"
    )
    registry = yaml.safe_load((DEFINITIONS_DIR / "registry.yaml").read_text())
    computed = _flatten(compute_published_hashes(registry))
    pinned = _flatten(load_pins())

    changed = sorted(
        key for key in computed.keys() & pinned.keys() if computed[key] != pinned[key]
    )
    missing = sorted(computed.keys() - pinned.keys())
    orphaned = sorted(pinned.keys() - computed.keys())

    problems = []
    if changed:
        problems.append(
            "published schema files EDITED IN PLACE (author a new version instead):\n    "
            + "\n    ".join(changed)
        )
    if missing:
        problems.append(
            "published versions with no pin (run "
            "`uv run python -m sema.tools.published_hashes`):\n    "
            + "\n    ".join(missing)
        )
    if orphaned:
        problems.append(
            "pins for entries that are no longer published:\n    "
            + "\n    ".join(orphaned)
        )
    assert not problems, "Published-hash pin violations:\n  " + "\n  ".join(problems)
