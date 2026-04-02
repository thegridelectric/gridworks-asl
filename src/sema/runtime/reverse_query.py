from __future__ import annotations

import yaml
from pathlib import Path
from typing import Set, Tuple


def find_repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "definitions").exists() and (parent / "indexes").exists():
            return parent
    raise RuntimeError("Could not locate repo root (definitions/ and indexes/ not found)")


ROOT = find_repo_root()
REVERSE_PATH = ROOT / "indexes" / "reverse_dependencies.yaml"


def load_reverse_index() -> dict:
    with open(REVERSE_PATH, "r") as f:
        return yaml.safe_load(f)


def _key(name: str, version: str | None) -> str:
    return f"{name}:{version}" if version else name



def reverse_transitive(
    *,
    category: str,   # "type" | "enum" | "format"
    name: str,
    version: str | None = None,
) -> Set[str]:
    """
    Returns all nodes that depend (directly or transitively) on the given node.

    Output format: set of "type:version"
    """

    reverse = load_reverse_index()

    visited: Set[str] = set()
    stack: list[Tuple[str, str | None, str]] = [(category, name, version)]

    result: Set[str] = set()

    while stack:
        cat, n, v = stack.pop()

        if cat == "type":
            users = reverse.get("types", {}).get(n, {}).get(v, {}).get("used_by", [])

        elif cat == "enum":
            users = reverse.get("enums", {}).get(n, {}).get(v, {}).get("used_by", [])

        elif cat == "format":
            users = reverse.get("formats", {}).get(n, {}).get("used_by", [])

        else:
            raise ValueError(f"Unknown category: {cat}")

        for user in users:
            if user in visited:
                continue

            visited.add(user)
            result.add(user)

            # user is always a type:version
            user_name, user_version = user.split(":")

            stack.append(("type", user_name, user_version))

    return result