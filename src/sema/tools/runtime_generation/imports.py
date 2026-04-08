from __future__ import annotations

from sema.tools.runtime_generation.naming import class_name_for_node, sema_name_to_module


def import_path_and_symbol_for_node(
    node: tuple[str, str, str | None],
    latest_map: dict[tuple[str, str], str | None],
    package_name: str,
) -> tuple[str, str]:
    kind, name, version = node
    if kind == "format":
        return (f"{package_name}.sema.property_format", class_name_for_node(node, latest_map))

    module_name = sema_name_to_module(name)
    symbol_name = class_name_for_node(node, latest_map)
    if version is not None and latest_map[(kind, name)] != version:
        module_name = f"{module_name}_{version}"
        return (f"{package_name}.sema.{kind}s.old_versions.{module_name}", symbol_name)
    return (f"{package_name}.sema.{kind}s.{module_name}", symbol_name)


def target_path_for_node(
    node: tuple[str, str, str | None],
    latest_map: dict[tuple[str, str], str | None],
    output_root,
):
    kind, name, version = node
    module_name = sema_name_to_module(name)
    if kind == "format":
        raise ValueError("Formats are written into property_format.py")
    if version is not None and latest_map[(kind, name)] != version:
        return output_root / f"{kind}s" / "old_versions" / f"{module_name}_{version}.py"
    return output_root / f"{kind}s" / f"{module_name}.py"
