from __future__ import annotations

import argparse
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "definitions" / "registry.yaml"
DEFAULT_SEED = ROOT / "output" / "seed_expanded.yaml"

FORMAT_REF_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/formats/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)$"
)
ENUM_REF_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/enums/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)/(?P<version>\d{3})$"
)
VERSIONED_TYPE_REF_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/types/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)/(?P<version>\d{3})$"
)
VERSIONLESS_TYPE_REF_PATTERN = re.compile(
    r"^https://schemas\.electricity\.works/types/(?P<name>[a-z0-9]+(?:[.-][a-z0-9]+)*)$"
)

NodeKey: TypeAlias = tuple[str, str, str | None]


@dataclass
class SeedDag:
    nodes: set[NodeKey]
    dependencies: dict[NodeKey, set[NodeKey]]
    upgrades: dict[NodeKey, NodeKey]

    def topo_sort(self) -> list[NodeKey]:
        return topo_sort(self.nodes, self.dependencies, self.upgrades)

    def print_edges(self) -> str:
        return format_edges(self.dependencies, self.upgrades)

    def dag_max(self) -> dict[tuple[str, str], str | None]:
        """Per-(kind, name) maximum version present in this DAG.

        This is *not* "the registry's latest_version" — it reflects only the
        versions selected into this DAG. Used by codegen for old-versions
        placement and class-name suffixing within a single generation.
        """
        return compute_dag_max(self.nodes)


def load_yaml(path: Path) -> dict:
    with path.open() as handle:
        return yaml.safe_load(handle)


def build_seed_dag(seed_path: Path, registry_path: Path = REGISTRY_PATH) -> SeedDag:
    seed = load_yaml(seed_path)
    registry = load_yaml(registry_path)
    return build_seed_dag_from_data(seed, registry)


def build_seed_dag_from_data(seed: dict, registry: dict) -> SeedDag:
    type_registry = registry["types"]
    enum_registry = registry["enums"]
    format_registry = registry["formats"]

    nodes = build_nodes_from_worklist(seed)
    dependencies: dict[NodeKey, set[NodeKey]] = {node: set() for node in nodes}
    upgrades: dict[NodeKey, NodeKey] = {}

    for node in sorted(nodes):
        node_registry_entry = resolve_registry_entry(node, type_registry, enum_registry, format_registry)
        schema_path = ROOT / schema_path_for_node(seed, node)
        schema = load_yaml(schema_path)

        for ref in extract_refs(schema):
            ref = normalize_ref(ref)
            dep = resolve_ref_to_node(ref, type_registry, enum_registry)
            if dep is None:
                continue
            if dep not in nodes:
                raise ValueError(
                    f"{node_to_string(node)} references {node_to_string(dep)} "
                    "but that node is not present in the expanded seed worklist"
                )
            dependencies[node].add(dep)

        if node[0] == "type" and node[2] is not None:
            for dep in node_registry_entry.get("direct_dependencies", {}).get("axiom", []) or []:
                dep_node = resolve_registry_dependency(dep, type_registry, enum_registry, format_registry)
                if dep_node not in nodes:
                    raise ValueError(
                        f"{node_to_string(node)} has axiom dependency {node_to_string(dep_node)} "
                        "but that node is not present in the expanded seed worklist"
                    )
                dependencies[node].add(dep_node)

    for type_name, versions in selected_type_versions(seed).items():
        ordered = sorted(versions, key=int)
        available_versions = set(type_registry[type_name]["versions"].keys())
        for current, nxt in zip(ordered, ordered[1:]):
            if current not in available_versions or nxt not in available_versions:
                raise ValueError(f"Type {type_name} has selected version not declared in registry")
            current_node: NodeKey = ("type", type_name, current)
            next_node: NodeKey = ("type", type_name, nxt)
            upgrades[current_node] = next_node

    topo_sort(nodes, dependencies, upgrades)
    return SeedDag(nodes=nodes, dependencies=dependencies, upgrades=upgrades)


