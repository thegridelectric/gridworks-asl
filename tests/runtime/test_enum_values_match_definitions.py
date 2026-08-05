"""Generated runtime enum values match the definition files, in order.

Consumers store enum states as positional indexes derived from ``values()``
on the generated classes, so the generated order must equal the definition
file's ``enum`` list exactly — an artifact-level check that catches a
generator reordering bug regardless of how the definitions evolve.
"""

import importlib
import pkgutil
from pathlib import Path

import yaml

import sema.runtime.enums as runtime_enums

REPO_ROOT = Path(__file__).resolve().parents[2]
ENUMS_ROOT = REPO_ROOT / "definitions" / "enums"


def _iter_enum_classes():
    packages = [runtime_enums]
    old_versions_name = f"{runtime_enums.__name__}.old_versions"
    try:
        packages.append(importlib.import_module(old_versions_name))
    except ModuleNotFoundError:
        pass
    seen: set[type] = set()
    for package in packages:
        for module_info in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"{package.__name__}.{module_info.name}")
            for attr in vars(module).values():
                if (
                    isinstance(attr, type)
                    and attr.__module__ == module.__name__
                    and hasattr(attr, "enum_name")
                    and hasattr(attr, "enum_version")
                    and hasattr(attr, "values")
                ):
                    if attr not in seen:
                        seen.add(attr)
                        yield attr


def test_runtime_enum_values_match_definitions() -> None:
    findings: list[str] = []
    checked = 0
    for cls in _iter_enum_classes():
        try:
            name = cls.enum_name()
            version = cls.enum_version()
        except NotImplementedError:
            continue  # the abstract base class
        definition_path = ENUMS_ROOT / name / f"{version}.yaml"
        if not definition_path.exists():
            findings.append(
                f"{cls.__name__}: no definition file at "
                f"definitions/enums/{name}/{version}.yaml"
            )
            continue
        defined = yaml.safe_load(definition_path.read_text()).get("enum", [])
        if cls.values() != defined:
            findings.append(
                f"{cls.__name__} ({name}/{version}): runtime values "
                f"{cls.values()} != definition {defined}"
            )
        checked += 1
    assert checked > 0, "No runtime enum classes found to check"
    assert not findings, "Runtime enums diverge from definitions:\n" + "\n".join(
        findings
    )
