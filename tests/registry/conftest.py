from pathlib import Path

import pytest
import yaml


LOOKUP_PATH = Path("indexes/lookup.yaml")


def load_yaml_file(path: Path) -> dict:
    with path.open("r") as handle:
        return yaml.safe_load(handle)


def _key_from_id(sid: str, fallback: str) -> str:
    """Derive a short, unique, diagnostic key from a schema's `$id`.

    Examples
    --------
    - `.../formats/uuid4.str`       -> `uuid4.str`
    - `.../enums/sh.actor.role/000` -> `sh.actor.role:000`
    - `.../types/bid/000`           -> `bid:000`
    - `.../types/gw` (versionless)  -> `gw`

    Falls back to ``fallback`` (typically the file path or stem) if the
    `$id` is missing or doesn't match a known shape.
    """
    if not isinstance(sid, str) or not sid:
        return fallback
    for prefix in ("/formats/", "/enums/", "/types/"):
        if prefix in sid:
            tail = sid.split(prefix, 1)[1]
            return tail.replace("/", ":")
    return fallback


DEFINITIONS_DIR = Path("definitions")


@pytest.fixture(scope="session")
def all_schemas() -> dict:
    """Every schema file on the filesystem under `definitions/`.

    Includes published, draft, and registry-orphan
    schemas. Per the spec, draft schemas relax immutability and some
    completeness checks but MUST still be well-formed Sema schemas;
    orphan files (present on disk but not in `registry.yaml`) are also
    in scope because a broken schema file is a broken schema file
    regardless of registration status.

    Keys are short canonical identifiers derived from `$id` (e.g.,
    `bid:000`, `gw`, `uuid4.str`). For schemas whose `$id` includes a
    `/draft/` segment the key still drops the `draft/` prefix, so an
    published and draft schemas of the same name+version would collide
    (which would be a registry inconsistency the duplicate-key check
    surfaces).
    """
    schemas: dict[str, dict] = {}

    paths: list[Path] = []
    paths.extend(sorted(DEFINITIONS_DIR.glob("formats/*.yaml")))
    paths.extend(sorted(DEFINITIONS_DIR.glob("enums/*/*.yaml")))
    paths.extend(sorted(DEFINITIONS_DIR.glob("types/*.yaml")))
    paths.extend(sorted(DEFINITIONS_DIR.glob("types/*/*.yaml")))

    for path in paths:
        schema = load_yaml_file(path)
        if not isinstance(schema, dict):
            raise RuntimeError(f"{path}: schema file does not parse to a mapping")
        key = _key_from_id(schema.get("$id", ""), fallback=str(path))
        if key in schemas:
            raise RuntimeError(
                f"all_schemas: duplicate key {key!r} (path={path}); "
                f"two schemas claim the same canonical identifier."
            )
        schemas[key] = schema

    return schemas
