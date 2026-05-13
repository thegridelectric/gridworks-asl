from pathlib import Path

import pytest
import yaml


LOOKUP_PATH = Path("indexes/lookup.yaml")


def load_yaml_file(path: Path) -> dict:
    with path.open("r") as handle:
        return yaml.safe_load(handle)


@pytest.fixture(scope="session")
def all_schemas() -> dict:
    lookup = load_yaml_file(LOOKUP_PATH)
    schemas = {}

    paths: list[Path] = []
    paths.extend(Path(path) for path in lookup["formats"].values())
    for entry in lookup["enums"].values():
        if "schema" in entry:
            paths.append(Path(entry["schema"]))
        else:
            paths.extend(Path(path) for path in entry["versions"].values())
    for entry in lookup["types"].values():
        if "schema" in entry:
            paths.append(Path(entry["schema"]))
        else:
            paths.extend(Path(path) for path in entry["versions"].values())

    for path in sorted(paths):
        schema = load_yaml_file(path)

        name = schema.get("title") or path.stem
        schemas[name] = schema

    return schemas