def build_nodes_from_worklist(seed: dict) -> set[NodeKey]:
    nodes: set[NodeKey] = set()

    for name in seed["worklist"]["formats"]:
        nodes.add(("format", name, None))

    for name, enum_entry in seed["worklist"]["enums"].items():
        for version in sorted(normalize_worklist_versions(enum_entry), key=int):
            nodes.add(("enum", name, version))

    for name, type_entry in seed["worklist"]["types"].items():
        if type_entry.get("versioning_strategy") == "none":
            nodes.add(("type", name, None))
            continue
        for version in sorted(normalize_worklist_versions(type_entry), key=int):
            nodes.add(("type", name, version))

    return nodes


def compute_dag_max(nodes: set[NodeKey]) -> dict[tuple[str, str], str | None]:
    """Compute per-(kind, name) maximum version across DAG nodes.

    Returns a dict mapping (kind, sema_name) -> max-version-string-in-DAG.
    Versionless words map to None.

    Note: this is the DAG-local maximum, not the registry's latest_version.
    """
    dag_max: dict[tuple[str, str], str | None] = {}

    for kind, name, version in nodes:
        key = (kind, name)
        if version is None:
            dag_max[key] = None
            continue
        current = dag_max.get(key)
        if current is None or int(version) > int(current):
            dag_max[key] = version

    return dag_max


def normalize_worklist_versions(entry: dict) -> list[str]:
    versions: list[str] = []
    for key in entry:
        if isinstance(key, int):
            versions.append(f"{key:03d}")
        elif isinstance(key, str) and key.isdigit():
            versions.append(key.zfill(3))
    return versions


def selected_type_versions(seed: dict) -> dict[str, list[str]]:
    selected: dict[str, list[str]] = {}
    for name, type_entry in seed["worklist"]["types"].items():
        if type_entry.get("versioning_strategy") == "none":
            continue
        versions = normalize_worklist_versions(type_entry)
        if versions:
            selected[name] = sorted(versions, key=int)
    return selected


def resolve_registry_entry(
    node: NodeKey,
    type_registry: dict,
    enum_registry: dict,
    format_registry: dict,
) -> dict:
    category, name, version = node
    if category == "format":
        return format_registry[name]
    if category == "enum":
        enum_entry = enum_registry[name]
        if enum_entry["enum_type"] == "literal":
            return enum_entry
        if version is None:
            raise ValueError(f"Enum node missing version: {node_to_string(node)}")
        return enum_entry["versions"][version]
    if category == "type":
        type_entry = type_registry[name]
        if type_entry["versioning_strategy"] == "none":
            return type_entry
        if version is None:
            raise ValueError(f"Type node missing version: {node_to_string(node)}")
        return type_entry["versions"][version]
    raise ValueError(f"Unknown node category: {category}")


def schema_path_for_node(seed: dict, node: NodeKey) -> str:
    category, name, version = node
    if category == "format":
        return seed["worklist"]["formats"][name]["path"]
    if category == "enum":
        if version is None:
            raise ValueError(f"Enum node missing version: {node_to_string(node)}")
        return seed["worklist"]["enums"][name][version]["path"]
    if category == "type":
        type_entry = seed["worklist"]["types"][name]
        if type_entry.get("versioning_strategy") == "none":
            return type_entry["path"]
        if version is None:
            raise ValueError(f"Type node missing version: {node_to_string(node)}")
        return type_entry[version]["path"]
    raise ValueError(f"Unknown node category: {category}")


def extract_refs(node: object) -> set[str]:
    refs: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                refs.add(value)
            else:
                refs.update(extract_refs(value))
    elif isinstance(node, list):
        for item in node:
            refs.update(extract_refs(item))
    return refs


def normalize_ref(ref: str) -> str:
    ref = ref.strip()

    if ref.startswith("https://schemas.electricity.works/"):
        return ref

    if ref.startswith("/"):
        return "https://schemas.electricity.works" + ref

    if ref.startswith("types/") or ref.startswith("enums/") or ref.startswith("formats/"):
        return "https://schemas.electricity.works/" + ref

    return ref


