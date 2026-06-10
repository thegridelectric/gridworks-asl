from pathlib import Path

from sema.tools.runtime_generation.generate_runtime import _write_base, _write_codec
from sema.tools.snapshot_lint import format_in_place


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = ROOT / "src" / "sema" / "runtime"


def normalize_runtime_import_root(text: str) -> str:
    return text.replace("sema.runtime.sema", "sema.runtime")


def test_generated_base_matches_runtime_base(tmp_path: Path) -> None:
    _write_base(tmp_path)
    format_in_place(tmp_path)

    assert (tmp_path / "base.py").read_text() == (
        RUNTIME_ROOT / "base.py"
    ).read_text()


def test_generated_codec_matches_runtime_codec(tmp_path: Path) -> None:
    _write_codec(tmp_path, "sema.runtime")
    format_in_place(tmp_path)

    generated = normalize_runtime_import_root((tmp_path / "codec.py").read_text())
    assert generated == (RUNTIME_ROOT / "codec.py").read_text()
