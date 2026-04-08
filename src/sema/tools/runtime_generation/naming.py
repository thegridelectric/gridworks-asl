from __future__ import annotations

import re


def sema_name_to_module(name: str) -> str:
    return name.replace(".", "_").replace("-", "_")


def sema_name_to_class(name: str) -> str:
    parts = re.split(r"[.\-]", name)
    rendered: list[str] = []
    for part in parts:
        if not part:
            continue
        lower = part.lower()
        if lower == "utc":
            rendered.append("UTC")
            continue
        if lower.startswith("uuid") and lower[4:].isdigit():
            rendered.append("UUID" + lower[4:])
            continue
        rendered.append(part[:1].upper() + part[1:])
    return "".join(rendered)


def pascal_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def to_enum_member(value: str) -> str:
    member = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_")
    if not member:
        member = "Value"
    if member[0].isdigit():
        member = f"Value_{member}"
    return member


def class_name_for_node(
    node: tuple[str, str, str | None],
    latest_map: dict[tuple[str, str], str | None],
) -> str:
    kind, name, version = node
    base = sema_name_to_class(name)
    if kind == "format" or version is None:
        return base
    latest_version = latest_map.get((kind, name))
    if latest_version == version:
        return base
    return f"{base}{version}"
