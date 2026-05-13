# runtime_generation/formats.py

from __future__ import annotations

from sema.tools.runtime_generation.helpers import load_schema_for_node
from sema.tools.runtime_generation.templates.format import FORMAT_TEMPLATES


BASE_IMPORTS = [
    "import re",
    "from typing import Annotated",
    "from pydantic import BeforeValidator",
]


def _pattern_const_name(format_name: str) -> str:
    return format_name.upper().replace(".", "_") + "_PATTERN"


def _render_imports(imports: set[str]) -> str:
    plain_imports: list[str] = []
    from_imports: dict[str, set[str]] = {}
    for imp in imports:
        if imp.startswith("import "):
            plain_imports.append(imp)
            continue
        if not imp.startswith("from "):
            plain_imports.append(imp)
            continue
        module, names = imp.removeprefix("from ").split(" import ", 1)
        from_imports.setdefault(module, set()).update(
            name.strip() for name in names.split(",")
        )

    stdlib_lines = sorted(plain_imports)
    third_party_lines: list[str] = []
    for module in sorted(from_imports):
        names = ", ".join(sorted(from_imports[module]))
        line = f"from {module} import {names}"
        if module == "pydantic":
            third_party_lines.append(line)
        else:
            stdlib_lines.append(line)

    if third_party_lines:
        return "\n".join(stdlib_lines + [""] + sorted(third_party_lines))
    return "\n".join(stdlib_lines)


def generate_property_format(formats, schemas) -> str:
    """
    formats: list[str]
    schemas: dict[str, dict]  # expects {"pattern": "..."} optionally
    """

    formats = sorted(formats)

    imports = set(BASE_IMPORTS)
    pattern_lines: list[str] = []
    method_blocks: list[str] = []
    annotated_blocks: list[str] = []
    helper_blocks: list[str] = []

    for name in formats:
        if name not in FORMAT_TEMPLATES:
            raise ValueError(f"Missing template for format: {name}")

        spec = FORMAT_TEMPLATES[name]

        # required
        if "methods" not in spec or "annotated_type" not in spec:
            raise ValueError(f"Incomplete template for format: {name}")

        # imports
        for imp in spec.get("imports", []):
            imports.add(imp)

        # pattern (schema overrides template)
        schema_pattern = schemas.get(name, {}).get("pattern")
        pattern = schema_pattern or spec.get("pattern")

        if pattern:
            const_name = _pattern_const_name(name)
            pattern_lines.append(
                f"{const_name} = re.compile(\n"
                f"    r\"{pattern}\"\n"
                ")"
            )

        # sections
        methods = spec["methods"].strip()
        if methods:
            method_blocks.append(methods)
        annotated_blocks.append(spec["annotated_type"].strip())

        if "helpers" in spec:
            helper_blocks.append(spec["helpers"].strip())

    # assemble
    parts = []

    # imports
    parts.append(_render_imports(imports))

    # patterns
    if pattern_lines:
        parts.append("# --- patterns ---\n" + "\n\n".join(pattern_lines))

    # methods
    if method_blocks:
        parts.append("# --- methods ---\n" + "\n\n\n".join(method_blocks))

    # annotated types
    parts.append("# --- annotated types ---\n" + "\n\n".join(annotated_blocks))

    # helpers
    if helper_blocks:
        parts.append("# --- helpers ---\n" + "\n\n\n".join(helper_blocks))

    return "\n\n\n".join(parts) + "\n"


def generate_property_format_test(formats, import_root: str = "sema.runtime") -> str:
    formats = sorted(formats)
    mapping_lines = [
        f'    "{name}": property_format.{FORMAT_TEMPLATES[name]["class_name"]},'
        for name in formats
    ]
    schema_path_lines = [
        f'    DEFINITIONS_DIR / "formats" / "{name}.yaml",'
        for name in formats
    ]
    return (
        "from pathlib import Path\n"
        "from typing import Any\n"
        "\n"
        "import pytest\n"
        "import yaml\n"
        "from pydantic import TypeAdapter, ValidationError\n"
        "\n"
        f"from {import_root} import property_format\n"
        "\n"
        "\n"
        "PACKAGE_ROOT = Path(__file__).resolve().parents[1]\n"
        'DEFINITIONS_DIR = PACKAGE_ROOT / "definitions"\n'
        "FORMAT_SCHEMA_PATHS = [\n"
        + "\n".join(schema_path_lines)
        + "\n]\n"
        "RUNTIME_FORMAT_TYPES: dict[str, Any] = {\n"
        + "\n".join(mapping_lines)
        + "\n}\n"
        "\n"
        "\n"
        "def load_yaml(path: Path) -> dict[str, Any]:\n"
        "    return yaml.safe_load(path.read_text())\n"
        "\n"
        "\n"
        "def format_adapter(format_name: str) -> TypeAdapter:\n"
        "    return TypeAdapter(RUNTIME_FORMAT_TYPES[format_name])\n"
        "\n"
        "\n"
        '@pytest.mark.parametrize("schema_path", FORMAT_SCHEMA_PATHS)\n'
        "def test_property_format_schema_examples_validate(schema_path: Path) -> None:\n"
        "    schema = load_yaml(schema_path)\n"
        '    adapter = format_adapter(schema["title"])\n'
        "\n"
        '    for example in schema.get("examples", []):\n'
        "        assert adapter.validate_python(example) == example\n"
        "\n"
        "\n"
        '@pytest.mark.parametrize("schema_path", FORMAT_SCHEMA_PATHS)\n'
        "def test_property_format_schema_counterexamples_fail(schema_path: Path) -> None:\n"
        "    schema = load_yaml(schema_path)\n"
        '    adapter = format_adapter(schema["title"])\n'
        "\n"
        '    for counterexample in schema.get("counterexamples", []):\n'
        "        with pytest.raises((TypeError, ValueError, ValidationError)):\n"
        "            adapter.validate_python(counterexample)\n"
    )


def generate_formats(
    target_root,
    dag,
    seed=None,
    import_root: str = "sema.runtime",
    write_tests: bool = False,
) -> None:
    if seed is None:
        return

    formats: list[str] = []
    schemas: dict[str, dict] = {}
    for node in dag.topo_sort():
        if node[0] != "format":
            continue
        _, name, _ = node
        formats.append(name)
        schemas[name] = load_schema_for_node(node, seed)

    target_root.mkdir(parents=True, exist_ok=True)
    (target_root / "property_format.py").write_text(
        generate_property_format(formats, schemas)
    )
    if write_tests:
        (target_root / "tests").mkdir(parents=True, exist_ok=True)
        (target_root / "tests" / "test_property_format.py").write_text(
            generate_property_format_test(formats, import_root)
        )
