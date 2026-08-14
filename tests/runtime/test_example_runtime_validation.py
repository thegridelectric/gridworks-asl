"""Every type example MUST decode against the runtime, not just be valid JSON.

Background (OPS-442): the suite checks type examples are valid JSON
(tests/registry/test_example_format.py) but did not decode them against the
runtime, so an example could go stale — reference a type that was reshaped in
place — while the main suite stayed green; the break then surfaced later at a
consumer's snapshot build (whose round-trip gate DOES decode every example).
This test closes the gap for ALL examples, replacing the earlier
grown-as-touched allowlist.

Decode semantics:
- Own version (auto_upgrade=False), matching the snapshot round-trip gate —
  a version behind a context-dependent upgrade still decodes at its own
  version.
- Draft versions are skipped: a draft generates no runtime class, so there is
  nothing to decode against. A NON-draft version whose examples cannot find a
  runtime class fails here (the decode raises Unknown type / Unsupported
  version), so a registered-but-ungenerated published version cannot hide.
- Versions without an `examples:` block are skipped — latest versions MAY
  omit an example (non-latest versions are required to carry one by
  tests/registry/test_superseded_examples.py).
"""

import json
from pathlib import Path

import pytest
import yaml

from sema.runtime.codec import default_codec

REPO_ROOT = Path(__file__).resolve().parents[2]
TYPES_DIR = REPO_ROOT / "definitions" / "types"


def _example_bearing_schemas() -> list[tuple[str, Path]]:
    """(test-id, schema-path) for every non-draft type schema carrying examples."""
    cases = []
    paths = sorted(TYPES_DIR.glob("*.yaml")) + sorted(TYPES_DIR.glob("*/*.yaml"))
    for path in paths:
        schema = yaml.safe_load(path.read_text())
        if "/draft/" in schema.get("$id", ""):
            continue
        if not schema.get("examples"):
            continue
        rel = path.relative_to(TYPES_DIR)
        cases.append((str(rel.with_suffix("")).replace("/", "_"), path))
    return cases


CASES = _example_bearing_schemas()


@pytest.mark.parametrize(
    "schema_path", [path for _, path in CASES], ids=[case_id for case_id, _ in CASES]
)
def test_example_decodes_against_runtime(schema_path: Path) -> None:
    schema = yaml.safe_load(schema_path.read_text())
    for i, ex in enumerate(schema["examples"]):
        # Caught before the decode so the YAML-mapping mistake reports as
        # itself: json.loads on a dict raises a bare TypeError that says
        # nothing about the rule it broke.
        if not isinstance(ex, str):
            raise AssertionError(
                f"{schema_path.relative_to(REPO_ROOT)} examples[{i}] is a "
                f"{type(ex).__name__}, not a JSON string. \"Examples SHALL be "
                "serialized JSON documents, not YAML object representations\" "
                "(spec/authoring/types.md \"Examples\"). Write it as a block "
                "scalar:\n"
                "    examples:\n"
                "      - |\n"
                "        {\n"
                '          "TypeName": "your.type.name",\n'
                '          "Version": "000"\n'
                "        }"
            )
        try:
            default_codec.from_dict(json.loads(ex), auto_upgrade=False)
        except Exception as exc:  # noqa: BLE001 - surface the decode failure verbatim
            raise AssertionError(
                f"{schema_path.relative_to(REPO_ROOT)} examples[{i}] does not decode "
                f"against the runtime at its own version: {exc}"
            ) from exc
