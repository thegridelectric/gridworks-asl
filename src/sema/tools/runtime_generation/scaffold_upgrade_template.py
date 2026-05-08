from __future__ import annotations

from pathlib import Path

import yaml

from sema.tools.runtime_generation.helpers import (
    REPO_ROOT,
    sema_name_to_template_identifier,
)


DEFINITIONS_TYPES_DIR = REPO_ROOT / "definitions" / "types"
UPGRADE_TEMPLATE_DIR = (
    REPO_ROOT / "src" / "sema" / "tools" / "runtime_generation" / "templates" / "upgrades"
)


def scaffold_upgrade_template(
    type_name: str,
    version: str,
    next_version: str,
    *,
    upgrade_template_dir: Path = UPGRADE_TEMPLATE_DIR,
) -> Path:
    """Create a stub upgrade template for ``type_name`` v ``version`` -> ``next_version``.

    Existing templates are returned unchanged (idempotent). Newly created
    templates render an ``upgrade()`` method with a ``NotImplementedError``,
    forcing hand-written upgrade logic to be added before the next codegen.
    """
    template_id = sema_name_to_template_identifier(type_name)
    template_path = (
        upgrade_template_dir
        / f"{template_id}_{version}_to_{next_version}.py.jinja2"
    )
    if template_path.exists():
        return template_path

    next_class_name_variable = f"{template_id}_{next_version}_class_name"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(
        f"    def upgrade(self) -> {{{{ {next_class_name_variable} }}}}:\n"
        f'        """Upgrade {type_name}:{version} -> {next_version}."""\n'
        f"        raise NotImplementedError(\n"
        f'            "{type_name}:{version} -> {next_version} upgrade not implemented"\n'
        f"        )\n"
    )
    return template_path


def scaffold_upgrade_templates_for_seed(
    seed: dict,
    *,
    definitions_types_dir: Path = DEFINITIONS_TYPES_DIR,
    upgrade_template_dir: Path = UPGRADE_TEMPLATE_DIR,
) -> list[Path]:
    """Ensure upgrade templates exist for every non-latest type version in ``seed``.

    For each type in the expanded seed worklist, sort the included versions
    ascending and pair consecutive versions. Each (vN -> vN+1) pair requires
    a Jinja upgrade template; ``scaffold_upgrade_template`` creates a
    ``NotImplementedError`` stub if one is missing. Existing templates are
    returned unchanged.

    Versionless types (``versioning_strategy: "none"``) and types with only
    one version selected have no upgrade chain and are skipped.
    """
    paths: list[Path] = []
    for type_name, entry in sorted(seed.get("worklist", {}).get("types", {}).items()):
        if entry.get("versioning_strategy") == "none":
            continue
        versions = sorted(
            (key for key in entry if isinstance(key, str) and key.isdigit()),
            key=int,
        )
        if len(versions) < 2:
            continue
        # Ensure each version's schema exists before scaffolding (catches
        # registry/seed drift early with a clearer error).
        for version in versions:
            schema_path = definitions_types_dir / type_name / f"{version}.yaml"
            if not schema_path.exists():
                raise ValueError(f"Missing type schema: {schema_path}")
            yaml.safe_load(schema_path.read_text())  # parse-ability check
        for version, next_version in zip(versions, versions[1:]):
            paths.append(
                scaffold_upgrade_template(
                    type_name,
                    version,
                    next_version,
                    upgrade_template_dir=upgrade_template_dir,
                )
            )
    return paths
