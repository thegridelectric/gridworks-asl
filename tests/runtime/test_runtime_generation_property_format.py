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
        import_root="sema.runtime",
    )

    generated = (target_root / "property_format.py").read_text()
    checked_in = (REPO_ROOT / "src" / "sema" / "runtime" / "property_format.py").read_text()
    assert generated == checked_in
