from __future__ import annotations

from pathlib import Path

import yaml


def load_schema_for_node(
    node: tuple[str, str, str | None],
    seed: dict,
    definitions_root: Path,
) -> dict:
    kind, name, version = node
    if kind == "format":
        relative_path = seed["worklist"]["formats"][name]["path"]
    elif kind == "enum":
        relative_path = seed["worklist"]["enums"][name][version]["path"]
    elif kind == "type":
        type_entry = seed["worklist"]["types"][name]
        if version is None:
            relative_path = type_entry["path"]
        else:
            relative_path = type_entry[version]["path"]
    else:
        raise ValueError(f"Schema loading not supported for node: {node}")
    definition_path = definitions_root / Path(relative_path).relative_to("definitions")
    return yaml.safe_load(definition_path.read_text())
