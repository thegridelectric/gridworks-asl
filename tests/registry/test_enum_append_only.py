"""Versioned enums evolve append-only, mechanically enforced.

The spec (spec/authoring/enums.md "Evolution Rules") requires that a new
enum version only append values: prior values keep their relative order and
none are removed or reordered. Published-hash pinning freezes each version's
own file but says nothing across versions — this test closes that gap by
requiring each version's ``enum`` list to start with the previous version's
list verbatim. Consumers store enum states as positional indexes, so a
mid-list insertion would silently change the meaning of already-stored
integers.
"""

import re
from pathlib import Path

import yaml

ENUMS_ROOT = Path(__file__).resolve().parents[2] / "definitions" / "enums"
VERSION_RE = re.compile(r"^\d{3}$")


def test_enum_versions_append_only() -> None:
    findings: list[str] = []
    for enum_dir in sorted(p for p in ENUMS_ROOT.iterdir() if p.is_dir()):
        versions = sorted(
            p.stem for p in enum_dir.glob("*.yaml") if VERSION_RE.match(p.stem)
        )
        if len(versions) < 2:
            continue
        values_by_version = {
            v: yaml.safe_load((enum_dir / f"{v}.yaml").read_text()).get("enum", [])
            for v in versions
        }
        for prev, nxt in zip(versions, versions[1:]):
            prev_values = values_by_version[prev]
            nxt_values = values_by_version[nxt]
            if nxt_values[: len(prev_values)] != prev_values:
                findings.append(
                    f"{enum_dir.name}: {nxt} does not start with {prev}'s values "
                    f"verbatim ({prev}: {prev_values} vs {nxt}: {nxt_values})"
                )
    assert not findings, "Enum versions violate append-only evolution:\n" + "\n".join(
        findings
    )
