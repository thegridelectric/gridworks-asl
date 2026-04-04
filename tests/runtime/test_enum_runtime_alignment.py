from importlib import import_module
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "definitions" / "registry.yaml"
ENUMS_DIR = ROOT / "definitions" / "enums"


def load_registry() -> dict:
    return yaml.safe_load(REGISTRY_PATH.read_text())


def load_enum_schema(enum_name: str, version: str) -> dict:
    path = ENUMS_DIR / enum_name / f"{version}.yaml"
    return yaml.safe_load(path.read_text())


def load_current_runtime_enum(enum_name: str):
    module_name = enum_name.replace(".", "_").replace("-", "_")
    module = import_module(f"sema.runtime.enums.{module_name}")
    for attr_name in dir(module):
        obj = getattr(module, attr_name)
        if (
            isinstance(obj, type)
            and hasattr(obj, "enum_name")
            and hasattr(obj, "enum_version")
        ):
            try:
                if obj.__module__ == module.__name__ and obj.enum_name() == enum_name:
                    return obj
            except NotImplementedError:
                continue
    raise AssertionError(f"Could not find current runtime enum for {enum_name}")


def load_old_runtime_enum(enum_name: str, version: str):
    module_name = enum_name.replace(".", "_").replace("-", "_")
    module = import_module(f"sema.runtime.enums.old_versions.{module_name}_{version}")
    for attr_name in dir(module):
        obj = getattr(module, attr_name)
        if (
            isinstance(obj, type)
            and hasattr(obj, "enum_name")
            and hasattr(obj, "enum_version")
        ):
            try:
                if (
                    obj.__module__ == module.__name__
                    and obj.enum_name() == enum_name
                    and obj.enum_version() == version
                ):
                    return obj
            except NotImplementedError:
                continue
    raise AssertionError(
        f"Could not find old runtime enum for {enum_name}:{version}"
    )


def test_enum_runtime_matches_schema() -> None:
    registry = load_registry()
    problems: list[str] = []

    for enum_name, enum_entry in registry["enums"].items():
        if enum_entry["enum_type"] == "literal":
            schema = load_enum_schema(enum_name, "000")
            try:
                enum_cls = load_current_runtime_enum(enum_name)
            except ModuleNotFoundError:
                problems.append(
                    f"missing current runtime enum module for {enum_name}:000"
                )
                continue
            except AssertionError as e:
                problems.append(str(e))
                continue
            if set(enum_cls.values()) != set(schema["enum"]):
                problems.append(f"{enum_name}:000 runtime values do not match schema")
            if enum_cls.enum_version() != "000":
                problems.append(
                    f"{enum_name}:000 runtime enum_version is {enum_cls.enum_version()}"
                )
            continue

        latest_version = enum_entry["latest_version"]
        schema = load_enum_schema(enum_name, latest_version)
        try:
            enum_cls = load_current_runtime_enum(enum_name)
        except ModuleNotFoundError:
            problems.append(
                f"missing current runtime enum module for {enum_name}:{latest_version}"
            )
            continue
        except AssertionError as e:
            problems.append(str(e))
            continue
        if set(enum_cls.values()) != set(schema["enum"]):
            problems.append(
                f"{enum_name}:{latest_version} runtime values do not match schema"
            )
        if enum_cls.enum_version() != latest_version:
            problems.append(
                f"{enum_name}:{latest_version} runtime enum_version is {enum_cls.enum_version()}"
            )

        for version in enum_entry["versions"]:
            if version == latest_version:
                continue
            path = ENUMS_DIR / enum_name / f"{version}.yaml"
            old_module_path = (
                ROOT
                / "src"
                / "sema"
                / "runtime"
                / "enums"
                / "old_versions"
                / f"{enum_name.replace('.', '_').replace('-', '_')}_{version}.py"
            )
            if not path.exists() or not old_module_path.exists():
                continue
            schema = load_enum_schema(enum_name, version)
            try:
                enum_cls = load_old_runtime_enum(enum_name, version)
            except (ModuleNotFoundError, AssertionError) as e:
                problems.append(str(e))
                continue
            if set(enum_cls.values()) != set(schema["enum"]):
                problems.append(
                    f"{enum_name}:{version} old runtime values do not match schema"
                )
            if enum_cls.enum_version() != version:
                problems.append(
                    f"{enum_name}:{version} old runtime enum_version is {enum_cls.enum_version()}"
                )

    assert not problems, "\n" + "\n".join(f"- {p}" for p in problems)
