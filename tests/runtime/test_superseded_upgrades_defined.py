"""Guard: every superseded published version's upgrade is *defined*.

The scaffold tool seeds new upgrade templates with `raise NotImplementedError`
(see test_scaffold_upgrade_template). This guard catches a left-behind stub: for
every superseded published type version that carries an example, decoding it with
auto_upgrade must reach the latest version — or deliberately refuse with
`UpgradeRequiresContext` (the spec-sanctioned outcome for context-dependent
upgrades). A `NotImplementedError` means the upgrade was never implemented.
"""
import json
from pathlib import Path

import pytest
import yaml

from sema.runtime.base import UpgradeRequiresContext
from sema.runtime.codec import SemaCodec

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = yaml.safe_load((REPO_ROOT / "definitions" / "registry.yaml").read_text())


def _superseded_with_examples():
    cases = []
    for type_name, entry in sorted(REGISTRY["types"].items()):
        if entry.get("versioning_strategy") == "none":
            continue
        latest = entry.get("latest_version")
        for version in sorted((entry.get("versions") or {}), key=int):
            ver_entry = entry["versions"][version]
            if ver_entry.get("status", "published") == "draft" or version == latest:
                continue
            schema = REPO_ROOT / "definitions" / "types" / type_name / f"{version}.yaml"
            if not schema.exists():
                continue
            data = yaml.safe_load(schema.read_text())
            examples = data.get("examples")
            if examples:
                cases.append((type_name, version, latest, examples[0]))
    return cases


@pytest.mark.parametrize(
    "type_name,version,latest,example",
    _superseded_with_examples(),
    ids=[f"{tn}_{v}_to_{lv}" for tn, v, lv, _ in _superseded_with_examples()],
)
def test_superseded_upgrade_is_defined(type_name, version, latest, example) -> None:
    codec = SemaCodec()
    try:
        codec.from_dict(json.loads(example), auto_upgrade=True)
    except UpgradeRequiresContext:
        # Deliberate, spec-sanctioned refusal for context-dependent upgrades.
        pass
    except NotImplementedError as exc:  # pragma: no cover - this is the guard
        pytest.fail(
            f"{type_name}/{version} -> {latest} upgrade is an unimplemented stub: {exc}"
        )
