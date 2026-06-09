"""A version's upgrade delta is recorded in two human-readable places that
MUST stay in sync: the upgrade template's docstring and the registry summary.

For every upgrade template
``templates/upgrades/<type_snake>_<a>_to_<b>.py.jinja2`` there is a registry
entry ``types.<type>.versions.<b>.summary``. Both are the prose change-list for
the ``<a> -> <b>`` step, and by convention they are mirror copies. This test
asserts they are equal (modulo whitespace).

Why it exists: the `layout.lite` `007 -> 008` upgrade once lifted no embedded
``ShNodes`` and its registry summary likewise omitted the
``spaceheat.node.gt:200 -> 300`` line, while ``direct_dependencies`` already
carried the truth — so the prose drifted silently from the machine record. This
gate catches that drift: editing one side without the other fails here. The
deeper requirement (nested sub-types whose version changes between two versions
MUST be lifted in the upgrade body) is in ``spec/authoring/type-semantics.md``
"Nested Upgrades".
"""

from __future__ import annotations

import re
from pathlib import Path

from sema.tools.build_public_registry import load_registry

REPO_ROOT = Path(__file__).resolve().parents[2]
UPGRADES_DIR = (
    REPO_ROOT / "src" / "sema" / "tools" / "runtime_generation" / "templates" / "upgrades"
)
_NAME_RE = re.compile(r"^(?P<snake>.+)_(?P<a>\d{3})_to_(?P<b>\d{3})$")
_DOCSTRING_RE = re.compile(r'"""(.*?)"""', re.DOTALL)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def test_upgrade_template_docstring_matches_registry_summary() -> None:
    registry = load_registry()
    types = registry["types"]
    findings: list[str] = []

    for path in sorted(UPGRADES_DIR.glob("*.py.jinja2")):
        stem = path.name[: -len(".py.jinja2")]
        m = _NAME_RE.match(stem)
        if not m:
            findings.append(f"{path.name}: filename is not <type>_<NNN>_to_<NNN>")
            continue
        dotted = m.group("snake").replace("_", ".")
        target_version = m.group("b")

        doc_match = _DOCSTRING_RE.search(path.read_text())
        if not doc_match:
            findings.append(f"{path.name}: no docstring found in upgrade template")
            continue
        docstring = _normalize(doc_match.group(1))

        entry = types.get(dotted)
        if entry is None or "versions" not in entry:
            findings.append(f"{path.name}: no versioned registry entry for type '{dotted}'")
            continue
        version_entry = entry["versions"].get(target_version)
        if version_entry is None:
            findings.append(
                f"{path.name}: registry has no version '{target_version}' for '{dotted}'"
            )
            continue
        summary = _normalize(version_entry.get("summary"))

        if docstring != summary:
            findings.append(
                f"{dotted} {m.group('a')}->{target_version}: upgrade docstring and "
                f"registry summary disagree.\n"
                f"      docstring: {docstring}\n"
                f"      summary  : {summary}"
            )

    assert not findings, (
        "Upgrade docstring / registry summary mismatches — reconcile BOTH the "
        "template docstring and `versions.<b>.summary` (and check the change is "
        "reflected in `direct_dependencies`):\n  " + "\n  ".join(findings)
    )
