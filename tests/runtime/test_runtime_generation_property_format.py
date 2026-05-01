from dataclasses import dataclass
from pathlib import Path

from sema.tools.runtime_generation.formats import generate_formats


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class FormatOnlyDag:
    formats: list[str]

    def topo_sort(self) -> list[tuple[str, str, None]]:
        return [("format", name, None) for name in self.formats]


def test_generated_property_format_matches_runtime_property_format(tmp_path: Path) -> None:
    format_names = sorted(
        path.stem for path in (REPO_ROOT / "definitions" / "formats").glob("*.yaml")
    )
    seed = {
        "worklist": {
            "formats": {
                name: {"path": f"definitions/formats/{name}.yaml"}
                for name in format_names
            }
        }
    }
    target_root = tmp_path / "sema" / "runtime"

    generate_formats(
        target_root,
        FormatOnlyDag(format_names),
        seed,
        REPO_ROOT / "definitions",
    )

    generated = (target_root / "property_format.py").read_text()
    checked_in = (REPO_ROOT / "src" / "sema" / "runtime" / "property_format.py").read_text()
    assert generated == checked_in


def test_generate_formats_writes_snapshot_property_format_test(tmp_path: Path) -> None:
    format_names = ["left.right.dot", "positive.int"]
    seed = {
        "worklist": {
            "formats": {
                name: {"path": f"definitions/formats/{name}.yaml"}
                for name in format_names
            }
        }
    }
    target_root = tmp_path / "sema" / "runtime"

    generate_formats(
        target_root,
        FormatOnlyDag(format_names),
        seed,
        REPO_ROOT / "definitions",
    )

    generated_test = (target_root / "tests" / "test_property_format.py").read_text()
    assert 'DEFINITIONS_DIR / "formats" / "left.right.dot.yaml"' in generated_test
    assert 'DEFINITIONS_DIR / "formats" / "positive.int.yaml"' in generated_test
    assert "utc.seconds.yaml" not in generated_test
    assert '"left.right.dot": property_format.LeftRightDot' in generated_test
    assert '"positive.int": property_format.PositiveInt' in generated_test