def resolve_ref_to_node(ref: str, type_registry: dict, enum_registry: dict) -> NodeKey | None:
    format_match = FORMAT_REF_PATTERN.match(ref)
    if format_match:
        return ("format", format_match.group("name"), None)

    enum_match = ENUM_REF_PATTERN.match(ref)
    if enum_match:
        return ("enum", enum_match.group("name"), enum_match.group("version"))

    versioned_type_match = VERSIONED_TYPE_REF_PATTERN.match(ref)
    if versioned_type_match:
        return ("type", versioned_type_match.group("name"), versioned_type_match.group("version"))

    versionless_type_match = VERSIONLESS_TYPE_REF_PATTERN.match(ref)
    if versionless_type_match:
        name = versionless_type_match.group("name")
        type_entry = type_registry[name]
        if type_entry["versioning_strategy"] == "none":
            return ("type", name, None)
        latest = type_entry["latest_version"]
        return ("type", name, latest)

    return None


def resolve_registry_dependency(
    dep: str,
    type_registry: dict,
    enum_registry: dict,
    format_registry: dict,
) -> NodeKey:
    if ":" in dep:
        name, version = dep.rsplit(":", 1)
        if name in type_registry:
            return ("type", name, version)
        if name in enum_registry:
            return ("enum", name, version)
        raise ValueError(f"Unknown versioned dependency: {dep}")
    if dep in format_registry:
        return ("format", dep, None)
    if dep in type_registry and type_registry[dep].get("versioning_strategy") == "none":
        return ("type", dep, None)
    if dep in enum_registry:
        raise ValueError(f"Enum dependency missing version: {dep}")
    if dep in type_registry:
        raise ValueError(f"Versioned type dependency missing version: {dep}")
    raise ValueError(f"Unknown dependency: {dep}")


def topo_sort(
    nodes: set[NodeKey],
    dependencies: dict[NodeKey, set[NodeKey]],
    upgrades: dict[NodeKey, NodeKey],
) -> list[NodeKey]:
    outgoing: dict[NodeKey, set[NodeKey]] = {node: set() for node in nodes}
    indegree: dict[NodeKey, int] = {node: 0 for node in nodes}

    for source, deps in dependencies.items():
        for dep in deps:
            outgoing[dep].add(source)
            indegree[source] += 1

    for source, target in upgrades.items():
        outgoing[source].add(target)
        indegree[target] += 1

    queue = deque(sorted([node for node in nodes if indegree[node] == 0]))
    ordered: list[NodeKey] = []

    while queue:
        node = queue.popleft()
        ordered.append(node)
        for nxt in sorted(outgoing[node]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    if len(ordered) != len(nodes):
        remaining = sorted(node_to_string(node) for node, degree in indegree.items() if degree > 0)
        raise ValueError("Graph is not a DAG; cycle detected involving: " + ", ".join(remaining))

    return ordered


def format_edges(dependencies: dict[NodeKey, set[NodeKey]], upgrades: dict[NodeKey, NodeKey]) -> str:
    lines: list[str] = ["Dependencies:"]
    for node in sorted(dependencies):
        deps = sorted(dependencies[node])
        if not deps:
            continue
        lines.append(f"  {node_to_string(node)}")
        for dep in deps:
            lines.append(f"    -> {node_to_string(dep)}")

    lines.append("")
    lines.append("Upgrades:")
    for source in sorted(upgrades):
        lines.append(f"  {node_to_string(source)} -> {node_to_string(upgrades[source])}")

    return "\n".join(lines)


def node_to_string(node: NodeKey) -> str:
    category, name, version = node
    if version is None:
        return f"{category}:{name}"
    return f"{category}:{name}:{version}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a seed-scoped DAG from an expanded seed worklist using schema $ref "
            "dependencies, registry axiom dependencies, and type upgrade edges."
        )
    )
    parser.add_argument("seed", type=Path, nargs="?", default=DEFAULT_SEED)
    parser.add_argument("--print-edges", action="store_true")
    parser.add_argument("--print-topo", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dag = build_seed_dag(args.seed.resolve())
    print(f"Built DAG with {len(dag.nodes)} nodes")
    if args.print_edges:
        print(dag.print_edges())
    if args.print_topo:
        print("Topological order:")
        for node in dag.topo_sort():
            print(f"  {node_to_string(node)}")


if __name__ == "__main__":
    main()
