import re
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REGISTRY_PATH = REPO_ROOT / "indexes" / "public_registry.yaml"
DEPENDENCY_CLOSURE_PATH = REPO_ROOT / "indexes" / "dependency_closure.yaml"
AXIOM_TEMPLATE_DIR = (
    REPO_ROOT / "src" / "sema" / "tools" / "runtime_generation" / "templates" / "axioms"
)
UPGRADE_TEMPLATE_DIR = (
    REPO_ROOT / "src" / "sema" / "tools" / "runtime_generation" / "templates" / "upgrades"
)
JINJA_VARIABLE_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def template_identifier(sema_name: str, version: str) -> str:
    return f"{sema_name.replace('.', '_')}_{version}_class_name"


def class_name_variable_refs(template_path: Path) -> set[str]:
    return {
        variable
        for variable in JINJA_VARIABLE_RE.findall(template_path.read_text())
        if variable.endswith("_class_name")
    }


def registry_template_variable_map(registry: dict[str, Any]) -> dict[str, str]:
    variables: dict[str, str] = {}
    for section in ("enums", "types"):
        for sema_name, entry in registry[section].items():
            versions = entry.get("versions")
            if versions is None:
                if section == "enums" and entry["enum_type"] == "literal":
                    versions = {"000": entry}
                else:
                    continue
            for version in versions:
                variables[template_identifier(sema_name, version)] = (
                    f"{sema_name}:{version}"
                )
    return variables


def closure_refs(
    closure: dict[str, Any],
    sema_name: str,
    version: str,
) -> set[str]:
    type_closure = closure["types"][sema_name][version]
    return (
        set(type_closure["types"])
        | set(type_closure["enums"])
        | {f"{sema_name}:{version}"}
    )


def axiom_template_target(template_path: Path) -> tuple[str, str]:
    stem = template_path.name.removesuffix(".py.jinja2")
    sema_name, version = stem.rsplit("_", 1)
    return sema_name.replace("_", "."), version


def upgrade_template_target(template_path: Path) -> tuple[str, str, str]:
    stem = template_path.name.removesuffix(".py.jinja2")
    sema_name, source_version, _, target_version = stem.rsplit("_", 3)
    return sema_name.replace("_", "."), source_version, target_version


def test_logic_template_class_refs_are_in_dependency_closure() -> None:
    registry = load_yaml(PUBLIC_REGISTRY_PATH)
    closure = load_yaml(DEPENDENCY_CLOSURE_PATH)
    variable_to_ref = registry_template_variable_map(registry)

    findings: list[str] = []

    for template_path in sorted(AXIOM_TEMPLATE_DIR.glob("*.py.jinja2")):
        sema_name, version = axiom_template_target(template_path)
        if sema_name not in closure["types"] or version not in closure["types"][sema_name]:
            continue
        allowed_refs = closure_refs(closure, sema_name, version)

        for variable in sorted(class_name_variable_refs(template_path)):
            ref = variable_to_ref.get(variable)
            if ref is None:
                findings.append(f"{template_path.name}: unknown template variable {variable}")
            elif ref not in allowed_refs:
                findings.append(
                    f"{template_path.name}: {ref} is referenced by template logic "
                    f"but is not in dependency_closure.types.{sema_name}.{version}"
                )

    for template_path in sorted(UPGRADE_TEMPLATE_DIR.glob("*.py.jinja2")):
        sema_name, source_version, target_version = upgrade_template_target(template_path)
        if (
            sema_name not in closure["types"]
            or source_version not in closure["types"][sema_name]
        ):
            continue
        allowed_refs = closure_refs(closure, sema_name, source_version)
        allowed_refs.add(f"{sema_name}:{target_version}")
        if target_version in closure["types"].get(sema_name, {}):
            allowed_refs |= closure_refs(closure, sema_name, target_version)

        for variable in sorted(class_name_variable_refs(template_path)):
            ref = variable_to_ref.get(variable)
            if ref is None:
                findings.append(f"{template_path.name}: unknown template variable {variable}")
            elif ref not in allowed_refs:
                findings.append(
                    f"{template_path.name}: {ref} is referenced by template logic "
                    f"but is not in dependency_closure.types.{sema_name}.{source_version}"
                )

    assert not findings, "\n" + "\n".join(findings)
