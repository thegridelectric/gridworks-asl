from __future__ import annotations

from pathlib import Path

from sema.tools.build_seed_dag import build_seed_dag_from_data
from sema.tools.runtime_generation.enums import generate_enums
from sema.tools.runtime_generation.formats import generate_formats
from sema.tools.runtime_generation.helpers import load_local_names_yaml
from sema.tools.runtime_generation.types import generate_types


RUNTIME_INIT = '''"""
Generated snapshot runtime package.
"""
'''


def _ensure_package_layout(target_root) -> None:
    (target_root / "enums" / "old_versions").mkdir(parents=True, exist_ok=True)
    (target_root / "types" / "old_versions").mkdir(parents=True, exist_ok=True)
    (target_root / "__init__.py").write_text(RUNTIME_INIT)


def _write_codec(target_root, package_name: str) -> None:
    (target_root / "codec.py").write_text(
        f'''import json
from importlib import import_module
from pathlib import Path
from typing import Literal

from {package_name}.sema.base import SemaError, SemaType, recursively_pascal


class SemaCodec:
    def __init__(self) -> None:
        self.registry = get_current_types()
        self.old_versions = get_old_versions()

    def from_dict(
        self,
        data: dict,
        mode: Literal["strict", "degraded"] = "strict",
        auto_upgrade: bool = True,
    ) -> SemaType:
        if mode != "strict":
            raise ValueError("Generated snapshot codec only supports strict mode")
        if not isinstance(data, dict):
            raise ValueError("Input must be dict")
        if "TypeName" not in data:
            raise ValueError("Missing TypeName")
        if not recursively_pascal(data := dict(data)):
            raise ValueError("Input must be PascalCase")

        type_name = data["TypeName"]
        version = data.get("Version")
        if type_name not in self.registry:
            raise ValueError(f"Unknown type {{type_name}}")

        current_cls = self.registry[type_name]
        if version == current_cls.version_value():
            return current_cls.from_dict(data)

        old_cls = self.old_versions.get(type_name, {{}}).get(version)
        if old_cls is None:
            raise ValueError(f"Unsupported version {{version}} for {{type_name}}")

        old_instance = old_cls.from_dict(data)
        return old_instance.upgrade() if auto_upgrade else old_instance

    def from_bytes(self, data: bytes) -> SemaType:
        try:
            decoded = json.loads(data.decode("utf-8"))
        except Exception as e:
            raise SemaError(f"Invalid JSON: {{e}}") from e
        return self.from_dict(decoded)

    def to_bytes(self, msg: SemaType) -> bytes:
        return msg.to_bytes()


def _sema_type_classes(module_name: str) -> list[type[SemaType]]:
    module = import_module(module_name)
    classes: list[type[SemaType]] = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, SemaType) and obj is not SemaType:
            classes.append(obj)
    return classes


def get_current_types() -> dict[str, type[SemaType]]:
    registry: dict[str, type[SemaType]] = {{}}
    types_dir = Path(__file__).resolve().parent / "types"
    for path in sorted(types_dir.glob("*.py")):
        if path.stem == "__init__":
            continue
        module_name = f"{package_name}.sema.types.{{path.stem}}"
        for cls in _sema_type_classes(module_name):
            registry[cls.type_name_value()] = cls
    return registry


def get_old_versions() -> dict[str, dict[str | None, type[SemaType]]]:
    registry: dict[str, dict[str | None, type[SemaType]]] = {{}}
    old_versions_dir = Path(__file__).resolve().parent / "types" / "old_versions"
    for path in sorted(old_versions_dir.glob("*.py")):
        if path.stem == "__init__":
            continue
        module_name = f"{package_name}.sema.types.old_versions.{{path.stem}}"
        for cls in _sema_type_classes(module_name):
            registry.setdefault(cls.type_name_value(), {{}})[cls.version_value()] = cls
    return registry


default_codec = SemaCodec()
'''
    )


def generate_runtime_from_dag(
    target_root,
    seed,
    registry,
    definitions_root=None,
    package_name="gjk",
    local_names=None,
):
    dag = build_seed_dag_from_data(seed, registry)
    latest = dag.latest_in_dag()
    if isinstance(local_names, str | Path):
        local_names = load_local_names_yaml(Path(local_names))

    _ensure_package_layout(target_root)

    generate_formats(target_root, dag, seed, definitions_root)
    generate_enums(
        target_root,
        dag,
        latest,
        seed,
        definitions_root,
        package_name,
        local_names,
    )
    _write_codec(target_root, package_name)
    generate_types(
        target_root,
        dag,
        latest,
        seed,
        registry,
        definitions_root,
        package_name,
        local_names,
    )
